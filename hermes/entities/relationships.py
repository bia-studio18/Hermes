from typing import Protocol

from hermes.entities.records import RelationshipAssertion


class RelationshipService(Protocol):
    def record_assertion(self, relationship: RelationshipAssertion) -> str: ...

    def get(self, relationship_id: str) -> RelationshipAssertion | None: ...

    def for_entity(self, entity_id: str) -> tuple[RelationshipAssertion, ...]: ...

    def conflicts(self, entity_id: str) -> tuple[tuple[RelationshipAssertion, ...], ...]: ...


__all__ = ["RelationshipService"]
