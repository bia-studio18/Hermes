import io

import polars as pl

from hermes.core.errors import ParseError


class ParquetParser:
    def parse(self, raw_data: object, **kwargs: object) -> pl.DataFrame:
        try:
            src = raw_data
            if isinstance(src, (bytes, bytearray)):
                src = io.BytesIO(src)
            return pl.read_parquet(src, **kwargs)  # type: ignore[arg-type]
        except ParseError:
            raise
        except Exception as exc:
            raise ParseError(f"Failed to parse Parquet: {exc}") from exc
