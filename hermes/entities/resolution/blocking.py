from typing import Protocol

from hermes.entities.resolution.models import Candidate


class BlockingEngine(Protocol):
    def candidates(self, records: object, policy: object) -> tuple[Candidate, ...]: ...


__all__ = ["BlockingEngine"]
