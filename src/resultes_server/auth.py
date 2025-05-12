import datetime as _dt
import logging as _log

import fastapi as _fapi
import jwt as _jwt
import passlib.context as _plctx
import pydantic as _pyd
import sqlmodel as _sqlm

import resultes_server.models.user as _mu
import resultes_server.users as _users

_LOGGER = _log.getLogger(__name__)

# to get a string like this run:
# openssl rand -hex 32
_SECRET_KEY = "7fb0ec55e5fb59fbd849d971c04b5f867aa6b933248f9176ad62347dc768e3c3"
_ALGORITHM = "HS256"
_ACCESS_TOKEN_EXPIRE_MINUTES = 30

_PWD_CONTEXT = _plctx.CryptContext(schemes=["bcrypt"], deprecated="auto")


class Token(_pyd.BaseModel):
    access_token: str
    token_type: str


def get_hashed_password(plain_password: str) -> str:
    return _PWD_CONTEXT.hash(plain_password)


def get_current_user(token: str, session: _sqlm.Session) -> _mu.User:
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

    user = _users.get_user(user_name, session)
    if user is None:
        raise credentials_exception

    return user


def get_current_active_user(
    current_user: _mu.User,
) -> _mu.User:
    if current_user.disabled:
        raise _fapi.HTTPException(status_code=400, detail="Inactive user")
    return current_user


def create_token(user_name: str, plain_password: str, session: _sqlm.Session) -> Token:
    user = authenticate_user(user_name, plain_password, session)
    if not user:
        raise _fapi.HTTPException(
            status_code=_fapi.status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = _create_token(user.user_name)
    return Token(access_token=access_token, token_type="bearer")


def authenticate_user(
    user_name: str, plain_password: str, session: _sqlm.Session
) -> _mu.User | None:
    user = _users.get_user(user_name, session)
    if not user:
        return None
    if not _verify_password(plain_password, user.hashed_password):
        return None
    return user


def _verify_password(plain_password: str, hashed_password) -> bool:
    return _PWD_CONTEXT.verify(plain_password, hashed_password)


def _create_token(user_name: str) -> str:
    expires = _dt.datetime.now(_dt.UTC) + _dt.timedelta(
        minutes=_ACCESS_TOKEN_EXPIRE_MINUTES
    )
    data = dict(sub=user_name, exp=expires)
    token = _jwt.encode(data, _SECRET_KEY, algorithm=_ALGORITHM)
    return token
