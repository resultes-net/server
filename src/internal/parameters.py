import resultes_pydantic_models.simulations.parameters as _pparams
import sqlmodel.ext.asyncio.session as _sqlmas

import query_helpers as _qh
import sqlmodel_models.simulations.parameters as _params


async def get_parameters(
    simulation_id: str,
    session: _sqlmas.AsyncSession,
) -> _pparams.Parameters:
    parameters = await _qh.get_single_any_id_name(
        _params.Parameters, simulation_id, session, id_name="simulation_id"
    )

    return parameters.value
