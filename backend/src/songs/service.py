# def upload_mp3_file()
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_, and_

from src.auth import schemas as _auth_schemas

from .. import models as _global_models


async def check_owner_of_song(user, song_id, db: AsyncSession):
    if (
        await db.execute(
            select(_global_models.UserSong.user_id).where(
                _global_models.UserSong.user_id == user.id,
                _global_models.UserSong.song_id == song_id,
            )
        )
    ).scalar_one_or_none:
        return True


async def check_access_to_song(user: _auth_schemas.UserId, song, db: AsyncSession):
    result = await db.execute(
        select(_global_models.UserSong).where(
            or_(
                _global_models.UserSong.user_id == user.id,
                and_(
                    _global_models.Payment.user_id == user.id,
                    _global_models.Payment.song_id == song.id,
                    _global_models.Payment.status == "successfully",
                ),
            )
        )
    )

    access = result.scalar_one_or_none() is not None

    return access
