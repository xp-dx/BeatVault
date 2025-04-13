from fastapi import HTTPException, UploadFile

from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

import json

import base64

from src.auth import schemas as _user_schemas

from . import schemas as _schemas, constants as _constants, service as _service

from .. import models as _global_models


async def read_all_albums(db: AsyncSession):
    albums_result = await db.execute(select(_global_models.Album))
    albums = albums_result.scalars().all()

    albums_json = [
        {"id": album.id, "title": album.title, "description": album.description}
        for album in albums
    ]

    return albums_json


async def read_album_songs(db: AsyncSession, album_id: int):
    album_result = await db.execute(
        select(_global_models.Album).where(_global_models.Album.id == album_id)
    )
    album = album_result.scalar_one_or_none()  # Получаем альбом

    if not album:
        raise HTTPException(status_code=404, detail="Album not found")

    songs_result = await db.execute(
        select(_global_models.Song).where(_global_models.Song.album_id == album_id)
    )
    album_songs = songs_result.scalars().all()

    album_songs_json = {
        "album": {
            "id": album.id,
            "title": album.title,
            "description": album.description,
        },
        "songs": [
            {
                "id": album_song.id,
                "title": album_song.title,
                "artist": album_song.artist,
                "genre": album_song.genre,
                "price": album_song.price,
            }
            for album_song in album_songs
        ],
    }

    return album_songs_json


async def create_album(
    db: AsyncSession,
    user: _user_schemas.UserId,
    album: _schemas.Album,
    cover: UploadFile | None,
):
    if cover:
        cover_data = await cover.read()
    else:
        cover_data = _constants.DEFAULT_COVER

    db_album = _global_models.Album(
        title=album.title,
        description=album.description,
        cover=cover_data,
    )
    db.add(db_album)
    await db.commit()
    await db.refresh(db_album)

    db_user_album = _global_models.UserAlbum(user_id=user.id, album_id=db_album.id)
    db.add(db_user_album)
    await db.commit()

    return {
        "id": db_album.id,
        "title": db_album.title,
        "description": db_album.description,
        "cover": base64.b64encode(db_album.cover).decode("ascii"),
    }


async def delete_album(
    current_user: _user_schemas.UserId, album_id: int, db: AsyncSession
):
    is_owner = await _service.check_owner_of_album(
        user_id=current_user.id, album_id=album_id, db=db
    )
    if is_owner:
        await db.execute(
            delete(_global_models.UserAlbum).where(
                _global_models.UserAlbum.album_id == album_id
            )
        )

        await db.execute(
            delete(_global_models.Album).where(_global_models.Album.id == album_id)
        )

        await db.commit()
        return True
    return False
