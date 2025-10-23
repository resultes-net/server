import typing as _tp

import pydantic as _pyd
import sqlalchemy as _sqla
import sqlalchemy.types as _sqlt
import sqlmodel as _sqlm


def create_pydantic_json_field[T: _pyd.BaseModel](
    clazz: type[T],
) -> _tp.Any:
    class TypeDecorator(_sqlt.TypeDecorator[T]):
        impl = _sqla.JSON

        def process_bind_param(self, value: T, dialect) -> _pyd.JsonValue:
            return value.model_dump()

        def process_result_value(self, value, dialect) -> T:
            return clazz(**value)

    return _sqlm.Field(sa_type=TypeDecorator)
