from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from hermes.connectors.world_bank import World_bank
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


class TestWorldBank:
    def test_fetch_success(self):
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
            df = wb._fetch("USA", "NY.GDP.MKTP.KD.ZG")
            assert not df.is_empty()
            assert df["value"].item(0) == 2.5
            assert df["country"].item(0) == "USA"
            assert df["source"].item(0) == "World_Bank"

    def test_fetch_no_data(self):
        wb = World_bank(cache=None)
        mock_response = [{"page": 1, "pages": 1}, []]

        with patch("hermes.connectors.base.Client") as client_cls:
            _mock_client(client_cls, payload=mock_response)
            df = wb._fetch("XYZ", "SOME.IND")
            assert df.is_empty()

    def test_fetch_http_error(self):
        wb = World_bank(cache=None)

        with patch("hermes.connectors.base.Client") as client_cls:
            _mock_client(client_cls, error=AcquisitionError("404", status_code=404))
            with pytest.raises(AcquisitionError):
                wb._fetch("USA", "BAD")

    def test_fetch_retry_on_timeout(self):
        wb = World_bank(cache=None)

        with patch("hermes.connectors.base.Client") as client_cls:
            _mock_client(client_cls, error=AcquisitionError("timeout"))
            with pytest.raises(AcquisitionError):
                wb._fetch("USA", "NY.GDP.MKTP.KD.ZG", retries=1)

    def test_public_fetch_uses_cache(self, tmp_cache):
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
            df1 = wb.fetch("USA", "GDP.PROT")
            df2 = wb.fetch("USA", "GDP.PROT")
            assert client.get.call_count == 1
            assert not df1.is_empty()
            assert not df2.is_empty()
