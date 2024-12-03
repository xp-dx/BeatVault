from fastapi import APIRouter, Depends

from sqlalchemy.orm import Session


from .. import dependencies as _global_dependencies

from src.auth.service import get_user_by_username
from src.auth.schemas import User


router = APIRouter()


@router.get("/users/", tags=["users"])
async def read_users():
    return [{"username": "Rick"}, {"username": "Morty"}]


@router.get("/users/me", tags=["users"])
async def read_user_me():
    return {"username": "fakecurrentuser"}


@router.get("/users/{username}", tags=["users"])
async def read_user(
    username: str, db: Session = Depends(_global_dependencies.get_db)
) -> User:
    user = get_user_by_username(db=db, username=username)
    return user
