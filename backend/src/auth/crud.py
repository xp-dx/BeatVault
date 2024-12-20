from sqlalchemy.orm import Session

from . import service as _service, schemas as _schemas

from .. import models as _global_models


def create_user(db: Session, user: _schemas.UserCreate):
    hashed_password = _service.get_password_hash(user.password)
    db_user = _global_models.User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password,
        stripe_account_id=user.stripe_account_id,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user
