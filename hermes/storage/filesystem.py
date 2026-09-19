from __future__ import annotations

import json
import os
import re
import shutil
import uuid
from datetime import UTC, datetime
from pathlib import Path

import polars as pl

try:
    import pyarrow as pa
    import pyarrow.parquet as pq
except ImportError:
    pa = None
    pq = None

from hermes.core.config import get_config
from hermes.core.dataset import Dataset
from hermes.core.errors import StorageError
from hermes.core.lineage import Lineage
from hermes.core.metadata import MetaData
from hermes.core.provenance import Provenance
from hermes.storage.base import StorageBackend
from hermes.storage.errors import (
    DatasetAlreadyExistsError,
    DatasetNotFoundError,
    StorageCorruptionError,
    StorageReadError,
    StorageWriteError,
)
from hermes.storage.metadata import StorageInfo, StoredDatasetMetadata

_DATA_FILE = "data.parquet"
_METADATA_FILE = "metadata.json"
_SAFE_NAME = re.compile(r"^[A-Za-z0-9._-]+$")


def _assert_safe_name(name: str) -> str:

    if not isinstance(name, str) or not name or not _SAFE_NAME.fullmatch(name) or name in {".", ".."}:
        raise StorageError(f"unsafe dataset name {name!r}")
    return name


def _now() -> datetime:
    return datetime.now(tz=UTC)


def _write_parquet(data: object, target: Path) -> None:
    if isinstance(data, pl.DataFrame):
        data.write_parquet(target)
    elif isinstance(data, pl.LazyFrame):
        data.sink_parquet(target)
    elif pa is not None and isinstance(data, pa.Table):
        pq.write_table(data, target)
    else:
        raise StorageWriteError(f"cannot persist data of type {type(data).__name__}; expected Polars/Arrow")


def _stats_from_file(path: Path) -> tuple[int, int, list[dict[str, str]]]:

    schema = pl.read_parquet_schema(path)
    rows = int(pl.scan_parquet(path).select(pl.len()).collect().item())
    return rows, len(schema), [{"name": col, "dtype": str(dtype)} for col, dtype in schema.items()]


def _atomic_write(target: Path, writer) -> None:
    tmp = target.with_name(f".{target.stem}.{uuid.uuid4().hex}.tmp")
    try:
        writer(tmp)
        os.replace(tmp, target)
    finally:
        tmp.unlink(missing_ok=True)


