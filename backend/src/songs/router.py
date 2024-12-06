from fastapi import APIRouter, Depends, Form

from sqlalchemy.orm import Session

from typing import Annotated

from . import schemas as _schemas, crud as _crud

from .. import dependencies as _global_dependencies

router = APIRouter(tags=["songs"])


@router.post("/upload-song")
def upload_song(
    song: Annotated[_schemas.SongUpload, Form()],
    db: Session = Depends(_global_dependencies.get_db),
):
    return _crud.upload_song(db=db, song=song)
