from datetime import datetime, timedelta, timezone

from fastapi import HTTPException
from jose import JWTError
from sqlalchemy.orm import Session

from celery import Celery

import jwt

import json

import redis

import aiosmtplib

from . import config as _config, dependencies as _dependencies, crud as _crud

from .. import models as _global_models, config as _global_config


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


def get_user_by_email(db: Session, email: str):
    return (
        db.query(_global_models.User).filter(_global_models.User.email == email).first()
    )


def get_user_by_id(db: Session, user_id: int):
    return (
        db.query(_global_models.User).filter(_global_models.User.id == user_id).first()
    )


def get_all_users(db: Session):
    users = db.query(_global_models.User.id, _global_models.User.username).all()
    return [{"id": user[0], "username": user[1]} for user in users]
    # users_json = []
    # for user in users:
    #     users_json.append({"id": user[0], "username": user[1]})
    # return json.loads(json.dumps(users_json, default=str))


async def confirm_email(token: str, db: Session):
    payload = jwt.decode(
        token, _global_config.JWT_SECRET_KEY, algorithms=[_global_config.JWT_ALGORITHM]
    )
    email: str = payload.get("sub")
    if email is None:
        raise HTTPException(status_code=400, detail="Invalid token")
    _crud.update_verified_status(db, email)
    return {"message": "Email confirmed", "email": email}


def is_verified(email: str, db: Session):
    user = (
        db.query(_global_models.User).filter(_global_models.User.email == email).first()
    )
    if user.is_verified:
        return True
    return False
