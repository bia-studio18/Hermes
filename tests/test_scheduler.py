from __future__ import annotations

from datetime import datetime, timedelta
from unittest.mock import patch

import pytest

from hermes.core.scheduler import (
    _cron_field,
    _cron_matches,
    _execute,
    _is_cron,
    _Job,
    _next_cron_dt,
    _parse_cron,
    _parse_interval,
    _registry,
    _run_job,
    list_jobs,
    schedule,
)


@pytest.fixture(autouse=True)
def clean_registry():
    _registry.clear()
    yield
    _registry.clear()


class TestCronField:
    def test_star(self):
        result = _cron_field("*", 0, 59)
        assert result == set(range(0, 60))

    def test_single_value(self):
        result = _cron_field("15", 0, 59)
        assert result == {15}

    def test_comma_separated(self):
        result = _cron_field("0,15,30,45", 0, 59)
        assert result == {0, 15, 30, 45}

    def test_range(self):
        result = _cron_field("10-15", 0, 59)
        assert result == {10, 11, 12, 13, 14, 15}

    def test_step_from_star(self):
        result = _cron_field("*/15", 0, 59)
        assert result == {0, 15, 30, 45}

    def test_step_from_base(self):
        result = _cron_field("1/5", 0, 59)
        assert result == {1, 6, 11, 16, 21, 26, 31, 36, 41, 46, 51, 56}

    def test_step_from_range(self):
        result = _cron_field("10-20/3", 0, 59)
        assert result == {10, 13, 16, 19}

    def test_invalid_step_zero(self):
        with pytest.raises(ValueError, match="step must be > 0"):
            _cron_field("*/0", 0, 59)

    def test_out_of_range_value(self):
        with pytest.raises(ValueError, match="outside range"):
            _cron_field("60", 0, 59)

    def test_day_of_week_range(self):
        result = _cron_field("1-3", 0, 6)
        assert result == {1, 2, 3}


class TestParseCron:
    def test_valid(self):
        result = _parse_cron("*/15 * * * *")
        assert len(result) == 5
        assert result[0] == {0, 15, 30, 45}

    def test_invalid_field_count(self):
        with pytest.raises(ValueError, match="5 fields"):
            _parse_cron("* * *")


class TestCronMatches:
    def test_matches(self):
        cron = _parse_cron("*/15 * * * *")
        dt = datetime(2024, 1, 1, 0, 15)
        assert _cron_matches(dt, cron) is True

    def test_no_match(self):
        cron = _parse_cron("*/15 * * * *")
        dt = datetime(2024, 1, 1, 0, 7)
        assert _cron_matches(dt, cron) is False

    def test_specific_day(self):
        cron = _parse_cron("0 9 * * 1")
        monday = datetime(2024, 1, 1, 9, 0)
        tuesday = datetime(2024, 1, 2, 9, 0)
        assert _cron_matches(monday, cron) is True
        assert _cron_matches(tuesday, cron) is False


class TestNextCronDt:
    def test_next_minute(self):
        cron = _parse_cron("* * * * *")
        now = datetime(2024, 1, 1, 0, 0, 30)
        result = _next_cron_dt("* * * * *", now, cron)
        assert result == datetime(2024, 1, 1, 0, 1)

    def test_next_specific_time(self):
        cron = _parse_cron("0 12 * * *")
        now = datetime(2024, 1, 1, 11, 30)
        result = _next_cron_dt("0 12 * * *", now, cron)
        assert result == datetime(2024, 1, 1, 12, 0)


class TestIsCron:
    def test_cron_string(self):
        assert _is_cron("*/15 * * * *") is True

    def test_interval_string(self):
        assert _is_cron("30m") is False


