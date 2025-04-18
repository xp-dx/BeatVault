from fastapi import APIRouter, Depends, Form, HTTPException
from pydantic import EmailStr
from sqlalchemy.ext.asyncio import AsyncSession

from typing import Annotated

from src.auth import dependencies as _auth_dependencies
from src.auth import schemas as _auth_schemas

from . import crud as _crud
from .. import dependencies as _global_dependencies


router = APIRouter(tags=["admin"], prefix="/admin")


@router.delete("/delete/user")
async def admin_delete_user(
    current_user: Annotated[
        _auth_schemas.UserEmail, Depends(_auth_dependencies.get_current_active_user)
    ],
    email_user: Annotated[EmailStr, Form()],
    db: AsyncSession = Depends(_global_dependencies.get_async_session),
):
    if not await _crud.check_role(current_user=current_user, db=db):
        raise HTTPException(status_code=403, detail="Forbidden")
    if await _crud.delete_user(user_email=email_user, db=db):
        return {"message": f"User {email_user} deleted"}


@router.delete("/delete/song")
async def admin_delete_song(
    current_user: Annotated[
        _auth_schemas.UserEmail, Depends(_auth_dependencies.get_current_active_user)
    ],
    song_id: Annotated[int, Form()],
    db: AsyncSession = Depends(_global_dependencies.get_async_session),
):
    if not await _crud.check_role(current_user=current_user, db=db):
        raise HTTPException(status_code=403, detail="Forbidden")
    if await _crud.delete_song(song_id=song_id, db=db):
        return {"message": f"Song {song_id} deleted"}


@router.patch("/deactivate-user")
async def admin_deactivate_user(
    current_user: Annotated[
        _auth_schemas.UserEmail, Depends(_auth_dependencies.get_current_active_user)
    ],
    email_user: Annotated[EmailStr, Form()],
    db: AsyncSession = Depends(_global_dependencies.get_async_session),
):
    if not await _crud.check_role(current_user=current_user, db=db):
        raise HTTPException(status_code=403, detail="Forbidden")
    if await _crud.deactivate_user(user_email=email_user, db=db):
        return {"message": f"User {email_user} deactivated"}


@router.patch("/activate-user")
async def admin_activate_user(
    current_user: Annotated[
        _auth_schemas.UserEmail, Depends(_auth_dependencies.get_current_active_user)
    ],
    email_user: Annotated[EmailStr, Form()],
    db: AsyncSession = Depends(_global_dependencies.get_async_session),
):
    if not await _crud.check_role(current_user=current_user, db=db):
        raise HTTPException(status_code=403, detail="Forbidden")
    if await _crud.activate_user(user_email=email_user, db=db):
        return {"message": f"User {email_user} deactivated"}
