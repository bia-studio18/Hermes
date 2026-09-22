from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class LineageStep:
    operation: str
    input_ref: str | None = None
    output_ref: str | None = None
    timestamp: datetime = field(default_factory=datetime.utcnow)
    params: dict = field(default_factory=dict)
    component_version: str | None = None


@dataclass
class Lineage:
    steps: list[LineageStep] = field(default_factory=list)

    def add_step(self, step: LineageStep) -> None:
        self.steps.append(step)

    def trace(self) -> list[LineageStep]:
        return self.steps

    def last_operation(self) -> LineageStep | None:
        if len(self.steps) == 0:
            return None
        return self.steps[-1]
