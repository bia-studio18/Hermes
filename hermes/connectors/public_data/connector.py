import logging
from functools import lru_cache
from pathlib import Path

import polars as pl

from hermes.parsing.engine import ParserEngine

logger = logging.getLogger(__name__)

CURRENT_DIR = Path(__file__).resolve().parent.parent

HRS_PATH = CURRENT_DIR / "lib" / "datasets" / "hrs.csv"
HDI_PATH = CURRENT_DIR / "lib" / "datasets" / "hdi1.csv"
CPI_PATH = CURRENT_DIR / "lib" / "datasets" / "global_cpi_all.csv"
FSI_PATH = CURRENT_DIR / "lib" / "datasets" / "fsi.csv"
NATO_PATH = CURRENT_DIR / "lib" / "datasets" / "nato.csv"
CRS_PATH = CURRENT_DIR / "lib" / "datasets" / "crs.csv"
CVS_PATH = CURRENT_DIR / "lib" / "datasets" / "cvs.csv"
SIPRI_PATH = CURRENT_DIR / "lib" / "datasets" / "sipri.csv"
SEC_MAP = CURRENT_DIR / "lib" / "datasets" / "cik.parquet"
COUNTRIES_PATH = CURRENT_DIR / "lib" / "datasets" / "countries.parquet"


class PUBLIC_DATASET:
    def __init__(self) -> None:
        self._parser = ParserEngine()

    def _read_csv(self, path: Path) -> pl.DataFrame:
        return self._parser.parse(path, "csv")

    def fetch_hrs(self, country: str) -> pl.DataFrame:
        df = self._read_csv(HRS_PATH)
        data = df.filter(pl.col("country") == country)
        data = data.with_columns(pl.col("date").str.to_date())
        return data

    def fetch_hdi(self, country: str) -> pl.DataFrame:
        df = self._read_csv(HDI_PATH)
        df.columns = [c if c != "" else "index" for c in df.columns]
        data = df.select(["country", "Year", "HDI"])
        data.columns = ["iso3", "year", "score"]
        data = data.with_columns(pl.col("year").cast(pl.Utf8).str.to_date())
        data = data.filter(pl.col("iso3") == country)
        return data

    def fetch_cpi(self, country: str) -> pl.DataFrame:
        df = self._read_csv(CPI_PATH)
        data = df.select(["iso3", "year", "score"])
        data = data.with_columns(pl.col("year").cast(pl.Utf8).str.to_date())
        data = data.filter(pl.col("iso3") == country)
        return data

    def fetch_fsi(self, country: str) -> pl.DataFrame:
        df = self._read_csv(FSI_PATH)
        data = df.filter(pl.col("country") == country)
        data = data.with_columns(pl.col("date").str.to_date())
        return data

    def fetch_nato(self, country: str) -> pl.DataFrame:
        df = self._read_csv(NATO_PATH)
        data = df.filter(pl.col("ISO3") == country)
        data = data.with_columns(pl.col("Year").cast(pl.Utf8).str.to_date())
        return data

    def fetch_crs(self, country: str) -> pl.DataFrame:
        df = self._read_csv(CRS_PATH)
        data = df.filter(pl.col("ISO3") == country)
        data = data.with_columns(pl.col("year").cast(pl.Utf8).str.to_date())
        return data

    def fetch_cvs(self, country: str) -> pl.DataFrame:
        df = self._read_csv(CVS_PATH)
        data = df.filter(pl.col("ISO3") == country)
        data = data.with_columns(pl.col("year").cast(pl.Utf8).str.to_date())
        return data

    def fetch_sipri(self, country: str) -> pl.DataFrame:
        df = self._read_csv(SIPRI_PATH)
        data = df.filter(pl.col("iso3") == country)
        data = data.with_columns(pl.col("year").cast(pl.Utf8).str.to_date())
        return data


def sec_mapping(symbol: str) -> str:
    _df = pl.scan_parquet(SEC_MAP)
    df = _df.filter(pl.col("ticker") == symbol).collect()
    return df["cik_str"].item()


@lru_cache(maxsize=1)
def _countries() -> pl.DataFrame:
    return pl.read_parquet(COUNTRIES_PATH)


@lru_cache(maxsize=1)
def _country_aliases() -> dict[str, str]:
    aliases: dict[str, str] = {}

    for country in _countries().to_dicts():
        alpha2 = country.get("alpha_2")

        if not alpha2:
            continue

        for field in (
            "alpha_2",
            "alpha_3",
            "name",
            "official_name",
            "common_name",
        ):
            value = country.get(field)

            if isinstance(value, str) and value:
                aliases[value.casefold()] = alpha2

    return aliases


@lru_cache(maxsize=1)
def _iso3_index() -> dict[str, str]:
    return {
        country["alpha_3"].upper(): country["alpha_2"] for country in _countries().to_dicts() if country.get("alpha_3")
    }


def iso3_to_iso2(iso3_code: str) -> str:
    return _iso3_index().get(iso3_code.upper(), "Not Found")


def check_iso3(code: str) -> None:
    if code.upper() not in _iso3_index():
        raise RuntimeError(f"The {code} is not iso3")


if __name__ == "__main__":
    print(sec_mapping("AAPL"))  # working
