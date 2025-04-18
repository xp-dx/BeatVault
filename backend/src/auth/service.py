from datetime import datetime, timedelta, timezone

from fastapi import HTTPException

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

import jwt

from . import config as _config, dependencies as _dependencies, crud as _crud
from .. import models as _global_models, config as _global_config


def get_password_hash(password):
    return _dependencies.pwd_context.hash(password)


def verify_password(plain_password, hashed_password):
    return _dependencies.pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=5)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, _config.SECRET_KEY, algorithm=_config.ALGORITHM)
    return encoded_jwt


async def authenticate_user(db: AsyncSession, username: str, password: str):
    user = await get_user_by_username(db, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


async def get_user_by_username(db: AsyncSession, username: str):
    result = await db.execute(
        select(_global_models.User).where(_global_models.User.username == username)
    )
    return result.scalar_one_or_none()


async def get_user_by_email(db: AsyncSession, email: str):
    result = await db.execute(
        select(_global_models.User).where(_global_models.User.email == email)
    )
    return result.scalar_one_or_none()


async def get_user_by_id(db: AsyncSession, user_id: int):
    result = await db.execute(
        select(_global_models.User).where(_global_models.User.user_id == user_id)
    )
    return result.scalar_one_or_none()


async def get_all_users(db: AsyncSession):
    result = await db.execute(
        select(_global_models.User.id, _global_models.User.username)
    )
    users = result.all()
    return [{"id": user.id, "username": user.username} for user in users]


async def confirm_email(token: str, db: AsyncSession):
    payload = jwt.decode(
        token, _global_config.JWT_SECRET_KEY, algorithms=[_global_config.JWT_ALGORITHM]
    )
    email: str = payload.get("sub")
    if email is None:
        raise HTTPException(status_code=400, detail="Invalid token")
    await _crud.update_verified_status(db, email)
    return {"message": "Email confirmed", "email": email}


async def is_verified(email: str, db: AsyncSession):
    user = (
        await db.execute(
            select(_global_models.User).where(_global_models.User.email == email)
        )
    ).scalar_one_or_none()
    return user is not None and user.is_verified
