import resultes_pydantic_models.weather_data as _pwd
import sqlalchemy as _sqla
import sqlmodel as _sqlm

import database_utils.helpers as _dbh
import sqlmodel_models.base as _smb


class WeatherData(_pwd.GetWeatherData, _smb.SQLModelWithID, table=True):
    __table_args__ = (
        _sqla.UniqueConstraint("user_id", "name", postgresql_nulls_not_distinct=True),
    )

    id: str = _dbh.ID_FIELD
    name: str = _sqlm.Field(max_length=128)
    file_name: str = _sqlm.Field(max_length=1024)

    user_id: str | None = _sqlm.Field(
        default=None, foreign_key="user.id", max_length=16, nullable=True
    )

    @property
    def is_shared(self) -> bool:
        return self.user_id is None

    def to_model_weather_data(self) -> _pwd.GetWeatherData:
        return _pwd.GetWeatherData(
            id=self.id,
            name=self.name,
            file_name=self.file_name,
            format=self.format,
            user_id=self.user_id,
        )
