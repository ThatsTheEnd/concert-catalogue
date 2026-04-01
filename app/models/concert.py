from __future__ import annotations

from datetime import date, datetime

from sqlalchemy import Date, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class ConcertArtist(Base):
    __tablename__ = "concert_artists"

    concert_id: Mapped[int] = mapped_column(ForeignKey("concerts.id"), primary_key=True)
    artist_id: Mapped[int] = mapped_column(ForeignKey("artists.id"), primary_key=True)
    role: Mapped[str] = mapped_column(String(100), default="")

    concert: Mapped[Concert] = relationship(back_populates="artist_links")
    artist: Mapped[Artist] = relationship(back_populates="concert_links")


class ConcertPiece(Base):
    __tablename__ = "concert_pieces"

    concert_id: Mapped[int] = mapped_column(ForeignKey("concerts.id"), primary_key=True)
    piece_id: Mapped[int] = mapped_column(ForeignKey("pieces.id"), primary_key=True)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    notes: Mapped[str] = mapped_column(Text, default="")

    concert: Mapped[Concert] = relationship(back_populates="piece_links")
    piece: Mapped[Piece] = relationship(back_populates="concert_links")


class Concert(Base):
    __tablename__ = "concerts"

    id: Mapped[int] = mapped_column(primary_key=True)
    date: Mapped[date] = mapped_column(Date)
    title: Mapped[str] = mapped_column(String(300))
    orchestra: Mapped[str] = mapped_column(String(200), default="")
    venue_id: Mapped[int | None] = mapped_column(ForeignKey("venues.id"), default=None)
    conductor_id: Mapped[int | None] = mapped_column(ForeignKey("conductors.id"), default=None)
    notes: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    venue: Mapped[Venue | None] = relationship(back_populates="concerts")
    conductor: Mapped[Conductor | None] = relationship(back_populates="concerts")
    artist_links: Mapped[list[ConcertArtist]] = relationship(
        back_populates="concert", cascade="all, delete-orphan"
    )
    piece_links: Mapped[list[ConcertPiece]] = relationship(
        back_populates="concert",
        cascade="all, delete-orphan",
        order_by="ConcertPiece.sort_order",
    )
    attachments: Mapped[list[Attachment]] = relationship(
        back_populates="concert", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"{self.date} — {self.title}"
