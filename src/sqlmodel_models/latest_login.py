import sqlmodel as _sqlm

import resultes_pydantic_models.common as _pcom
import resultes_pydantic_models.server as _psrv


class LatestLogin(_psrv.LatestLogin, _sqlm.SQLModel, table=True):
    on: _pcom.AwarePastDatetime = _sqlm.Field(
        sa_column=_sqlm.Column(_sqlm.DateTime(timezone=True), primary_key=True)
    )
