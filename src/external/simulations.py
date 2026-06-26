import collections.abc as _cabc
import typing as _tp

import fastapi as _fapi
import resultes_pydantic_models.simulations.simulation as _psim
import sqlmodel as _sqlm
import sqlmodel.ext.asyncio.session as _sqlmas

import query_helpers as _qh
import sqlmodel_models.simulations.simulation as _sim
import sqlmodel_models.user as _muser


async def update_state(
    simulation_id: str,
    new_state: _tp.Literal[_psim.SimulationState.WAITING_FOR_VARIATIONS_CREATION],
    user: _muser.User,
    session: _sqlmas.AsyncSession,
) -> _psim.SimulationState:
    simulation = await _get_db_simulation(simulation_id, user, session)

    if simulation.state != _psim.SimulationState.ERROR:
        raise _fapi.HTTPException(
            status_code=_fapi.status.HTTP_409_CONFLICT,
            detail="You can only reset simulations in the erorr state.",
        )

    simulation.state = new_state

    await session.commit()

    return new_state


async def get_simulation(
    simulation_id: str,
    user: _muser.User,
    session: _sqlmas.AsyncSession,
) -> _psim.Simulation:
    simulation = await _get_db_simulation(simulation_id, user, session)

    return simulation.to_model_simulation()


async def _get_db_simulation(
    simulation_id: str,
    user: _muser.User,
    session: _sqlmas.AsyncSession,
) -> _sim.Simulation:
    simulation = await _qh.get_single(_sim.Simulation, simulation_id, session)

    if simulation.user_id != user.id:
        raise _fapi.HTTPException(
            status_code=_fapi.status.HTTP_404_NOT_FOUND,
        )

    return simulation


async def get_simulations(
    user: _muser.User,
    session: _sqlmas.AsyncSession,
) -> _cabc.Sequence[_psim.Simulation]:
    query = _sqlm.select(_sim.Simulation).where(
        _sim.Simulation.user_id == user.id,
    )

    result = await session.exec(query)

    model_simulations = [s.to_model_simulation() for s in result.all()]

    return model_simulations
