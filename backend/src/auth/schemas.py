from pydantic import BaseModel, EmailStr


class Token(BaseModel):
    access_token: str
    token_type: str


class UserBase(BaseModel):
    username: str


class User(UserBase):
    # id: int
    username: str
    is_artist: bool
    is_active: bool = True


class UserCreate(User):
    email: EmailStr
    # username: str
    password: str
    # is_artist: bool
