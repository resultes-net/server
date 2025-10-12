import typing as _tp

import pydantic as _pyd
import resultes_pydantic_models.common as _pcom
import resultes_pydantic_models.simulations.parameters.ptes as _pptes
import resultes_pydantic_models.simulations.parameters.ttes as _pttes
import resultes_pydantic_models.simulations.simulation as _psim

import database_utils.helpers as _dbh
import sqlmodel_models.base as _smb
import sqlmodel_models.simulations.variation as _var
import type_decorators as _td

if _tp.TYPE_CHECKING:
    from sqlmodel_models.user import User


class Simulation(
    _psim.SimulationBase, _smb.SQLModelWithIDAndState[_psim.SimulationState], table=True
):
    id: str | None = _dbh.ID_FIELD

    created_on: _pcom.AwarePastDatetime = _dbh.create_utc_now_field()
    state_changed_on: _pcom.AwarePastDatetime = _dbh.create_utc_now_field()

    parameters: _pttes.TtesParameters | _pptes.PtesParameters = _td.PARAMETERS_FIELD

    user_id: str = _dbh.create_id_field(foreign_key="user.id")
    user: "User" = _dbh.create_eager_relationship("simulations")

    object_storage_url: _pyd.HttpUrl | None = _dbh.HTTP_URL_FIELD

    variations: list[_var.Variation] = _dbh.create_eager_relationship("simulation")

    def to_model_simulation(self) -> _psim.Simulation:
        if not self.id:
            raise ValueError("ID not set.")

        return _psim.Simulation(
            id=self.id,
            created_on=self.created_on,
            state=self.state,
            state_changed_on=self.state_changed_on,
            user_id=self.user_id,
            parameters=self.parameters,
            object_storage_url=self.object_storage_url,
        )
