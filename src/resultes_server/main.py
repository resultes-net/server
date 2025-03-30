import contextlib as _ctx
import io as _io
import logging as _log
import typing as _tp

import fastapi as _fapi
import pandas as _pd
import sqlmodel as _sqlm
import uvicorn as _uc

import months as _months
import resultes_server.api.ttes as _tapi
import resultes_server.db_model as _dbm

LOG_FORMAT = "%(asctime)s - %(levelname)s - %(module)s - %(message)s"

# engine = _sqlm.create_engine("postgresql+psycopg://postgres:postgres@postgres/resultes", echo=True)


def create_db_and_tables() -> None:
    # sqlm.SQLModel.metadata.create_all(engine)
    pass


def get_session() -> _tp.Iterable[_sqlm.Session]:
    with _sqlm.Session(engine) as session:
        yield session


SessionDep = None # _tp.Annotated[_sqlm.Session, _fapi.Depends(get_session)]


@_ctx.asynccontextmanager
async def lifespan(_: _fapi.FastAPI) -> _tp.AsyncIterable[None]:
    create_db_and_tables()
    yield


app = _fapi.FastAPI(lifespan=lifespan)


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
    data = await params.demand.profile.read()

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


@app.post("/simulations/new/ttes")
async def create_and_run_new_ttes_simulation(_: _tapi.TtesParameters, session: SessionDep) -> dict:
    run = _dbm.Run()
    session.add_all([run])
    session.commit()
    return {"href": f"/simulations/ttes/{run.id}"}


if __name__ == "__main__":
    _log.basicConfig(format=LOG_FORMAT, level=_log.INFO)
    _log.info("Starting server...")
    _uc.run(app, host="localhost", port=80, log_config=None)
