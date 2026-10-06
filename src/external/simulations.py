import collections.abc as _cabc
import http as _http
import typing as _tp
import unittest.mock as _um

import fastapi as _fapi
import pytest as _pt
import resultes_openstack_utils.swift_multithreaded as _sm
import resultes_pydantic_models.common as _pcom
import resultes_pydantic_models.results as _pres
import resultes_pydantic_models.runner as _mrunner
import resultes_pydantic_models.simulations.simulation as _psim
import sqlmodel as _sqlm
import sqlmodel.ext.asyncio.session as _sqlmas

import query_helpers as _qh
import sqlmodel_models.simulations.simulation as _sim
import sqlmodel_models.user as _muser


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


async def update_state(
    simulation_id: str,
    new_state: _tp.Literal[_psim.SimulationState.WAITING_FOR_VARIATIONS_CREATION],
    user: _muser.User,
    session: _sqlmas.AsyncSession,
    swift: _sm.Swift,
) -> _psim.SimulationState:
    simulation = await _get_db_simulation(simulation_id, user, session)

    if simulation.state != _psim.SimulationState.ERROR:
        raise _fapi.HTTPException(
            status_code=_fapi.status.HTTP_409_CONFLICT,
            detail="You can only reset simulations in the erorr state.",
        )

    variations = list(simulation.variations)
    variation_ids = [v.id for v in variations]

    now = _pcom.utc_now()

    simulation.state = _psim.SimulationState.WAITING_FOR_VARIATIONS_CREATION
    simulation.created_on = now
    simulation.state_changed_on = now
    simulation.progress = 0

    for variation in variations:
        await session.delete(variation)

    await session.commit()
    del variations

    for variation_id in variation_ids:
        await _delete_results_if_they_exist(variation_id, swift)

    return new_state


async def _delete_results_if_they_exist(variation_id: str, swift: _sm.Swift) -> None:
    results_dir_path = _mrunner.ObjectStorageInputFilePath(
        container=_pres.OBJECT_STORAGE_CONTAINER,
        path=_pres.get_variation_dir_path(variation_id),
    )
    await swift.delete_folder(results_dir_path)

    zip_path = _mrunner.ObjectStorageInputZipFilePath(
        container=_pres.OBJECT_STORAGE_CONTAINER,
        path=_pres.get_variation_zip_path(variation_id),
    )
    try:
        await swift.delete(zip_path)
    except _sm.ClientException as client_exception:
        if client_exception.http_status != _http.HTTPStatus.NOT_FOUND:
            raise


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


@_pt.mark.asyncio
async def test_delete_results_if_they_exist() -> None:
    swift = _um.AsyncMock()

    await _delete_results_if_they_exist("5e0a17c3d2", swift)

    swift.delete_folder.assert_awaited_once_with(
        _mrunner.ObjectStorageInputFilePath(
            container="resultes-results", path="results/5e0a17c3d2/"
        )
    )
    swift.delete.assert_awaited_once_with(
        _mrunner.ObjectStorageInputZipFilePath(
            container="resultes-results", path="results/5e0a17c3d2.zip"
        )
    )


@_pt.mark.asyncio
async def test_delete_results_if_they_exist_ignores_missing_zip() -> None:
    swift = _um.AsyncMock()
    swift.delete.side_effect = _sm.ClientException("Not found", http_status=404)

    await _delete_results_if_they_exist("5e0a17c3d2", swift)


@_pt.mark.asyncio
async def test_delete_results_if_they_exist_raises_other_errors() -> None:
    swift = _um.AsyncMock()
    swift.delete.side_effect = _sm.ClientException("Server error", http_status=500)

    with _pt.raises(_sm.ClientException):
        await _delete_results_if_they_exist("5e0a17c3d2", swift)
