from typing import Any, Dict
from fastapi import HTTPException, UploadFile

from sqlalchemy import delete, desc, select, join
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth import schemas as _user_schemas

import base64

from . import schemas as _schemas, constants as _constants

from .. import models as _global_models


async def get_all_songs(db: AsyncSession):
    songs = (
        await db.execute(
            select(
                _global_models.Song.id,
                _global_models.Song.title,
                _global_models.Song.artist,
                _global_models.Song.genre,
                _global_models.Song.price,
                _global_models.Song.cover,
            )
        )
    ).all()
    songs_json = []
    for song in songs:
        songs_json.append(
            {
                "id": song.id,
                "title": song.title,
                "artist": song.artist,
                "genre": song.genre,
                "price": song.price,
                "cover": song.cover,
            }
        )
    return songs_json


async def get_part_songs(offset: int, limit: int, db: AsyncSession):
    songs = (
        await db.execute(
            select(
                _global_models.Song.id,
                _global_models.Song.title,
                _global_models.Song.artist,
                _global_models.Song.genre,
                _global_models.Song.price,
                _global_models.Song.cover,
            )
            .offset(offset)
            .limit(limit)
        )
    ).all()
    songs_json = []
    for song in songs:
        songs_json.append(
            {
                "id": song.id,
                "title": song.title,
                "artist": song.artist,
                "genre": song.genre,
                "price": song.price,
                "cover": base64.b64encode(song.cover).decode("utf-8"),
            }
        )
    return songs_json


async def get_song_by_id(song_id: int, db: AsyncSession):
    song = (
        await db.execute(
            select(
                _global_models.Song.id,
                _global_models.Song.title,
                _global_models.Song.artist,
                _global_models.Song.genre,
                _global_models.Song.price,
                _global_models.Song.lyrics,
                _global_models.Song.cover,
            ).where(_global_models.Song.id == song_id)
        )
    ).first()
    return {
        "id": song.id,
        "title": song.title,
        "artist": song.artist,
        "genre": song.genre,
        "price": song.price,
        "lyrics": song.lyrics,
        "cover": base64.b64encode(song.cover).decode("utf-8"),
    }


# import base64


# def get_part_songs(offset: int, limit: int, db: AsyncSession):
#     songs = db.query(_global_models.Song).offset(offset).limit(limit).all()
#     songs_json = []

#     for song in songs:
#         cover_base64 = None
#         if song.cover:  # Проверяем, есть ли изображение
#             cover_base64 = base64.b64encode(song.cover).decode("utf-8")

#         songs_json.append(
#             {
#                 "id": song.id,
#                 "title": song.title,
#                 "artist": song.artist,
#                 "genre": song.genre,
#                 "price": song.price,
#                 "cover": cover_base64,
#             }
#         )

#     return songs_json  # JSON-формат


async def get_all_uploaded_songs(user, db: AsyncSession):
    try:
        j = join(
            _global_models.UserSong,
            _global_models.Song,
            _global_models.UserSong.song_id == _global_models.Song.id,
        )

        stmt = (
            select(
                _global_models.Song.id,
                _global_models.Song.title,
                _global_models.Song.artist,
                _global_models.Song.genre,
                _global_models.Song.price,
            )
            .select_from(j)
            .where(_global_models.UserSong.user_id == user.id)
            .order_by(desc(_global_models.UserSong.song_id))
        )

        result = await db.execute(stmt)
        songs = result.all()

        songs_json = [
            {
                "id": song.id,
                "title": song.title,
                "artist": song.artist,
                "genre": song.genre,
                "price": song.price,
            }
            for song in songs
        ]

    except:
        return {"message": "You don't uploaded any songs"}
    if not songs_json:
        return {"message": "You don't uploaded any songs"}

    return songs_json


async def get_all_purchased_songs(user, db: AsyncSession):
    j = join(
        _global_models.Payment,
        _global_models.Song,
        _global_models.Payment.song_id == _global_models.Song.id,
    )

    stmt = (
        select(
            _global_models.Song.id,
            _global_models.Song.title,
            _global_models.Song.artist,
            _global_models.Song.genre,
        )
        .select_from(j)
        .where(
            _global_models.Payment.user_id == user.id,
            _global_models.Payment.status == "successfully",
        )
        .order_by(desc(_global_models.Payment.payment_date))
    )

    result = await db.execute(stmt)
    songs = result.all()

    if not songs:
        return {"message": "You don't purchased any songs"}

    songs_json = [
        {"id": song.id, "title": song.title, "artist": song.artist, "genre": song.genre}
        for song in songs
    ]

    return songs_json


async def upload_song(
    db: AsyncSession,
    user: _user_schemas.UserId,
    song: _schemas.SongUpload,
    file: UploadFile,
    cover: UploadFile | None,
):
    file_data = await file.read()
    cover_data = await cover.read() if cover else _constants.DEFAULT_COVER

    db_song = _global_models.Song(
        title=song.title,
        artist=song.artist,
        genre=song.genre,
        lyrics=song.lyrics,
        price=song.price,
        file=file_data,
        cover=cover_data,
        album_id=song.album_id,
    )
    db.add(db_song)
    await db.commit()
    await db.refresh(db_song)

    db_user_song = _global_models.UserSong(user_id=user.id, song_id=db_song.id)
    db.add(db_user_song)
    await db.commit()

    return {
        "id": db_song.id,
        "title": db_song.title,
        "artist": db_song.artist,
        "genre": db_song.genre,
        "lyrics": db_song.lyrics,
        "price": db_song.price,
        # "cover": str(db_song.cover),
        # "cover": base64.b64encode(db_song.cover).decode("ascii"),
        "album_id": db_song.album_id,
    }


async def update_song(song_id: int, update_data: Dict[str, Any], db: AsyncSession):
    db_song = await db.execute(
        select(_global_models.Song).where(_global_models.Song.id == song_id)
    )

    if not db_song:
        raise HTTPException(status_code=404, detail="Song not found")

    for field, value in update_data.items():
        if hasattr(db_song, field):
            setattr(db_song, field, value)

    await db.commit()
    await db.refresh(db_song)

    # return {
    #     "id": db_song.id,
    #     "title": db_song.title,
    #     "artist": db_song.artist,
    #     "genre": db_song.genre,
    #     "lyrics": db_song.lyrics,
    #     "price": db_song.price,
    #     "cover": base64.b64encode(db_song.cover).decode("ascii"),
    #     "file": base64.b64encode(db_song.cover).decode("ascii"),
    #     "album_id": db_song.album_id,
    # }
    return {"message": "The song was uploaded successfully"}


async def delete_song(song_id, db: AsyncSession):
    await db.execute(
        delete(_global_models.UserSong).where(
            _global_models.UserSong.song_id == song_id
        )
    )

    # I will add ON DELETE to the models
    await db.execute(
        delete(_global_models.Song).where(_global_models.Song.id == song_id)
    )

    await db.commit()
    return True
