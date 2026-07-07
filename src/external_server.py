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
    return _sqlae.create_async_engine(_config.DB_CONNECTION_STRING)


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
    create_simulation: _psim.CreateSimulation,
    user: ActiveUserDep,
    session: SessionDep,
) -> _psim.SimulationBase:
    simulation = _sim.Simulation(
        name=create_simulation.name,
        location=create_simulation.location,
        parameters=create_simulation.parameters,
        user=user,
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


@app.put("/simulations/{simulation_id}/state")
async def update_simulation_state(
    simulation_id: str,
    new_state: _tp.Literal[_psim.SimulationState.WAITING_FOR_VARIATIONS_CREATION],
    user: ActiveUserDep,
    session: SessionDep,
) -> _psim.SimulationState:
    return await _sims.update_state(simulation_id, new_state, user, session, swift)


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


@app.head("/variations/{variation_id}/results/{result_path:path}")
async def get_variation_result_headers(
    variation_id: str,
    result_path: str,
    user: ActiveUserDep,
    session: SessionDep,
) -> _fapi.Response:
    _ = await _vars.get_variation(variation_id, user, session)

    object_storage_input_file_path = _pr.ObjectStorageInputFilePath(
        container="resultes-results",
        path=f"results/{variation_id}/{result_path}",
    )

    try:
        size_in_bytes = await swift.get_size_in_bytes(object_storage_input_file_path)
    except _sm.ClientException as client_exception:
        raise _fapi.HTTPException(
            status_code=client_exception.http_status,
            detail=client_exception.http_reason,
        )

    headers = {"Content-Length": str(size_in_bytes)}

    response = _fapi.Response(headers=headers)

    return response


@app.get("/variations/{variation_id}/results/{result_path:path}")
async def get_variation_result(
    variation_id: str,
    result_path: str,
    user: ActiveUserDep,
    session: SessionDep,
) -> _fresp.StreamingResponse:
    _ = await _vars.get_variation(variation_id, user, session)

    path = f"results/{variation_id}/{result_path}"

    _, chunks = await _read_variation_result(path)

    if result_path.endswith(".png"):
        media_type = "image/png"
    elif result_path.endswith(".log"):
        media_type = "text/plain"
    elif result_path.endswith(".json"):
        media_type = "application/json"
    else:
        media_type = None

    return _fresp.StreamingResponse(chunks, media_type=media_type)


@app.get("/variations/{variation_id}/results")
async def get_variation_results(
    variation_id: str,
    user: ActiveUserDep,
    session: SessionDep,
) -> _fresp.StreamingResponse:
    _ = await _vars.get_variation(variation_id, user, session)

    media_type = "application/zip"

    path = f"results/{variation_id}.zip"

    headers, chunks = await _read_variation_result(path)

    return _fresp.StreamingResponse(chunks, headers=headers, media_type=media_type)


Headers = _tp.TypedDict("Headers", {"Content-Length": str})


async def _read_variation_result(path: str) -> tuple[Headers, _sm.AsyncChunks]:
    object_storage_input_file_path = _pr.ObjectStorageInputFilePath(
        container="resultes-results", path=path
    )
    try:
        all_headers, chunks = await swift.download_chunks(
            object_storage_input_file_path
        )
    except _sm.ClientException as client_exception:
        _log.exception("An error occurred.")
        raise _fapi.HTTPException(
            status_code=client_exception.http_status,
            detail=client_exception.http_reason,
        )
    except:
        _log.exception("An error occurred.")
        raise

    headers: Headers = {"Content-Length": all_headers["Content-Length"]}

    return headers, chunks


if __name__ == "__main__":
    _log.basicConfig(format=LOG_FORMAT, level=_log.INFO)
    _log.info("Starting server...")
    port = int(_os.environ.get("PORT", "8080"))
    _uc.run(app, host="0.0.0.0", port=port, log_config=None)
