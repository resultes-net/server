
import pydantic as _pyd
import sqlalchemy as _sqla
import sqlalchemy.types as _sqlt


def create_pydantic_json_type_decorator[T: _pyd.BaseModel](
    clazz: type[T],
) ->type[_sqla.TypeDecorator[T]]:
    class TypeDecorator(_sqlt.TypeDecorator[T]):
        impl = _sqla.JSON

        def process_bind_param(self, value: T, dialect) -> _pyd.JsonValue:
            return value.model_dump()

        def process_result_value(self, value, dialect) -> T:
            return clazz(**value)

    return TypeDecorator
