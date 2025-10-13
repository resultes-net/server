import pydantic as _pyd
import resultes_pydantic_models.simulations.parameters.ptes as _pptes
import resultes_pydantic_models.simulations.parameters.ttes as _pttes
import sqlalchemy as _sqla
import sqlalchemy.types as _sqlt
import sqlmodel as _sqlm


class SimulationParametersTypeDecorator(_sqlt.TypeDecorator):
    impl = _sqla.JSON
    python_type = _pyd.BaseModel

    def process_bind_param(self, value, dialect) -> _pyd.JsonValue:
        assert isinstance(value, (_pttes.TtesParameters, _pptes.PtesParameters))

        return value.model_dump()

    def process_result_value(self, value, dialect) -> _pttes.TtesParameters:
        if "type" not in value:
            raise ValueError(
                "Values don't seem to represent simulation parameters as they are missing the `type` discriminator."
            )

        parameters_type = value["type"]

        if parameters_type == "ttes":
            return _pttes.TtesParameters(**value)
        elif parameters_type == "ptes":
            return _pptes.PtesParameters(**value)
        else:
            raise ValueError("Unknown paramters type.", parameters_type)


SIMULATION_PARAMETERS_FIELD = _sqlm.Field(sa_type=SimulationParametersTypeDecorator, discriminator="type")
