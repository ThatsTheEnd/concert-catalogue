from __future__ import annotations

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Conductor(Base):
    __tablename__ = "conductors"

    id: Mapped[int] = mapped_column(primary_key=True)
    first_name: Mapped[str] = mapped_column(String(100), default="")
    last_name: Mapped[str] = mapped_column(String(100))

    concerts: Mapped[list[Concert]] = relationship(back_populates="conductor")

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}".strip()

    def __repr__(self) -> str:
        return self.full_name


class Artist(Base):
    __tablename__ = "artists"

    id: Mapped[int] = mapped_column(primary_key=True)
    first_name: Mapped[str] = mapped_column(String(100), default="")
    last_name: Mapped[str] = mapped_column(String(100))
    instrument: Mapped[str] = mapped_column(String(100), default="")

    concert_links: Mapped[list[ConcertArtist]] = relationship(back_populates="artist")

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}".strip()

    def __repr__(self) -> str:
        return self.full_name


class Composer(Base):
    __tablename__ = "composers"

    id: Mapped[int] = mapped_column(primary_key=True)
    first_name: Mapped[str] = mapped_column(String(100), default="")
    last_name: Mapped[str] = mapped_column(String(100))
    birth_year: Mapped[int | None] = mapped_column(default=None)
    death_year: Mapped[int | None] = mapped_column(default=None)
    nationality: Mapped[str] = mapped_column(String(100), default="")

    pieces: Mapped[list[Piece]] = relationship(back_populates="composer")

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}".strip()

    def __repr__(self) -> str:
        return self.full_name
