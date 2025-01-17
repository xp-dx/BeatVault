from fastapi import HTTPException, UploadFile

from sqlalchemy import desc
from sqlalchemy.orm import Session

from src.auth import schemas as _user_schemas

import json

import base64

from . import schemas as _schemas, constants as _constants

from .. import models as _global_models


def get_all_songs(db: Session):
    songs = db.query(_global_models.Song).all()
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
    return json.loads(json.dumps(songs_json, default=str))


def get_all_uploaded_songs(user, db: Session):
    try:
        users_songs = (
            db.query(_global_models.UserSong)
            .filter(_global_models.UserSong.user_id == user.id)
            .order_by(desc(_global_models.UserSong.song_id))
            .all()
        )

        songs_json = []
        for user_song in users_songs:
            song = (
                db.query(_global_models.Song)
                .filter(_global_models.Song.id == user_song.song_id)
                .first()
            )
            songs_json.append(
                {
                    "id": song.id,
                    "title": song.title,
                    "artist": song.artist,
                    "genre": song.genre,
                    "price": song.price,
                }
            )
    except:
        return {"message": "You don't uploaded any songs"}
    if not songs_json:
        return {"message": "You don't uploaded any songs"}

    return json.loads(json.dumps(songs_json, default=str))


def get_all_purchased_songs(user, db: Session):
    payments = (
        db.query(_global_models.Payment)
        .filter(
            _global_models.Payment.user_id == user.id,
            _global_models.Payment.status == "successfully",
        )
        .order_by(desc(_global_models.Payment.payment_date))
        .all()
    )
    songs_json = []
    for payment in payments:
        song = (
            db.query(_global_models.Song)
            .filter(_global_models.Song.id == payment.song_id)
            .first()
        )
        songs_json.append(
            {
                "id": song.id,
                "title": song.title,
                "artist": song.artist,
                "genre": song.genre,
            }
        )
    if not songs_json:
        return {"message": "You don't purchased any songs"}

    return json.loads(json.dumps(songs_json, default=str))


async def upload_song(
    db: Session,
    user: _user_schemas.UserId,
    song: _schemas.SongUpload,
    file: UploadFile,
    cover: UploadFile | None,
):
    # try:
    file_data = await file.read()
    cover_data = await cover.read() if cover else _constants.DEFAULT_COVER
    # if cover:
    #     cover_data = await cover.read()
    # else:
    #     cover_data = _constants.DEFAULT_COVER
    # except UnicodeDecodeError:
    #     raise HTTPException(status_code=400, detail="Invalid file format")

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
    db.commit()
    db.refresh(db_song)

    db_user_song = _global_models.UserSong(user_id=user.id, song_id=db_song.id)
    db.add(db_user_song)
    db.commit()

    return {
        "id": db_song.id,
        "title": db_song.title,
        "artist": db_song.artist,
        "genre": db_song.genre,
        "lyrics": db_song.lyrics,
        "price": db_song.price,
        # "cover": str(db_song.cover),
        "cover": base64.b64encode(db_song.cover).decode("ascii"),
        "album_id": db_song.album_id,
    }


def update_song(song_id, updated_song, db: Session):
    db_updated_song = _global_models.Song(**updated_song)
    db.add(db_updated_song)
    db.commit()
    db.refresh(db_updated_song)
    return db_updated_song
    # return {"message": "The song was uploaded successfully"}
