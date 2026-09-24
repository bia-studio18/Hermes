from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from hermes.connectors.binance import Binance
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


class TestBinanceBuildUrl:
    def test_spot_ohlcv(self):
        b = Binance(cache=None)
        url, params = b._build_url("spot", "ohlcv", "BTCUSDT", interval="1d", limit="30")
        assert "api.binance.com" in url
        assert params["symbol"] == "BTCUSDT"
        assert params["interval"] == "1d"
        assert params["limit"] == "30"

    def test_future_trades(self):
        b = Binance(cache=None)
        url, params = b._build_url("future", "trades", "BTCUSDT", limit="100")
        assert "fapi.binance.com" in url
        assert params["symbol"] == "BTCUSDT"

    def test_unknown_endpoint(self):
        b = Binance(cache=None)
        with pytest.raises(ValueError, match="unknown endpoint"):
            b._build_url("spot", "nonexistent", "BTCUSDT")

    def test_missing_required_param(self):
        b = Binance(cache=None)
        with pytest.raises(ValueError, match="requires"):
            b._build_url("spot", "ohlcv", "BTCUSDT")

    def test_order_book(self):
        b = Binance(cache=None)
        url, params = b._build_url("spot", "order_book", "BTCUSDT", limit="20")
        assert "depth" in url
        assert params["limit"] == "20"

    def test_funding_rate(self):
        b = Binance(cache=None)
        url, params = b._build_url("future", "fundingRate", "BTCUSDT", limit="5")
        assert "fundingRate" in url


class TestBinanceFetch:
    def test_fetch_success(self):
        b = Binance(cache=None)
        mock_response = [[1711900800000, "65000", "65500", "64800", "65200", "1000"]]

        with patch("hermes.connectors.base.Client") as client_cls:
            _mock_client(client_cls, payload=mock_response)
            result = b._fetch(mode="spot", endpoint="ohlcv", symbol="BTCUSDT", interval="1d", limit=30)
            assert result == mock_response

    def test_fetch_404(self):
        b = Binance(cache=None)

        with patch("hermes.connectors.base.Client") as client_cls:
            _mock_client(client_cls, error=AcquisitionError("404", status_code=404))
            result = b._fetch(mode="spot", endpoint="ohlcv", symbol="BAD", interval="1d", limit=30)
            assert result is None

    def test_fetch_403_uses_client_retry_auth(self):
        b = Binance(cache=None)
        mock_response = [[1711900800000, "65000", "65500", "64800", "65200", "1000"]]

        with patch("hermes.connectors.base.Client") as client_cls:
            _mock_client(client_cls, payload=mock_response)
            result = b._fetch(mode="spot", endpoint="ohlcv", symbol="BTCUSDT", interval="1d", limit=30)
            assert result is not None
            client_cls.assert_called_once_with(timeout=30.0, max_retries=3, retry_auth=True)

    def test_fetch_http_error(self):
        b = Binance(cache=None)

        with patch("hermes.connectors.base.Client") as client_cls:
            _mock_client(client_cls, error=AcquisitionError("500", status_code=500))
            with pytest.raises(AcquisitionError):
                b._fetch(mode="spot", endpoint="ohlcv", symbol="BTCUSDT", interval="1d", limit=30)

    def test_fetch_returns_data(self, tmp_cache):
        b = Binance(cache=tmp_cache)
        mock_response = [[1711900800000, "65000", "65500", "64800", "65200", "1000"]]

        with patch("hermes.connectors.base.Client") as client_cls:
            _mock_client(client_cls, payload=mock_response)
            r1 = b.fetch(mode="spot", endpoint="ohlcv", symbol="BTCUSDT", interval="1d", limit=30)
            assert r1.data == mock_response
