from dataclasses import dataclass


@dataclass
class DatasetDescriptor:
    id: str
    name: str
    description: str = ""
    source: str = ""
    schema_name: str | None = None
    coverage: str | None = None
    frequency: str | None = None
    version: str = "0.0.1"
    quality: str | None = None
