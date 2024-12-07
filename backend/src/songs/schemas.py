from pydantic import BaseModel


class SongBase(BaseModel):
    title: str
    artist: str


class SongUpload(SongBase):
    genre: str
    lyrics: str
    album_id: int | None = None
