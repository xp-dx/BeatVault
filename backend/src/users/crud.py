from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth import schemas as _auth_schemas

from .. import models as _global_models


async def delete_user(current_user: _auth_schemas.User, db: AsyncSession):
    await db.execute(
        delete(_global_models.User).where(_global_models.User.id == current_user.id)
    )
    await db.commit()
    return True


async def update_username(
    current_user: _auth_schemas.User, new_username: str, db: AsyncSession
):
    user = (
        await db.execute(
            select(_global_models.User.username).where(
                _global_models.User.id == current_user.id
            )
        )
    ).scalar_one_or_none()
    user.username = new_username
    await db.commit()
    return user.username
