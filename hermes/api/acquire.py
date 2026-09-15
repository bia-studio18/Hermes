from __future__ import annotations

import logging
from collections.abc import Callable
from datetime import timedelta
from pathlib import Path
from typing import Any, cast

import polars as pl

from hermes.acquisition.sync import SyncEngine, SyncState
from hermes.core.errors import AcquisitionError, ConnectorNotFoundError, HermesError
from hermes.core.result import Result

logger = logging.getLogger(__name__)

_CONNECTOR_CLASSES: dict[str, type] = {}


def register_connector(name: str, connector_cls: type) -> None:
    """Register *connector_cls* under *name* so ``hr.fetch(name, ...)`` can use it."""
    _CONNECTOR_CLASSES[name] = connector_cls


def _connector_class(source: str) -> type:
    _ensure_registered()
    if source not in _CONNECTOR_CLASSES:
        raise ConnectorNotFoundError(f"Unknown connector {source!r}; registered: {sorted(_CONNECTOR_CLASSES)}")
    return _CONNECTOR_CLASSES[source]


def _ensure_registered() -> None:
    if _CONNECTOR_CLASSES:
        return
    from hermes.connectors import (
        FINNHUB,
        FRED,
        GDELT,
        IMF,
        PUBLIC_DATASET,
        SECEDGAR,
        Binance,
        OpenSanction,
        World_bank,
        Yfinance,
    )

    _CONNECTOR_CLASSES.update(
        {
            "binance": Binance,
            "finnhub": FINNHUB,
            "fred": FRED,
            "gdelt": GDELT,
            "imf": IMF,
            "opensanctions": OpenSanction,
            "public_data": PUBLIC_DATASET,
            "sec": SECEDGAR,
            "world_bank": World_bank,
            "yfinance": Yfinance,
        }
    )


def _instantiate(source: str, **connector_kwargs: Any) -> Any:
    cls = _connector_class(source)
    if source == "sec":
        username = connector_kwargs.pop("username", None)
        email = connector_kwargs.pop("email", None)
        if not username or not email:
            raise AcquisitionError("SEC requires 'username' and 'email' for its User-Agent header")
        return cls(username=username, email=email)
    return cls(**connector_kwargs)


def _apply(fn: Callable[..., Any], *args: Any, **kwargs: Any) -> Any:
    """Call an (async or sync) connector method and await when needed.

    Works both inside and outside a running event loop by running the
    coroutine in a fresh thread when a loop is already active.
    """
    import asyncio

    out = fn(*args, **kwargs)
    if asyncio.iscoroutine(out) or hasattr(out, "__await__"):

        def run() -> Any:
            try:
                asyncio.get_running_loop()
            except RuntimeError:
                return asyncio.run(out)
            import threading

            holder: dict[str, Any] = {}

            def target() -> None:
                holder["result"] = asyncio.run(out)

            thread = threading.Thread(target=target)
            thread.start()
            thread.join()
            return holder.get("result")

        return run()
    return out


def fetch(source: str, **kwargs: object) -> Result:
    """Acquire data from *source* using the registered connector (cached).

    Returns a :class:`~hermes.core.result.Result` with ``data`` set to the
    connector's output (typically a polars DataFrame).
    """
    result = Result(status="success")
    try:
        connector = _instantiate(source, **kwargs)
        data = _apply(connector.fetch)
        result.data = data
        return result
    except HermesError as exc:
        result.status = "failure"
        result.add_error(exc)
        return result


def fetch_raw(source: str, **kwargs: object) -> Result:
    """Acquire raw data from *source* bypassing the cache layer."""
    result = Result(status="success")
    try:
        connector = _instantiate(source, **kwargs)
        data = _apply(connector._fetch)
        result.data = data
        return result
    except HermesError as exc:
        result.status = "failure"
        result.add_error(exc)
        return result


def ingest(source: str, **kwargs: object) -> Result:
    """Fetch *source* and return the data packaged with metadata."""
    result = fetch(source, **kwargs)
    if result.errors:
        return result
    data = result.data
    rows = data.height if isinstance(data, pl.DataFrame) else len(data or [])
    result.metadata = {
        "source": source,
        "rows": rows,
        "raw": False,
    }
    return result


def sync(source: str, **kwargs: object) -> Result:
    """Synchronize *source* incrementally using a :class:`SyncEngine`.

    Keyword arguments accepted (beyond connector args):
      - ``fetch_fn``: async callable returning new/changed records
        (``since=<cursor>`` is passed for incremental fetches).
      - ``state_path``: where to persist :class:`SyncState`.
      - ``interval``: str/timedelta; skip sync when run more recently than this.
      - ``cursor``: next cursor to persist with :class:`SyncState`.
    """
    result = Result(status="success")
    fetch_fn = cast("Callable[..., Any] | None", kwargs.pop("fetch_fn", None))
    state_path = cast("str | Path | None", kwargs.pop("state_path", None))
    interval = cast("str | timedelta | None", kwargs.pop("interval", None))
    cursor = cast("object | None", kwargs.pop("cursor", None))

    try:
        connector = _instantiate(source, **kwargs)
        loader: Callable[..., Any] = fetch_fn or connector.fetch
        engine = SyncEngine(source, loader)
        if state_path is not None:
            loaded = SyncState.load(source, state_path)
            if loaded is not None:
                engine.state = loaded

        def call() -> Any:
            return engine.sync(
                interval=interval,
                state_path=state_path,
                cursor=cursor,
            )

        data, report, state = _apply(call)
        result.data = data
        result.statistics = report.model_dump()
        return result
    except HermesError as exc:
        result.status = "failure"
        result.add_error(exc)
        return result


def read(path: str, **kwargs: object) -> Result:
    """Read a local file (csv/parquet/json/jsonl) into a polars DataFrame."""
    result = Result(status="success")
    options: dict[str, Any] = {k: v for k, v in kwargs.items()}
    try:
        p = Path(path)
        if not p.exists():
            raise AcquisitionError(f"File not found: {path}")
        suffix = p.suffix.lower()
        if suffix == ".csv":
            df = pl.read_csv(p, **options)
        elif suffix in (".parquet", ".pq"):
            df = pl.read_parquet(p)
        elif suffix == ".json":
            df = pl.DataFrame(pl.read_json(p), **options)
        elif suffix in (".jsonl", ".ndjson"):
            df = pl.read_ndjson(p, **options)
        else:
            raise AcquisitionError(f"Unsupported file format: {suffix}")
        result.data = df
        return result
    except HermesError as exc:
        result.status = "failure"
        result.add_error(exc)
        return result
