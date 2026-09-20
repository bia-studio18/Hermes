from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from hermes.connectors.fred import FRED
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


class TestFRED:
    async def test_fetch_success(self):
        fred = FRED(api="test-key", cache=None)
        mock_response = {
            "observations": [
                {
                    "realtime_start": "2024-01-01",
                    "realtime_end": "2024-01-01",
                    "date": "2023-10-01",
                    "value": "27360.863",
                },
                {
                    "realtime_start": "2024-01-01",
                    "realtime_end": "2024-01-01",
                    "date": "2023-07-01",
                    "value": "27061.152",
                },
            ],
            "units": "Billions of Dollars",
        }

        with patch("hermes.connectors.base.Client") as client_cls:
            _mock_client(client_cls, payload=mock_response)
            df = await fred._fetch(series_id="GDPC1")
            assert not df.is_empty()
            assert df["value"].item(0) == "27360.863"
            assert df["series_id"].item(0) == "GDPC1"
            assert df["unit"].item(0) == "Billions of Dollars"

    async def test_fetch_404(self):
        fred = FRED(api="test-key", cache=None)

        with patch("hermes.connectors.base.Client") as client_cls:
            _mock_client(client_cls, error=AcquisitionError("404", status_code=404))
            result = await fred._fetch(series_id="BAD_SERIES")
            assert result is None

    async def test_fetch_http_error(self):
        fred = FRED(api="test-key", cache=None)

        with patch("hermes.connectors.base.Client") as client_cls:
            _mock_client(client_cls, error=AcquisitionError("500", status_code=500))
            with pytest.raises(AcquisitionError):
                await fred._fetch(series_id="GDPC1")

    async def test_fetch_retry_on_timeout(self):
        fred = FRED(api="test-key", cache=None)

        with patch("hermes.connectors.base.Client") as client_cls:
            _mock_client(client_cls, error=TimeoutError("timeout"))
            with pytest.raises(TimeoutError):
                await fred._fetch(series_id="GDPC1", retries=1)

    async def test_fetch_uses_cache(self, tmp_cache):
        fred = FRED(api="test-key", cache=tmp_cache)
        mock_response = {
            "observations": [
                {
                    "realtime_start": "2024-01-01",
                    "realtime_end": "2024-01-01",
                    "date": "2023-10-01",
                    "value": "27360.863",
                },
            ],
            "units": "Billions of Dollars",
        }

        with patch("hermes.connectors.base.Client") as client_cls:
            client = _mock_client(client_cls, payload=mock_response)
            df1 = await fred.fetch(series_id="GDPC1")
            df2 = await fred.fetch(series_id="GDPC1")
            assert client.get.await_count == 1
            assert not df1.is_empty()
            assert not df2.is_empty()
