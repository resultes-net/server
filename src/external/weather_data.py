import collections.abc as _cabc
import pathlib as _pl
import tempfile as _tf
import zipfile as _zf

import fastapi as _fapi
import pvlib.iotools as _pviot
import resultes_openstack_utils.swift_multithreaded as _sm
import resultes_pydantic_models.weather_data as _pwd
import sqlalchemy.exc as _saexc
import sqlmodel as _sqlm
import sqlmodel.ext.asyncio.session as _sqlmas
import sqlmodel.sql.expression as _sqlmse

import sqlmodel_models.user as _muser
import sqlmodel_models.weather_data as _wd

N_HOURS_PER_TYPICAL_YEAR = 8760


def _create_accessible_by_query(
    user: _muser.User,
) -> _sqlmse.SelectOfScalar[_wd.WeatherData]:
    return _sqlm.select(_wd.WeatherData).where(
        _sqlm.or_(
            _sqlm.col(_wd.WeatherData.user_id).is_(None),
            _wd.WeatherData.user_id == user.id,
        )
    )


async def get_all_weather_data(
    user: _muser.User,
    session: _sqlmas.AsyncSession,
) -> _cabc.Sequence[_pwd.GetWeatherData]:
    query = _create_accessible_by_query(user).order_by(
        _sqlm.col(_wd.WeatherData.user_id).is_not(None), _wd.WeatherData.name
    )

    rows = await session.exec(query)

    return [r.to_model_weather_data() for r in rows.all()]


async def get_weather_data(
    weather_data_id: str,
    user: _muser.User,
    session: _sqlmas.AsyncSession,
) -> _pwd.GetWeatherData:
    weather_data = await get_accessible_weather_data_or_none(
        weather_data_id, user, session
    )

    if not weather_data:
        raise _fapi.HTTPException(
            status_code=_fapi.status.HTTP_404_NOT_FOUND,
        )

    return weather_data.to_model_weather_data()


async def get_accessible_weather_data_or_none(
    weather_data_id: str,
    user: _muser.User,
    session: _sqlmas.AsyncSession,
) -> _wd.WeatherData | None:
    query = _create_accessible_by_query(user).where(
        _wd.WeatherData.id == weather_data_id
    )

    rows = await session.exec(query)

    return rows.one_or_none()


async def create_weather_data(
    create_weather_data: _pwd.CreateWeatherData,
    user: _muser.User,
    session: _sqlmas.AsyncSession,
    swift: _sm.Swift,
) -> _pwd.GetWeatherData:
    try:
        # `Base64Str` has already decoded the contents during validation.
        contents = fix_up_and_validate_tm2_contents(create_weather_data.contents)
    except ValueError:
        detail = """\
The contents provided are not in the TMY2 format. For more details see
https://pvlib-python.readthedocs.io/en/v0.9.0/generated/pvlib.iotools.read_tmy2.html#pvlib-iotools-read-tmy2.
"""
        raise _fapi.HTTPException(
            status_code=_fapi.status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=detail,
        )

    weather_data = _wd.WeatherData(
        name=create_weather_data.name,
        file_name=create_weather_data.file_name,
        format=create_weather_data.format,
        user_id=user.id,
    )

    session.add(weather_data)

    # Committing *before* uploading rejects a duplicate name before anything is uploaded.
    try:
        await session.commit()
    except _saexc.IntegrityError:
        await session.rollback()
        raise _fapi.HTTPException(
            status_code=_fapi.status.HTTP_409_CONFLICT,
            detail="Weather data with given name already exists.",
        )

    try:
        with _tf.TemporaryDirectory() as temporary_dir_path:
            zip_file_path = _pl.Path(temporary_dir_path) / "weather-data.zip"
            write_zip_file(
                weather_data.to_model_weather_data(), contents, zip_file_path
            )

            object_storage_file_path = _pwd.get_object_storage_output_file_path(
                weather_data
            )
            await swift.upload(zip_file_path, object_storage_file_path)
    except:
        await session.delete(weather_data)
        await session.commit()
        raise

    return weather_data.to_model_weather_data()


def write_zip_file(
    weather_data: _pwd.GetWeatherData, contents: str, zip_file_path: _pl.Path
) -> None:
    """Writes the zip in which the object store holds `weather_data` (see `pydantic-models`)."""
    with _zf.ZipFile(zip_file_path, "w", compression=_zf.ZIP_DEFLATED) as zip_file:
        zip_file.writestr(_pwd.get_data_file_name(weather_data.format), contents)
        zip_file.writestr(_pwd.README_FILE_NAME, _create_readme_contents(weather_data))


