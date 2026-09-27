from typing import Protocol

from hermes.entities.records import EntityIdentity, RelationshipAssertion


class EntityService(Protocol):
    def create_entity(self, entity_type: str) -> EntityIdentity: ...

    def get_entity(self, entity_id: str) -> EntityIdentity | None: ...

    def record_relationship(self, relationship: RelationshipAssertion) -> str: ...


__all__ = ["EntityService"]
