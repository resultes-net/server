import typing as _tp

import pydantic as _pyd
import resultes_pydantic_models.common as _pcom
import resultes_pydantic_models.simulations.parameters as _params
import resultes_pydantic_models.simulations.simulation as _psim
import sqlmodel as _sqlm

import database_utils.helpers as _dbh
import sqlmodel_models.base as _smb
import sqlmodel_models.simulations.variation as _var
import sqlmodel_models.type_decorators as _td

if _tp.TYPE_CHECKING:
    from sqlmodel_models.user import User

ParametersTypeDecorator = _td.create_pydantic_json_type_decorator(_params.Parameters)


class Simulation(
    _psim.SimulationBase, _smb.SQLModelWithIDAndState[_psim.SimulationState], table=True
):
    id: str = _dbh.ID_FIELD
    name: str = _sqlm.Field(max_length=1024)
    created_on: _pcom.AwarePastDatetime = _dbh.create_utc_now_field()
    state_changed_on: _pcom.AwarePastDatetime = _dbh.create_utc_now_field()

    parameters: _params.Parameters = _sqlm.Field(sa_type=ParametersTypeDecorator)

    user_id: str = _dbh.create_id_field(foreign_key="user.id")
    user: "User" = _dbh.create_eager_relationship("simulations")

    variations: list[_var.Variation] = _dbh.create_eager_relationship("simulation")

    def to_model_simulation(self) -> _psim.Simulation:
        if not self.id:
            raise ValueError("ID not set.")

        return _psim.Simulation(
            id=self.id,
            name=self.name,
            created_on=self.created_on,
            state=self.state,
            state_changed_on=self.state_changed_on,
            progress=self.progress,
            user_id=self.user_id,
            parameters=self.parameters,
            variations=self.variations,
        )
