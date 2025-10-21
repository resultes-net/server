import collections.abc as _cabc

import resultes_pydantic_models.simulations.simulation as _psim
import sqlmodel as _sqlm
import sqlmodel.ext.asyncio.session as _sqlmas

import sqlmodel_models.simulations.simulation as _sim
import sqlmodel_models.user as _muser


async def get_simulations(
    user: _muser.User,
    session: _sqlmas.AsyncSession,
) -> _cabc.Sequence[_psim.Simulation]:
    query = _sqlm.select(_sim.Simulation).where(
        _sim.Simulation.user_id == user.id,
    )

    result = await session.exec(query)

    return result.all()
