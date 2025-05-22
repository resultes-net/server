import collections.abc as _cabc
import logging as _log
import typing as _tp

import fastapi as _fapi
import resultes_pydantic_models.simulations.simulation as _psim
import sqlmodel as _sqlm
import uvicorn as _uc

import resultes_server.config as _config
import resultes_server.simulations as _sims
import resultes_server.sqlmodel_models.simulations.variation as _var
import resultes_server.variations as _vars

LOG_FORMAT = "%(asctime)s - %(levelname)s - %(module)s - %(message)s"


engine = _sqlm.create_engine(_config.DB_CONNECTION_STRING, echo=True)


def get_session() -> _tp.Iterable[_sqlm.Session]:
    with _sqlm.Session(engine) as session:
        yield session


SessionDep = _tp.Annotated[_sqlm.Session, _fapi.Depends(get_session)]


app = _fapi.FastAPI(root_path=_config.ROOT_PATH)


@app.get("/variations")
async def get_waiting_variations_by_user_id(
    state: _tp.Literal["waiting"],
    session: SessionDep,
) -> _cabc.Mapping[str, _cabc.Sequence[_var.Variation]]:
    return _vars.get_waiting_variations_by_user_id(session)


@app.get("/simulations")
async def get_simulations_waiting_for_variations_creation_by_user_id(
    state: _tp.Literal["waiting-for-variations-creation"], session: SessionDep
) -> _cabc.Mapping[str, _cabc.Sequence[_psim.Simulation]]:
    return _sims.get_simulations_waiting_for_variations_creation_by_user_id(session)


if __name__ == "__main__":
    _log.basicConfig(format=LOG_FORMAT, level=_log.INFO)
    _log.info("Starting server...")
    _uc.run(app, host="0.0.0.0", port=8000, log_config=None)
