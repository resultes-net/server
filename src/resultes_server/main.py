import contextlib as _ctx
import io as _io
import logging as _log
import os as _os
import typing as _tp

import fastapi as _fapi
import fastapi.security as _fsec
import pandas as _pd
import sqlmodel as _sqlm
import uvicorn as _uc

import resultes_server.auth as _auth
import resultes_server.models.simulations.parameters.common.demand as _dapi
import resultes_server.models.simulations.parameters.ttes as _tapi
import resultes_server.models.simulations.simulation as _sim
import resultes_server.models.user as _mu
import resultes_server.months as _months

LOG_FORMAT = "%(asctime)s - %(levelname)s - %(module)s - %(message)s"

PORT = int(_os.environ.get("PORT", "8080"))

DB_HOST_NAME = _os.environ.get("DB_HOST_NAME")
if not DB_HOST_NAME:
    import socket
    host_name = socket.gethostname()
    # Can't access Windows' `localhost` using "localhost".
    # Cf.:https://superuser.com/questions/1679757/accessing-windows-localhost-from-wsl2
    DB_HOST_NAME = f"{host_name}.local"
    print(f"Accessing Windows localhost via '{DB_HOST_NAME}'.")

DB_PORT = _os.environ.get("DB_PORT", "8432")

ROOT_PATH = _os.environ.get("ROOT_PATH", "")


engine = _sqlm.create_engine(
    f"postgresql+psycopg://postgres:postgres@{DB_HOST_NAME}:{DB_PORT}/resultes", echo=True
)


def create_db_and_tables() -> None:
    _sqlm.SQLModel.metadata.create_all(engine)
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


app = _fapi.FastAPI(root_path=ROOT_PATH, lifespan=lifespan)


@app.post("/token")
async def create_token(
    form_data: _tp.Annotated[_fsec.OAuth2PasswordRequestForm, _fapi.Depends()],
    session: SessionDep,
) -> _auth.Token:
    token = _auth.create_token(form_data.username, form_data.password, session)
    return token


@app.post("/profiles/")
async def create_file(
    file: _tp.Annotated[_fapi.UploadFile, _fapi.File()],
) -> dict:
    data = await file.read()

    bytes_io = _io.BytesIO(data)

    df = _pd.read_csv(bytes_io, sep="\t")

    total = df["Tot"]
    monthly_total = total[:8761].groupby(_months.get_month).sum() / 1000

    monthly_values = {
        "monthly_data": {
            "months": monthly_total.index.tolist(),
            "energy": monthly_total.values.tolist(),
            "remark": "Energy in MWh.",
        },
        "yearly_data": {"total": monthly_total.sum()},
    }

    return monthly_values


@app.post("/ttes/params")
async def post_params(params: _tapi.TtesParameters) -> dict:
    profile = params.demand.profile

    if isinstance(profile, _dapi.PreDefinedProfile):
        raise ValueError("User defined profiles not supported.")

    data = await profile.data.read()

    bytes_io = _io.BytesIO(data)

    df = _pd.read_csv(bytes_io, sep="\t")

    total = df["Tot"]
    monthly_total = total[:8761].groupby(_months.get_month).sum() / 1000

    monthly_values = {
        "monthly_data": {
            "months": monthly_total.index.tolist(),
            "energy": monthly_total.values.tolist(),
            "remark": "Energy in MWh.",
        },
        "yearly_data": {"total": monthly_total.sum()},
    }

    return monthly_values


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
    _uc.run(app, host="0.0.0.0", port=PORT, log_config=None)
