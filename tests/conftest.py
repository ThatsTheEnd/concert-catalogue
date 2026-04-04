import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base

# Register the NiceGUI user-simulation pytest plugin so that the ``user``
# fixture (defined in ``tests/e2e/conftest.py``) is available to all
# end-to-end tests under ``tests/e2e/``.
pytest_plugins = ["nicegui.testing.user_plugin"]


@pytest.fixture
def session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine, expire_on_commit=False)
    with factory() as s:
        yield s
    Base.metadata.drop_all(engine)
