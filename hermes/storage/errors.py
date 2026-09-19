from hermes.core.errors import StorageError


class DatasetNotFoundError(StorageError):
    pass


class DatasetAlreadyExistsError(StorageError):
    pass


class StorageWriteError(StorageError):
    pass


class StorageReadError(StorageError):
    pass


class StorageCorruptionError(StorageError):
    pass


__all__ = [
    "DatasetAlreadyExistsError",
    "DatasetNotFoundError",
    "StorageCorruptionError",
    "StorageReadError",
    "StorageWriteError",
]
