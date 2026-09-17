from __future__ import annotations

import logging

logger = logging.getLogger(__name__)


def fetch(source: str):
    return NotImplementedError()


def fetch_raw(source: str):
    return NotImplementedError()


def ingest(source: str):
    return NotImplementedError()


def sync(source: str, fn):
    return NotImplementedError()


def read(path: str):
    return NotImplementedError()


def dataset(name: str):
    return NotImplementedError()
