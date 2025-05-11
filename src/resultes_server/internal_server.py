import logging as _log
import typing as _tp
import collections.abc as _cabc

import fastapi as _fapi
import sqlmodel as _sqlm
import uvicorn as _uc

import resultes_server.config as _config
import resultes_server.models.simulations.variation as _var
import resultes_server.variations as _vars

LOG_FORMAT = "%(asctime)s - %(levelname)s - %(module)s - %(message)s"


engine = _sqlm.create_engine(_config.DB_CONNECTION_STRING, echo=True)


def get_session() -> _tp.Iterable[_sqlm.Session]:
    with _sqlm.Session(engine) as session:
        yield session


SessionDep = _tp.Annotated[_sqlm.Session, _fapi.Depends(get_session)]


app = _fapi.FastAPI(root_path=_config.ROOT_PATH)



@app.get("/variations")
async def create_and_run_new_simulation(
    session: SessionDep,
    state: _tp.Literal["waiting"]
) -> _cabc.Mapping[str, _cabc.Sequence[_var.Variation]]:
    return _vars.get_waiting_variations_by_user_id(session)

if __name__ == "__main__":
    _log.basicConfig(format=LOG_FORMAT, level=_log.INFO)
    _log.info("Starting server...")
    _uc.run(app, host="0.0.0.0", port=8000, log_config=None)
