import collections.abc as _cabc

import sqlmodel as _sqlm
import sqlmodel.ext.asyncio.session as _sqlmas

import sqlmodel_models.simulations as _sim
import sqlmodel_models.simulations.variation as _var


async def get_waiting_variations_by_user_id(
    session: _sqlmas.AsyncSession,
) -> _cabc.Mapping[str, _cabc.Sequence[_var.Variation]]:
    query = (
        _sqlm.select(_sim.Simulation, _var.Variation)
        .join(_sim.Simulation)
        .where(_var.Variation.state == _var.VariationState.WAITING)
    )

    rows = await session.exec(query)

    variations_and_user_id = [(v, s.user_id) for s, v in rows]

    variations_by_user_id = dict[str, list[_var.Variation]]()
    for variation, user_id in variations_and_user_id:
        variations = variations_by_user_id.get(user_id)

        if not variations:
            variations = []
            variations_by_user_id[user_id] = variations

        variations.append(variation)

    return variations_by_user_id
