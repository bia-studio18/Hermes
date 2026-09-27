from typing import Protocol

from hermes.entities.records import ResolutionResult


class EvidenceStore(Protocol):
    def record(self, result: ResolutionResult) -> None: ...

    def get(self, result_id: str) -> ResolutionResult | None: ...


__all__ = ["EvidenceStore"]
