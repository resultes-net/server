import collections.abc as _cabc
import logging as _log
import typing as _tp

import fastapi as _fapi
import resultes_pydantic_models.simulations.simulation as _psim
import sqlalchemy.ext.asyncio.engine as _sqlae
import sqlmodel.ext.asyncio.session as _sqlmas
import uvicorn as _uc

import config as _config
import database_utils.helpers as _dbh
import simulations as _sims
import sqlmodel_models.simulations.variation as _var
import variations as _vars

LOG_FORMAT = "%(asctime)s - %(levelname)s - %(module)s - %(message)s"


engine = _sqlae.create_async_engine(_config.DB_CONNECTION_STRING, echo=True)


async def get_session() -> _cabc.AsyncIterable[_sqlmas.AsyncSession]:
    async with _dbh.create_session(engine) as session:
        yield session


SessionDep = _tp.Annotated[_sqlmas.AsyncSession, _fapi.Depends(get_session)]


app = _fapi.FastAPI(root_path=_config.ROOT_PATH)


@app.get("/variations")
async def get_waiting_variations_by_user_id(
    state: _tp.Literal["waiting"],
    session: SessionDep,
) -> _cabc.Mapping[str, _cabc.Sequence[_var.Variation]]:
    return await _vars.get_waiting_variations_by_user_id(session)


@app.get("/simulations")
async def get_simulations_waiting_for_variations_creation_by_user_id(
    state: _tp.Literal["waiting-for-variations-creation"], session: SessionDep
) -> _cabc.Mapping[str, _cabc.Sequence[_psim.Simulation]]:
    return await _sims.get_simulations_waiting_for_variations_creation_by_user_id(
        session
    )


@app.patch("/simulations/{simulation_id}")
async def set_simulation_state(
    simulation_id: str, state: _psim.SimulationState, session: SessionDep
) -> _psim.UpdateSimulation:
    return await _sims.set_simulation_state(simulation_id, state, session)


if __name__ == "__main__":
    _log.basicConfig(format=LOG_FORMAT, level=_log.INFO)
    _log.info("Starting server...")
    _uc.run(app, host="0.0.0.0", port=8000, log_config=None)
