import datetime as _dt
import logging as _log
import typing as _tp

import fastapi as _fapi
import jwt as _jwt
import passlib.context as _plctx
import pydantic as _pyd
import resultes_pydantic_models.common as _rpmc
import resultes_pydantic_models.server as _rsrv
import sqlmodel.ext.asyncio.session as _sqlmas

import sqlmodel_models.user as _mu
import external.users as _users
import sqlmodel_models.latest_login as _sll
import sqlmodel as _sqlm

_LOGGER = _log.getLogger(__name__)

# to get a string like this run:
# openssl rand -hex 32
_SECRET_KEY = "7fb0ec55e5fb59fbd849d971c04b5f867aa6b933248f9176ad62347dc768e3c3"
_ALGORITHM = "HS256"
_ACCESS_TOKEN_EXPIRE_MINUTES = 30

_PWD_CONTEXT = _plctx.CryptContext(schemes=["bcrypt"], deprecated="auto")


def _is_timezone_aware_in_future(datetime: _dt.datetime) -> _dt.datetime:
    if datetime.tzinfo is None:
        raise ValueError("Datetime must have an explicit time zone.", datetime)

    if datetime <= _rpmc.utc_now():
        raise ValueError("Datetime must be in the future.", datetime)

    return datetime


AwareFutureDateTime = _tp.Annotated[
    _dt.datetime, _pyd.AfterValidator(_is_timezone_aware_in_future)
]


class Token(_pyd.BaseModel):
    token_type: str
    valid_until: AwareFutureDateTime
    access_token: str


def get_hashed_password(plain_password: str) -> str:
    return _PWD_CONTEXT.hash(plain_password)


async def get_current_user(token: str, session: _sqlmas.AsyncSession) -> _mu.User:
    credentials_exception = _fapi.HTTPException(
        status_code=_fapi.status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = _jwt.decode(token, _SECRET_KEY, algorithms=[_ALGORITHM])
    except _jwt.InvalidTokenError as invalidTokenError:
        _LOGGER.info("Failed to decode token: %s.", invalidTokenError)
        raise credentials_exception

    user_name = payload.get("sub")
    if user_name is None:
        raise credentials_exception

    user = await _users.get_user(user_name, session)
    if user is None:
        raise credentials_exception

    return user


def get_current_active_user(
    current_user: _mu.User,
) -> _mu.User:
    if current_user.disabled:
        raise _fapi.HTTPException(status_code=400, detail="Inactive user")
    return current_user


async def create_token(
    user_name: str, plain_password: str, session: _sqlmas.AsyncSession
) -> Token:
    user = await authenticate_user(user_name, plain_password, session)
    if not user:
        raise _fapi.HTTPException(
            status_code=_fapi.status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    await _update_latest_login(session)

    return _create_token(user.user_name)


async def _update_latest_login(session: _sqlmas.AsyncSession) -> None:
    now = _rpmc.utc_now()

    latest_login = await _get_latest_login(session)
    latest_login.on = now

    await session.commit()


async def get_latest_login(session: _sqlmas.AsyncSession) -> _rsrv.LatestLogin:
    return await _get_latest_login(session)


async def _get_latest_login(session: _sqlmas.AsyncSession) -> _sll.LatestLogin:
    statement = _sqlm.select(_sll.LatestLogin)
    rows = await session.exec(statement)
    latest_login = rows.one()
    return latest_login


async def authenticate_user(
    user_name: str, plain_password: str, session: _sqlmas.AsyncSession
) -> _mu.User | None:
    user = await _users.get_user(user_name, session)
    if not user:
        return None
    if not _verify_password(plain_password, user.hashed_password):
        return None
    return user


def _verify_password(plain_password: str, hashed_password: str) -> bool:
    return _PWD_CONTEXT.verify(plain_password, hashed_password)


def _create_token(user_name: str) -> Token:
    expires = _dt.datetime.now(_dt.UTC) + _dt.timedelta(
        minutes=_ACCESS_TOKEN_EXPIRE_MINUTES
    )
    data = dict(sub=user_name, exp=expires)

    access_token = _jwt.encode(data, _SECRET_KEY, algorithm=_ALGORITHM)

    token = Token(token_type="bearer", valid_until=expires, access_token=access_token)

    return token
