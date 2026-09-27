from typing import Protocol

from hermes.entities.records import ResolutionResult, ResolutionRun


class EntityResolutionEngine:
    def resolve(
        self,
        left: object,
        right: object,
        *,
        policy: object | None = None,
    ) -> ResolutionResult:
        raise NotImplementedError

    def resolve_data(
        self,
        data: object,
        *,
        schema: object | None = None,
        policy: object | None = None,
    ) -> ResolutionRun:
        raise NotImplementedError


__all__ = ["EntityResolutionEngine", "ResolutionPipeline"]


class ResolutionPipeline(Protocol):
    def run(self, data: object) -> ResolutionRun: ...
