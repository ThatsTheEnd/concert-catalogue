from pathlib import Path

from loguru import logger
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

DB_PATH = Path(__file__).parent.parent / "data" / "konzert.db"


class Base(DeclarativeBase):
    pass


def get_engine(db_path: Path = DB_PATH):
    db_path.parent.mkdir(parents=True, exist_ok=True)
    return create_engine(f"sqlite:///{db_path}", echo=False)


def create_session_factory(db_path: Path = DB_PATH) -> sessionmaker[Session]:
    engine = get_engine(db_path)
    Base.metadata.create_all(engine)
    logger.info("Database ready at {}", db_path)
    return sessionmaker(bind=engine, expire_on_commit=False)


# Module-level session factory (initialized on first import of models)
_SessionFactory: sessionmaker[Session] | None = None


def get_session() -> Session:
    global _SessionFactory
    if _SessionFactory is None:
        _SessionFactory = create_session_factory()
    return _SessionFactory()
