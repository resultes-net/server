import enum as _enum

import pydantic as _pyd
import sqlmodel as _sqlm

import resultes_server.database_utils.helpers as _dbh
from . import variation as _var
from .. import user as _user


@_enum.verify(_enum.UNIQUE)
class Type(_enum.Enum):
    TTES = "ttes"
    PTES = "ptes"
    BTES = "btes"


@_enum.verify(_enum.UNIQUE)
class State(_enum.Enum):
    WAITING_FOR_VARIATION_CREATION = "waiting-for-variation-creation"
    WAITING_FOR_VARIATION_RUNS = "waiting-for-variation-runs"
    WAITING_FOR_CROSS_VARIATION_PROCESSING = "waiting-for-cross-variation-processing"
    DONE = "done"


class Simulation(_sqlm.SQLModel, table=True):
    id: str | None = _dbh.ID_FIELD
    created_on: _dbh.AwarePastDatetime = _dbh.UTC_NOW_FIELD
    type: Type
    parameters: str

    user_id: str = _dbh.create_id_field(foreign_key="user.id")
    user: "_user.User" = _sqlm.Relationship(back_populates="simulations")

    object_storage_url: _pyd.HttpUrl = _dbh.HTTP_URL_FIELD

    state: State = State.WAITING_FOR_VARIATION_CREATION
    state_changed_on: _dbh.AwarePastDatetime = _dbh.UTC_NOW_FIELD

    variations: list[_var.Variation] = _sqlm.Relationship(back_populates="simulation")
