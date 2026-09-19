import io
from typing import Any, cast

import polars as pl

from hermes.core.errors import ParseError


class CSVParser:
    def parse(self, raw_data: object, **kwargs: object) -> pl.DataFrame:
        try:
            src = raw_data
            if isinstance(src, (bytes, bytearray)):
                src = io.BytesIO(bytes(src))
            elif isinstance(src, str) and "\n" in src:
                src = io.BytesIO(src.encode())
            return pl.read_csv(cast(Any, src), **cast(Any, kwargs))
        except ParseError:
            raise
        except Exception as exc:
            raise ParseError(f"Failed to parse CSV: {exc}") from exc
