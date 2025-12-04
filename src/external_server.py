import collections.abc as _cabc
import concurrent.futures as _cf
import contextlib as _ctx
import logging as _log
import os as _os
import pathlib as _pl
import typing as _tp

import fastapi as _fapi
import fastapi.responses as _fresp
import fastapi.security as _fsec
import resultes_openstack_utils.swift_multithreaded as _sm
import resultes_pydantic_models.runner as _pr
import resultes_pydantic_models.simulations.parameters as _params
import resultes_pydantic_models.simulations.simulation as _psim
import resultes_pydantic_models.simulations.variation as _pvar
import resultes_pydantic_models.user as _pu
import sqlalchemy.ext.asyncio.engine as _sqlae
import sqlmodel.ext.asyncio.session as _sqlmas
import uvicorn as _uc

import config as _config
import database_utils.helpers as _dbh
import external.auth as _auth
import external.simulations as _sims
import external.users as _users
import external.variations as _vars
import sqlmodel_models.simulations.simulation as _sim
import sqlmodel_models.user as _mu

LOG_FORMAT = "%(asctime)s - %(levelname)s - %(module)s - %(message)s"

CLOUDS_YAML_FILE_PATH = _pl.Path(
    _pl.Path(__file__).parents[1] / "config" / "clouds.yaml"
)

N_MAX_SWIFT_WORKERS = 16


def create_engine():
    return _sqlae.create_async_engine(_config.DB_CONNECTION_STRING, echo=True)


engine = create_engine()


async def get_session() -> _cabc.AsyncIterable[_sqlmas.AsyncSession]:
    async with _dbh.create_session(engine) as session:
        yield session


SessionDep = _tp.Annotated[_sqlmas.AsyncSession, _fapi.Depends(get_session)]

PASSWORD_BEARER = _fsec.OAuth2PasswordBearer(tokenUrl="token")

TokenDep = _tp.Annotated[str, _fapi.Depends(PASSWORD_BEARER)]


async def get_current_user(token: TokenDep, session: SessionDep) -> _mu.User:
    return await _auth.get_current_user(token, session)


UserDep = _tp.Annotated[_mu.User, _fapi.Depends(get_current_user)]


def get_current_active_user(current_user: UserDep) -> _mu.User:
    return _auth.get_current_active_user(current_user)


ActiveUserDep = _tp.Annotated[_mu.User, _fapi.Depends(get_current_active_user)]


@_ctx.asynccontextmanager
async def lifespan(_: _fapi.FastAPI) -> _cabc.AsyncIterator[None]:
    global swift
    with _cf.ThreadPoolExecutor(N_MAX_SWIFT_WORKERS) as executor:
        async with _sm.Swift(
            CLOUDS_YAML_FILE_PATH, executor, N_MAX_SWIFT_WORKERS
        ) as swift:
            yield


app = _fapi.FastAPI(root_path=_config.ROOT_PATH, lifespan=lifespan)


@app.post("/token")
async def create_token(
    form_data: _tp.Annotated[_fsec.OAuth2PasswordRequestForm, _fapi.Depends()],
    session: SessionDep,
) -> _auth.Token:
    token = await _auth.create_token(form_data.username, form_data.password, session)
    return token


@app.post("/user")
async def create_user(user_create: _pu.UserCreate, session: SessionDep) -> _pu.UserRead:
    return await _users.create_user(user_create, session)


@app.put("/user")
async def modify_user(
    user_modify: _pu.UserModify, user: ActiveUserDep, session: SessionDep
) -> _pu.UserRead:
    return await _users.modify_user(user_modify, user, session)


@app.post("/simulations")
async def create_and_run_new_simulation(
    parameters: _params.Parameters,
    user: ActiveUserDep,
    session: SessionDep,
) -> _psim.SimulationBase:
    simulation = _sim.Simulation(
        user=user,
        parameters=parameters,
    )

    session.add(simulation)
    await session.commit()

    return simulation


@app.get("/simulations/{simulation_id}")
async def get_simulation(
    simulation_id: str,
    user: ActiveUserDep,
    session: SessionDep,
) -> _psim.Simulation:
    return await _sims.get_simulation(simulation_id, user, session)


@app.get("/simulations")
async def get_simulations(
    user: ActiveUserDep,
    session: SessionDep,
) -> _cabc.Sequence[_psim.Simulation]:
    return await _sims.get_simulations(user, session)


@app.get("/variations/{variation_id}")
async def get_variation(
    variation_id: str,
    user: ActiveUserDep,
    session: SessionDep,
) -> _pvar.Variation:
    return await _vars.get_variation(variation_id, user, session)


@app.get("/variations/{variation_id}/results/{result_path:path}")
async def get_variation_result(
    variation_id: str,
    result_path: str,
    user: ActiveUserDep,
    session: SessionDep,
) -> _fresp.StreamingResponse:
    _ = await _vars.get_variation(variation_id, user, session)

    media_type = "image/png" if result_path.endswith(".png") else None

    read_coroutine = _read_variation_result(variation_id, result_path)

    return _fresp.StreamingResponse(read_coroutine, media_type=media_type)


@app.get("/variations/{variation_id}/results")
async def get_variation_result(
    variation_id: str,
    user: ActiveUserDep,
    session: SessionDep,
) -> _fresp.StreamingResponse:
    _ = await _vars.get_variation(variation_id, user, session)

    media_type = "application/zip"

    object_storage_input_zip_file_path = _pr.ObjectStorageInputZipFilePath(
        container="resultes-results", path=f"results/{variation_id}.zip"
    )

    size_in_bytes = await swift.get_size_in_bytes(object_storage_input_zip_file_path)
    headers = {"Content-Length": str(size_in_bytes)}

    read_coroutine = _read_variation_results(object_storage_input_zip_file_path)

    return _fresp.StreamingResponse(
        read_coroutine, headers=headers, media_type=media_type
    )


async def _read_variation_result(
    variation_id: str, result_path: str
) -> _cabc.AsyncIterator[bytes]:
    object_storage_input_file_path = _pr.ObjectStorageInputFilePath(
        container="resultes-results", path=f"results/{variation_id}/{result_path}"
    )
    chunks = swift.download_chunks(object_storage_input_file_path)

    async for chunk in chunks:
        yield chunk


async def _read_variation_results(
    object_storage_input_zip_file_path: _pr.ObjectStorageInputZipFilePath,
) -> _cabc.AsyncIterator[bytes]:
    chunks = swift.download_chunks(object_storage_input_zip_file_path)

    async for chunk in chunks:
        yield chunk


if __name__ == "__main__":
    _log.basicConfig(format=LOG_FORMAT, level=_log.INFO)
    _log.info("Starting server...")
    port = int(_os.environ.get("PORT", "8080"))
    _uc.run(app, host="0.0.0.0", port=port, log_config=None)
