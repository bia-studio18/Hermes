from dataclasses import dataclass, field


@dataclass
class Expression:
    operator: str
    operands: list[object] = field(default_factory=list)


def and_(*filters: object) -> Expression:
    raise NotImplementedError()


def or_(*filters: object) -> Expression:
    raise NotImplementedError()


def not_(filter_obj: object) -> Expression:
    raise NotImplementedError()
