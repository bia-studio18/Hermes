import logging
from datetime import timedelta
from functools import partial

import polars as pl

from hermes.acquisition.cache import RawCache
from hermes.connectors.base import BaseConnector
from hermes.core.errors import AcquisitionError
from hermes.entities.companies import get_cik

logger = logging.getLogger(__name__)


class SECEDGAR(BaseConnector):
    def __init__(self, username: str, email: str, cache: RawCache | None = None):
        super().__init__(cache)
        self._email = email
        self._username = username
        self._url = "https://data.sec.gov/api/xbrl/companyfacts"

    async def _fetch(self, symbol: str, retries: int = 3, timeout: float = 30.0):
        cik = get_cik(ticker=symbol)
        url = f"{self._url}/{cik}.json"

        headers = {"User-Agent": f"{self._username} {self._email}"}

        try:
            return await self._get_json(url, headers=headers, timeout=timeout, retries=retries)
        except AcquisitionError as e:
            if self._not_found(e):
                logger.warning("404: cik=%s", cik)
                return None
            logger.error("HTTP error: %s", e)
            raise

    async def fetch(
        self,
        symbol: str,
        timeout: float = 30.0,
        retries: int = 3,
        force: bool = False,
    ) -> pl.DataFrame | dict:
        cache_params = {
            "company": symbol,
        }

        return await self._cache.get_or_fetch(
            source="sec_edgar",
            params=cache_params,
            fetch_fn=partial(
                self._fetch,
                symbol=symbol,
                timeout=timeout,
                retries=retries,
            ),
            force=force,
            ttl=timedelta(days=7),
        )
