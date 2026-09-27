from typing import Protocol

from hermes.entities.records import ResolutionResult
from hermes.entities.resolution.config import ResolutionPolicy
from hermes.entities.resolution.models import Candidate


class ScoringEngine(Protocol):
    def score(self, candidates: tuple[Candidate, ...], policy: ResolutionPolicy) -> tuple[ResolutionResult, ...]: ...


__all__ = ["ScoringEngine"]
