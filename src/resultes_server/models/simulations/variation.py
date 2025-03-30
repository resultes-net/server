import enum as _enum

import sqlmodel as _sqlm

import resultes_server.database_utils.helpers as _dbh
from resultes_server.models.simulations import simulation as _sim


class State(_enum.Enum):
    WAITING = "waiting"
    RUNNING = "running"
    DONE = "done"


class Variation(_sqlm.SQLModel):
    id: int | None = _dbh.ID_FIELD
    perisistent_id: str = _dbh.PERSISTENT_ID_FIELD
    created_on: _dbh.AwareDatetime = _dbh.UTC_NOW_FIELD
    simulation: _sim.Simulation = _sqlm.Relationship(back_populates="variations")

    object_storage_url: _dbh.HTTP_URL_FIELD
    relative_deck_file_path: _dbh.PURE_WINDOWS_PATH_FIELD
    relative_process_script_path: _dbh.PURE_WINDOWS_PATH_FIELD

    state: State = State.WAITING
