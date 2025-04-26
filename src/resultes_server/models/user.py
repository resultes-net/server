import typing as _tp

import pydantic as _pyd
import sqlmodel as _sqlm

import resultes_server.database_utils.helpers as _dbh

if _tp.TYPE_CHECKING:
    from .simulations import simulation as _sim


class UserBase(_sqlm.SQLModel):
    id: str | None = _dbh.ID_FIELD
    user_name: str
    email: _pyd.EmailStr
    full_name: str
    disabled: bool


class User(UserBase, table=True):
    hashed_password: str

    simulations: list["_sim.Simulation"] = _sqlm.Relationship(back_populates="user")
