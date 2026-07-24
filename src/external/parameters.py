import resultes_pydantic_models.simulations.parameters as _pparams
import sqlmodel.ext.asyncio.session as _sqlmas

import external.simulations as _sims
import query_helpers as _qh
import sqlmodel_models.simulations.parameters as _params
import sqlmodel_models.user as _muser


async def get_parameters(
    simulation_id: str,
    user: _muser.User,
    session: _sqlmas.AsyncSession,
) -> _pparams.Parameters:
    _ = await _sims.get_simulation(simulation_id, user, session)

    parameters = await _qh.get_single_any_id_name(
        _params.Parameters, simulation_id, session, id_name="simulation_id"
    )

    return parameters.parameters
