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


class UserCreate(UserBase):
    email: EmailStr
    password: str
    stripe_account_id: str


class UserMe(UserEmail):
    avatar: bytes
    default_avatar: bytes
    is_verified: bool = False


class PasswordResetRequest(BaseModel):
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str
