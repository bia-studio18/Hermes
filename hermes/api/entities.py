from typing import TYPE_CHECKING, Any

from hermes.core.result import Result

if TYPE_CHECKING:
    from polars import DataFrame


def resolve(data: "DataFrame | Any", **options: Any) -> Result:
    raise NotImplementedError("entity resolution is not built yet; value similarity is available on hermes._rust.er")


__all__ = ["resolve"]
