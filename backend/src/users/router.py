import base64

from fastapi import APIRouter, Depends

from sqlalchemy.ext.asyncio import AsyncSession

from typing import Annotated

from src.auth.service import get_user_by_username, get_all_users
from src.auth.schemas import UserMe, User
from src.auth.dependencies import get_current_active_user

from . import crud as _crud
from .. import dependencies as _global_dependencies


router = APIRouter(tags=["users"], prefix="/users")


@router.get("/")
async def read_users(
    db: AsyncSession = Depends(_global_dependencies.get_async_session),
):
    return await get_all_users(db=db)


@router.get("/me")
async def read_user_me(
    current_user: Annotated[UserMe, Depends(get_current_active_user)],
):
    return {
        "username": current_user.username,
        "email": current_user.email,
        "avatar": base64.b64encode(
            current_user.avatar if current_user.avatar else current_user.default_avatar
        ),
    }


@router.get("/{username}")
async def read_user(
    username: str, db: AsyncSession = Depends(_global_dependencies.get_async_session)
):
    user = await get_user_by_username(db=db, username=username)
    return {
        "username": user.username,
        "email": user.email,
        "avatar": base64.b64encode(user.avatar if user.avatar else user.default_avatar),
    }


@router.delete("/delete-my-account")
async def delete_user(
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: AsyncSession = Depends(_global_dependencies.get_async_session),
):
    await _crud.delete_user(current_user=current_user, db=db)
    return {"message": "User deleted"}


@router.patch("/change-my-username")
async def update_username(
    current_user: Annotated[User, Depends(get_current_active_user)],
    new_username: str,
    db: AsyncSession = Depends(_global_dependencies.get_async_session),
):

    return {
        "message": f"Your new username: {await _crud.update_username(
            current_user=current_user, new_username=new_username, db=db
        )}"
    }
