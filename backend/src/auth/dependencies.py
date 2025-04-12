import base64
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from sqlalchemy.orm import Session

from typing import Annotated

from passlib.context import CryptContext

import jwt
from jwt.exceptions import InvalidTokenError

from . import config as _config, schemas as _schemas, service as _service

from .. import dependencies as _global_dependencies


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Session = Depends(_global_dependencies.get_async_session),
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer", "Location": "/auth/login"},
    )
    try:
        payload = jwt.decode(token, _config.SECRET_KEY, algorithms=[_config.ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = _schemas.TokenData(username=username)

    except InvalidTokenError:
        raise credentials_exception
    user = _service.get_user_by_username(db, username=token_data.username)
    # user_json = [
    #     {
    #         "id": user.id,
    #         "username": user.username,
    #         "email": user.email,
    #         "avatar": base64.b64encode(user.avatar).decode("utf-8"),
    #         "is_verified": user.is_verified,
    #         "is_active": user.is_active,
    #         "is_verified": user.is_verified,
    #     }
    # ]

    if user is None:
        raise credentials_exception
    return user


def get_current_active_user(
    current_user: Annotated[_schemas.User, Depends(get_current_user)],
):
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


async def confirm_email(token: str):
    try:
        payload = jwt.decode(token, _config.SECRET_KEY, algorithms=[_config.ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=400, detail="Invalid token")
        # Активируйте пользователя в базе данных
        # user.is_active = True
        return {"message": "Email confirmed"}
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=400, detail="Token expired")
    except jwt.JWTError:
        raise HTTPException(status_code=400, detail="Invalid token")
