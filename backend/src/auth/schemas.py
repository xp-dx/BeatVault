from pydantic import BaseModel


class Token(BaseModel):
    access_token: str
    token_type: str


class UserBase(BaseModel):
    username: str


class User(UserBase):
    id: int
    disabled: bool = False
