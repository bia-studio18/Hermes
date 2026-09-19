from abc import ABC, abstractmethod

from hermes.core.dataset import Dataset
from hermes.storage.metadata import StorageInfo


class StorageBackend(ABC):
    @abstractmethod
    def save(self, dataset: Dataset, name: str | None = None, overwrite: bool = False) -> StorageInfo:
        pass

    @abstractmethod
    def load(self, name: str) -> Dataset:
        pass

    @abstractmethod
    def exists(self, name: str) -> bool:
        pass

    @abstractmethod
    def delete(self, name: str) -> None:
        pass

    @abstractmethod
    def list(self) -> list[str]:
        pass

    @abstractmethod
    def info(self, name: str) -> StorageInfo:
        pass


__all__ = ["StorageBackend"]
