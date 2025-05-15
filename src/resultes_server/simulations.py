import collections.abc as _cabc
import itertools as _it

import sqlmodel as _sqlm

import resultes_server.models.simulations.simulation as _sim


def get_simulations_waiting_for_variations_creation_by_user_id(
    session: _sqlm.Session,
) -> _cabc.Mapping[str, _cabc.Sequence[_sim.Simulation]]:
    query = _sqlm.select(_sim.Simulation).where(
        _sim.Simulation.state == _sim.SimulationState.WAITING_FOR_VARIATIONS_CREATION
    )

    rows = session.exec(query)

    def get_user_id(simulation: _sim.Simulation) -> str:
        assert simulation.id
        return simulation.id

    simulations_by_user_id = {k: list(g) for k, g in _it.groupby(rows, key=get_user_id)}

    return simulations_by_user_id
