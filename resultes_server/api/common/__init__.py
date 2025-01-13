import dataclasses as _dc
import typing as _tp


_T_inv = _tp.TypeVar("_T_inv")


@_dc.dataclass
class ScaledValue(_tp.Generic[_T_inv]):
    """This value's unit needs to be multiplied by the unit indicated by `scaling` to arrive at the final unit."""

    scaling: _T_inv
    value: float


def field(title: str | None = None, **kwargs) -> _dc.Field:
    metadata = {**kwargs}
    if title:
        metadata["title"] = title
    return _dc.field(metadata=metadata)
