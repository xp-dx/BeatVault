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

from jose import JWTError, jwt
from sqlalchemy.orm import Session

from pydantic import EmailStr

from typing import Annotated

from datetime import timedelta

import aiosmtplib

from src.celery import utils as _celery_utils
from src.celery import tasks as _celery_tasks


from . import (
    schemas as _schemas,
    service as _service,
    config as _config,
    crud as _crud,
    dependencies as _dependencies,
)

from .. import dependencies as _global_dependencies


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
    db: Session = Depends(_global_dependencies.get_db),
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
    db: Session = Depends(_global_dependencies.get_db),
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


@router.post("/confirm-email")
async def confirm_email(
    current_user: Annotated[
        _schemas.UserEmail, Depends(_dependencies.get_current_active_user)
    ],
    db: Session = Depends(_global_dependencies.get_db),
):
    email = current_user.email
    if not _service.is_verified(email, db):
        token = _celery_utils.create_confirmation_token(email)
        confirmation_url = f"http://127.0.0.1:8000/confirm-email?token={token}"

        await _celery_tasks.send_confirmation_email_async(email, confirmation_url)

        return {"message": "Confirmation email sent", "email": email}
    return {"message": "Email already confirmed", "email": email}


@router.get("/confirm-email")
async def confirm_email(token: str, db: Session = Depends(_global_dependencies.get_db)):
    try:
        return await _service.confirm_email(token, db)
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=400, detail="Token expired")
    except JWTError:
        raise HTTPException(status_code=400, detail="Invalid token")
