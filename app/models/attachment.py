from __future__ import annotations

from enum import StrEnum

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class AttachmentType(StrEnum):
    TICKET = "ticket"
    PROGRAM = "program"
    REVIEW = "review"


class Attachment(Base):
    __tablename__ = "attachments"

    id: Mapped[int] = mapped_column(primary_key=True)
    concert_id: Mapped[int] = mapped_column(ForeignKey("concerts.id"))
    type: Mapped[str] = mapped_column(String(20))  # AttachmentType value
    file_path: Mapped[str] = mapped_column(String(500))
    original_filename: Mapped[str] = mapped_column(String(300))
    description: Mapped[str] = mapped_column(Text, default="")

    concert: Mapped[Concert] = relationship(back_populates="attachments")
