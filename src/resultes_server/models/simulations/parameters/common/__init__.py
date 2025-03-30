import typing as _tp

import pydantic as _pc

_T_inv = _tp.TypeVar("_T_inv")


class ScaledValue(_pc.BaseModel, _tp.Generic[_T_inv]):
    """This value's unit needs to be multiplied by the unit indicated by `scaling` to arrive at the final unit."""

    scaling: _T_inv
    value: float
