from datetime import datetime
from typing import Protocol

from hermes.entities.records import EntityLifecycleEvent


class TemporalService(Protocol):
    def valid_at(self, entity_id: str, at: datetime) -> object | None: ...

    def history(self, entity_id: str) -> tuple[object, ...]: ...

    def lifecycle_events(self, entity_id: str) -> tuple[EntityLifecycleEvent, ...]: ...


__all__ = ["TemporalService"]
