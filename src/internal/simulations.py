import collections.abc as _cabc
import typing as _tp

import resultes_pydantic_models.simulations.simulation as _psim
import resultes_pydantic_models.simulations.variation as _pvar
import sqlmodel.ext.asyncio.session as _sqlmas

import query_helpers as _qh
import sqlmodel_models.simulations.simulation as _sim

_RUNNING_STATES = [
    _psim.SimulationState.CREATING_VARIATIONS,
    _psim.SimulationState.WAITING_FOR_VARIATION_RUNS,
    _psim.SimulationState.RUNNING_VARIATIONS,
    _psim.SimulationState.WAITING_FOR_CROSS_VARIATION_PROCESSING,
    _psim.SimulationState.CROSS_PROCESSING_VARIATIONS,
    _psim.SimulationState.CREATING_VARIATIONS,
]


async def get_simulations(
    state: _psim.SimulationState | _tp.Literal["running"],
    session: _sqlmas.AsyncSession,
) -> _cabc.Sequence[_psim.Simulation]:
    states = _RUNNING_STATES if state == "running" else [state]

    db_simulations = await _qh.get(_sim.Simulation, states, session)

    simulations = [s.to_model_simulation() for s in db_simulations]

    return simulations


async def get_simulation(
    simulation_id: str,
    session: _sqlmas.AsyncSession,
) -> _psim.Simulation:
    db_simulation = await _qh.get_single(_sim.Simulation, simulation_id, session)
    return db_simulation.to_model_simulation()


async def update_simulation_state(
    simulation_id: str,
    new_state: _psim.SimulationState,
    session: _sqlmas.AsyncSession,
) -> _psim.SimulationState:
    await _qh.set_state(_sim.Simulation, simulation_id, new_state, session)
    return new_state


async def update_simulation_progress(
    simulation_id: str,
    new_progress: int,
    session: _sqlmas.AsyncSession,
) -> int:
    instance = await _qh.get_single(_sim.Simulation, simulation_id, session)
    instance.progress = new_progress
    await session.commit()
    return new_progress


async def get_variations(
    simulation_id: str,
    session: _sqlmas.AsyncSession,
) -> _cabc.Sequence[_pvar.Variation]:
    simulation = await _qh.get_single(_sim.Simulation, simulation_id, session)

    return simulation.variations
