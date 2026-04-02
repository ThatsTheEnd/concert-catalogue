from loguru import logger
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Orchestra


def create_orchestra(session: Session, name: str) -> Orchestra:
    obj = Orchestra(name=name)
    session.add(obj)
    session.commit()
    logger.info("Created orchestra: {!r}", name)
    return obj


def update_orchestra(session: Session, orchestra_id: int, **kwargs) -> Orchestra | None:
    obj = session.get(Orchestra, orchestra_id)
    if obj is None:
        return None
    for k, v in kwargs.items():
        setattr(obj, k, v)
    session.commit()
    logger.info("Updated orchestra id={} fields={}", orchestra_id, list(kwargs.keys()))
    return obj


def delete_orchestra(session: Session, orchestra_id: int) -> None:
    obj = session.get(Orchestra, orchestra_id)
    if obj is not None:
        session.delete(obj)
        session.commit()
        logger.info("Deleted orchestra id={}", orchestra_id)


def list_orchestras(session: Session) -> list[Orchestra]:
    return list(session.scalars(select(Orchestra).order_by(Orchestra.name)))
