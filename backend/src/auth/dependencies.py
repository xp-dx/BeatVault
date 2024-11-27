from fastapi import Depends, HTTPException, status

from fastapi.security import OAuth2PasswordBearer

from sqlalchemy.orm import Session

from typing import Annotated

from jwt.exceptions import InvalidTokenError

import jwt

from . import config as _config, schemas as _schemas, service as _service

from .. import dependencies as _global_dependencies

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")


def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Session = Depends(_global_dependencies.get_db),
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer", "Location": "/login"},
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
    if user is None:
        raise credentials_exception
    return user


def get_current_active_user(
    current_user: Annotated[_schemas.User, Depends(get_current_user)]
):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user
