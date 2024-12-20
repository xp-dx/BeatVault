from pydantic import BaseModel, EmailStr


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None


class UserId(BaseModel):
    id: int


class UserBase(BaseModel):
    username: str


class User(UserBase):
    id: int
    is_active: bool = True


class UserEmail(User):
    email: EmailStr


class UserCreate(UserEmail):
    # email: EmailStr
    # username: str
    password: str
    # is_artist: bool
