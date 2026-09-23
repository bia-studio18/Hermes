from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from hermes.connectors.imf import IMF
from hermes.core.errors import AcquisitionError
from hermes.entities.countries import iso3_to_iso2


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


@pytest.fixture
def sample_sdmx_response():
    return {
        "data": {
            "structures": [
                {
                    "dimensions": {
                        "series": [
                            {"id": "FREQ", "values": [{"id": "A", "name": "Annual"}]},
                            {"id": "INDICATOR", "values": [{"id": "PPI.IX.A", "name": "PPI"}]},
                            {"id": "COUNTRY", "values": [{"id": "USA", "name": "United States"}]},
                        ],
                        "observation": [
                            {
                                "id": "TIME_PERIOD",
                                "values": [
                                    {"id": "2023", "name": "2023", "value": "2023"},
                                    {"id": "2022", "name": "2022", "value": "2022"},
                                ],
                            },
                        ],
                    }
                }
            ],
            "dataSets": [
                {
                    "series": {
                        "0:0:0": {
                            "observations": {
                                "0": [110.5],
                                "1": [107.2],
                            }
                        }
                    }
                }
            ],
        }
    }


class TestIso3ToIso2:
    def test_valid(self):
        assert iso3_to_iso2("USA") == "US"

    def test_invalid(self):
        assert iso3_to_iso2("ZZZ") == "Not Found"


class TestIMF:
    def test_fetch_success(self, sample_sdmx_response):
        imf = IMF(cache=None)

        with patch("hermes.connectors.base.Client") as client_cls:
            _mock_client(client_cls, payload=sample_sdmx_response)
            df = imf._fetch("USA", "IMF.STA", "PPI", "PPI.IX.A")
            assert not df.is_empty()
            assert df["value"].item(0) == 110.5
            assert df["country"].item(0) == "USA"
            assert df["source"].item(0) == "IMF"

    def test_fetch_no_series(self):
        imf = IMF(cache=None)
        mock_response = {
            "data": {
                "structures": [
                    {
                        "dimensions": {
                            "series": [],
                            "observation": [{"id": "TIME_PERIOD", "values": []}],
                        }
                    }
                ],
                "dataSets": [{}],
            }
        }

        with patch("hermes.connectors.base.Client") as client_cls:
            _mock_client(client_cls, payload=mock_response)
            df = imf._fetch("USA", "IMF.STA", "PPI", "PPI.IX.A")
            assert df.is_empty()

    def test_fetch_404(self):
        imf = IMF(cache=None)

        with patch("hermes.connectors.base.Client") as client_cls:
            _mock_client(client_cls, error=AcquisitionError("404", status_code=404))
            df = imf._fetch("USA", "IMF.STA", "BAD", "X")
            assert df.is_empty()

    def test_fetch_http_error(self):
        imf = IMF(cache=None)

        with patch("hermes.connectors.base.Client") as client_cls:
            _mock_client(client_cls, error=AcquisitionError("500", status_code=500))
            with pytest.raises(AcquisitionError):
                imf._fetch("USA", "IMF.STA", "PPI", "PPI.IX.A")
