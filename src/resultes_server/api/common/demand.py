import typing as _tp

import fastapi as _fapi
import pydantic as _pc


class Demand(_pc.BaseModel):
    profile: _tp.Union["PreDefinedProfile", "UserProvidedProfile"] = _pc.Field(
        discriminator="profile_type"
    )


class PreDefinedProfile(_pc.BaseModel):
    profile_type: _tp.Literal["predefined"]
    name: str


class UserProvidedProfile(_pc.BaseModel):
    profile_type: _tp.Literal["user-provided"]
    data: _fapi.UploadFile
