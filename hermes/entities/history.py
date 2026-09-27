from typing import Protocol

from hermes.entities.records import ResolutionResult


class ResolutionHistory(Protocol):
    def save(self, result: ResolutionResult) -> None: ...

    def list_for_run(self, run_id: str) -> tuple[ResolutionResult, ...]: ...


__all__ = ["ResolutionHistory"]
