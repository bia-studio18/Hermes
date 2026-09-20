from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import aiohttp
import pytest

from hermes.connectors.world_bank import World_bank
from hermes.core.errors import AcquisitionError


def _mock_client(client_cls, payload=None, error=None, effects=None):
    client = MagicMock()
    if effects is not None:
        client.get = AsyncMock(side_effect=effects)
    elif error is not None:
        client.get = AsyncMock(side_effect=error)
    else:
        client.get = AsyncMock(return_value=payload)
    client_cls.return_value.__aenter__.return_value = client
    return client


class TestWorldBank:
    async def test_fetch_success(self):
        wb = World_bank(cache=None)
        mock_response = [
            {"page": 1, "pages": 1, "per_page": 1000, "total": 1},
            [
                {
                    "indicator": {"id": "NY.GDP.MKTP.KD.ZG", "value": "GDP growth"},
                    "countryiso3code": "USA",
                    "date": "2023",
                    "value": 2.5,
                }
            ],
        ]

        with patch("hermes.connectors.base.Client") as client_cls:
            _mock_client(client_cls, payload=mock_response)
            df = await wb._fetch("USA", "NY.GDP.MKTP.KD.ZG")
            assert not df.is_empty()
            assert df["value"].item(0) == 2.5
            assert df["country"].item(0) == "USA"
            assert df["source"].item(0) == "World_Bank"

    async def test_fetch_no_data(self):
        wb = World_bank(cache=None)
        mock_response = [{"page": 1, "pages": 1}, []]

        with patch("hermes.connectors.base.Client") as client_cls:
            _mock_client(client_cls, payload=mock_response)
            df = await wb._fetch("XYZ", "SOME.IND")
            assert df.is_empty()

    async def test_fetch_http_error(self):
        wb = World_bank(cache=None)

        with patch("hermes.connectors.base.Client") as client_cls:
            _mock_client(client_cls, error=AcquisitionError("404", status_code=404))
            with pytest.raises(AcquisitionError):
                await wb._fetch("USA", "BAD")

    async def test_fetch_retry_on_timeout(self):
        wb = World_bank(cache=None)

        with patch("hermes.connectors.base.Client") as client_cls:
            _mock_client(client_cls, error=aiohttp.ClientError("timeout"))
            with pytest.raises(aiohttp.ClientError):
                await wb._fetch("USA", "NY.GDP.MKTP.KD.ZG", retries=1)

    async def test_public_fetch_uses_cache(self, tmp_cache):
        wb = World_bank(cache=tmp_cache)
        mock_response = [
            {"page": 1, "pages": 1, "per_page": 1000, "total": 1},
            [
                {
                    "indicator": {"id": "GDP.PROT", "value": "Test"},
                    "countryiso3code": "USA",
                    "date": "2023",
                    "value": 3.0,
                }
            ],
        ]

        with patch("hermes.connectors.base.Client") as client_cls:
            client = _mock_client(client_cls, payload=mock_response)
            df1 = await wb.fetch("USA", "GDP.PROT")
            df2 = await wb.fetch("USA", "GDP.PROT")
            assert client.get.await_count == 1
            assert not df1.is_empty()
            assert not df2.is_empty()
