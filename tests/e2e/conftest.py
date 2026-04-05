"""E2E test configuration.

Provides a ``user`` fixture that runs the real application against a per-test
copy of ``data/konzert.db``.  This means every test starts with exactly the
same known dataset and database mutations are fully isolated between tests.

The NiceGUI ``user_plugin`` is registered at the top-level ``tests/conftest.py``
(required by pytest 9 – plugins must be declared in the root conftest).
"""

import shutil
from pathlib import Path

import pytest
from nicegui.testing import User, user_simulation
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool

import app.database as db_module
import app.models  # noqa: F401 — registers all ORM models with Base.metadata
from app.database import Base

_REPO_ROOT = Path(__file__).parent.parent.parent
_TEST_DB_SRC = _REPO_ROOT / "data" / "konzert.db"
_MAIN_FILE = _REPO_ROOT / "main.py"


@pytest.fixture
async def user(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> User:  # type: ignore[override]
    """NiceGUI User fixture backed by a per-test copy of ``data/konzert.db``.

    Each test gets its own isolated SQLite database pre-populated with the
    sample data committed to the repository, so tests can freely add and
    delete records without affecting one another.
    """
    test_db = tmp_path / "konzert.db"
    shutil.copy(_TEST_DB_SRC, test_db)

    engine = create_engine(f"sqlite:///{test_db}", echo=False, poolclass=NullPool)
    Base.metadata.create_all(engine)  # creates any tables missing from the snapshot
    test_factory = sessionmaker(bind=engine, expire_on_commit=False)

    # Patch the module-level session factory so all app code uses the test DB.
    monkeypatch.setattr(db_module, "_SessionFactory", test_factory)
    monkeypatch.setattr(db_module, "create_session_factory", lambda db_path=None: test_factory)
    monkeypatch.setattr(db_module, "DB_PATH", test_db)

    async with user_simulation(main_file=_MAIN_FILE) as u:
        yield u
