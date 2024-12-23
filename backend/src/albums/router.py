from fastapi import APIRouter, Depends, Form

from sqlalchemy.orm import Session

from typing import Annotated

from . import schemas as _schemas, crud as _crud

from .. import dependencies as _global_dependencies, models as _global_models

from src.auth import dependencies as _auth_dependencies, schemas as _auth_schemas

router = APIRouter(tags=["albums"])


@router.get("/albums")
def read_albums(db: Session = Depends(_global_dependencies.get_db)):
    return _crud.read_all_albums(db=db)


# @router.get("/album/{album_id}")
# def read_album(album_id: int, db: Session = Depends(_global_dependencies.get_db)):
#     return _crud.read_album(db=db, album_id=album_id)


@router.get("/album/{album_id}")
def read_album(album_id: int, db: Session = Depends(_global_dependencies.get_db)):
    return _crud.read_album_songs(db=db, album_id=album_id)


@router.post("/create-album")
def create_album(
    current_user: Annotated[
        _auth_schemas.User, Depends(_auth_dependencies.get_current_active_user)
    ],
    album: Annotated[_schemas.Album, Form()],
    db: Session = Depends(_global_dependencies.get_db),
):
    return _crud.create_album(db=db, user=current_user, album=album)
