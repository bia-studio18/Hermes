from __future__ import annotations

import math
from unittest.mock import AsyncMock, MagicMock, patch

import numpy as np
import pytest

from hermes.features.financial.technical import TechnicalFeatures as TAfeatures


class TestSafeDiv:
    def test_normal(self):
        assert TAfeatures._safe_div(10.0, 2.0) == 5.0

    def test_zero_divisor(self):
        assert math.isnan(TAfeatures._safe_div(10.0, 0))

    def test_none_divisor(self):
        assert math.isnan(TAfeatures._safe_div(10.0, None))


class TestSma:
    def test_valid(self):
        values = [1.0, 2.0, 3.0, 4.0, 5.0]
        assert TAfeatures._sma(values, 3) == pytest.approx(4.0)

    def test_insufficient_data(self):
        assert math.isnan(TAfeatures._sma([1.0, 2.0], 5))


class TestEma:
    def test_valid(self):
        values = list(range(1, 21))
        result = TAfeatures._ema(values, 10)
        assert isinstance(result, float)
        assert not math.isnan(result)

    def test_insufficient_data(self):
        assert math.isnan(TAfeatures._ema([1.0], 10))


class TestZscore:
    def test_valid(self):
        values = [10.0, 12.0, 11.0, 13.0, 10.5]
        result = TAfeatures._zscore(values)
        assert isinstance(result, float)
        assert not math.isnan(result)

    def test_single_value(self):
        assert math.isnan(TAfeatures._zscore([10.0]))

    def test_constant_values(self):
        result = TAfeatures._zscore([5.0, 5.0, 5.0, 5.0])
        assert result == 0.0


class TestReturns:
    def test_valid(self):
        closes = [100.0, 105.0, 103.0]
        rets = TAfeatures._returns(closes)
        assert len(rets) == 2
        assert rets[0] == pytest.approx(np.log(105.0 / 100.0))
        assert rets[1] == pytest.approx(np.log(103.0 / 105.0))


class TestCalculatePriceFeatures:
    def test_returns_dict(self):
        ta = TAfeatures()
        candles = [
            [1711900800000, "100", "105", "98", "102", "1000", "0", "100000", "500", "600"],
            [1711987200000, "102", "108", "101", "106", "1200", "0", "120000", "600", "700"],
            [1712073600000, "106", "110", "104", "109", "1100", "0", "110000", "550", "650"],
        ] * 80  # enough candles for vol_20
        result = ta.calculate_price_features(candles)
        assert isinstance(result, dict)
        assert "open" in result
        assert "close" in result
        assert "ret_1b" in result
        assert "vol_20" in result
        assert "atr_14_norm" in result

    def test_price_values(self):
        ta = TAfeatures()
        candles = [
            [1711900800000, "100", "105", "98", "102", "1000", "0", "100000", "500", "600"],
        ] * 80
        result = ta.calculate_price_features(candles)
        assert result["open"] == 100.0
        assert result["high"] == 105.0
        assert result["low"] == 98.0
        assert result["close"] == 102.0
        assert result["volume"] == 1000.0


class TestTAfeaturesSnapshot:
    async def test_snapshot_with_mocked_data(self):
        ta = TAfeatures()
        ta.binance = MagicMock()

        candles = [
            [
                1711900800000 + i * 3600000,
                str(100 + i),
                str(105 + i),
                str(98 + i),
                str(102 + i),
                "1000",
                "0",
                "100000",
                "500",
                "600",
            ]
            for i in range(250)
        ]

        trades = [{"qty": "0.5", "price": "102.0", "isBuyerMaker": False}] * 100

        order_book = {
            "bids": [["101.5", "10"], ["101.0", "20"]],
            "asks": [["102.5", "8"], ["103.0", "15"]],
        }

        day_stats = {
            "highPrice": "110.0",
            "lowPrice": "98.0",
            "lastPrice": "109.0",
            "priceChangePercent": "2.5",
            "weightedAvgPrice": "103.0",
            "volume": "50000",
            "quoteVolume": "5000000",
            "trades": "1500",
            "bidPrice": "101.5",
            "askPrice": "102.5",
        }

        funding = [{"fundingRate": "0.0001", "fundingTime": 1711900800}]

        oi = {"openInterest": "12345", "sumValue": "1234567"}

        oi_hist = [{"sumOpenInterest": "12000", "sumOpenInterestValue": "1200000"}]

        long_short = [{"longShortRatio": "1.2"}]

        premium = {"lastFundingRate": "0.0001", "nextFundingTime": 1711900800000}

        async def mock_fetch(mode, endpoint, symbol, **kwargs):
            if endpoint == "ohlcv":
                return candles
            elif endpoint == "trades":
                return trades
            elif endpoint == "order_book":
                return order_book
            elif endpoint == "24hr":
                return day_stats
            elif endpoint == "fundingRate":
                return funding
            elif endpoint == "openInterest":
                return oi
            elif endpoint == "openInterestHist":
                return oi_hist
            elif endpoint == "longShortRatio":
                return long_short
            elif endpoint == "premiumIndex":
                return premium
            return []

        ta.binance.fetch = AsyncMock(side_effect=mock_fetch)

        result = await ta.build_snapshot("BTCUSDT")
        assert result.symbol == "BTCUSDT"
        assert result.close == 351.0
        assert result.open == 349.0
