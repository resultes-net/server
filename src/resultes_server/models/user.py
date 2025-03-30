import typing as _tp

import pydantic as _pyd
import sqlmodel as _sqlm

if _tp.TYPE_CHECKING:
    from .simulations import simulation as _sim


class UserBase(_sqlm.SQLModel):
    user_name: str
    email: _pyd.EmailStr
    full_name: str
    disabled: bool

    simulations: list[_sim.Simulation] = _sqlm.Relationship(back_populates="user")


class User(UserBase, table=True):
    hashed_password: str
