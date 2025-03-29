from fastapi import UploadFile

from sqlalchemy.orm import Session

import json

import base64

from src.auth import schemas as _user_schemas

from . import schemas as _schemas, constants as _constants, service as _service

from .. import models as _global_models


def read_all_albums(db: Session):
    db_albums = db.query(_global_models.Album).all()
    albums_json = []
    for album in db_albums:
        albums_json.append(
            {"id": album.id, "title": album.title, "description": album.description}
        )
    return json.loads(json.dumps(albums_json, default=str))


# def read_album(db: Session, album_id: int):
#     db_album = (
#         db.query(_global_models.Album)
#         .filter(_global_models.Album.id == album_id)
#         .first()
#     )
#     return db_album


def read_album_songs(db: Session, album_id: int):
    db_album = (
        db.query(_global_models.Album)
        .filter(_global_models.Album.id == album_id)
        .first()
    )

    db_album_songs = (
        db.query(_global_models.Song)
        .filter(_global_models.Song.album_id == album_id)
        .all()
    )
    album_songs_json = {
        "album": {
            "id": db_album.id,
            "title": db_album.title,
            "description": db_album.description,
        },
        "songs": [],
    }

    for album_song in db_album_songs:
        album_songs_json["songs"].append(
            {
                "id": album_song.id,
                "title": album_song.title,
                "artist": album_song.artist,
                "genre": album_song.genre,
                "price": album_song.price,
            }
        )
    return json.loads(json.dumps(album_songs_json, default=str))


async def create_album(
    db: Session,
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
    db.commit()
    db.refresh(db_album)

    # stmt = insert(_global_models.artist_album).values(
    #     artist_id=user.id, album_id=db_album.id
    # )
    # db.execute(stmt)
    # db.commit()

    db_user_album = _global_models.UserAlbum(user_id=user.id, album_id=db_album.id)
    db.add(db_user_album)
    db.commit()

    return {
        "id": db_album.id,
        "title": db_album.title,
        "description": db_album.description,
        "cover": base64.b64encode(db_album.cover).decode("ascii"),
    }


def delete_album(current_user: _user_schemas.UserId, album_id: int, db: Session):
    if _service.check_owner_of_album(user_id=current_user.id, album_id=album_id, db=db):
        db.query(_global_models.UserAlbum).filter(
            _global_models.UserAlbum.album_id == album_id
        ).delete()
        db.query(_global_models.Album).filter(
            _global_models.Album.id == album_id
        ).delete()
        db.commit()
        return True
    return False
