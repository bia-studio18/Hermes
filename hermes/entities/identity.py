from datetime import datetime
from typing import Protocol

from hermes.entities.records import EntityIdentity, EntityLifecycleEvent


class IdentityService(Protocol):
    def create(self, entity_type: str) -> EntityIdentity: ...

    def get(self, entity_id: str) -> EntityIdentity | None: ...

    def rename(self, entity_id: str, name: str, valid_from: datetime | None = None) -> None: ...

    def merge(self, source_entity_ids: tuple[str, ...], result_entity_id: str) -> EntityLifecycleEvent: ...

    def split(self, source_entity_id: str, result_entity_ids: tuple[str, ...]) -> EntityLifecycleEvent: ...

    def retire(self, entity_id: str, effective_at: datetime | None = None) -> EntityLifecycleEvent: ...


__all__ = ["IdentityService"]
