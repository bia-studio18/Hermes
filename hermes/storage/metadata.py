from datetime import datetime

from pydantic import BaseModel, Field

from hermes.core.lineage import Lineage
from hermes.core.metadata import MetaData
from hermes.core.provenance import Provenance
from hermes.core.versioning import DataVersion


class StoredDatasetMetadata(BaseModel):
    schema_version: int = 1
    name: str
    dataset_id: str | None = None
    version: str | None = None
    schema_ref: str | None = None
    format: str = "parquet"
    source: str | None = None
    data_file: str = "data.parquet"
    row_count: int = 0
    column_count: int = 0
    column_schema: list[dict[str, str]] = Field(default_factory=list)
    created: datetime
    modified: datetime
    dataset_metadata: MetaData | None = None
    provenance: Provenance | None = None
    lineage: Lineage | None = None
    data_version: DataVersion | None = None


class StorageInfo(BaseModel):
    dataset: str
    format: str
    path: str
    size: int
    rows: int
    columns: int
    created: datetime | None = None
    modified: datetime | None = None
    column_schema: list[dict[str, str]] = Field(default_factory=list)
    version: str | None = None
    source: str | None = None


__all__ = ["StorageInfo", "StoredDatasetMetadata"]
