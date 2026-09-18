import polars as pl
from typing import Literal

from hermes.normalization.rule import NormalizationRule

class Rename(NormalizationRule):

    def __init__(self, rename: dict[str, str]):
        self._renames = rename

    def apply(self, data: pl.DataFrame):
        return data.rename(self._renames)


class Cast(NormalizationRule):

    def __init__(self, cast: dict[str, str]):
        self._cast = cast

    def apply(self, data: pl.DataFrame) -> pl.DataFrame:
        type_mapping = {
            col: getattr(pl, _type) for col, _type in self._cast.items()
        }
        
        return data.cast(type_mapping)
"""
NormalizeString(
    "company_name",
    strip=True,
    collapse_whitespace=True,
    case="lower",
    unicode="NFKC",
)
"""
class NormalizeString(NormalizationRule):

    def __init__(
        self,
        strip: bool = True,
        collapse_whitespace: bool = True,
        case: Literal['lower', 'upper'] = 'lower'
    ): ...