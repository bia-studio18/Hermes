from __future__ import annotations

from datetime import UTC, datetime, timedelta, timezone
from pathlib import Path

import polars as pl
import pytest

from hermes.acquisition.sync import ChangeReport, SyncEngine, SyncState, _parse_interval


class TestSyncState:
    def test_needs_sync_when_never_synced(self):
        state = SyncState(source="src")
        assert state.needs_sync("1h") is True

    def test_needs_sync_false_when_recent(self):
        state = SyncState(source="src", last_sync=datetime.now(UTC))
        assert state.needs_sync("1h") is False

    def test_needs_sync_true_when_stale(self):
        state = SyncState(source="src", last_sync=datetime.now(UTC) - timedelta(hours=2))
        assert state.needs_sync("1h") is True

    def test_update_sets_cursor_and_time(self):
        state = SyncState(source="src")
        state.update(cursor="c-123")
        assert state.get_cursor() == "c-123"
        assert state.last_sync is not None

    def test_update_keeps_cursor_when_none(self):
        state = SyncState(source="src", cursor="keep")
        state.update()
        assert state.get_cursor() == "keep"

    def test_persist_and_load_roundtrip(self, tmp_path: Path):
        state = SyncState(source="wb", cursor={"page": 3}).update()
        path = state.save(tmp_path / "wb.json")
        loaded = SyncState.load("wb", path)
        assert loaded is not None
        assert loaded.source == "wb"
        assert loaded.get_cursor() == {"page": 3}

    def test_load_missing_returns_none(self, tmp_path: Path):
        assert SyncState.load("nope", tmp_path / "missing.json") is None

    def test_load_corrupt_returns_none(self, tmp_path: Path):
        path = tmp_path / "bad.json"
        path.write_text("{not json")
        assert SyncState.load("bad", path) is None


class TestParseInterval:
    def test_string_intervals(self):
        assert _parse_interval("1h") == timedelta(hours=1)
        assert _parse_interval("30m") == timedelta(minutes=30)
        assert _parse_interval("2d") == timedelta(days=2)
        assert _parse_interval("90s") == timedelta(seconds=90)

    def test_timedelta_passthrough(self):
        td = timedelta(minutes=5)
        assert _parse_interval(td) is td

    def test_unknown_unit_raises(self):
        with pytest.raises(ValueError):
            _parse_interval("3x")


class TestSyncEngine:
    def test_sync_state_init(self):
        engine = SyncEngine("src", lambda: None)
        assert engine.state.source == "src"
        assert engine.state.last_sync is None

    async def test_full_sync_and_persist(self, tmp_path: Path):
        async def fetch_fn(**kwargs):
            return pl.DataFrame({"a": [1, 2]})

        engine = SyncEngine("src", fetch_fn)
        data, report, state = await engine.full_sync(state_path=tmp_path / "s.json")
        assert isinstance(data, pl.DataFrame)
        assert state.last_sync is not None

    async def test_incremental_sync_uses_cursor(self):
        fetched_with: list = []

        async def fetch_fn(since=None, **kwargs):
            fetched_with.append(since)
            return pl.DataFrame({"row": [1, 2, 3]})

        engine = SyncEngine("src", fetch_fn)
        engine.state = engine.state.update(cursor="cursor-9")
        await engine.incremental_sync()
        assert fetched_with == ["cursor-9"]

    async def test_incremental_sync_no_cursor_no_report_warn(self, tmp_path: Path):
        async def fetch_fn(since=None, **kwargs):
            return pl.DataFrame({"row": [1]})

        engine = SyncEngine("src", fetch_fn)
        data, report, _ = await engine.incremental_sync(state_path=tmp_path / "s.json")
        assert report.total_current == 1
        assert data.height == 1

    async def test_sync_skips_when_not_due(self):
        engine = SyncEngine("src", lambda: object())
        engine.state = engine.state.update()
        result, report, state = await engine.sync(interval="1h")
        assert result is None
        assert report.total_current == 0

    async def test_sync_forces_when_force(self):
        calls = []

        async def fetch_fn(**kwargs):
            calls.append(1)
            return pl.DataFrame({"a": [1]})

        engine = SyncEngine("src", fetch_fn)
        engine.state = engine.state.update()
        await engine.sync(interval="1h", force=True)
        assert calls == [1]


class TestDetectChanges:
    def test_changes_with_hashes(self):
        engine = SyncEngine("src", lambda: None)
        baseline = pl.DataFrame({"id": ["1", "2"], "v": [1, 2]})
        engine.detect_changes(current=baseline, key="id")

        current = pl.DataFrame({"id": ["1", "2", "3"], "v": [1, 2, 3]})
        report = engine.detect_changes(current=current, key="id")
        assert isinstance(report, ChangeReport)
        assert report.added == 1  # "3"
        assert report.removed == 0
        assert report.modified == 0
        assert report.unchanged == 2

    def test_changes_modified_detected(self):
        state = SyncState(source="src", hashes={"1": "hash-a"})
        engine = SyncEngine("src", lambda: None, state=state)
        current = pl.DataFrame({"id": ["1"], "v": [99]})
        report = engine.detect_changes(current=current, key="id")
        assert report.modified == 1

    def test_changes_from_populated_state(self):
        engine = SyncEngine("src", lambda: None)
        engine.detect_changes(current=[{"id": "1", "v": 1}, {"id": "2", "v": 2}], key="id")
        report = engine.detect_changes(current=[{"id": "2", "v": 99}], key="id")
        assert report.removed == 1
        assert report.modified == 1

    def test_changes_removed_detected(self):
        state = SyncState(source="src", hashes={"1": "hash-a", "2": "hash-b"})
        engine = SyncEngine("src", lambda: None, state=state)
        current = pl.DataFrame({"id": ["1"], "v": [1]})
        report = engine.detect_changes(current=current, key="id")
        assert report.removed == 1

    def test_changes_without_state_only_totals(self):
        engine = SyncEngine("src", lambda: None)
        current = [{"id": 1}, {"id": 2}]
        report = engine.detect_changes(current=current, key="id")
        assert report.total_current == 2
        assert report.total_previous == 0

    def test_unions_into_state(self):
        engine = SyncEngine("src", lambda: None)
        engine.detect_changes(current=[{"id": 1, "x": "a"}], key="id")
        engine.detect_changes(current=[{"id": 1, "x": "a"}, {"id": 2, "x": "b"}], key="id")
        assert set(engine.state.hashes) == {"1", "2"}
