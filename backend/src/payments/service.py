from sqlalchemy.orm import Session

from src.songs import schemas as _songs_schemas
from src.auth import dependencies as _auth_dependencies, schemas as _auth_schemas

from .. import models as _global_models


def access_to_song(
    db: Session,
    user_id: int,
    song_id: int,
):
    return (
        db.query(_global_models.Payment)
        .filter(
            _global_models.Payment.song_id == song_id,
            _global_models.Payment.user_id == user_id,
            _global_models.Payment.status == "successfully",
        )
        .first()
    )
