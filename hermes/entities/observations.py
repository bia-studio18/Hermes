from typing import Protocol

from hermes.entities.records import Observation


class ObservationService(Protocol):
    def record(self, observation: Observation) -> str: ...

    def get(self, observation_id: str) -> Observation | None: ...

    def normalize(self, observation_id: str) -> Observation: ...

    def entity_links(self, observation_id: str) -> tuple[str, ...]: ...


__all__ = ["ObservationService"]
