import pathlib as _pl
import typing as _tp

import resultes_pydantic_models.common as _pcom
import resultes_pydantic_models.simulations.variation as _pvar

import database_utils.helpers as _dbh
import sqlmodel_models.base as _smb

if _tp.TYPE_CHECKING:
    from .simulation import Simulation


class Variation(
    _pvar.VariationBase, _smb.SQLModelWithIDAndState[_pvar.VariationState], table=True
):
    id: str | None = _dbh.ID_FIELD
    created_on: _pcom.AwarePastDatetime = _dbh.create_utc_now_field()

    state_changed_on: _pcom.AwarePastDatetime = _dbh.create_utc_now_field()

    simulation_id: str = _dbh.create_id_field(foreign_key="simulation.id")
    simulation: "Simulation" = _dbh.create_eager_relationship("variations")

    relative_deck_file_containing_dir_path: _pl.PureWindowsPath = _dbh.PURE_WINDOWS_PATH_FIELD

    def to_model_variation(self) -> _pvar.Variation:
        if not self.id:
            raise ValueError("ID not set.")

        return _pvar.Variation(
            id=self.id,
            created_on=self.created_on,
            state=self.state,
            state_changed_on=self.state_changed_on,
            simulation_id=self.simulation_id,
            relative_deck_file_containing_dir_path=self.relative_deck_file_containing_dir_path,
        )
