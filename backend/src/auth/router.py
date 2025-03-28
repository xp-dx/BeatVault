import io
import secrets
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
from fastapi.responses import StreamingResponse
from fastapi.security import OAuth2PasswordRequestForm

from jose import JWTError, jwt
from sqlalchemy.orm import Session

from pydantic import EmailStr

from typing import Annotated

from datetime import timedelta

import aiosmtplib

from src.celery import utils as _celery_utils, tasks as _celery_tasks, redis as _redis
from src.sms.service import verify_sms_code

from . import (
    schemas as _schemas,
    service as _service,
    config as _config,
    crud as _crud,
    dependencies as _dependencies,
)

from .. import dependencies as _global_dependencies


router = APIRouter(tags=["auth"])


@router.post("/registration")
async def registration(
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


@router.get("/registration")
def registration(request: Request):
    return "asd"


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
            status_code=status.HTTP_401_UNAUTHORIZED,
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


@router.post("/request-password-reset", tags=["users"])
async def request_password_reset(
    email: str,
    db: Session = Depends(_global_dependencies.get_db),
):
    user = _service.get_user_by_email(db, email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User with this email not found",
        )

    reset_token = secrets.token_urlsafe(32)

    await _redis.redis_client.setex(
        f"password_reset:{reset_token}", 900, email  # 15 минут
    )

    reset_url = f"http://127.0.0.1:8000/reset-password?token={reset_token}"
    await _celery_tasks.send_password_reset_email_async(email, reset_url)

    return {"message": "Password reset link sent to your email"}


@router.post("/reset-password", tags=["users"])
async def reset_password(
    token: str,
    new_password: Annotated[str, Form()],
    db: Session = Depends(_global_dependencies.get_db),
):
    email_bytes = await _redis.redis_client.get(f"password_reset:{token}")
    if not email_bytes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired token",
        )
    email = (
        email_bytes.decode("utf-8") if isinstance(email_bytes, bytes) else email_bytes
    )

    await _crud.change_password(email, new_password, db=db)

    await _redis.redis_client.delete(f"password_reset:{token}")

    return {"message": "Password successfully changed"}


@router.post("/confirm-email", tags=["users"])
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


@router.get("/confirm-email", tags=["users"])
async def confirm_email(token: str, db: Session = Depends(_global_dependencies.get_db)):
    try:
        return await _service.confirm_email(token, db)
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=400, detail="Token expired")
    except JWTError:
        raise HTTPException(status_code=400, detail="Invalid token")


@router.post("/send-confirmation", tags=["users"])
async def send_confirmation_sms(phone: str):
    """Запускает отправку SMS с кодом подтверждения"""
    task = await _celery_tasks.send_phone_confirmation_sms_async(phone)
    return {"message": "SMS отправляется", "task_id": task.id}


@router.post("/verify", tags=["users"])
async def verify_sms(phone: str, code: str):
    """Проверяет код подтверждения из SMS"""
    is_valid = await verify_sms_code(phone, code)
    if not is_valid:
        raise HTTPException(status_code=400, detail="Неверный код подтверждения")
    return {"message": "Телефон успешно подтвержден"}


# @router.post("/auth-via-qr", tags=["users"])
# async def auth_via_qr(token: str, db: Session = Depends(_global_dependencies.get_db)):
#     return await _qr_service.authenticate_via_qr(token, db)


# @router.get("/generate-qr")
# async def generate_qr(user_id: str = None):
#     """Генерирует QR-код для входа"""
#     result = await _celery_tasks.generate_login_qr_task(user_id)
#     return StreamingResponse(
#         io.BytesIO(result["qr_image"]),
#         media_type="image/png",
#         headers={"X-QR-Token": result["token"]},
#     )


# @router.get("/check-qr-status/{token}")
# async def check_qr_status(token: str):
#     """Проверяет статус QR-аутентификации"""
#     result = await _celery_tasks.verify_qr_token_task(token)
#     if result["status"] == "invalid":
#         raise HTTPException(status_code=404, detail="Token not found")
#     return result


# @router.post("/confirm-qr-login/{token}")
# async def confirm_qr_login(token: str, user_id: str):
#     """Подтверждает вход по QR-коду"""
#     result = await _celery_tasks.authenticate_via_qr_task(token, user_id)
#     if result["status"] == "error":
#         raise HTTPException(status_code=400, detail="Invalid token")
#     return result


# @router.post("/send-code")
# async def send_verification_code(phone: str):
#     send_sms_code(phone)
#     return {"message": "Код отправлен"}


# @router.post("/verify-code")
# async def verify_code(phone: str, user_code: str):
#     """Проверяет введенный код."""
#     stored_code = _redis.redis_client.get(f"phone_verify:{phone}")
#     if not stored_code:
#         raise HTTPException(status_code=400, detail="Код устарел или не существует")

#     if stored_code.decode() != user_code:
#         raise HTTPException(status_code=400, detail="Неверный код")

#     return {"success": True, "message": "Номер подтвержден"}
