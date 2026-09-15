from __future__ import annotations

import json
import logging
from collections.abc import Callable
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

DEFAULT_STATE_DIR = Path.home() / ".hermes" / "sync"


class ChangeReport(BaseModel):
    """Result of :meth:`SyncEngine.detect_changes`."""

    added: int = 0
    removed: int = 0
    modified: int = 0
    unchanged: int = 0
    total_previous: int = 0
    total_current: int = 0


class SyncState(BaseModel):
    """Persisted state describing the last successful synchronization.

    Attributes:
        source: Logical name of the source being synchronized.
        last_sync: ISO timestamp of the last successful sync.
        cursor: Source-specific cursor/token left at the last successful sync.
        hashes: Optional map of record key → content hash for change detection.
    """

    source: str
    last_sync: datetime | None = None
    cursor: Any | None = None
    hashes: dict[str, str] = Field(default_factory=dict)

    def update(self, cursor: object | None = None) -> SyncState:
        """Record a successful sync at the current time with an optional cursor."""
        self.last_sync = datetime.now(UTC)
        if cursor is not None:
            self.cursor = cursor
        return self

    def needs_sync(self, interval: str | timedelta) -> bool:
        """Return ``True`` if *interval* has elapsed since the last sync.

        ``interval`` can be a ``timedelta`` or a string like ``"1h"``, ``"24h"``,
        ``"1d"``, ``"30m"``.
        """
        if self.last_sync is None:
            return True
        delta = _parse_interval(interval)
        age = datetime.now(UTC) - self.last_sync
        return age >= delta

    def get_cursor(self) -> object | None:
        """Return the stored cursor (``None`` when no cursor is recorded)."""
        return self.cursor

    # -- persistence -------------------------------------------------------

    def save(self, path: str | Path | None = None) -> Path:
        """Persist the state to ``path`` (default: ``~/.hermes/sync/<source>.json``)."""
        target = Path(path) if path else DEFAULT_STATE_DIR / f"{self.source}.json"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(self.model_dump_json(indent=2))
        return target

    @classmethod
    def load(cls, source: str, path: str | Path | None = None) -> SyncState | None:
        """Load a persisted state for *source*, or ``None`` if absent/unreadable."""
        target = Path(path) if path else DEFAULT_STATE_DIR / f"{source}.json"
        if not target.exists():
            return None
        try:
            return cls.model_validate_json(target.read_text())
        except (json.JSONDecodeError, ValueError) as exc:
            logger.warning("Corrupt sync state at %s: %s", target, exc)
            return None