class TestParseInterval:
    def test_alias_hourly(self):
        assert _parse_interval("hourly") == timedelta(hours=1)

    def test_alias_daily(self):
        assert _parse_interval("daily") == timedelta(days=1)

    def test_alias_weekly(self):
        assert _parse_interval("weekly") == timedelta(weeks=1)

    def test_minutes(self):
        assert _parse_interval("30m") == timedelta(minutes=30)

    def test_hours(self):
        assert _parse_interval("2h") == timedelta(hours=2)

    def test_days(self):
        assert _parse_interval("7d") == timedelta(days=7)

    def test_weeks(self):
        assert _parse_interval("2w") == timedelta(weeks=2)

    def test_invalid(self):
        assert _parse_interval("invalid") is None


class TestJob:
    def test_interval_job(self):
        job = _Job(name="test", fn=lambda: None, spec="30m")
        assert job.interval == timedelta(minutes=30)
        assert job.cron is None

    def test_cron_job(self):
        job = _Job(name="test", fn=lambda: None, spec="*/15 * * * *")
        assert job.interval is None
        assert job.cron is not None

    def test_invalid_spec(self):
        with pytest.raises(ValueError, match="Unsupported schedule spec"):
            _Job(name="test", fn=lambda: None, spec="invalid")

    def test_calculate_next_run_interval(self):
        job = _Job(name="test", fn=lambda: None, spec="30m")
        now = datetime(2024, 1, 1, 0, 0)
        assert job.calculate_next_run(now) == datetime(2024, 1, 1, 0, 30)

    def test_calculate_next_run_cron(self):
        job = _Job(name="test", fn=lambda: None, spec="0 * * * *")
        now = datetime(2024, 1, 1, 0, 30)
        result = job.calculate_next_run(now)
        assert result.hour == 1
        assert result.minute == 0


class TestScheduleDecorator:
    def test_registers_job(self):
        @schedule(time="30m", name="my_job")
        def my_fn():
            pass

        assert "my_job" in _registry
        assert _registry["my_job"].fn is my_fn

    def test_default_name(self):
        @schedule(time="30m")
        def auto_named():
            pass

        assert "auto_named" in _registry

    def test_duplicate_name_raises(self):
        @schedule(time="30m", name="dup")
        def first():
            pass

        with pytest.raises(ValueError, match="already registered"):

            @schedule(time="30m", name="dup")
            def second():
                pass

    def test_invalid_timeout(self):
        with pytest.raises(ValueError, match="timeout must be > 0"):

            @schedule(time="30m", timeout=-1)
            def bad():
                pass

    def test_invalid_retries(self):
        with pytest.raises(ValueError, match="retries must be >= 0"):

            @schedule(time="30m", retries=-1)
            def bad():
                pass


class TestExecute:
    def test_sync_function(self):
        called = False

        def sync_fn():
            nonlocal called
            called = True

        _execute(_Job(name="t", fn=sync_fn, spec="30m"))
        assert called


class TestRunJob:
    def test_success(self):
        job = _Job(name="t", fn=lambda: None, spec="30m")
        _run_job(job)
        assert job.last_status == "success"
        assert job.runs == 1
        assert job.next_run_at is not None

    def test_failure_with_retries(self):
        def bad():
            raise ValueError("boom")

        job = _Job(name="t", fn=bad, spec="30m", retries=1)
        _run_job(job)
        assert job.last_status == "failed"
        assert job.failures == 1
        assert job.error == "boom"

    def test_failure_propagates_after_last_retry(self):
        def bad():
            raise ValueError("boom")

        job = _Job(name="t", fn=bad, spec="30m", retries=0)
        _run_job(job)
        assert job.last_status == "failed"
        assert job.error == "boom"


class TestListJobs:
    def test_empty(self):
        assert list_jobs() == []

    def test_with_jobs(self):
        @schedule(time="30m", name="j1")
        def fn1():
            pass

        result = list_jobs()
        assert len(result) == 1
        assert result[0]["name"] == "j1"
        assert result[0]["schedule"] == "30m"
        assert result[0]["last_status"] == "pending"
