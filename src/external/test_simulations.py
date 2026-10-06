# pyright: reportPrivateUsage=false

# These tests need pytest at import time, so they can't live next to the code in `simulations.py`: the server image
# doesn't install pytest.

import unittest.mock as _um

import pytest as _pt
import resultes_openstack_utils.swift_multithreaded as _sm
import resultes_pydantic_models.runner as _mrunner

import external.simulations as _sims


@_pt.mark.asyncio
async def test_delete_results_if_they_exist() -> None:
    swift = _um.AsyncMock()

    await _sims._delete_results_if_they_exist("5e0a17c3d2", swift)

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

    await _sims._delete_results_if_they_exist("5e0a17c3d2", swift)


@_pt.mark.asyncio
async def test_delete_results_if_they_exist_raises_other_errors() -> None:
    swift = _um.AsyncMock()
    swift.delete.side_effect = _sm.ClientException("Server error", http_status=500)

    with _pt.raises(_sm.ClientException):
        await _sims._delete_results_if_they_exist("5e0a17c3d2", swift)
