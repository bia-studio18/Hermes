from __future__ import annotations

import logging
import threading
import time
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any

logger = logging.getLogger(__name__)

JobFn = Callable[..., Any]


def _cron_field(pattern: str, low: int, high: int) -> set[int]:
    result: set[int] = set()

    for part in pattern.split(","):
        part = part.strip()

        if "/" in part:
            base, step_str = part.split("/", 1)
            step = int(step_str)

            if step <= 0:
                raise ValueError("cron step must be > 0")

            if base == "*":
                values = range(low, high + 1)
            elif "-" in base:
                start, end = map(int, base.split("-", 1))
                values = range(start, end + 1)
            else:
                start = int(base)
                values = range(start, high + 1)

            result.update(value for index, value in enumerate(values) if index % step == 0)

        elif "-" in part:
            start, end = map(int, part.split("-", 1))
            result.update(range(start, end + 1))

        elif part == "*":
            result.update(range(low, high + 1))

        else:
            result.add(int(part))

    invalid = result - set(range(low, high + 1))
    if invalid:
        raise ValueError(f"cron values {invalid} outside range {low}-{high}")

    return result


def _parse_cron(
    expr: str,
) -> tuple[set[int], set[int], set[int], set[int], set[int]]:
    parts = expr.split()

    if len(parts) != 5:
        raise ValueError(f"cron must have 5 fields, got {len(parts)}: {expr!r}")

    return (
        _cron_field(parts[0], 0, 59),
        _cron_field(parts[1], 0, 23),
        _cron_field(parts[2], 1, 31),
        _cron_field(parts[3], 1, 12),
        _cron_field(parts[4], 0, 6),
    )


def _cron_matches(
    dt: datetime,
    cron: tuple[set[int], set[int], set[int], set[int], set[int]],
) -> bool:
    minutes, hours, days, months, weekdays = cron
    cron_weekday = (dt.weekday() + 1) % 7

    return (
        dt.minute in minutes and dt.hour in hours and dt.day in days and dt.month in months and cron_weekday in weekdays
    )


def _next_cron_dt(
    cron_expr: str,
    now: datetime,
    parsed: tuple | None = None,
) -> datetime:
    cron = parsed or _parse_cron(cron_expr)

    candidate = (now + timedelta(minutes=1)).replace(
        second=0,
        microsecond=0,
    )

    for _ in range(366 * 24 * 60):
        if _cron_matches(candidate, cron):
            return candidate

        candidate += timedelta(minutes=1)

    raise ValueError(f"No cron match found for {cron_expr!r}")


ALIASES = {
    "hourly": timedelta(hours=1),
    "daily": timedelta(days=1),
    "weekly": timedelta(weeks=1),
}


def _is_cron(spec: str) -> bool:
    return len(spec.split()) == 5


def _parse_interval(spec: str) -> timedelta | None:
    spec = spec.lower()

    if spec in ALIASES:
        return ALIASES[spec]

    if len(spec) > 1 and spec[-1] in "mhdw":
        value = spec[:-1]

        if value.isdigit():
            units = {
                "m": timedelta(minutes=1),
                "h": timedelta(hours=1),
                "d": timedelta(days=1),
                "w": timedelta(weeks=1),
            }
            return int(value) * units[spec[-1]]

    return None


@dataclass(slots=True)
class _Job:
    name: str
    fn: JobFn
    spec: str
    timeout: float = 300.0
    retries: int = 2
    last_run: datetime | None = None
    next_run_at: datetime | None = None
    last_status: str = "pending"
    runs: int = 0
    failures: int = 0
    error: str | None = None
    interval: timedelta | None = field(init=False, default=None)
    cron: tuple | None = field(init=False, default=None)

    def __post_init__(self) -> None:
        self.interval = _parse_interval(self.spec)

        if self.interval is None:
            if not _is_cron(self.spec):
                raise ValueError(f"Unsupported schedule spec: {self.spec!r}")
            self.cron = _parse_cron(self.spec)

    def calculate_next_run(self, now: datetime) -> datetime:
        if self.interval is not None:
            return now + self.interval

        if self.cron is None:
            raise ValueError("self.cron must be set before this operation")

        return _next_cron_dt(
            self.spec,
            now,
            self.cron,
        )


_registry: dict[str, _Job] = {}
_running = False
_stop_event = threading.Event()
_loop_thread: threading.Thread | None = None
# ponytail: single condition variable guards _registry; add per-job locks if jobs run concurrently
_cond = threading.Condition()


def schedule(
    *,
    time: str,
    name: str | None = None,
    timeout: float = 300.0,
    retries: int = 2,
) -> Callable[[JobFn], JobFn]:

    if timeout <= 0:
        raise ValueError("timeout must be > 0")

    if retries < 0:
        raise ValueError("retries must be >= 0")

    def decorator(fn: JobFn) -> JobFn:
        job_name = name or fn.__name__

        if job_name in _registry:
            raise ValueError(f"Job {job_name!r} already registered")

        _registry[job_name] = _Job(
            name=job_name,
            fn=fn,
            spec=time.strip().lower(),
            timeout=timeout,
            retries=retries,
        )

        return fn

    return decorator


def _execute(job: _Job) -> None:
    job.fn()


def _run_job(job: _Job) -> None:
    job.last_status = "running"
    job.error = None

    started = datetime.now()

    for attempt in range(job.retries + 1):
        try:
            _execute(job)

            job.last_status = "success"
            job.last_run = started
            job.runs += 1
            job.next_run_at = job.calculate_next_run(datetime.now())
            return

        except Exception as exc:
            job.error = str(exc)

            if attempt < job.retries:
                time.sleep(min(2**attempt, 60))

    job.last_status = "failed"
    job.last_run = started
    job.runs += 1
    job.failures += 1
    job.next_run_at = job.calculate_next_run(datetime.now())

    logger.exception(
        "Job %s failed after %d attempts",
        job.name,
        job.retries + 1,
    )


def _loop() -> None:
    global _running

    _running = True
    now = datetime.now()

    for job in _registry.values():
        job.next_run_at = now

    while _running:
        now = datetime.now()

        due = [
            job
            for job in _registry.values()
            if (job.next_run_at is not None and job.next_run_at <= now and job.last_status != "running")
        ]

        for job in due:
            _run_job(job)

        next_times = [job.next_run_at for job in _registry.values() if job.next_run_at is not None]

        if not next_times:
            _stop_event.wait(1)
            continue

        delay = max(
            0.1,
            min((next_time - now).total_seconds() for next_time in next_times),
        )

        _stop_event.wait(min(delay, 60))


def start() -> None:
    global _loop_thread

    _loop_thread = threading.Thread(target=_loop, daemon=True)
    _loop_thread.start()

    try:
        _stop_event.wait()
    except KeyboardInterrupt:
        pass
    finally:
        stop()
        if _loop_thread:
            _loop_thread.join()


def stop() -> None:
    global _running

    _running = False
    _stop_event.set()


def run_now(name: str | None = None) -> None:
    if name is None:
        jobs = list(_registry.values())
    else:
        if name not in _registry:
            raise KeyError(f"Unknown job: {name!r}")

        jobs = [_registry[name]]

    for job in jobs:
        _run_job(job)


def list_jobs() -> list[dict[str, Any]]:
    return [
        {
            "name": job.name,
            "schedule": job.spec,
            "next_run": (job.next_run_at.isoformat() if job.next_run_at else None),
            "last_run": (job.last_run.isoformat() if job.last_run else None),
            "last_status": job.last_status,
            "runs": job.runs,
            "failures": job.failures,
            "error": job.error,
        }
        for job in _registry.values()
    ]
