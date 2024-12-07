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
