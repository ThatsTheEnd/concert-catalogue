"""Smoke tests that verify the three main pages load correctly."""

from nicegui import ElementFilter, ui
from nicegui.testing import User


async def test_concerts_page_loads(user: User) -> None:
    await user.open('/concerts')
    await user.should_see('KonzertKatalog')


async def test_concerts_list_shows_seed_data(user: User) -> None:
    """The seeded DB contains one concert – verify the orchestra shows in the table."""
    await user.open('/concerts')
    with user:
        tables = list(ElementFilter(kind=ui.table, only_visible=True))
        assert tables
        orchestra_values = [r.get('orchestra', '') for r in tables[0].rows]
        assert any('Münchner' in v for v in orchestra_values)


async def test_reference_data_page_loads(user: User) -> None:
    await user.open('/reference')
    await user.should_see('KonzertKatalog')


async def test_search_page_loads(user: User) -> None:
    await user.open('/search')
    await user.should_see('KonzertKatalog')
