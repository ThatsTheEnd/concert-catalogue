from loguru import logger
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.models import Artist, Composer, Conductor


def create_conductor(
    session: Session, first_name: str = "", last_name: str = "", **kwargs
) -> Conductor:
    obj = Conductor(first_name=first_name, last_name=last_name, **kwargs)
    session.add(obj)
    session.commit()
    logger.info("Created conductor: {} {}", first_name, last_name)
    return obj


def list_conductors(session: Session) -> list[Conductor]:
    return list(session.scalars(select(Conductor).order_by(Conductor.last_name)))


def search_conductors(session: Session, query: str) -> list[Conductor]:
    p = f"%{query}%"
    stmt = select(Conductor).where(
        or_(Conductor.first_name.ilike(p), Conductor.last_name.ilike(p))
    ).order_by(Conductor.last_name)
    return list(session.scalars(stmt))


def create_composer(
    session: Session, first_name: str = "", last_name: str = "", **kwargs
) -> Composer:
    obj = Composer(first_name=first_name, last_name=last_name, **kwargs)
    session.add(obj)
    session.commit()
    logger.info("Created composer: {} {}", first_name, last_name)
    return obj


def list_composers(session: Session) -> list[Composer]:
    return list(session.scalars(select(Composer).order_by(Composer.last_name)))


def search_composers(session: Session, query: str) -> list[Composer]:
    p = f"%{query}%"
    stmt = select(Composer).where(
        or_(Composer.first_name.ilike(p), Composer.last_name.ilike(p))
    ).order_by(Composer.last_name)
    return list(session.scalars(stmt))


def create_artist(
    session: Session, first_name: str = "", last_name: str = "", instrument: str = "", **kwargs
) -> Artist:
    obj = Artist(first_name=first_name, last_name=last_name, instrument=instrument, **kwargs)
    session.add(obj)
    session.commit()
    logger.info("Created artist: {} {} ({})", first_name, last_name, instrument)
    return obj


def list_artists(session: Session) -> list[Artist]:
    return list(session.scalars(select(Artist).order_by(Artist.last_name)))


def search_artists(session: Session, query: str) -> list[Artist]:
    p = f"%{query}%"
    stmt = select(Artist).where(
        or_(Artist.first_name.ilike(p), Artist.last_name.ilike(p), Artist.instrument.ilike(p))
    ).order_by(Artist.last_name)
    return list(session.scalars(stmt))
