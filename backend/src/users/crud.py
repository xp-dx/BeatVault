import base64


from fastapi import APIRouter, Depends

from sqlalchemy.orm import Session

from typing import Annotated

from .. import dependencies as _global_dependencies, models as _global_models

from src.auth.service import get_user_by_username, get_all_users
from src.auth import schemas as _auth_schemas
from src.auth.dependencies import get_current_active_user


def delete_user(current_user: _auth_schemas.User, db: Session):
    db.query(_global_models.User).filter(
        _global_models.User.id == current_user.id
    ).delete()
    db.commit()
    return True


def update_username(current_user: _auth_schemas.User, new_username: str, db: Session):
    user = (
        db.query(_global_models.User)
        .filter(_global_models.User.id == current_user.id)
        .first()
    )
    user.username = new_username
    db.commit()
    return user.username
