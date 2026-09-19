from abc import ABC, abstractmethod
from typing import Any

from hermes.validation.result import RuleResult


class ValidationRule(ABC):
    @property
    def name(self) -> str:
        return type(self).__name__

    @abstractmethod
    def check(self, data: Any, context: Any = None) -> RuleResult:
        raise NotImplementedError

    def validate(self) -> None:
        pass

    def describe(self) -> dict[str, Any]:
        return {"name": self.name}

    def __repr__(self) -> str:
        return f"{self.name}()"


__all__ = ["ValidationRule"]
