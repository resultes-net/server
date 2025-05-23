import pydantic as _pyd
import resultes_pydantic_models.simulations.parameters.ttes as _pttes
import sqlalchemy as _sqla
import sqlalchemy.types as _sqlt
import sqlmodel as _sqlm


class PydanticJsonTypeDecorator(_sqlt.TypeDecorator):
    impl = _sqla.JSON
    python_type = _pttes.TtesParameters

    def process_bind_param(self, value, dialect) -> _pyd.JsonValue:
        assert isinstance(value, _pttes.TtesParameters)

        return value.model_dump()

    def process_result_value(self, value, dialect) -> _pttes.TtesParameters:
        return _pttes.TtesParameters(**value)


TTES_PARAMETERS_FIELD = _sqlm.Field(sa_type=PydanticJsonTypeDecorator)
