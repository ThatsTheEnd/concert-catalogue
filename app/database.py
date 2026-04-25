import os
import sys
from datetime import datetime
from pathlib import Path

from loguru import logger
from sqlalchemy import create_engine, text
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

_schema_backup_path: Path | None = None


class Base(DeclarativeBase):
    pass


def get_engine(db_path: Path = DB_PATH):
    db_path.parent.mkdir(parents=True, exist_ok=True)
    return create_engine(f"sqlite:///{db_path}", echo=False, poolclass=NullPool)


def _is_schema_compatible(engine) -> bool:
    """Return True if the on-disk schema matches the current models.

    An empty database (no tables yet) is considered compatible — ``create_all``
    will build it from scratch.  Only an existing database that is missing the
    new columns is flagged as stale.
    """
    with engine.connect() as conn:
        rows = conn.execute(text("PRAGMA table_info(artists)")).fetchall()
        if not rows:
            return True  # table absent → brand-new DB, create_all will handle it
        cols = {row[1] for row in rows}
        return "default_instrument" in cols


def get_schema_backup() -> Path | None:
    """Return the backup path if a stale DB was renamed on startup, else None."""
    return _schema_backup_path


def create_session_factory(db_path: Path = DB_PATH) -> sessionmaker[Session]:
    global _schema_backup_path
    db_path.parent.mkdir(parents=True, exist_ok=True)
    if db_path.exists():
        engine = get_engine(db_path)
        if not _is_schema_compatible(engine):
            engine.dispose()
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup = db_path.with_name(f"konzert_backup_{ts}.db")
            db_path.rename(backup)
            _schema_backup_path = backup
            logger.warning("Stale DB schema — backed up to {}", backup)
            engine = get_engine(db_path)
    else:
        engine = get_engine(db_path)
    Base.metadata.create_all(engine)

    # Seed reference data into a brand-new (empty) database
    with engine.connect() as conn:
        count = conn.execute(text("SELECT COUNT(*) FROM composers")).scalar()
    if count == 0:
        factory = sessionmaker(bind=engine, expire_on_commit=False)
        with factory() as session:
            from app.seeds import seed_reference_data  # lazy import — avoids circular
            seed_reference_data(session)
            session.commit()

    logger.info("Database ready at {}", db_path)
    return sessionmaker(bind=engine, expire_on_commit=False)


# Module-level session factory (initialized on first import of models)
_SessionFactory: sessionmaker[Session] | None = None


def get_session() -> Session:
    global _SessionFactory
    if _SessionFactory is None:
        _SessionFactory = create_session_factory()
    return _SessionFactory()
