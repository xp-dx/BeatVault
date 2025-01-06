from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
    Request,
    Form,
    UploadFile,
    File,
)
from fastapi.security import OAuth2PasswordRequestForm

from sqlalchemy.orm import Session

from pydantic import EmailStr

from typing import Annotated

from datetime import timedelta

from . import schemas as _schemas, service as _service, config as _config, crud as _crud

from ..dependencies import get_db


router = APIRouter(tags=["auth"])


@router.get("/registration")
def registration(request: Request):
    return "asd"


@router.post("/registration")
async def registration(
    # new_user_form: Annotated[_schemas.UserCreate, Form()],
    username: Annotated[str, Form()],
    email: Annotated[EmailStr, Form()],
    password: Annotated[str, Form()],
    stripe_account_id: Annotated[str, Form()],
    avatar: Annotated[UploadFile | None, File()] = None,
    db: Session = Depends(get_db),
):
    new_user = _schemas.UserCreate(
        username=username,
        email=email,
        password=password,
        stripe_account_id=stripe_account_id,
    )
    db_user = _service.get_user_by_username(db, new_user.username)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="User already exists"
        )
    return await _crud.create_user(db=db, user=new_user, avatar=avatar)


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
    access_token_expires = timedelta(minutes=int(_config.ACCESS_TOKEN_EXPIRE_MINUTES))
    access_token = _service.create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return _schemas.Token(access_token=access_token, token_type="bearer")


@router.get("/login")
def login(request: Request):
    return "asd"
