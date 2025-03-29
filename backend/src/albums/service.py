from sqlalchemy.orm import Session

from .. import models as _global_models


def check_owner_of_album(user_id: int, album_id: int, db: Session):
    if (
        db.query(_global_models.UserAlbum)
        .filter(
            _global_models.UserAlbum.user_id == user_id,
            _global_models.UserAlbum.album_id == album_id,
        )
        .first()
    ):
        return True
    return False
