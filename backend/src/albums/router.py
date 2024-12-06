from fastapi import APIRouter, Depends, Form

from sqlalchemy.orm import Session

from typing import Annotated

from . import schemas as _schemas, crud as _crud

from .. import dependencies as _global_dependencies

router = APIRouter(tags=["albums"])


@router.post("/create-album")
def create_album(
    album: Annotated[_schemas.Album, Form()],
    db: Session = Depends(_global_dependencies.get_db),
):
    return _crud.create_album(db=db, album=album)
