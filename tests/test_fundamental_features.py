from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from hermes.features.financial.fundamental import FAfeatures


class TestExtractFundsSec:
    def test_extracts_fields(self):
        fa = FAfeatures(finnhub_api="key", sec_email="e@e.com", sec_username="u", fred_api="key")
        data = {
            "facts": {
                "us-gaap": {
                    "Revenues": {"units": {"USD": [{"val": 394328000000}]}},
                    "CostOfRevenue": {"units": {"USD": [{"val": 214137000000}]}},
                    "GrossProfit": {"units": {"USD": [{"val": 180191000000}]}},
                    "NetIncomeLoss": {"units": {"USD": [{"val": 96995000000}]}},
                    "EarningsPerShareBasic": {"units": {"USD/Shares": [{"val": 6.13}]}},
                    "EarningsPerShareDiluted": {"units": {"USD/Shares": [{"val": 6.07}]}},
                    "AssetsCurrent": {"units": {"USD": [{"val": 143534000000}]}},
                    "Assets": {"units": {"USD": [{"val": 352755000000}]}},
                    "LiabilitiesCurrent": {"units": {"USD": [{"val": 145308000000}]}},
                    "Liabilities": {"units": {"USD": [{"val": 290437000000}]}},
                    "StockholdersEquity": {"units": {"USD": [{"val": 62318000000}]}},
                }
            }
        }
        result = fa.extract_funds_sec(data)
        assert result["revenue"] == 394328000000
        assert result["cost_of_revenue"] == 214137000000
        assert result["gross_profit"] == 180191000000
        assert result["net_income"] == 96995000000
        assert result["eps_basic"] == 6.13
        assert result["eps_diluted"] == 6.07
        assert result["current_assets"] == 143534000000
        assert result["total_assets"] == 352755000000
        assert result["equity"] == 62318000000

    def test_missing_tags_return_none(self):
        fa = FAfeatures(finnhub_api="key", sec_email="e@e.com", sec_username="u", fred_api="key")
        data = {"facts": {"us-gaap": {}}}
        result = fa.extract_funds_sec(data)
        assert result["revenue"] is None
        assert result["net_income"] is None


class TestExtractFilingMeta:
    def test_extracts_meta(self):
        fa = FAfeatures(finnhub_api="key", sec_email="e@e.com", sec_username="u", fred_api="key")
        data = {
            "facts": {
                "us-gaap": {
                    "Revenues": {
                        "units": {"USD": [{"val": 100, "filed": "2023-10-27", "fy": 2023, "fp": "FY", "form": "10-K"}]}
                    }
                }
            }
        }
        result = fa.extract_filing_meta(data)
        assert result["filing_date"] == "2023-10-27"
        assert result["fiscal_year"] == 2023
        assert result["fiscal_period"] == "FY"
        assert result["filing_type"] == "10-K"

    def test_empty_facts(self):
        fa = FAfeatures(finnhub_api="key", sec_email="e@e.com", sec_username="u", fred_api="key")
        data = {"facts": {"us-gaap": {}}}
        result = fa.extract_filing_meta(data)
        assert result["filing_date"] is None
        assert result["fiscal_year"] is None
