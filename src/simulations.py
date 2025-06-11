import collections.abc as _cabc
import itertools as _it

import resultes_pydantic_models.common as _pcom
import resultes_pydantic_models.simulations.simulation as _psim
import sqlmodel as _sqlm
import sqlmodel.ext.asyncio.session as _sqlmas

import sqlmodel_models.simulations.simulation as _sim


async def get_simulations_waiting_for_variations_creation_by_user_id(
    session: _sqlmas.AsyncSession,
) -> _cabc.Mapping[str, _cabc.Sequence[_sim.Simulation]]:
    query = _sqlm.select(_sim.Simulation).where(
        _sim.Simulation.state == _psim.SimulationState.WAITING_FOR_VARIATIONS_CREATION
    )

    rows = await session.exec(query)

    def get_user_id(simulation: _sim.Simulation) -> str:
        return simulation.user_id

    simulations_by_user_id = {k: list(g) for k, g in _it.groupby(rows, key=get_user_id)}

    return simulations_by_user_id


async def update_simulation(
    simulation_id: str,
    update_simulation: _psim.UpdateSimulation,
    session: _sqlmas.AsyncSession,
) -> _psim.UpdateSimulation:
    query = _sqlm.select(_sim.Simulation).where(_sim.Simulation.id == simulation_id)

    rows = await session.exec(query)

    simulation = rows.one()

    update_dict = update_simulation.model_dump()
    for key, value in update_dict.items():
        setattr(simulation, key, value)

    simulation.state_changed_on = _pcom.utc_now()

    await session.commit()

    return simulation
