# def upload_mp3_file()
from sqlalchemy.orm import Session

from src.auth import schemas as _auth_schemas

from .. import models as _global_models


def check_owner_of_song(user, song_id, db: Session):
    if (
        db.query(_global_models.UserSong)
        .filter(
            _global_models.UserSong.user_id == user.id,
            _global_models.UserSong.song_id == song_id,
        )
        .first()
    ):
        return True
    return False


def check_access_to_song(user: _auth_schemas.UserId, song, db: Session):
    # user_song = db.query(_global_models.UserSong)
    payments = db.query(_global_models.Payment)
    if (
        check_owner_of_song(user=user, song_id=song.id, db=db)
        or payments.filter(
            _global_models.Payment.user_id == user.id,
            _global_models.Payment.song_id == song.id,
            _global_models.Payment.status == "successfully",
        ).first()
    ):
        return True


# def shuffle_songs()
