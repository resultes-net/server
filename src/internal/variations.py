import collections.abc as _cabc

import fastapi as _fapi
import resultes_pydantic_models.server as _psrv
import resultes_pydantic_models.simulations.simulation as _psim
import resultes_pydantic_models.simulations.variation as _pvar
import sqlmodel as _sqlm
import sqlmodel.ext.asyncio.session as _sqlmas

import query_helpers as _qh
import sqlmodel_models.simulations as _sim
import sqlmodel_models.simulations.variation as _var


async def get_waiting_variations(
    session: _sqlmas.AsyncSession,
) -> _psrv.WaitingVariations:
    simulation_ids_subquery = _sqlm.select(_sim.Variation.simulation_id).where(
        _sim.Variation.state == _pvar.VariationState.WAITING
    )

    query = (
        _sqlm.select(_sim.Simulation, _sim.Variation)
        .join(_sim.Variation)
        .where(_sqlm.col(_sim.Simulation.id).in_(simulation_ids_subquery))
    )

    rows = await session.exec(query)

    simulations = list[_psim.Simulation]()
    waiting_variations = list[_pvar.Variation]()
    other_variations = list[_pvar.Variation]()

    for simulation, variation in rows:
        simulations.append(simulation.to_model_simulation())

        if variation.state == _pvar.VariationState.WAITING:
            waiting_variations.append(variation.to_model_variation())
        else:
            other_variations.append(variation.to_model_variation())

    associated_simulations = _remove_duplicates(simulations)

    result = _psrv.WaitingVariations(
        waiting_variations=waiting_variations,
        associated_simulations=associated_simulations,
        other_variations=other_variations,
    )

    return result


def _remove_duplicates(
    simulations: _cabc.Sequence[_psim.Simulation],
) -> _cabc.Sequence[_psim.Simulation]:
    simulations_by_id = {s.id: s for s in simulations}
    unique_simulations = simulations_by_id.values()
    return list(unique_simulations)


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

    await session.commit()

    return variation.to_model_variation()


async def update_variation_state(
    variation_id: str,
    new_state: _pvar.VariationState,
    session: _sqlmas.AsyncSession,
) -> _pvar.VariationState:
    await _qh.set_state(_var.Variation, variation_id, new_state, session)
    return new_state
