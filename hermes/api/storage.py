from hermes.core.dataset import Dataset
from hermes.core.errors import StorageError
from hermes.core.result import Result
from hermes.storage.filesystem import FilesystemStorage
from hermes.storage.metadata import StorageInfo


def _backend() -> FilesystemStorage:
    return FilesystemStorage()


def save(dataset: Dataset, name: str | None = None, overwrite: bool = False) -> Result:
    try:
        info = _backend().save(dataset, name=name, overwrite=overwrite)
        return Result(
            status="success",
            data=info,
            statistics={
                "name": info.dataset,
                "rows": info.rows,
                "columns": info.columns,
                "path": info.path,
            },
        )
    except StorageError as exc:
        result = Result(status="failure")
        result.add_error(exc)
        return result


def load(name: str) -> Dataset:
    """Reconstruct the Dataset stored under *name* (data materialized)."""
    return _backend().load(name)


def exists(name: str) -> bool:
    """Return True if a dataset named *name* is stored."""
    return _backend().exists(name)


def delete(name: str) -> None:
    """Remove the stored dataset named *name* (raises if not present)."""
    _backend().delete(name)


def list_datasets() -> list[str]:
    """Return the names of all datasets stored in Hermes storage."""
    return _backend().list()


def storage_info(name: str) -> StorageInfo:
    """Return metadata about a stored dataset without loading its data."""
    return _backend().info(name)
