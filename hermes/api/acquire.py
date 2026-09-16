from __future__ import annotations

import logging

import polars as pl

from hermes.core.errors import AcquisitionError, ConnectorNotFoundError, HermesError
from hermes.core.result import Result
from hermes.core.dataset import Dataset

logger = logging.getLogger(__name__)


def fetch(source: str) -> Result:
    return NotImplementedError()

def fetch_raw(source: str) -> Result:
    return NotImplementedError()

def ingest(source: str) -> Result:
    return NotImplementedError()

def sync(source: str, fn) -> Result:
    return NotImplementedError()

def read(path: str) -> Result:
    return NotImplementedError()

def dataset(name: str) -> Dataset:
    return NotImplementedError()