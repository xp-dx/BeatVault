from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm

from sqlalchemy.orm import Session

from typing import Annotated

from datetime import timedelta

from . import schemas as _schemas, service as _service, config as _config

from ..dependencies import get_db


router = APIRouter(tags=["auth"])


@router.post("/login")
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Session = Depends(get_db),
) -> _schemas.Token:
    user = _service.authenticate_user(
        db=db, username=form_data.username, password=form_data.password
    )
    if not user:
        raise HTTPException(
            status=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(
        minutes=timedelta(_config.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    access_token = _service.create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return _schemas.Token(access_token=access_token, token_type="bearer")


@router.get("/login")
def login(request: Request):
    return "asd"
