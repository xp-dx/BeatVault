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
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from pydantic import EmailStr

from typing import Annotated

from datetime import timedelta

import aiosmtplib

from src.celery.qr import (
    service as _qr_service,
    tasks as _qr_tasks,
    dependencies as _qr_dependencies,
)
from src.celery.sms import (
    service as _sms_service,
    tasks as _sms_tasks,
    dependencies as _sms_dependencies,
)
from src.celery.email import (
    service as _email_service,
    tasks as _email_tasks,
    dependencies as _email_dependencies,
)


from . import (
    schemas as _schemas,
    service as _service,
    config as _config,
    crud as _crud,
    dependencies as _dependencies,
)

from .. import dependencies as _global_dependencies


router = APIRouter(tags=["auth"], prefix="/auth")


@router.post("/registration")
async def registration(
    username: Annotated[str, Form()],
    email: Annotated[EmailStr, Form()],
    password: Annotated[str, Form()],
    stripe_account_id: Annotated[str, Form()],
    avatar: Annotated[UploadFile | None, File()] = None,
    db: AsyncSession = Depends(_global_dependencies.get_async_session),
):
    new_user = _schemas.UserCreate(
        username=username,
        email=email,
        password=password,
        stripe_account_id=stripe_account_id,
    )
    db_user = await _service.get_user_by_username(db, new_user.username)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="User already exists"
        )
    return await _crud.create_user(db=db, user=new_user, avatar=avatar)


@router.post("/login")
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: AsyncSession = Depends(_global_dependencies.get_async_session),
) -> _schemas.Token:
    user = await _service.authenticate_user(
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


@router.post("/request-password-reset", tags=["users"])
async def request_password_reset(
    email: str,
    db: AsyncSession = Depends(_global_dependencies.get_async_session),
    email_client: Redis = Depends(_email_dependencies.get_email_client),
):

    user = await _service.get_user_by_email(db, email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User with this email not found",
        )

    reset_url = await _email_service.create_password_reset_link(email, email_client)
    await _email_tasks.send_password_reset_email_async(email, reset_url)

    return {"message": "Password reset link sent to your email"}


@router.post("/reset-password", tags=["users"])
async def reset_password(
    token: str,
    new_password: Annotated[str, Form()],
    db: AsyncSession = Depends(_global_dependencies.get_async_session),
):
    _email_service.reset_user_password(token=token, new_password=new_password, db=db)
    return {"message": "Password successfully changed"}


@router.post("/request-confirm-email", tags=["users"])
async def confirm_email(
    current_user: Annotated[
        _schemas.UserEmail, Depends(_dependencies.get_current_active_user)
    ],
    db: AsyncSession = Depends(_global_dependencies.get_async_session),
):
    email = current_user.email
    if not await _service.is_verified(email, db):
        token = _email_service.create_confirmation_token(email)
        confirmation_url = f"http://127.0.0.1:8000/confirm-email?token={token}"

        await _email_tasks.send_confirmation_email_async(email, confirmation_url)

        return {"message": "Confirmation email sent", "email": email}
    return {"message": "Email already confirmed", "email": email}


@router.get("/confirm-email", tags=["users"])
async def confirm_email(
    token: str, db: AsyncSession = Depends(_global_dependencies.get_async_session)
):
    try:
        return await _service.confirm_email(token, db)
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=400, detail="Token expired")
    except JWTError:
        raise HTTPException(status_code=400, detail="Invalid token")


# @router.post("/request-confirm-sms", tags=["users"])
# async def send_confirmation_sms(phone: str):
#     """Запускает отправку SMS с кодом подтверждения"""
#     task = await _sms_tasks.send_phone_confirmation_sms_async(phone)
#     return {"message": "SMS отправляется", "task_id": task.id}


# @router.post("/confirm-sms", tags=["users"])
# async def verify_sms(phone: str, code: str):
#     """Проверяет код подтверждения из SMS"""
#     is_valid = await _sms_service.verify_sms_code(phone, code)
#     if not is_valid:
#         raise HTTPException(status_code=400, detail="Неверный код подтверждения")
#     return {"message": "Телефон успешно подтвержден"}


@router.get("/generate-qr")
async def generate_qr(
    user_id: str = None,
    qr_client: Redis = Depends(_qr_dependencies.get_qr_client),
):
    """Генерирует QR-код для входа"""
    result = await _qr_tasks.generate_login_qr_task(qr_client, user_id)
    return StreamingResponse(
        io.BytesIO(result["qr_image"]),
        media_type="image/png",
        headers={"X-QR-Token": result["token"]},
    )


@router.post("/auth-via-qr", tags=["users"])
async def auth_via_qr(
    token: str,
    qr_client: Redis = Depends(_qr_dependencies.get_qr_client),
):
    return await _qr_tasks.authenticate_via_qr_task(token, qr_client)


@router.get("/check-qr-status/{token}")
async def check_qr_status(token: str):
    """Проверяет статус QR-аутентификации"""
    result = await _qr_tasks.verify_qr_token_task(token)
    if result["status"] == "invalid":
        raise HTTPException(status_code=404, detail="Token not found")
    return result


@router.post("/confirm-qr-login/{token}")
async def confirm_qr_login(token: str, user_id: str):
    """Подтверждает вход по QR-коду"""
    result = await _qr_tasks.authenticate_via_qr_task(token, user_id)
    if result["status"] == "error":
        raise HTTPException(status_code=400, detail="Invalid token")
    return result


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
