from fastapi import APIRouter, Depends, Form, HTTPException
from pydantic import EmailStr
from sqlalchemy.orm import Session

from typing import Annotated

from src.auth import dependencies as _auth_dependencies
from src.auth import schemas as _auth_schemas

from . import crud as _crud
from .. import dependencies as _global_dependencies


router = APIRouter(tags=["admin"])


@router.delete("/admin/delete/user")
def admin_delete_user(
    current_user: Annotated[
        _auth_schemas.UserEmail, Depends(_auth_dependencies.get_current_active_user)
    ],
    email_user: Annotated[EmailStr, Form()],
    db: Session = Depends(_global_dependencies.get_db),
):
    # db.query(_auth_schemas.UserEmail).filter(
    #     _auth_schemas.UserEmail.email == email_user
    # )
    if not _crud.check_role(current_user=current_user, db=db):
        raise HTTPException(status_code=403, detail="Forbidden")
    if _crud.delete_user(user_email=email_user, db=db):
        return {"message": f"User {email_user} deleted"}
