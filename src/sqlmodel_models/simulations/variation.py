import pathlib as _pl
import typing as _tp

import resultes_pydantic_models.common as _pcom
import resultes_pydantic_models.simulations.variation as _pydvar
import sqlmodel as _sqlm

import database_utils.helpers as _dbh

if _tp.TYPE_CHECKING:
    from .simulation import Simulation


class Variation(_pydvar.Variation, _sqlm.SQLModel, table=True):
    id: str | None = _dbh.ID_FIELD
    created_on: _pcom.AwarePastDatetime = _dbh.create_utc_now_field()

    simulation_id: str = _dbh.create_id_field(foreign_key="simulation.id")
    simulation: "Simulation" = _dbh.create_eager_relationship("variations")

    relative_deck_file_path: _pl.PureWindowsPath = _dbh.PURE_WINDOWS_PATH_FIELD
