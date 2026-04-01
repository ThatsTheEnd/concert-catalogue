from __future__ import annotations

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Orchestra(Base):
    __tablename__ = "orchestras"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(200))

    concerts: Mapped[list[Concert]] = relationship(back_populates="orchestra")

    def __repr__(self) -> str:
        return self.name
