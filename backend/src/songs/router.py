from fastapi import APIRouter, Depends, Form

from sqlalchemy.orm import Session

from typing import Annotated

from src.auth import dependencies as _auth_dependencies, schemas as _auth_schemas

from . import schemas as _schemas, crud as _crud

from .. import dependencies as _global_dependencies

router = APIRouter(tags=["songs"])


@router.post("/upload-song")
def upload_song(
    current_user: Annotated[
        _auth_schemas.User, Depends(_auth_dependencies.get_current_active_user)
    ],
    song: Annotated[_schemas.SongUpload, Form()],
    db: Session = Depends(_global_dependencies.get_db),
):
    return _crud.upload_song(db=db, user=current_user, song=song)
