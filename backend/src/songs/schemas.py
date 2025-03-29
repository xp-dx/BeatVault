from pydantic import BaseModel
from decimal import Decimal


class SongID(BaseModel):
    id: int


class SongBase(BaseModel):
    title: str
    artist: str
    price: Decimal


class SongUpload(SongBase):
    genre: str
    lyrics: str
    album_id: int | None = None


class SongUpdate(BaseModel):
    title: str | None
    artist: str | None
    price: Decimal | None
    genre: str | None
    lyrics: str | None
    album_id: int | None
    file: bytes | None
    cover: bytes | None
