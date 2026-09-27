from typing import Protocol

from hermes.entities.records import RelationshipAssertion


class EntityGraph(Protocol):
    def entity_ids(self) -> tuple[str, ...]: ...

    def relationship_ids(self) -> tuple[str, ...]: ...

    def neighbors(self, entity_id: str) -> tuple[str, ...]: ...

    def relationships_for(self, entity_id: str) -> tuple[RelationshipAssertion, ...]: ...

    def snapshot(self, observed_at: str | None = None) -> object: ...


__all__ = ["EntityGraph"]
