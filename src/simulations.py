import collections.abc as _cabc
import itertools as _it

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
