from pydantic import BaseModel


class SongID(BaseModel):
    id: int


class SongBase(BaseModel):
    title: str
    artist: str


class SongUpload(SongBase):
    genre: str
    lyrics: str
    album_id: int | None = None
