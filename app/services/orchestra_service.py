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


def list_orchestras(session: Session) -> list[Orchestra]:
    return list(session.scalars(select(Orchestra).order_by(Orchestra.name)))
