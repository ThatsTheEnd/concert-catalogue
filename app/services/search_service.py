from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.models import (
    Artist,
    Composer,
    Conductor,
    Orchestra,
    Venue,
)
from app.services.concert_service import list_concerts


def search_all(session: Session, query: str) -> dict:
    p = f"%{query}%"

    concerts = list_concerts(session, search=query, limit=200)

    conductors = list(session.scalars(
        select(Conductor).where(
            or_(Conductor.first_name.ilike(p), Conductor.last_name.ilike(p))
        ).order_by(Conductor.last_name)
    ))

    composers = list(session.scalars(
        select(Composer).where(
            or_(Composer.first_name.ilike(p), Composer.last_name.ilike(p))
        ).order_by(Composer.last_name)
    ))

    artists = list(session.scalars(
        select(Artist).where(
            or_(Artist.first_name.ilike(p), Artist.last_name.ilike(p))
        ).order_by(Artist.last_name)
    ))

    venues = list(session.scalars(
        select(Venue).where(
            or_(Venue.name.ilike(p), Venue.city.ilike(p))
        ).order_by(Venue.name)
    ))

    orchestras = list(session.scalars(
        select(Orchestra).where(Orchestra.name.ilike(p)).order_by(Orchestra.name)
    ))

    return {
        "concerts": concerts,
        "conductors": conductors,
        "composers": composers,
        "artists": artists,
        "venues": venues,
        "orchestras": orchestras,
    }
