from sqlalchemy.orm import Session

from . import schemas as _schemas

from .. import models as _global_models
from src.auth.dependencies import get_current_active_user
from src.auth import schemas as _user_schemas


def create_album(db: Session, user: _user_schemas.UserId, album: _schemas.Album):
    db_album = _global_models.Album(title=album.title, description=album.description)
    db.add(db_album)
    db.commit()
    db.refresh(db_album)

    # stmt = insert(_global_models.artist_album).values(
    #     artist_id=user.id, album_id=db_album.id
    # )
    # db.execute(stmt)
    # db.commit()

    db_artist_album = _global_models.ArtistAlbum(
        artist_id=user.id, album_id=db_album.id
    )
    db.add(db_artist_album)
    db.commit()

    return db_album
