import enum as _enum
import typing as _tp

import pydantic as _pyd
import sqlmodel as _sqlm

import resultes_server.database_utils.helpers as _dbh
from .. import user as _user

if _tp.TYPE_CHECKING:
    from . import variation as _var


@_enum.verify(_enum.UNIQUE)
class Type(_enum.Enum):
    TTES = "ttes"
    PTES = "ptes"
    BTES = "btes"


@_enum.verify(_enum.UNIQUE)
class State:
    WAITING_FOR_VARIATION_CREATION = "waiting-for-variation-creation"
    WAITING_FOR_VARIATION_RUNS = "waiting-for-variation-runs"
    WAITING_FOR_CROSS_VARIATION_PROCESSING = "waiting-for-cross-variation-processing"
    DONE = "done"


class Simulation(_sqlm.SQLModel):
    id: int | None = _dbh.ID_FIELD
    persistent_id: str = _dbh.PERSISTENT_ID_FIELD
    created_on: _dbh.AwareDatetime = _dbh.UTC_NOW_FIELD
    type: Type
    json: _pyd.JsonValue

    user: "_user.User" = _sqlm.Relationship(back_populates="simulations")

    object_storage_url: _dbh.HTTP_URL_FIELD

    state: State = State.WAITING_FOR_VARIATION_CREATION
    state_changed_on: _dbh.UTC_NOW_FIELD

    variations: list["_var.Variation"] = _sqlm.Relationship(back_populates="simulation")
