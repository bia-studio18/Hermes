from __future__ import annotations

import logging
from typing import Any

import polars as pl

from hermes.acquisition.cache import RawCache
from hermes.acquisition.client import Client
from hermes.core.errors import AcquisitionError
from hermes.normalization import NormalizationEngine
from hermes.normalization.rule import NormalizationRule
from hermes.validation import validate
from hermes.validation.rule import ValidationRule

logger = logging.getLogger(__name__)


class BaseConnector:
    def __init__(
        self,
        cache: RawCache | None = None,
        *,
        retry_auth: bool = False,
        headers: dict[str, str] | None = None,
    ) -> None:
        self._cache = cache or RawCache()
        self._retry_auth = retry_auth
        self._headers = dict(headers or {})

    async def _get_json(
        self,
        url: str,
        *,
        params: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
        timeout: float = 30.0,
        retries: int = 3,
    ) -> Any:
        merged = {**self._headers, **(headers or {})}
        async with Client(timeout=timeout, max_retries=retries, retry_auth=self._retry_auth) as client:
            return await client.get(url, params=params, headers=merged)

    @staticmethod
    def _not_found(error: Exception) -> bool:
        return isinstance(error, AcquisitionError) and getattr(error, "status_code", None) == 404

    def _normalize(self, data: pl.DataFrame, rules: list[NormalizationRule]) -> pl.DataFrame:
        if not rules:
            return data
        return NormalizationEngine(rules).normalize(data)

    def _validate(self, data: pl.DataFrame, rules: list[ValidationRule], source: str) -> None:
        if not rules or data.is_empty():
            return
        result = validate(data, rules)
        if not result.passed:
            logger.warning("%s validation failed:\n%s", source, result.summary())


__all__ = ["BaseConnector"]
