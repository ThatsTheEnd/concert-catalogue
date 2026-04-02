from loguru import logger
from sqlalchemy import or_, select
from sqlalchemy.orm import Session, joinedload

from app.models import Composer, Piece


def create_piece(session: Session, composer_id: int, title: str, **kwargs) -> Piece:
    piece = Piece(composer_id=composer_id, title=title, **kwargs)
    session.add(piece)
    session.commit()
    logger.info("Created piece: {!r} (composer_id={})", title, composer_id)
    return piece


def update_piece(session: Session, piece_id: int, **kwargs) -> Piece | None:
    obj = session.get(Piece, piece_id)
    if obj is None:
        return None
    for k, v in kwargs.items():
        setattr(obj, k, v)
    session.commit()
    logger.info("Updated piece id={} fields={}", piece_id, list(kwargs.keys()))
    return obj


def delete_piece(session: Session, piece_id: int) -> None:
    obj = session.get(Piece, piece_id)
    if obj is not None:
        session.delete(obj)
        session.commit()
        logger.info("Deleted piece id={}", piece_id)


def list_pieces(session: Session) -> list[Piece]:
    stmt = (
        select(Piece)
        .options(joinedload(Piece.composer))
        .join(Piece.composer)
        .order_by(Composer.last_name, Piece.title)
    )
    return list(session.scalars(stmt).unique())


def search_pieces(session: Session, query: str) -> list[Piece]:
    p = f"%{query}%"
    stmt = (
        select(Piece)
        .options(joinedload(Piece.composer))
        .join(Piece.composer)
        .where(
            or_(
                Piece.title.ilike(p),
                Composer.first_name.ilike(p),
                Composer.last_name.ilike(p),
            )
        )
        .order_by(Composer.last_name, Piece.title)
    )
    return list(session.scalars(stmt).unique())
