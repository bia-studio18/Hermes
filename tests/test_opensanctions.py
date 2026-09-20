from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from hermes.connectors.opensanctions import OpenSanction, iso3_to_iso2
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


class TestIso3ToIso2:
    def test_valid(self):
        assert iso3_to_iso2("USA") == "US"

    def test_invalid(self):
        assert iso3_to_iso2("ZZZ") == "Not Found"


class TestOpenSanction:
    async def test_fetch_success(self, tmp_cache):
        os = OpenSanction(cache=tmp_cache)

        with patch("hermes.connectors.base.Client") as client_cls:
            client = _mock_client(client_cls, payload={"results": []})
            await os.fetch("USA", dataset="default", limit=0)
            assert client.get.await_count == 1

    async def test_fetch_404(self, tmp_cache):
        os = OpenSanction(cache=tmp_cache)

        with patch("hermes.connectors.base.Client") as client_cls:
            _mock_client(client_cls, error=AcquisitionError("404", status_code=404))
            result = await os.fetch("USA", dataset="default", limit=0)
            assert result == {}

    async def test_fetch_http_error(self, tmp_cache):
        os = OpenSanction(cache=tmp_cache)

        with patch("hermes.connectors.base.Client") as client_cls:
            _mock_client(client_cls, error=AcquisitionError("500", status_code=500))
            with pytest.raises(AcquisitionError):
                await os.fetch("USA", dataset="default", limit=0)

    async def test_no_dataset_raises(self, tmp_cache):
        os = OpenSanction(cache=tmp_cache)
        with pytest.raises(ValueError, match="dataset parameter is empty"):
            await os.fetch("USA", dataset="", limit=0)
