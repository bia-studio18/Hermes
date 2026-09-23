from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from hermes.connectors.opensanctions import OpenSanction, iso3_to_iso2
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


class TestIso3ToIso2:
    def test_valid(self):
        assert iso3_to_iso2("USA") == "US"

    def test_invalid(self):
        assert iso3_to_iso2("ZZZ") == "Not Found"


class TestOpenSanction:
    def test_fetch_success(self, tmp_cache):
        os = OpenSanction(cache=tmp_cache)

        with patch("hermes.connectors.base.Client") as client_cls:
            client = _mock_client(client_cls, payload={"results": []})
            os.fetch("USA", dataset="default", limit=0)
            assert client.get.call_count == 1

    def test_fetch_404(self, tmp_cache):
        os = OpenSanction(cache=tmp_cache)

        with patch("hermes.connectors.base.Client") as client_cls:
            _mock_client(client_cls, error=AcquisitionError("404", status_code=404))
            result = os.fetch("USA", dataset="default", limit=0)
            assert result == {}

    def test_fetch_http_error(self, tmp_cache):
        os = OpenSanction(cache=tmp_cache)

        with patch("hermes.connectors.base.Client") as client_cls:
            _mock_client(client_cls, error=AcquisitionError("500", status_code=500))
            with pytest.raises(AcquisitionError):
                os.fetch("USA", dataset="default", limit=0)

    def test_no_dataset_raises(self, tmp_cache):
        os = OpenSanction(cache=tmp_cache)
        with pytest.raises(ValueError, match="dataset parameter is empty"):
            os.fetch("USA", dataset="", limit=0)
