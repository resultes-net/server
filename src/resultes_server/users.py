import sqlmodel as _sqlm
import fastapi as _fapi

import resultes_server.auth as _auth
import resultes_server.models.user as _mu



def get_user(user_name: str, session: _sqlm.Session) -> _mu.User | None:
    statement = _sqlm.select(_mu.User).where(_mu.User.user_name == user_name)
    results = session.exec(statement)
    user = results.one_or_none()
    return user


_REGISTRATION_KEY = "579e57a617ec"

def create_user(user_create: _mu.UserCreate, session: _sqlm.Session) -> _mu.User:
    if user_create.registration_key != _REGISTRATION_KEY:
        raise _fapi.HTTPException(
            status_code=_fapi.status.HTTP_403_FORBIDDEN,
            detail="Registration key is invalid.",
        )

    user = get_user(user_create.user_name, session)
    if user:
        raise _fapi.HTTPException(
            status_code=_fapi.status.HTTP_409_CONFLICT,
            detail="User name is taken.",
        )

    hashed_password = _auth.get_hashed_password(user_create.plain_password)

    user = _mu.User(
        user_name=user_create.user_name,
        full_name=user_create.full_name,
        email=user_create.email,
        hashed_password=hashed_password,
        disabled=False,
    )

    session.add(user)
    session.commit()

    return user

def update_user(user_modfiy: _mu.UserModify, user: _mu.User, session: _sqlm.Session) -> _mu.UserRead:
    user_or_none = _auth.authenticate_user(user.user_name, user_modfiy.old_plain_password, session)
    if not user_or_none:
        raise _fapi.HTTPException(
            status_code=_fapi.status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Old password is incorrect."
        )
    assert user_or_none == user

    new_hashed_password = _auth.get_hashed_password(user_modfiy.new_plain_password)

    user.hashed_password = new_hashed_password

    session.commit()

    return user
