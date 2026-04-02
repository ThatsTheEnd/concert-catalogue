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


def update_venue(session: Session, venue_id: int, **kwargs) -> Venue | None:
    obj = session.get(Venue, venue_id)
    if obj is None:
        return None
    for k, v in kwargs.items():
        setattr(obj, k, v)
    session.commit()
    logger.info("Updated venue id={} fields={}", venue_id, list(kwargs.keys()))
    return obj


def delete_venue(session: Session, venue_id: int) -> None:
    obj = session.get(Venue, venue_id)
    if obj is not None:
        session.delete(obj)
        session.commit()
        logger.info("Deleted venue id={}", venue_id)


def list_venues(session: Session) -> list[Venue]:
    return list(session.scalars(select(Venue).order_by(Venue.name)))
