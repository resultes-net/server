import dataclasses as _dc
import typing as _tp

import fastapi as _fapi

from .. import common as _acom


@_dc.dataclass
class Demand:
    profile: _tp.Union["PreDefinedProfile", "UserProvidedProfile"] = (
        _acom.field(discriminator="profile_type")
    )


@_dc.dataclass
class PreDefinedProfile:
    profile_type: _tp.Literal["predefined"]
    name: str


@_dc.dataclass
class UserProvidedProfile:
    profile_type: _tp.Literal["user-provided"]
    data: _fapi.UploadFile
