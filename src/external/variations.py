import fastapi as _fapi
import resultes_pydantic_models.simulations.variation as _pvar
import sqlmodel.ext.asyncio.session as _sqlmas

import query_helpers as _qh
import sqlmodel_models.simulations.variation as _var
import sqlmodel_models.user as _muser


async def get_variation(
    variation_id: str,
    user: _muser.User,
    session: _sqlmas.AsyncSession,
) -> _pvar.Variation:
    variation = await _qh.get_single(_var.Variation, variation_id, session)

    if variation.simulation.user_id != user.id:
        raise _fapi.HTTPException(_fapi.status.HTTP_404_NOT_FOUND)

    return variation.to_model_variation()
