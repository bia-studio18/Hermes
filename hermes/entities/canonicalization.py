from typing import Protocol

from hermes.entities.records import CanonicalProjection


class CanonicalizationService(Protocol):
    def current_projection(self, entity_id: str) -> CanonicalProjection | None: ...

    def apply_source_priority(self, entity_id: str) -> CanonicalProjection | None: ...

    def history(self, entity_id: str) -> tuple[object, ...]: ...


__all__ = ["CanonicalizationService"]
