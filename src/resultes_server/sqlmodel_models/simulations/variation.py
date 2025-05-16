import enum as _enum
import pathlib as _pl
import typing as _tp

import pydantic as _pyd
import sqlmodel as _sqlm

import resultes_server.database_utils.helpers as _dbh

if _tp.TYPE_CHECKING:
    from .simulation import Simulation


@_enum.verify(_enum.UNIQUE)
class VariationState(_enum.Enum):
    WAITING = "waiting"
    RUNNING = "running"
    DONE = "done"


class Variation(_sqlm.SQLModel, table=True):
    id: str | None = _dbh.ID_FIELD
    created_on: _dbh.AwarePastDatetime = _dbh.UTC_NOW_FIELD

    simulation_id: str = _dbh.create_id_field(foreign_key="simulation.id")
    simulation: "Simulation" = _sqlm.Relationship(back_populates="variations")

    object_storage_url: _pyd.HttpUrl = _dbh.HTTP_URL_FIELD
    relative_deck_file_path: _pl.PureWindowsPath = _dbh.PURE_WINDOWS_PATH_FIELD
    relative_process_script_path: _pl.PureWindowsPath = _dbh.PURE_WINDOWS_PATH_FIELD

    state: VariationState = VariationState.WAITING
