from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .. import models as _global_models


async def check_owner_of_album(user_id: int, album_id: int, db: AsyncSession):
    result = await db.execute(
        select(_global_models.UserAlbum).where(
            _global_models.UserAlbum.user_id == user_id,
            _global_models.UserAlbum.album_id == album_id,
        )
    )
    user_album = result.scalar_one_or_none()
    return user_album is not None
