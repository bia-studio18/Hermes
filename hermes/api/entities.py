from typing import TYPE_CHECKING, Any

from hermes.core.result import Result
import hermes._rust as rust_mod

if TYPE_CHECKING:
    from polars import DataFrame

def resolve(data: "DataFrame | Any", **options: Any) -> Result:
    raise NotImplementedError("hermes._rust.er is not implemented yet")


__all__ = ["resolve"]


