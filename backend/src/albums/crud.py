from sqlalchemy.orm import Session

from . import schemas as _schemas

from .. import models as _global_models


def create_album(db: Session, album: _schemas.Album):
    db_album = _global_models.Album(title=album.title, description=album.description)
    db.add(db_album)
    db.commit()
    db.refresh(db_album)
    return db_album
