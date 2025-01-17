from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    Boolean,
    ForeignKey,
    LargeBinary,
    DateTime,
    Numeric,
)

# from sqlalchemy import Column, Integer, String, Text, Boolean, ForeignKey, LargeBinary
from sqlalchemy.orm import relationship

from .database import Base

# Many-to-Many ( artist_album )
# artist_album = Table(
#     "artist_album",
#     Base.metadata,
#     Column("artist_id", Integer(), ForeignKey("users.id")),
#     Column("album_id", Integer(), ForeignKey("albums.id")),
# )


# Many-to-Many ( artist_album )
class UserAlbum(Base):
    __tablename__ = "user_album"

    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    album_id = Column(Integer, ForeignKey("albums.id"), primary_key=True)

    # Опционально: вы можете добавить отношения, если хотите
    # artist = relationship("User", back_populates="albums")
    # album = relationship("Album", back_populates="artists")


# # Many-to-Many ( artist_song )
# artist_song = Table(
#     "artist_song",
#     Base.metadata,
#     Column("artist_id", Integer(), ForeignKey("users.id")),
#     Column("song_id", Integer(), ForeignKey("songs.id")),
# )


# Many-to-Many ( artist_song )
class UserSong(Base):
    __tablename__ = "user_song"

    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    song_id = Column(Integer, ForeignKey("songs.id"), primary_key=True)


# Users
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    avatar = Column(LargeBinary, nullable=True)
    default_avatar = Column(LargeBinary)

    # is_artist = Column(Boolean, default=False)
    is_verified = Column(Boolean, default=False)
    is_superuser = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)

    stripe_account_id = Column(String)


# Albums
class Album(Base):
    __tablename__ = "albums"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(Text, index=True, nullable=True)
    cover = Column(LargeBinary, nullable=True)
    default_cover = Column(LargeBinary)

    songs = relationship("Song")  # One-to-Many ( Many songs )


# Songs
class Song(Base):
    __tablename__ = "songs"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    artist = Column(String, index=True)
    genre = Column(String, index=True)
    lyrics = Column(Text, index=True)
    price = Column(Numeric(10, 2), nullable=False)
    file = Column(LargeBinary)
    cover = Column(LargeBinary, nullable=True)
    default_cover = Column(LargeBinary)

    album_id = Column(
        Integer, ForeignKey("albums.id"), nullable=True
    )  # One-to-Many ( One album )


class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    song_id = Column(Integer, ForeignKey("songs.id"), nullable=False)
    amount = Column(Numeric(10, 2), nullable=False)
    payment_date = Column(DateTime, default=datetime.now())
    status = Column(String(20), nullable=False)

    # user = relationship("User", back_populates="payments")
    # song = relationship("Song", back_populates="payments")
