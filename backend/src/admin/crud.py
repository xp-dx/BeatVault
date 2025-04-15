from pydantic import EmailStr

from sqlalchemy import select, delete, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth import dependencies as _auth_dependencies
from src.auth import schemas as _auth_schemas

from .. import models as _global_models


async def delete_user(user_email: EmailStr, db: AsyncSession):
    user_result = await db.execute(
        select(_global_models.User.id).where(_global_models.User.email == user_email)
    )
    user = user_result.scalar_one_or_none()
    if not user:
        return False

    songs_result = await db.execute(
        select(_global_models.UserSong.song_id).where(
            _global_models.UserSong.user_id == user.id
        )
    )
    songs_ids = [row[0] for row in songs_result.all()]

    await db.execute(
        delete(_global_models.UserSong).where(
            _global_models.UserSong.user_id == user.id
        )
    )

    if songs_ids:
        await db.execute(
            delete(_global_models.Song).where(_global_models.Song.id.in_(songs_ids))
        )

    await db.execute(
        delete(_global_models.User).where(_global_models.User.email == user_email)
    )

    await db.commit()
    return True


async def delete_song(song_id: int, db: AsyncSession):
    await db.execute(
        delete(_global_models.UserSong).where(
            _global_models.UserSong.song_id == song_id
        )
    )
    await db.execute(
        delete(_global_models.Song).where(_global_models.Song.id == song_id)
    )
    await db.commit()
    return True


async def check_role(current_user: _auth_schemas.UserEmail, db: AsyncSession):
    result = await db.execute(
        select(_global_models.User).where(
            _global_models.User.email == current_user.email
        )
    )
    user = result.scalar_one_or_none()

    if user and user.is_superuser:
        return True
    return False


async def deactivate_user(user_email: EmailStr, db: AsyncSession):
    stmt = (
        update(_global_models.User)
        .where(_global_models.User.email == user_email)
        .values(is_active=False)
    )
    await db.execute(stmt)
    await db.commit()
    return True


async def activate_user(user_email: EmailStr, db: AsyncSession):
    stmt = (
        update(_global_models.User)
        .where(_global_models.User.email == user_email)
        .values(is_active=True)
    )
    await db.execute(stmt)
    await db.commit()
    return True
