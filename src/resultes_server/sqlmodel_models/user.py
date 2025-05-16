import typing as _tp

import resultes_pydantic_models.user as _puser
import sqlmodel as _sqlm

import resultes_server.database_utils.helpers as _dbh

if _tp.TYPE_CHECKING:
    from .simulations.simulation import Simulation


class User(_sqlm.SQLModel, _puser.UserRead, table=True):
    hashed_password: str
    simulations: list["Simulation"] = _sqlm.Relationship(back_populates="user")
    id: str | None = _dbh.ID_FIELD
