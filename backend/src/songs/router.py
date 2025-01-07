from fastapi import APIRouter, Depends, Form, File, UploadFile, HTTPException, status
from fastapi.responses import Response, StreamingResponse
from fastapi import APIRouter, Depends, Form, File, UploadFile, HTTPException
from fastapi.responses import Response

from sqlalchemy.exc import NoResultFound
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Session

from io import BytesIO

from typing import Annotated

from src.auth import dependencies as _auth_dependencies, schemas as _auth_schemas

from decimal import Decimal

from random import shuffle

from . import schemas as _schemas, crud as _crud, service as _service

from .. import dependencies as _global_dependencies, models as _global_models

router = APIRouter(tags=["songs"])


@router.get("/songs")
def read_songs(
    db: Session = Depends(_global_dependencies.get_db),
):
    songs = _crud.get_all_songs(db=db)
    shuffle(songs)
    return songs


# @router.get("/download-song/{song_id}")
# async def download_song(
#     current_user: Annotated[
#         _auth_schemas.UserId, Depends(_auth_dependencies.get_current_active_user)
#     ],
#     song_id: int,
#     file: Annotated[UploadFile, File()],
#     title: Annotated[str, Form()],
#     artist: Annotated[str, Form()],
#     genre: Annotated[str, Form()],
#     lyrics: Annotated[str | None, Form()] = None,
#     album_id: Annotated[int | None, Form()] = None,
#     db: Session = Depends(_global_dependencies.get_db),
# ):
#     try:
#         song = (
#             db.query(_global_models.Song)
#             .filter(_global_models.Song.id == song_id)
#             .one()
#         )
#     except NoResultFound:
#         raise HTTPException(status_code=404, detail="Song not found")
#     if not _payment_service.access_to_song(
#         db=db, user_id=current_user.id, song_id=song_id
#     ):
#         raise HTTPException(status_code=403, detail="Access denied. Payment required.")
#     return Response(
#         content=song.file,
#         media_type="audio/mpeg",
#         headers={"Content-Disposition": f"attachment; filename={song.title}.mp3"},
#     )
#     song = _schemas.SongUpload(
#         title=title,
#         artist=artist,
#         genre=genre,
#         lyrics=lyrics,
#         album_id=album_id,
#     )
#     return await _crud.upload_song(db=db, user=current_user, song=song, file=file)


@router.get("/download-song/{song_id}")
async def download_song(
    current_user: Annotated[
        _auth_schemas.UserId, Depends(_auth_dependencies.get_current_active_user)
    ],
    song_id: int,
    db: Session = Depends(_global_dependencies.get_db),
):
    try:
        song = (
            db.query(_global_models.Song)
            .filter(_global_models.Song.id == song_id)
            .one()
        )
        if _service.check_access_to_song(user=current_user, song=song, db=db):
            return Response(
                content=song.file,
                media_type="audio/mpeg",
                headers={
                    "Content-Disposition": f"attachment; filename={song.title}.mp3"
                },
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Access was forbidden"
            )

    except NoResultFound:
        raise HTTPException(status_code=404, detail="Song not found")


@router.get("/purchased-songs")
def get_purchased_songs(
    current_user: Annotated[
        _auth_schemas.User, Depends(_auth_dependencies.get_current_active_user)
    ],
    db: Session = Depends(_global_dependencies.get_db),
):
    return _crud.get_all_purchased_songs(user=current_user, db=db)


@router.get("/uploaded-songs")
def get_purchased_songs(
    current_user: Annotated[
        _auth_schemas.User, Depends(_auth_dependencies.get_current_active_user)
    ],
    db: Session = Depends(_global_dependencies.get_db),
):
    return _crud.get_all_uploaded_songs(user=current_user, db=db)


@router.get("/play-song/{song_id}")
async def play_song(
    song_id: int,
    db: Session = Depends(_global_dependencies.get_db),
):
    try:
        song = (
            db.query(_global_models.Song)
            .filter(_global_models.Song.id == song_id)
            .one()
        )
        file_stream = BytesIO(song.file)

        return StreamingResponse(
            file_stream,
            media_type="audio/mpeg",
        )
    except NoResultFound:
        raise HTTPException(status_code=404, detail="Song not found")


@router.post("/upload-song")
async def upload_song(
    current_user: Annotated[
        _auth_schemas.User, Depends(_auth_dependencies.get_current_active_user)
    ],
    file: Annotated[UploadFile, File()],
    title: Annotated[str, Form()],
    artist: Annotated[str, Form()],
    genre: Annotated[str, Form()],
    price: Annotated[Decimal, Form()],
    lyrics: Annotated[str | None, Form()] = None,
    cover: Annotated[UploadFile | None, File()] = None,
    album_id: Annotated[int | None, Form()] = None,
    db: Session = Depends(_global_dependencies.get_db),
):
    song = _schemas.SongUpload(
        title=title,
        artist=artist,
        genre=genre,
        lyrics=lyrics,
        price=price,
        album_id=album_id,
    )
    return await _crud.upload_song(
        db=db, user=current_user, song=song, file=file, cover=cover
    )


# @router.patch("/update-song/{song_id}")
# async def update_song(
#     current_user: Annotated[
#         _auth_schemas.User, Depends(_auth_dependencies.get_current_active_user)
#     ],
#     # file: Annotated[UploadFile, File()],
#     title: Annotated[str, Form()],
#     artist: Annotated[str, Form()],
#     genre: Annotated[str, Form()],
#     price: Annotated[Decimal, Form()],
#     lyrics: Annotated[str | None, Form()] = None,
#     album_id: Annotated[int | None, Form()] = None,
#     db: Session = Depends(_global_dependencies.get_db),
# ):
#     song =
#     return await _crud.
