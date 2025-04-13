from fastapi import APIRouter, Depends, Form, File, HTTPException, UploadFile

from sqlalchemy.ext.asyncio import AsyncSession

from typing import Annotated

from . import schemas as _schemas, crud as _crud

from .. import dependencies as _global_dependencies, models as _global_models

from src.auth import dependencies as _auth_dependencies, schemas as _auth_schemas

router = APIRouter(tags=["albums"], prefix="/albums")


@router.get("/")
async def read_albums(
    db: AsyncSession = Depends(_global_dependencies.get_async_session),
):
    return await _crud.read_all_albums(db=db)


@router.get("/{album_id}")
async def read_album(
    album_id: int, db: AsyncSession = Depends(_global_dependencies.get_async_session)
):
    return await _crud.read_album_songs(db=db, album_id=album_id)


@router.post("/create-album")
async def create_album(
    current_user: Annotated[
        _auth_schemas.User, Depends(_auth_dependencies.get_current_active_user)
    ],
    cover: Annotated[UploadFile, File()],
    title: Annotated[str, Form()],
    description: Annotated[str, Form()],
    db: AsyncSession = Depends(_global_dependencies.get_async_session),
):
    album = _schemas.Album(
        title=title,
        description=description,
    )
    return await _crud.create_album(db=db, user=current_user, album=album, cover=cover)


@router.delete("/delete-album/{album_id}")
async def delete_album(
    current_user: Annotated[
        _auth_schemas.User, Depends(_auth_dependencies.get_current_active_user)
    ],
    album_id: int,
    db: AsyncSession = Depends(_global_dependencies.get_async_session),
):
    if await _crud.delete_album(current_user=current_user, album_id=album_id, db=db):
        return {"message": "Album deleted"}
    raise HTTPException(status_code=403, detail="Forbidden")
