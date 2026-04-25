from loguru import logger
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.models import Artist, Composer


def create_composer(
    session: Session, first_name: str = "", last_name: str = "", **kwargs
) -> Composer:
    obj = Composer(first_name=first_name, last_name=last_name, **kwargs)
    session.add(obj)
    session.commit()
    logger.info("Created composer: {} {}", first_name, last_name)
    return obj


def update_composer(session: Session, composer_id: int, **kwargs) -> Composer | None:
    obj = session.get(Composer, composer_id)
    if obj is None:
        return None
    for k, v in kwargs.items():
        setattr(obj, k, v)
    session.commit()
    logger.info("Updated composer id={} fields={}", composer_id, list(kwargs.keys()))
    return obj


def delete_composer(session: Session, composer_id: int) -> None:
    obj = session.get(Composer, composer_id)
    if obj is not None:
        session.delete(obj)
        session.commit()
        logger.info("Deleted composer id={}", composer_id)


def list_composers(session: Session) -> list[Composer]:
    return list(session.scalars(select(Composer).order_by(Composer.last_name)))


def search_composers(session: Session, query: str) -> list[Composer]:
    p = f"%{query}%"
    stmt = select(Composer).where(
        or_(Composer.first_name.ilike(p), Composer.last_name.ilike(p))
    ).order_by(Composer.last_name)
    return list(session.scalars(stmt))


def create_artist(
    session: Session,
    first_name: str = "",
    last_name: str = "",
    default_instrument: str | None = None,
    **kwargs,
) -> Artist:
    obj = Artist(
        first_name=first_name, last_name=last_name, default_instrument=default_instrument, **kwargs
    )
    session.add(obj)
    session.commit()
    logger.info("Created artist: {} {} ({})", first_name, last_name, default_instrument)
    return obj


def update_artist(session: Session, artist_id: int, **kwargs) -> Artist | None:
    obj = session.get(Artist, artist_id)
    if obj is None:
        return None
    for k, v in kwargs.items():
        setattr(obj, k, v)
    session.commit()
    logger.info("Updated artist id={} fields={}", artist_id, list(kwargs.keys()))
    return obj


def delete_artist(session: Session, artist_id: int) -> None:
    obj = session.get(Artist, artist_id)
    if obj is not None:
        session.delete(obj)
        session.commit()
        logger.info("Deleted artist id={}", artist_id)


def list_artists(session: Session) -> list[Artist]:
    return list(session.scalars(select(Artist).order_by(Artist.last_name)))


def search_artists(session: Session, query: str) -> list[Artist]:
    p = f"%{query}%"
    stmt = select(Artist).where(
        or_(
            Artist.first_name.ilike(p),
            Artist.last_name.ilike(p),
            Artist.default_instrument.ilike(p),
        )
    ).order_by(Artist.last_name)
    return list(session.scalars(stmt))
