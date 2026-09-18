from abc import ABC, abstractmethod
from typing import Any


class NormalizationRule(ABC):

    @property
    def name(self) -> str:
        return type(self).__name__

    @abstractmethod
    def apply(self, data: Any, context: Any = None) -> Any:
        raise NotImplementedError

    def validate(self) -> None:
        pass

    def describe(self) -> dict[str, Any]:
        return {
            "name": self.name,
        }

    def __repr__(self) -> str:
        return f"{self.name}()"