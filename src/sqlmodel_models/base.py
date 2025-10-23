import resultes_pydantic_models.common as _pcom
import sqlmodel as _sqlm


class SQLModelWithID(_sqlm.SQLModel):
    id: str


class SQLModelWithIDAndState[S](SQLModelWithID):
    state: S
    state_changed_on: _pcom.AwarePastDatetime
