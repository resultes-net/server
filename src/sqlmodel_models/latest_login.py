import sqlmodel as _sqlm

import resultes_pydantic_models.common as _pcom


class LatestLogin(_sqlm.SQLModel, table=True):
    on: _pcom.AwarePastDatetime = _sqlm.Field(
        sa_column=_sqlm.Column(_sqlm.DateTime(timezone=True), primary_key=True)
    )
