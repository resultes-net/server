import collections.abc as _cabc

import resultes_pydantic_models.simulations.simulation as _psim
import sqlmodel.ext.asyncio.session as _sqlmas

import query_helpers as _qh
import sqlmodel_models.simulations.simulation as _sim


async def get_simulations(
    state: _psim.SimulationState,
    session: _sqlmas.AsyncSession,
) -> _cabc.Sequence[_psim.Simulation]:
    db_simulations = await _qh.get(_sim.Simulation, state, session)
    simulations = [s.to_model_simulation() for s in db_simulations]
    return simulations


async def update_simulation_state(
    simulation_id: str,
    new_state: _psim.SimulationState,
    session: _sqlmas.AsyncSession,
) -> _psim.SimulationState:
    await _qh.set_state(_sim.Simulation, simulation_id, new_state, session)
    return new_state
