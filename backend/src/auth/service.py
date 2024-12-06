from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

import jwt

import json

from . import config as _config, dependencies as _dependencies

from .. import models as _global_models


def get_password_hash(password):
    return _dependencies.pwd_context.hash(password)


def verify_password(plain_password, hashed_password):
    return _dependencies.pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=5)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, _config.SECRET_KEY, algorithm=_config.ALGORITHM)
    return encoded_jwt


def authenticate_user(db: Session, username: str, password: str):
    user = get_user_by_username(db, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


def get_user_by_username(db: Session, username: str):
    return (
        db.query(_global_models.User)
        .filter(_global_models.User.username == username)
        .first()
    )


def get_all_users(db: Session):
    users = db.query(_global_models.User.id, _global_models.User.username).all()
    users_json = []
    for user in users:
        users_json.append({"id": user[0], "username": user[1]})
    return json.loads(json.dumps(users_json, default=str))
