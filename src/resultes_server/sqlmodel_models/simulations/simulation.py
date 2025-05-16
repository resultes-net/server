import enum as _enum
import typing as _tp

import pydantic as _pyd
import resultes_pydantic_models.simulations.parameters.ttes as _ttes
import sqlmodel as _sqlm

import resultes_server.database_utils.helpers as _dbh
import resultes_server.sqlmodel_models.simulations.variation as _var
import resultes_server.type_decorators as _td

if _tp.TYPE_CHECKING:
    from resultes_server.sqlmodel_models.user import User


@_enum.verify(_enum.UNIQUE)
class Type(_enum.Enum):
    TTES = "ttes"
    PTES = "ptes"
    BTES = "btes"


@_enum.verify(_enum.UNIQUE)
class SimulationState(_enum.Enum):
    WAITING_FOR_VARIATIONS_CREATION = "waiting-for-variations-creation"
    WAITING_FOR_VARIATION_RUNS = "waiting-for-variation-runs"
    WAITING_FOR_CROSS_VARIATION_PROCESSING = "waiting-for-cross-variation-processing"
    DONE = "done"


class Simulation(_sqlm.SQLModel, table=True):
    type: Type
    parameters: _ttes.TtesParameters = _td.TTES_PARAMETERS_FIELD

    id: str | None = _dbh.ID_FIELD
    created_on: _dbh.AwarePastDatetime = _dbh.UTC_NOW_FIELD

    user_id: str = _dbh.create_id_field(foreign_key="user.id")
    user: "User" = _sqlm.Relationship(back_populates="simulations")

    object_storage_url: _pyd.HttpUrl | None = _dbh.HTTP_URL_FIELD

    state: SimulationState = SimulationState.WAITING_FOR_VARIATIONS_CREATION
    state_changed_on: _dbh.AwarePastDatetime = _dbh.UTC_NOW_FIELD

    variations: list[_var.Variation] = _sqlm.Relationship(back_populates="simulation")
