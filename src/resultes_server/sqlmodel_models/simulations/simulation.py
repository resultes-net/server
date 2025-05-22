import typing as _tp

import pydantic as _pyd
import resultes_pydantic_models.simulations.parameters.ttes as _pttes
import resultes_pydantic_models.simulations.simulation as _psim
import sqlmodel as _sqlm

import resultes_server.database_utils.helpers as _dbh
import resultes_server.sqlmodel_models.simulations.variation as _var
import resultes_server.type_decorators as _td

if _tp.TYPE_CHECKING:
    from resultes_server.sqlmodel_models.user import User


class Simulation(_psim.Simulation, _sqlm.SQLModel, table=True):
    parameters: _pttes.TtesParameters = _td.TTES_PARAMETERS_FIELD

    id: str | None = _dbh.ID_FIELD
    created_on: _dbh.AwarePastDatetime = _dbh.UTC_NOW_FIELD

    user_id: str = _dbh.create_id_field(foreign_key="user.id")
    user: "User" = _sqlm.Relationship(back_populates="simulations")

    object_storage_url: _pyd.HttpUrl | None = _dbh.HTTP_URL_FIELD

    state_changed_on: _dbh.AwarePastDatetime = _dbh.UTC_NOW_FIELD

    variations: list[_var.Variation] = _sqlm.Relationship(back_populates="simulation")
