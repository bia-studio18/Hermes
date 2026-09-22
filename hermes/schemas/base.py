from dataclasses import dataclass, field


@dataclass
class FieldDef:
    name: str
    dtype: str
    nullable: bool = True
    required: bool = False
    description: str | None = None
    unit: str | None = None
    constraints: dict = field(default_factory=dict)


@dataclass
class Schema:
    name: str
    version: str
    fields: list[FieldDef] = field(default_factory=list)
    primary_keys: list[str] = field(default_factory=list)
    description: str | None = None

    def validate_data(self, data: object) -> None:
        raise NotImplementedError()

    def compatibility(self, other: "Schema") -> None:
        raise NotImplementedError()

    def field_names(self) -> list[str]:
        raise NotImplementedError()