class SyncEngine:
    """Orchestrate full and incremental synchronization of a data source.

    ``fetch_fn`` is an async callable returning the fetched data. For
    incremental fetches it is additionally called with a ``since`` keyword
    argument (a ``datetime`` or the stored cursor) so the caller can honour
    timestamp/cursor-based incremental APIs.

    Usage::

        async def fetch(since=None):
            if since is not None:
                ...  # fetch only records newer than `since`
            return df

        engine = SyncEngine("world_bank", fetch)
        report = await engine.sync(state_path="sync-state.json")
    """

    def __init__(
        self,
        source: str,
        fetch_fn: Callable[..., Any],
        state: SyncState | None = None,
    ) -> None:
        self.source = source
        self.fetch_fn = fetch_fn
        self.state = state or SyncState(source=source)

    # -- public API --------------------------------------------------------

    async def sync(
        self,
        *,
        interval: str | timedelta | None = None,
        force: bool = False,
        state_path: str | Path | None = None,
        **kwargs: Any,
    ) -> tuple[Any, ChangeReport, SyncState]:
        """Perform an incremental sync if due, otherwise conditionally a full sync.

        When ``interval`` is given and the last sync is newer than the interval,
        no fetch is performed: the existing data fanout is preserved. Pass
        ``force=True`` to always fetch, or rely on :meth:`incremental_sync` /
        :meth:`full_sync` for explicit behaviour.
        """
        if interval is not None and not force and not self.state.needs_sync(interval):
            logger.info("Sync of %s not due (interval=%s)", self.source, interval)
            return None, ChangeReport(), self.state

        if self.state.cursor is not None and not force:
            return await self.incremental_sync(state_path=state_path, **kwargs)
        return await self.full_sync(state_path=state_path, **kwargs)

    async def incremental_sync(
        self,
        *,
        state_path: str | Path | None = None,
        **kwargs: Any,
    ) -> tuple[Any, ChangeReport, SyncState]:
        """Fetch only records that have changed since the last successful sync."""
        previous = self.state.cursor
        data = await self.fetch_fn(since=previous, **kwargs)
        report = (
            self.detect_changes(previous_state=self.state, current=data)
            if previous is not None
            else ChangeReport(total_current=_count(data))
        )
        self.state.update(cursor=previous)
        if state_path is not None:
            self._persist(state_path)
        return data, report, self.state

    async def full_sync(
        self,
        *,
        cursor: object | None = None,
        state_path: str | Path | None = None,
        **kwargs: Any,
    ) -> tuple[Any, ChangeReport, SyncState]:
        """Re-fetch the entire dataset from the source."""
        previous_state = self.state.model_copy(deep=True)
        data = await self.fetch_fn(**kwargs)
        report = self.detect_changes(previous_state=previous_state, current=data)
        self.state.update(cursor=cursor)
        if state_path is not None:
            self._persist(state_path)
        return data, report, self.state

    def detect_changes(
        self,
        *,
        current: Any,
        key: str | None = None,
        previous_state: SyncState | None = None,
    ) -> ChangeReport:
        """Diff ``current`` data against a previous snapshot/state.

        When ``previous_state.hashes`` is populated, the diff is exact
        (added/removed/modified per record keyed by *key*). Otherwise the
        report only carries totals.

        Args:
            current: Data produced by the latest fetch (a polars DataFrame,
                sequence of dicts, or iterable of records).
            key: Column/field used to identify records uniquely.
            previous_state: Optional earlier :class:`SyncState` carrying ``hashes``.
        """
        prev_state = previous_state or self.state
        curr = _normalize_records(current)
        total_current = len(curr)
        total_previous = len(prev_state.hashes) if prev_state.hashes else 0

        if key is None:
            if not prev_state.hashes:
                return ChangeReport(total_previous=total_previous, total_current=total_current)
            raise ValueError("detect_changes requires a 'key' when previous hashes are present")

        current_hashes: dict[str, str] = {}
        added = removed = modified = unchanged = 0
        seen: set[str] = set()
        for record in curr:
            k = str(record.get(key))
            seen.add(k)
            h = _hash_record(record)
            current_hashes[k] = h
            if k in prev_state.hashes:
                if prev_state.hashes[k] == h:
                    unchanged += 1
                else:
                    modified += 1
            else:
                added += 1
        removed = sum(1 for k in prev_state.hashes if k not in seen)

        self.state.hashes = current_hashes
        return ChangeReport(
            added=added,
            removed=removed,
            modified=modified,
            unchanged=unchanged,
            total_previous=total_previous,
            total_current=total_current,
        )

    # -- internals ---------------------------------------------------------

    def _persist(self, path: str | Path) -> Path:
        return self.state.save(path)


def _count(data: Any) -> int:
    if hasattr(data, "height"):  # polars.DataFrame
        return int(data.height)
    if hasattr(data, "__len__"):
        return len(data)
    return 0


def _normalize_records(data: Any) -> list[dict[str, Any]]:
    if hasattr(data, "to_dicts"):
        return data.to_dicts()  # polars DataFrame
    out: list[dict[str, Any]] = []
    for row in data:
        if isinstance(row, dict):
            out.append(row)
        else:
            raise TypeError(f"Unsupported record type in detect_changes: {type(row)!r}")
    return out


def _hash_record(record: dict[str, Any]) -> str:
    import hashlib

    blob = json.dumps(record, sort_keys=True, default=str).encode()
    return hashlib.sha256(blob).hexdigest()


def _parse_interval(interval: str | timedelta) -> timedelta:
    if isinstance(interval, timedelta):
        return interval
    text = interval.strip().lower()
    units = {"s": 1, "m": 60, "h": 3600, "d": 86400}
    amount = float(text[:-1])
    unit = text[-1:]
    if unit not in units:
        raise ValueError(f"Unsupported interval {interval!r}; use e.g. '1h', '24h', '30m', '7d'")
    return timedelta(seconds=amount * units[unit])
