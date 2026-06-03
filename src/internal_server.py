import collections.abc as _cabc
import logging as _log
import typing as _tp
import pydantic as _pyd

import fastapi as _fapi
import resultes_pydantic_models.server as _psrv
import resultes_pydantic_models.simulations.simulation as _psim
import resultes_pydantic_models.simulations.variation as _pvar
import sqlalchemy.ext.asyncio.engine as _sqlae
import sqlmodel.ext.asyncio.session as _sqlmas
import uvicorn as _uc

import config as _config
import database_utils.helpers as _dbh
import internal.simulations as _sims
import internal.variations as _vars
import external.auth as _auth

LOG_FORMAT = "%(asctime)s - %(levelname)s - %(module)s - %(message)s"

engine = _sqlae.create_async_engine(_config.DB_CONNECTION_STRING)


async def get_session() -> _cabc.AsyncIterable[_sqlmas.AsyncSession]:
    async with _dbh.create_session(engine) as session:
        yield session


SessionDep = _tp.Annotated[_sqlmas.AsyncSession, _fapi.Depends(get_session)]


app = _fapi.FastAPI(root_path=_config.ROOT_PATH)


@app.get("/simulations")
async def get_simulations_waiting_for_variations_creation(
    state: _tp.Literal["waiting-for-variations-creation"], session: SessionDep
) -> _cabc.Sequence[_psim.Simulation]:
    return await _sims.get_simulations(
        _psim.SimulationState.WAITING_FOR_VARIATIONS_CREATION, session
    )


@app.get("/simulation/{simulation_id}")
async def get_simulation(simulation_id: str, session: SessionDep) -> _psim.Simulation:
    return await _sims.get_simulation(simulation_id, session)


@app.get("/waiting-variations")
async def get_waiting_variations(
    session: SessionDep,
) -> _psrv.WaitingVariations:
    return await _vars.get_waiting_variations(session)


@app.get("/simulations/{simulation_id}/variations")
async def get_variations(
    simulation_id: str,
    session: SessionDep,
) -> _cabc.Sequence[_pvar.Variation]:
    return await _sims.get_variations(simulation_id, session)


@app.put("/simulations/{simulation_id}/state")
async def update_simulation_state(
    simulation_id: str, new_state: _psim.SimulationState, session: SessionDep
) -> _psim.SimulationState:
    return await _sims.update_simulation_state(simulation_id, new_state, session)


@app.put("/simulations/{simulation_id}/progress")
async def update_simulation_progress(
    simulation_id: str, new_progress: _pyd.NonNegativeInt, session: SessionDep
) -> int:
    return await _sims.update_simulation_progress(simulation_id, new_progress, session)


@app.post("/simulations/{simulation_id}/variations")
async def create_variation(
    simulation_id: str, variation: _pvar.CreateVariation, session: SessionDep
) -> _pvar.Variation:
    return await _vars.create_variation(simulation_id, variation, session)


@app.put("/variations/{variation_id}/state")
async def update_variation_state(
    variation_id: str, new_state: _pvar.VariationState, session: SessionDep
) -> _pvar.VariationState:
    return await _vars.update_variation_state(variation_id, new_state, session)


@app.put("/variations/{variation_id}/progress")
async def update_variation_progress(
    variation_id: str, new_progress: _pyd.NonNegativeInt, session: SessionDep
) -> int:
    return await _vars.update_variation_progress(variation_id, new_progress, session)


@app.get("/latest-login")
async def get_latest_login(session: SessionDep) -> _psrv.LatestLogin:
    return await _auth.get_latest_login(session)


if __name__ == "__main__":
    _log.basicConfig(format=LOG_FORMAT, level=_log.INFO)
    _log.info("Starting server...")
    _uc.run(app, host="0.0.0.0", port=8080, log_config=None)
