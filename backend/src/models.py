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
    func,
)
from sqlalchemy.orm import relationship
from .database import Base


# Many-to-Many ( artist_album )
class UserAlbum(Base):
    __tablename__ = "user_album"

    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    album_id = Column(
        Integer, ForeignKey("albums.id", ondelete="CASCADE"), primary_key=True
    )


# Many-to-Many ( artist_song )
class UserSong(Base):
    __tablename__ = "user_song"

    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    song_id = Column(
        Integer, ForeignKey("songs.id", ondelete="CASCADE"), primary_key=True
    )


# Users
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    avatar = Column(LargeBinary, nullable=True)
    default_avatar = Column(LargeBinary)
    is_verified = Column(Boolean, default=False)
    is_superuser = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    stripe_account_id = Column(String)

    # Relationships
    payments = relationship(
        "Payment", back_populates="user", cascade="all, delete-orphan"
    )
    albums = relationship("Album", secondary="user_album", backref="users")
    songs = relationship("Song", secondary="user_song", backref="users")


# Albums
class Album(Base):
    __tablename__ = "albums"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(Text, index=True, nullable=True)
    cover = Column(LargeBinary, nullable=True)
    default_cover = Column(LargeBinary)

    songs = relationship("Song", back_populates="album", cascade="all, delete-orphan")


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
        Integer, ForeignKey("albums.id", ondelete="SET NULL"), nullable=True
    )

    album = relationship("Album", back_populates="songs")
    payments = relationship(
        "Payment", back_populates="song", cascade="all, delete-orphan"
    )


# Payments
class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    song_id = Column(
        Integer, ForeignKey("songs.id", ondelete="CASCADE"), nullable=False
    )
    amount = Column(Numeric(10, 2), nullable=False)
    payment_date = Column(DateTime, server_default=func.now())
    status = Column(String(20), nullable=False)

    user = relationship("User", back_populates="payments")
    song = relationship("Song", back_populates="payments")
