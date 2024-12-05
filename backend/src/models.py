from sqlalchemy import Column, Integer, String, Text, Boolean, ForeignKey, Table
from sqlalchemy.orm import relationship

from .database import Base

# Many-to-Many ( artist_album )
artist_album = Table(
    "artist_album",
    Base.metadata,
    Column("artist_id", Integer(), ForeignKey("users.id")),
    Column("album_id", Integer(), ForeignKey("albums.id")),
)

# Many-to-Many ( artist_song )
artist_song = Table(
    "artist_song",
    Base.metadata,
    Column("artist_id", Integer(), ForeignKey("users.id")),
    Column("song_id", Integer(), ForeignKey("songs.id")),
)


# Users
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)

    # is_artist = Column(Boolean, default=False)
    is_verified = Column(Boolean, default=False)
    is_superuser = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)


# Albums
class Album(Base):
    __tablename__ = "albums"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(Text, index=True)
    songs = relationship("Song")  # One-to-Many ( Many songs )


# Songs
class Song(Base):
    __tablename__ = "songs"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    artist = Column(String, index=True)
    album = Column(String, index=True)
    genre = Column(String, index=True)
    year = Column(Integer, index=True)
    lyrics = Column(Text, index=True)
    album_id = Column(Integer, ForeignKey("albums.id"))  # One-to-Many ( One album )
