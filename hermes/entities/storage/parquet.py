from pathlib import Path

from hermes.entities.storage.base import EntityStore


class ParquetEntityStore(EntityStore):
    def __init__(self, root: str | Path) -> None:
        self.root = Path(root)

    def save_entities(self, entities: object) -> None:
        raise NotImplementedError

    def load_entities(self) -> object:
        raise NotImplementedError

    def save_observations(self, observations: object) -> None:
        raise NotImplementedError

    def load_observations(self) -> object:
        raise NotImplementedError

    def save_relationships(self, relationships: object) -> None:
        raise NotImplementedError

    def load_relationships(self) -> object:
        raise NotImplementedError


__all__ = ["ParquetEntityStore"]
