from loguru import logger
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Venue


def create_venue(session: Session, name: str, city: str, country: str = "") -> Venue:
    obj = Venue(name=name, city=city, country=country)
    session.add(obj)
    session.commit()
    logger.info("Created venue: {!r}, {}", name, city)
    return obj


def list_venues(session: Session) -> list[Venue]:
    return list(session.scalars(select(Venue).order_by(Venue.name)))
