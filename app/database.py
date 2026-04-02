import os
import sys
from pathlib import Path

from loguru import logger
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker
from sqlalchemy.pool import NullPool


def _default_db_path() -> Path:
    """Return the platform-appropriate default database path."""
    if sys.platform == "darwin":
        base = Path.home() / "Library" / "Application Support" / "KonzertKatalog"
    elif sys.platform == "win32":
        base = Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData" / "Local"))
        base = base / "KonzertKatalog"
    else:
        base = Path(os.environ.get("XDG_DATA_HOME", Path.home() / ".local" / "share"))
        base = base / "konzertkatalog"
    return base / "konzert.db"


DB_PATH = Path(os.environ.get("KONZERT_DB_PATH", _default_db_path()))


class Base(DeclarativeBase):
    pass


def get_engine(db_path: Path = DB_PATH):
    db_path.parent.mkdir(parents=True, exist_ok=True)
    return create_engine(f"sqlite:///{db_path}", echo=False, poolclass=NullPool)


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
