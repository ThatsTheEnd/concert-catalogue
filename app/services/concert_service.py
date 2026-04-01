from datetime import date

from loguru import logger
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, joinedload

from app.models import (
    Artist,
    Composer,
    Concert,
    ConcertArtist,
    ConcertPiece,
    Conductor,
    Orchestra,
    Piece,
    Venue,
)


def create_concert(
    session: Session,
    date: date,
    orchestra_id: int | None = None,
    venue_id: int | None = None,
    conductor_id: int | None = None,
    choir: str = "",
    choir_director_id: int | None = None,
    notes: str = "",
    pieces: list[dict] | None = None,
    artists: list[dict] | None = None,
) -> Concert:
    concert = Concert(
        date=date,
        orchestra_id=orchestra_id,
        venue_id=venue_id,
        conductor_id=conductor_id,
        choir=choir,
        choir_director_id=choir_director_id,
        notes=notes,
    )
    session.add(concert)
    session.flush()

    for item in pieces or []:
        session.add(ConcertPiece(
            concert_id=concert.id,
            piece_id=item["piece_id"],
            sort_order=item.get("sort_order", 0),
            notes=item.get("notes", ""),
        ))
    for item in artists or []:
        session.add(ConcertArtist(
            concert_id=concert.id,
            artist_id=item["artist_id"],
            role=item.get("role", ""),
        ))

    session.commit()
    logger.info(
        "Created concert id={} date={} orchestra_id={} venue_id={} conductor_id={}",
        concert.id, date, orchestra_id, venue_id, conductor_id,
    )
    return concert


def get_concert(session: Session, concert_id: int) -> Concert | None:
    return session.get(Concert, concert_id)


def _search_filter(search: str):
    """OR filter across orchestra name, choir, conductor, venue, composer, artist, piece."""
    if not search:
        return None
    pattern = f"%{search}%"
    return or_(
        Orchestra.name.ilike(pattern),
        Concert.choir.ilike(pattern),
        Conductor.first_name.ilike(pattern),
        Conductor.last_name.ilike(pattern),
        Venue.name.ilike(pattern),
        Venue.city.ilike(pattern),
        Artist.first_name.ilike(pattern),
        Artist.last_name.ilike(pattern),
        Composer.first_name.ilike(pattern),
        Composer.last_name.ilike(pattern),
        Piece.title.ilike(pattern),
    )


def _base_query(search: str = ""):
    stmt = (
        select(Concert)
        .outerjoin(Concert.orchestra)
        .outerjoin(Concert.conductor)
        .outerjoin(Concert.venue)
        .outerjoin(Concert.artist_links)
        .outerjoin(ConcertArtist.artist)
        .outerjoin(Concert.piece_links)
        .outerjoin(ConcertPiece.piece)
        .outerjoin(Piece.composer)
        .distinct()
    )
    f = _search_filter(search)
    if f is not None:
        stmt = stmt.where(f)
    return stmt


def list_concerts(
    session: Session,
    search: str = "",
    limit: int = 50,
    offset: int = 0,
) -> list[Concert]:
    stmt = (
        _base_query(search)
        .order_by(Concert.date.desc())
        .limit(limit)
        .offset(offset)
        .options(
            joinedload(Concert.orchestra),
            joinedload(Concert.venue),
            joinedload(Concert.conductor),
        )
    )
    return list(session.scalars(stmt).unique())


def count_concerts(session: Session, search: str = "") -> int:
    subq = _base_query(search).subquery()
    return session.scalar(select(func.count()).select_from(subq)) or 0


def update_concert(session: Session, concert_id: int, **kwargs) -> Concert | None:
    concert = session.get(Concert, concert_id)
    if concert is None:
        return None
    for key, value in kwargs.items():
        setattr(concert, key, value)
    session.commit()
    logger.info("Updated concert id={} fields={}", concert_id, list(kwargs.keys()))
    return concert


def delete_concert(session: Session, concert_id: int) -> None:
    concert = session.get(Concert, concert_id)
    if concert is not None:
        session.delete(concert)
        session.commit()
        logger.info("Deleted concert id={}", concert_id)
