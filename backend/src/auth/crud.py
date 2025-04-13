from fastapi import UploadFile

from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession

from . import service as _service, schemas as _schemas, constants as _constants

from .. import models as _global_models


async def create_user(
    db: AsyncSession, user: _schemas.UserCreate, avatar: UploadFile | None
):
    if avatar:
        avatar_data = await avatar.read()
    else:
        avatar_data = _constants.DEFAULT_AVATAR

    hashed_password = await _service.get_password_hash(user.password)
    db_user = _global_models.User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password,
        avatar=avatar_data,
        stripe_account_id=user.stripe_account_id,
    )
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user.email


async def update_verified_status(db: AsyncSession, email: str):
    stmt = (
        update(_global_models.User)
        .where(_global_models.User.email == email)
        .values(is_verified=True)
    )
    await db.execute(stmt)
    await db.commit()


async def change_password(email: str, new_password: str, db: AsyncSession):
    stmt = (
        update(_global_models.User)
        .where(_global_models.User.email == email)
        .values(hashed_password=_service.get_password_hash(new_password))
    )
    await db.execute(stmt)
    await db.commit()
