import collections.abc as _cabc
import typing as _tp

import fastapi as _fapi
import resultes_pydantic_models.common as _pcom
import sqlmodel as _sqlm
import sqlmodel.ext.asyncio.session as _sqlmas

import sqlmodel_models.base as _smb


async def get_single[M: _smb.SQLModelWithID](
    clazz: type[M], id: str, session: _sqlmas.AsyncSession
) -> M:
    query = _sqlm.select(clazz).where(clazz.id == id)

    rows = await session.exec(query)

    instance = rows.one_or_none()

    if not instance:
        raise _fapi.HTTPException(
            status_code=_fapi.status.HTTP_404_NOT_FOUND,
            detail=f"No {clazz.__name__} with id {id} found.",
        )

    return instance


async def get[M: _smb.SQLModelWithIDAndState[_tp.Any]](
    clazz: type[M],
    state: _tp.Any,
    session: _sqlmas.AsyncSession,
) -> _cabc.Sequence[M]:
    query = _sqlm.select(clazz).where(clazz.state == state)
    rows = await session.exec(query)
    return rows.all()


async def set_state[S](
    clazz: type[_smb.SQLModelWithIDAndState[S]],
    id: str,
    state: S,
    session: _sqlmas.AsyncSession,
) -> None:
    instance = await get_single(clazz, id, session)
    instance.state = state
    instance.state_changed_on = _pcom.utc_now()
    await session.commit()
