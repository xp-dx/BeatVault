from sqlalchemy.orm import Session

from src.auth import schemas as _user_schemas

from . import schemas as _schemas

from .. import models as _global_models


def upload_song(db: Session, user: _user_schemas.UserId, song: _schemas.SongUpload):
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

    db_user_song = _global_models.UserSong(user_id=user.id, song_id=db_song.id)
    db.add(db_user_song)
    db.commit()

    return {
        "id": db_song.id,
        "title": db_song.title,
        "artist": db_song.artist,
        "genre": db_song.genre,
        "lyrics": db_song.lyrics,
        "album_id": db_song.album_id,
    }
    # return {"message": "The song was uploaded successfully"}
