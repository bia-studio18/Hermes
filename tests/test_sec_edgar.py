from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from hermes.connectors.sec import SECEDGAR
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


class TestSECEDGAR:
    async def test_fetch_success(self):
        sec = SECEDGAR(cache=None)
        mock_response = {
            "facts": {
                "us-gaap": {
                    "Revenues": {
                        "units": {
                            "USD": [
                                {"val": 394328000000, "fy": 2023, "fp": "FY", "filed": "2023-10-27", "form": "10-K"}
                            ]
                        }
                    }
                }
            }
        }

        with patch("hermes.connectors.base.Client") as client_cls:
            _mock_client(client_cls, payload=mock_response)
            result = await sec._fetch(symbol="AAPL")
            assert result is not None
            assert "facts" in result

    async def test_fetch_404(self):
        sec = SECEDGAR(cache=None)

        with patch("hermes.connectors.base.Client") as client_cls:
            _mock_client(client_cls, error=AcquisitionError("404", status_code=404))
            result = await sec._fetch(symbol="BAD")
            assert result is None

    async def test_fetch_http_error(self):
        sec = SECEDGAR(cache=None)

        with patch("hermes.connectors.base.Client") as client_cls:
            _mock_client(client_cls, error=AcquisitionError("500", status_code=500))
            with pytest.raises(AcquisitionError):
                await sec._fetch(symbol="AAPL")

    async def test_fetch_retry_on_timeout(self):
        sec = SECEDGAR(cache=None)

        with patch("hermes.connectors.base.Client") as client_cls:
            _mock_client(client_cls, error=TimeoutError("timeout"))
            with pytest.raises(TimeoutError):
                await sec._fetch(symbol="AAPL", retries=1)

    async def test_fetch_sends_user_agent(self):
        sec = SECEDGAR(cache=None)

        with patch("hermes.connectors.base.Client") as client_cls:
            client = _mock_client(client_cls, payload={"facts": {"us-gaap": {}}})
            await sec._fetch(symbol="AAPL")
            headers = client.get.await_args.kwargs["headers"]
            assert "User-Agent" in headers
            assert "test@example.com" in headers["User-Agent"]

    async def test_fetch_returns_data(self, tmp_cache):
        sec = SECEDGAR(cache=tmp_cache)
        mock_response = {"facts": {"us-gaap": {"Revenues": {"units": {"USD": [{"val": 100}]}}}}}

        with patch("hermes.connectors.base.Client") as client_cls:
            _mock_client(client_cls, payload=mock_response)
            r1 = await sec.fetch(symbol="AAPL")
            assert r1 == mock_response
