import resultes_pydantic_models.weather_data as _pwd
import sqlmodel.ext.asyncio.session as _sqlmas

import query_helpers as _qh
import sqlmodel_models.weather_data as _wd


async def get_weather_data(
    weather_data_id: str,
    session: _sqlmas.AsyncSession,
) -> _pwd.GetWeatherData:
    weather_data = await _qh.get_single(_wd.WeatherData, weather_data_id, session)
    return weather_data.to_model_weather_data()