class FilesystemStorage(StorageBackend):
    def __init__(self, root: str | Path | None = None) -> None:
        root = root if root is not None else get_config().storage_root
        self.root = Path(root).expanduser().resolve()

    @property
    def _datasets_dir(self) -> Path:
        return self.root / "datasets"

    def _path_for(self, name: str) -> Path:
        return self._datasets_dir / _assert_safe_name(name)

    def _data_path(self, name: str) -> Path:
        return self._path_for(name) / _DATA_FILE

    def _metadata_path(self, name: str) -> Path:
        return self._path_for(name) / _METADATA_FILE

    def save(self, dataset: Dataset, name: str | None = None, overwrite: bool = False) -> StorageInfo:
        target_name = _assert_safe_name(dataset.name if name is None else name)
        if dataset.data is None:
            raise StorageWriteError(f"Dataset {target_name!r} has no in-memory data; load it first (dataset.load())")

        target_dir = self._path_for(target_name)
        data_path = target_dir / _DATA_FILE
        metadata_path = target_dir / _METADATA_FILE

        created = _now()
        existed = self.exists(target_name)
        if existed and not overwrite:
            raise DatasetAlreadyExistsError(f"Dataset {target_name!r} already exists; use overwrite=True to replace it")
        if existed:
            created = self._load_metadata(target_name).created

        created_dir = not target_dir.exists()
        try:
            target_dir.mkdir(parents=True, exist_ok=True)
            _atomic_write(data_path, lambda tmp: _write_parquet(dataset.data, tmp))
            rows, columns, column_schema = _stats_from_file(data_path)
            stored = self._build_metadata(dataset, target_name, rows, columns, column_schema, created)
            _atomic_write(
                metadata_path,
                lambda tmp: tmp.write_text(json.dumps(stored.model_dump(mode="json"), indent=2), encoding="utf-8"),
            )
        except StorageError:
            if created_dir:
                shutil.rmtree(target_dir, ignore_errors=True)
            raise
        except Exception as exc:
            if created_dir:
                shutil.rmtree(target_dir, ignore_errors=True)
            raise StorageWriteError(f"failed to save dataset {target_name!r}: {exc}") from exc

        return self._info_from(stored, data_path)

    def _build_metadata(
        self,
        dataset: Dataset,
        name: str,
        rows: int,
        columns: int,
        column_schema: list[dict[str, str]],
        created: datetime,
    ) -> StoredDatasetMetadata:
        source = dataset.provenance.source or dataset.metadata.source
        return StoredDatasetMetadata(
            name=name,
            dataset_id=str(dataset.id) if dataset.id else None,
            version=dataset.version,
            schema_ref=dataset.schema_ref,
            source=source,
            row_count=rows,
            column_count=columns,
            column_schema=column_schema,
            created=created,
            modified=_now(),
            dataset_metadata=dataset.metadata,
            provenance=dataset.provenance,
            lineage=dataset.lineage,
            data_version=dataset.data_version,
        )

    def load(self, name: str) -> Dataset:
        data_path = self._data_path(name)
        metadata_path = self._metadata_path(name)
        if not data_path.is_file() or not metadata_path.is_file():
            self._raise_not_found_or_corrupt(name, data_path, metadata_path)

        stored = self._load_metadata(name)
        try:
            data = pl.read_parquet(data_path)
        except Exception as exc:
            raise StorageReadError(f"failed to read Parquet for dataset {name!r}: {exc}") from exc
        return self._to_dataset(stored, data, data_path)

    def _raise_not_found_or_corrupt(self, name: str, data_path: Path, metadata_path: Path) -> None:
        target_dir = self._path_for(name)
        if target_dir.is_dir() and (data_path.is_file() or metadata_path.is_file()):
            raise StorageCorruptionError(
                f"dataset {name!r} is incomplete (missing {'data' if not data_path.is_file() else 'metadata'})"
            )
        raise DatasetNotFoundError(f"Dataset {name!r} not found in storage")

    def _load_metadata(self, name: str) -> StoredDatasetMetadata:
        path = self._metadata_path(name)
        try:
            return StoredDatasetMetadata.model_validate(json.loads(path.read_text(encoding="utf-8")))
        except (OSError, ValueError) as exc:
            raise StorageCorruptionError(f"metadata for dataset {name!r} is corrupt") from exc

    def _to_dataset(self, stored: StoredDatasetMetadata, data: pl.DataFrame, data_path: Path) -> Dataset:
        return Dataset(
            id=uuid.UUID(stored.dataset_id) if stored.dataset_id else uuid.uuid4(),
            name=stored.name,
            version=stored.version or "0.0.1",
            schema_ref=stored.schema_ref,
            data_ref=str(data_path),
            data=data,
            metadata=stored.dataset_metadata or MetaData(),
            provenance=stored.provenance or Provenance(),
            lineage=stored.lineage or Lineage(),
            data_version=stored.data_version,
        )

    def exists(self, name: str) -> bool:
        target_dir = self._path_for(name)
        return target_dir.is_dir() and (target_dir / _DATA_FILE).is_file() and (target_dir / _METADATA_FILE).is_file()

    def delete(self, name: str) -> None:
        if not self.exists(name):
            raise DatasetNotFoundError(f"Dataset {name!r} not found in storage")
        shutil.rmtree(self._path_for(name))

    def list(self) -> list[str]:
        datasets_dir = self._datasets_dir
        if not datasets_dir.is_dir():
            return []
        names = []
        for entry in datasets_dir.iterdir():
            if entry.is_dir() and (entry / _DATA_FILE).is_file() and (entry / _METADATA_FILE).is_file():
                names.append(entry.name)
        return sorted(names)

    def info(self, name: str) -> StorageInfo:
        if not self.exists(name):
            raise DatasetNotFoundError(f"Dataset {name!r} not found in storage")
        stored = self._load_metadata(name)
        return self._info_from(stored, self._data_path(name))

    def _info_from(self, stored: StoredDatasetMetadata, data_path: Path) -> StorageInfo:
        size = data_path.stat().st_size if data_path.is_file() else 0
        return StorageInfo(
            dataset=stored.name,
            format=stored.format,
            path=str(data_path),
            size=size,
            rows=stored.row_count,
            columns=stored.column_count,
            created=stored.created,
            modified=stored.modified,
            column_schema=stored.column_schema,
            version=stored.version,
            source=stored.source,
        )


__all__ = ["FilesystemStorage"]
