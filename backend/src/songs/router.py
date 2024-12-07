from fastapi import APIRouter, Depends, Form, File, UploadFile, HTTPException
from fastapi.responses import Response

from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Session

from typing import Annotated

from src.auth import dependencies as _auth_dependencies, schemas as _auth_schemas

from . import schemas as _schemas, crud as _crud

from .. import dependencies as _global_dependencies, models as _global_models

router = APIRouter(tags=["songs"])


@router.post("/upload-song")
async def upload_song(
    current_user: Annotated[
        _auth_schemas.User, Depends(_auth_dependencies.get_current_active_user)
    ],
    file: Annotated[UploadFile, File()],
    title: Annotated[str, Form()],
    artist: Annotated[str, Form()],
    genre: Annotated[str, Form()],
    lyrics: Annotated[str | None, Form()] = None,
    album_id: Annotated[int | None, Form()] = None,
    db: Session = Depends(_global_dependencies.get_db),
):
    song = _schemas.SongUpload(
        title=title,
        artist=artist,
        genre=genre,
        lyrics=lyrics,
        album_id=album_id,
    )
    return await _crud.upload_song(db=db, user=current_user, song=song, file=file)


@router.get("/download-song/{song_id}")
async def download_song(
    song_id: int, db: Session = Depends(_global_dependencies.get_db)
):
    try:
        song = (
            db.query(_global_models.Song)
            .filter(_global_models.Song.id == song_id)
            .one()
        )
    except NoResultFound:
        raise HTTPException(status_code=404, detail="Song not found")

    return Response(
        content=song.file,
        media_type="audio/mpeg",
        headers={"Content-Disposition": f"attachment; filename={song.title}.mp3"},
    )
