# def upload_mp3_file()
from sqlalchemy.orm import Session

from random import shuffle

from .. import models as _global_models


def check_access_to_song(user, song, db: Session):
    user_song = db.query(_global_models.UserSong)
    payments = db.query(_global_models.Payment)
    if (
        user_song.filter(
            _global_models.UserSong.user_id == user.id,
            _global_models.UserSong.song_id == song.id,
        ).first()
        or payments.filter(
            _global_models.Payment.user_id == user.id,
            _global_models.Payment.song_id == song.id,
            _global_models.Payment.status == "successfully",
        ).first()
    ):
        return True


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


# def shuffle_songs()
