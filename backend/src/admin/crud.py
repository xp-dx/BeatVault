from pydantic import EmailStr
from sqlalchemy.orm import Session
from src.auth import dependencies as _auth_dependencies

from src.auth import schemas as _auth_schemas

from .. import models as _global_models


def delete_user(user_email: EmailStr, db: Session):
    user = (
        db.query(_global_models.User)
        .filter(_global_models.User.email == user_email)
        .first()
    )
    songs_ids = (
        d.song_id
        for d in db.query(_global_models.UserSong)
        .filter(_global_models.UserSong.user_id == user.id)
        .all()
    )
    # return songs_id
    db.query(_global_models.UserSong).filter(
        _global_models.UserSong.user_id == user.id
    ).delete()

    db.query(_global_models.Song).filter(_global_models.Song.id.in_(songs_ids)).delete()

    db.query(_global_models.User).filter(
        _global_models.User.email == user_email
    ).delete()
    db.commit()
    return True


def delete_song(song_id: int, db: Session):
    db.query(_global_models.UserSong).filter(
        _global_models.UserSong.song_id == song_id
    ).delete()
    db.query(_global_models.Song).filter(_global_models.Song.id == song_id).delete()
    db.commit()
    return True


def check_role(current_user: _auth_schemas.UserEmail, db: Session):
    user = (
        db.query(_global_models.User)
        .filter(_global_models.User.email == current_user.email)
        .first()
    )
    if user.is_superuser:
        print("True")
        return True
    print("False")

    return False


def deactivate_user(user_email: EmailStr, db: Session):
    db.query(_global_models.User).filter(
        _global_models.User.email == user_email
    ).update({"is_active": False})
    db.commit()
    return True


def activate_user(user_email: EmailStr, db: Session):
    db.query(_global_models.User).filter(
        _global_models.User.email == user_email
    ).update({"is_active": True})
    db.commit()
    return True