def _create_readme_contents(weather_data: _pwd.GetWeatherData) -> str:
    data_file_name = _pwd.get_data_file_name(weather_data.format)
    origin = "shared" if weather_data.user_id is None else "uploaded by a user"

    return f"""\
# Weather data

The simulation used the weather data described below. Its data are in `{data_file_name}`.

- Name: {weather_data.name}
- Original file name: {weather_data.file_name}
- Format: {weather_data.format.value}
- Origin: {origin}
"""


def fix_up_and_validate_tm2_contents(contents: str) -> str:
    """Fixes up `contents` so that `pvlib` can read it and validates it by doing so.

    TMY2 files as, e.g., created by Meteonorm (and shipped with TRNSYS) deviate slightly from what
    `pvlib` expects. The fix-ups keep all fields at their positions, so the fixed up contents are
    still valid TMY2.

    Raises a `ValueError` if `pvlib` can't read the fixed up contents.
    """
    line_separator = "\r\n" if "\r\n" in contents else "\n"
    lines = contents.splitlines()

    if not len(lines) > 1:
        raise ValueError("Header and at least one data line expected.")

    n_data_lines = len(lines) - 1
    if n_data_lines != N_HOURS_PER_TYPICAL_YEAR:
        raise ValueError(
            f"Expected {N_HOURS_PER_TYPICAL_YEAR} data lines but got {n_data_lines}."
        )

    header_line = _fix_up_tm2_header_line(lines[0])
    data_lines = [_fix_up_tm2_data_line(l) for l in lines[1:]]

    fixed_up_contents = line_separator.join([header_line, *data_lines]) + line_separator

    with _tf.TemporaryDirectory() as temporary_dir_path:
        file_path = _pl.Path(temporary_dir_path) / "weather-data.tm2"
        file_path.write_text(fixed_up_contents, newline="")

        try:
            _ = _pviot.read_tmy2(str(file_path))
        except (IndexError, KeyError) as error:
            raise ValueError("Couldn't parse contents.") from error

    return fixed_up_contents


def _fix_up_tm2_header_line(header_line: str) -> str:
    # `pvlib` splits the header at whitespace, so the station number and the city must be separated
    # by whitespace, and neither the city nor the state may be empty or contain spaces.
    if not len(header_line) > 32:
        raise ValueError("Header line too short.")

    # Meteonorm uses six instead of five digits for the station number, which then runs into the
    # city. Moving it into the leading blank separates the two.
    station_number = header_line[:7]
    if station_number[0] == " " and station_number[-1] != " ":
        station_number = station_number[1:] + " "

    city = header_line[7:30]
    trimmed_city = city.rstrip()
    city = (trimmed_city.replace(" ", "_") or "XX").ljust(len(city))

    state = header_line[30:32]
    if state == "  ":
        state = "XX"

    return station_number + city + state + header_line[32:]


def _fix_up_tm2_data_line(data_line: str) -> str:
    # `pvlib` expects the (10 digits wide) "present weather" field to consist of digits only.
    if not len(data_line) > 123:
        raise ValueError("Data line too short.")

    if data_line[113:123] == "99999999?0":
        return data_line[:113] + ("9" * 10) + data_line[123:]

    return data_line


def test_fix_up_and_validate_tm2_contents() -> None:
    path = _pl.Path("/mnt/c/TRNSYS18/Weather/Meteonorm/Europe/BG-Pleven-155260.tm2")
    with path.open(newline="") as file:
        contents = file.read()

    fixed_up_contents = fix_up_and_validate_tm2_contents(contents)

    assert len(fixed_up_contents) == len(contents)


def test_write_zip_file(tmp_path: _pl.Path) -> None:
    weather_data = _pwd.GetWeatherData(
        id="5e0a17c3d2",
        name="My weather data",
        file_name="my-weather-data.tm2",
        format=_pwd.WeatherDataFormat.TM2,
        user_id="b4f29e7a01",
    )
    zip_file_path = tmp_path / "weather-data.zip"

    write_zip_file(weather_data, "contents\r\n", zip_file_path)

    with _zf.ZipFile(zip_file_path) as zip_file:
        assert sorted(zip_file.namelist()) == [
            "README.md",
            "data.tm2",
        ]
        assert zip_file.read("data.tm2") == b"contents\r\n"
        readme_contents = zip_file.read("README.md").decode()

    assert "My weather data" in readme_contents
    assert "my-weather-data.tm2" in readme_contents
    assert "5e0a17c3d2" not in readme_contents
