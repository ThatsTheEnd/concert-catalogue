from __future__ import annotations

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Piece(Base):
    __tablename__ = "pieces"

    id: Mapped[int] = mapped_column(primary_key=True)
    composer_id: Mapped[int] = mapped_column(ForeignKey("composers.id"))
    title: Mapped[str] = mapped_column(String(300))
    opus_number: Mapped[str] = mapped_column(String(50), default="")
    key: Mapped[str] = mapped_column(String(50), default="")

    composer: Mapped[Composer] = relationship(back_populates="pieces")
    concert_links: Mapped[list[ConcertPiece]] = relationship(back_populates="piece")

    @property
    def display_name(self) -> str:
        """title, key, opus — natural reading order."""
        parts = [self.title]
        if self.key:
            parts.append(self.key)
        if self.opus_number:
            parts.append(self.opus_number)
        return ", ".join(parts)

    def __repr__(self) -> str:
        return f"{self.composer.full_name} — {self.display_name}"
