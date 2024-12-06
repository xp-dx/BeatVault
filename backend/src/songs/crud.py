from sqlalchemy.orm import Session

from . import schemas as _schemas

from .. import models as _global_models


def upload_song(db: Session, song: _schemas.SongUpload):
    db_song = _global_models.Song(
        title=song.title,
        artist=song.artist,
        genre=song.genre,
        lyrics=song.lyrics,
        album_id=song.album_id,
    )
    db.add(db_song)
    db.commit()
    db.refresh(db_song)
    return db_song
