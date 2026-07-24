
import resultes_pydantic_models.simulations.parameters as _ppar
import sqlmodel as _sqlm

import sqlmodel_models.type_decorators as _td

ParametersTypeDecorator = _td.create_pydantic_json_type_decorator(_ppar.Parameters)


class Parameters(_sqlm.SQLModel, table=True):
    value: _ppar.Parameters = _sqlm.Field(sa_type=ParametersTypeDecorator)

    simulation_id: str = _sqlm.Field(
        primary_key=True,
        foreign_key="simulation.id",
    )
