import sqlmodel as _sqlm

import database_utils.helpers as _dbh
import resultes_pydantic_models.common as _pcom


class SQLModelWithID(_sqlm.SQLModel):
    id: str | None = _dbh.ID_FIELD


class SQLModelWithIDAndState[S](SQLModelWithID):
    state: S
    state_changed_on: _pcom.AwarePastDatetime
