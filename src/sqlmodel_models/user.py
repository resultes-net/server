import typing as _tp

import resultes_pydantic_models.user as _puser

import database_utils.helpers as _dbh
import sqlmodel_models.base as _smb

if _tp.TYPE_CHECKING:
    from .simulations.simulation import Simulation


class User(_puser.UserReadBase, _smb.SQLModelWithID, table=True):
    hashed_password: str
    simulations: list["Simulation"] = _dbh.create_eager_relationship("user")
    id: str | None = _dbh.ID_FIELD

    def to_model_user(self) -> _puser.UserRead:
        if not self.id:
            raise ValueError("ID not set.")

        return _puser.UserRead(
            id=self.id,
            user_name=self.user_name,
            full_name=self.full_name,
            email=self.email,
            disabled=self.disabled,
        )
