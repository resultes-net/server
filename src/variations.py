import collections.abc as _cabc

import fastapi as _fapi
import resultes_pydantic_models.simulations.simulation as _psim
import resultes_pydantic_models.simulations.variation as _pvar
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
        .where(_var.Variation.state == _pvar.VariationState.WAITING)
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


async def create_variation(
    simulation_id: str, variation: _pvar.CreateVariation, session: _sqlmas.AsyncSession
) -> _pvar.Variation:
    query = _sqlm.select(_sim.Simulation).where(
        _sim.Simulation.id == simulation_id,
        _sim.Simulation.state == _psim.SimulationState.CREATING_VARIATIONS,
    )
    rows = await session.exec(query)
    simulation = rows.one_or_none()

    if not simulation:
        raise _fapi.HTTPException(
            status_code=_fapi.status.HTTP_400_BAD_REQUEST,
            detail=(
                f"No simulation with id {simulation_id} with state "
                f"{_psim.SimulationState.CREATING_VARIATIONS.value} found."
            ),
        )

    create_variation_dict = variation.model_dump()
    variation = _var.Variation(simulation_id=simulation_id, **create_variation_dict)
    session.add(variation)
    return variation
