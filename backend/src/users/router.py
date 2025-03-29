import base64


from fastapi import APIRouter, Depends

from sqlalchemy.orm import Session

from typing import Annotated

from . import crud as _crud
from .. import dependencies as _global_dependencies, models as _global_models

from src.auth.service import get_user_by_username, get_all_users
from src.auth.schemas import UserMe, User
from src.auth.dependencies import get_current_active_user

router = APIRouter(tags=["users"], prefix="/users")


@router.get("/")
async def read_users(db: Session = Depends(_global_dependencies.get_db)):
    return get_all_users(db=db)


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
    username: str, db: Session = Depends(_global_dependencies.get_db)
) -> User:
    user = get_user_by_username(db=db, username=username)
    return user


@router.delete("/delete-my-account")
def delete_user(
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Session = Depends(_global_dependencies.get_db),
):
    _crud.delete_user(current_user=current_user, db=db)
    return {"message": "User deleted"}


@router.patch("/change-my-username")
def update_username(
    current_user: Annotated[User, Depends(get_current_active_user)],
    new_username: str,
    db: Session = Depends(_global_dependencies.get_db),
):

    return {
        "message": f"Your new username: {_crud.update_username(
            current_user=current_user, new_username=new_username, db=db
        )}"
    }
