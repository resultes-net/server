import pydantic as _pyd


class UserBase(_pyd.BaseModel):
    user_name: str
    email: _pyd.EmailStr
    full_name: str


class UserCreate(UserBase):
    plain_password: str
    registration_key: str


class UserModify(_pyd.BaseModel):
    old_plain_password: str
    new_plain_password: str


class UserRead(UserBase):
    id: str | None
    disabled: bool
