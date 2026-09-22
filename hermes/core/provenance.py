from dataclasses import dataclass
from datetime import datetime


@dataclass
class Provenance:
    source: str = ""
    endpoint: str | None = None
    retrieved_at: datetime | None = None
    connector: str | None = None
    connector_version: str | None = None
    raw_checksum: str | None = None
    parser_version: str | None = None
    normalizer_version: str | None = None
    schema_version: str | None = None
