import sqlmodel as _sqlm

import resultes_server.models.user as _mu


def get_user(user_name: str, session: _sqlm.Session) -> _mu.User | None:
    statement = _sqlm.select(_mu.User).where(_mu.User.user_name == user_name)
    results = session.exec(statement)
    user = results.one_or_none()
    return user


def create_user(user_create: _mu.UserCreate, session: _sqlm.Session) -> _mu.UserRead:
    user = _mu.User(**user_create.model_dump(), disabled=False)
    session.add(user)
    return user
