from typing import Protocol

from hermes.entities.records import IdentifierAssertion


class IdentifierService(Protocol):
    def assert_identifier(self, assertion: IdentifierAssertion) -> None: ...

    def resolve_identifier(self, scheme: str, value: str) -> str | None: ...

    def identifier_history(self, entity_id: str) -> tuple[IdentifierAssertion, ...]: ...


__all__ = ["IdentifierService"]
