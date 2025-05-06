import contextlib as _ctx
import logging as _log
import typing as _tp

import fastapi as _fapi
import fastapi.security as _fsec
import sqlmodel as _sqlm
import uvicorn as _uc

import resultes_server.auth as _auth
import resultes_server.config as _config
import resultes_server.models.simulations.parameters.ttes as _tapi
import resultes_server.models.simulations.simulation as _sim
import resultes_server.models.user as _mu
import resultes_server.users as _users

LOG_FORMAT = "%(asctime)s - %(levelname)s - %(module)s - %(message)s"


engine = _sqlm.create_engine(_config.DB_CONNECTION_STRING, echo=True)


def create_db_and_tables() -> None:
    # _sqlm.SQLModel.metadata.create_all(engine)
    pass


def get_session() -> _tp.Iterable[_sqlm.Session]:
    with _sqlm.Session(engine) as session:
        yield session


SessionDep = _tp.Annotated[_sqlm.Session, _fapi.Depends(get_session)]

PASSWORD_BEARER = _fsec.OAuth2PasswordBearer(tokenUrl="token")

TokenDep = _tp.Annotated[str, _fapi.Depends(PASSWORD_BEARER)]


def get_current_user(token: TokenDep, session: SessionDep) -> _mu.User:
    return _auth.get_current_user(token, session)


UserDep = _tp.Annotated[_mu.User, _fapi.Depends(get_current_user)]


def get_current_active_user(current_user: UserDep) -> _mu.User:
    return _auth.get_current_active_user(current_user)


ActiveUserDep = _tp.Annotated[_mu.User, _fapi.Depends(get_current_active_user)]


@_ctx.asynccontextmanager
async def lifespan(_: _fapi.FastAPI) -> _tp.AsyncIterator[None]:
    # create_db_and_tables()
    yield


app = _fapi.FastAPI(root_path=_config.ROOT_PATH, lifespan=lifespan)


@app.post("/token")
async def create_token(
    form_data: _tp.Annotated[_fsec.OAuth2PasswordRequestForm, _fapi.Depends()],
    session: SessionDep,
) -> _auth.Token:
    token = _auth.create_token(form_data.username, form_data.password, session)
    return token


# @app.post("/user")
# async def create_user(user_create: _mu.UserCreate, session: SessionDep) -> _mu.UserRead:
#     user = _users.get_user(user_create.user_name, session)
#     if user:
#         raise _fapi.HTTPException(
#             status_code=_fapi.status.HTTP_409_CONFLICT,
#             detail="User name is taken.",
#         )

#     user = _users.create_user(user_create, session)

#     return user


@app.post("/models/new/ttes")
async def create_and_run_new_ttes_simulation(
    _: _tapi.TtesParameters, session: SessionDep, user: ActiveUserDep
) -> dict:
    simulation = _sim.Simulation()
    session.add_all([simulation])
    session.commit()
    return {"href": f"/models/ttes/{simulation.id}"}


if __name__ == "__main__":
    _log.basicConfig(format=LOG_FORMAT, level=_log.INFO)
    _log.info("Starting server...")
    _uc.run(app, host="0.0.0.0", port=_config.PORT, log_config=None)
