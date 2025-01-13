import io as _io
import logging as _log
import typing as _tp

import fastapi as _fapi
import pandas as _pd
import uvicorn as _uc

import months as _months
import resultes_server.api.ttes as _tapi

LOG_FORMAT = "%(asctime)s - %(levelname)s - %(module)s - %(message)s"

app = _fapi.FastAPI()


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
async def create_and_run_new_ttes_simulation(params: _tapi.TtesParameters) -> dict:
    return {"href": "/simulations/1128"}


if __name__ == "__main__":
    _log.basicConfig(format=LOG_FORMAT, level=_log.INFO)
    _log.info("Starting server...")
    _uc.run(app, host="localhost", port=8000, log_config=None)
