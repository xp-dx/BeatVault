import aiosmtplib
import secrets

from fastapi import HTTPException, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from redis.asyncio import Redis
from src import config as _global_config
from email.mime.text import MIMEText
from datetime import timedelta, datetime
from jose import jwt

from src.auth import crud as _auth_crud


def create_confirmation_token(email: str):
    expires = datetime.now() + timedelta(minutes=int(_global_config.JWT_EXPIRE_MINUTES))
    to_encode = {"sub": email, "exp": expires}
    return jwt.encode(
        to_encode, _global_config.JWT_SECRET_KEY, algorithm=_global_config.JWT_ALGORITHM
    )


async def reset_user_password(
    email_client: Redis,
    token: str,
    new_password: str,
    db: AsyncSession,
):
    email_bytes = await email_client.get(f"password_reset:{token}")
    if not email_bytes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired token",
        )
    email = (
        email_bytes.decode("utf-8") if isinstance(email_bytes, bytes) else email_bytes
    )

    await _auth_crud.change_password(email, new_password, db=db)

    await email_client.delete(f"password_reset:{token}")


async def create_password_reset_link(
    email: str,
    email_client: Redis,
):
    reset_token = secrets.token_urlsafe(32)

    await email_client.setex(f"password_reset:{reset_token}", 900, email)  # 15 минут

    reset_url = f"http://127.0.0.1:8000/reset-password?token={reset_token}"
    return reset_url


async def send_email(to: str, subject: str, body: str):
    """Функция для отправки письма."""
    message = MIMEText(body)
    message["From"] = _global_config.SMTP_USER
    message["To"] = to
    message["Subject"] = subject

    await aiosmtplib.send(
        message,
        hostname=_global_config.SMTP_HOST,
        port=_global_config.SMTP_PORT,
        username=_global_config.SMTP_USER,
        password=_global_config.SMTP_PASSWORD,
        use_tls=True,
    )
