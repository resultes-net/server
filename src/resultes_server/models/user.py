import typing as _tp

import pydantic as _pyd
import sqlmodel as _sqlm

import resultes_server.database_utils.helpers as _dbh

if _tp.TYPE_CHECKING:
    from .simulations.simulation import Simulation


class UserBase(_sqlm.SQLModel):
    user_name: str
    email: _pyd.EmailStr
    full_name: str


class UserCreate(UserBase):
    plain_password: str
    registration_key: str

class UserModify(_pyd.BaseModel):
    old_plain_password: str
    new_plain_password: str


class UserRead(UserBase):
    id: str | None = _dbh.ID_FIELD
    disabled: bool


class User(UserRead, table=True):
    hashed_password: str
    simulations: list["Simulation"] = _sqlm.Relationship(back_populates="user")
