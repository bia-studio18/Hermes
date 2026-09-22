from dataclasses import dataclass, field


@dataclass
class Entity:
    id: str
    name: str
    entity_type: str
    country: str | None = None
    identifiers: dict[str, str] = field(default_factory=dict)
    aliases: list[str] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)


@dataclass
class EntityMatch:
    entity: Entity
    score: float
    match_type: str
