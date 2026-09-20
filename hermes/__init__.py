from hermes.api.acquire import fetch, fetch_raw, ingest, read, sync
from hermes.api.data import (
    anomaly_count,
    date_ranges,
    get_freqs,
    inspect,
    normalize,
    parse,
    profile,
    transform,
    validate,
)
from hermes.api.datasets import get_dataset, search_datasets
from hermes.api.entities import resolve_company, resolve_country, resolve_entity
from hermes.api.schemas import compare_schema, get_schema, migrate, register_schema
from hermes.api.storage import delete, exists, list_datasets, load, save, storage_info
from hermes.core.config import configure, get_config
from hermes.core.dataset import Dataset
from hermes.core.errors import (
    AcquisitionError,
    AuthenticationError,
    ConfigError,
    ConnectorNotFoundError,
    HermesError,
    NormalizationError,
    ParseError,
    QueryError,
    SchemaError,
    StorageError,
    ValidationError,
)
from hermes.core.result import Result
from hermes.credentials.manager import delete_cred, get_cred, has_cred, list_creds, set_cred
from hermes.features.financial.crpto import CryptoHistory
from hermes.features.financial.filling import CompanyFilling
from hermes.features.financial.fundamental import CompanyFundamental
from hermes.features.financial.technical import TechnicalFeatures


__all__ = [
    # Features
    "CryptoHistory",
    "CompanyFilling",
    "CompanyFundamental",
    "TechnicalFeatures"
    # Fetching
    "fetch",
    "fetch_raw",
    "ingest",
    "read",
    "sync",
    # Credentials
    "list_creds",
    "has_cred",
    "set_cred",
    "get_cred",
    "delete_cred",
    # Data operations
    "parse",
    "normalize",
    "validate",
    "transform",
    "profile",
    "inspect",
    "get_freqs",
    "date_ranges",
    "anomaly_count",
    # Datasets
    "Dataset",
    "get_dataset",
    "search_datasets",
    # Entities
    "resolve_entity",
    "resolve_country",
    "resolve_company",
    # Schemas
    "get_schema",
    "register_schema",
    "compare_schema",
    "migrate",
    # Storage
    "save",
    "load",
    "exists",
    "delete",
    "list_datasets",
    "storage_info",
    # Config
    "configure",
    "get_config",
    # Core
    "Result",
    "HermesError",
    "AcquisitionError",
    "ParseError",
    "SchemaError",
    "NormalizationError",
    "ValidationError",
    "StorageError",
    "QueryError",
    "ConfigError",
    "ConnectorNotFoundError",
    "AuthenticationError",
]
