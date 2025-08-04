import typing as _tp

import pydantic as _pyd
import resultes_pydantic_models.common as _pcom
import resultes_pydantic_models.simulations.parameters.ttes as _pttes
import resultes_pydantic_models.simulations.simulation as _psim
import sqlmodel as _sqlm

import database_utils.helpers as _dbh
import sqlmodel_models.simulations.variation as _var
import type_decorators as _td

if _tp.TYPE_CHECKING:
    from sqlmodel_models.user import User


class Simulation(_psim.SimulationBase, _sqlm.SQLModel, table=True):
    parameters: _pttes.TtesParameters = _td.TTES_PARAMETERS_FIELD

    id: str | None = _dbh.ID_FIELD
    created_on: _pcom.AwarePastDatetime = _dbh.create_utc_now_field()

    user_id: str = _dbh.create_id_field(foreign_key="user.id")
    user: "User" = _dbh.create_eager_relationship("simulations")

    object_storage_url: _pyd.HttpUrl | None = _dbh.HTTP_URL_FIELD

    state_changed_on: _pcom.AwarePastDatetime = _dbh.create_utc_now_field()

    variations: list[_var.Variation] = _dbh.create_eager_relationship("simulation")
