from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from hermes.connectors.finnhub import FINNHUB
from hermes.core.errors import AcquisitionError


def _mock_client(client_cls, payload=None, error=None, effects=None):
    client = MagicMock()
    if effects is not None:
        client.get = MagicMock(side_effect=effects)
    elif error is not None:
        client.get = MagicMock(side_effect=error)
    else:
        client.get = MagicMock(return_value=payload)
    client_cls.return_value.__enter__.return_value = client
    return client


class TestFinnhubBuildUrl:
    def test_valid_endpoints(self):
        finn = FINNHUB(cache=None)
        for endpoint in [
            "quote",
            "profile",
            "metric",
            "peers",
            "earnings",
            "insider",
            "eps",
            "ebitda",
            "revenue",
            "news",
            "symbol",
            "candles",
        ]:
            url = finn.build_url(endpoint)
            assert url.startswith("https://finnhub.io/api/v1/")

    def test_quote_url(self):
        finn = FINNHUB(cache=None)
        url = finn.build_url("quote")
        assert url.endswith("/quote")

    def test_invalid_endpoint(self):
        finn = FINNHUB(cache=None)
        with pytest.raises(ValueError, match="Unsupported endpoint"):
            finn.build_url("nonexistent")


class TestFinnhubFetch:
    def test_fetch_quote(self):
        finn = FINNHUB(cache=None)
        mock_response = {"c": 150.0, "d": 2.5, "dp": 1.69, "h": 152.0, "l": 148.0, "o": 149.0, "pc": 147.5}

        with patch("hermes.connectors.base.Client") as client_cls:
            _mock_client(client_cls, payload=mock_response)
            result = finn._fetch(endpoint="quote", symbol="AAPL")
            assert result["c"] == 150.0

    def test_fetch_profile(self):
        finn = FINNHUB(cache=None)
        mock_response = {"ticker": "AAPL", "name": "Apple Inc.", "exchange": "NASDAQ"}

        with patch("hermes.connectors.base.Client") as client_cls:
            _mock_client(client_cls, payload=mock_response)
            result = finn._fetch(endpoint="profile", symbol="AAPL")
            assert result["ticker"] == "AAPL"

    def test_fetch_candles_requires_params(self):
        finn = FINNHUB(cache=None)
        with pytest.raises(ValueError, match="requires resolution"):
            finn._fetch(endpoint="candles", symbol="AAPL")

    def test_fetch_404(self):
        finn = FINNHUB(cache=None)

        with patch("hermes.connectors.base.Client") as client_cls:
            _mock_client(client_cls, error=AcquisitionError("404", status_code=404))
            result = finn._fetch(endpoint="quote", symbol="BAD")
            assert result is None

    def test_fetch_http_error(self):
        finn = FINNHUB(cache=None)

        with patch("hermes.connectors.base.Client") as client_cls:
            _mock_client(client_cls, error=AcquisitionError("500", status_code=500))
            with pytest.raises(AcquisitionError):
                finn._fetch(endpoint="quote", symbol="AAPL")

    def test_fetch_returns_data(self, tmp_cache):
        finn = FINNHUB(cache=tmp_cache)
        mock_response = {"c": 150.0, "d": 2.5}

        with patch("hermes.connectors.base.Client") as client_cls:
            _mock_client(client_cls, payload=mock_response)
            r1 = finn.fetch(endpoint="quote", symbol="AAPL")
            assert r1 == mock_response
