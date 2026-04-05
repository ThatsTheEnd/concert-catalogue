"""E2E tests for the advanced Search page (``/search``).

The search page offers filtering by date range, piece text, composer,
conductor, artist, orchestra, and venue.  These tests verify the core
search scenarios against the seeded ``data/konzert.db``.
"""

import asyncio

from nicegui import ElementFilter, events, ui
from nicegui.testing import User, UserInteraction

from .helpers import fire_value_change

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _result_rows(user: User) -> list[dict]:
    """Return the rows of the search results table."""
    with user:
        tables = list(ElementFilter(kind=ui.table, only_visible=True))
    return tables[0].rows if tables else []  # type: ignore[return-value]


def _open_and_select(user: User, select_el: ui.select, label: str) -> None:
    """Open a select widget popup and pick the option matching *label*."""
    UserInteraction(user, {select_el}, None).click()
    UserInteraction(user, {select_el}, label).click()


def _get_selects(user: User) -> list[ui.select]:
    with user:
        return list(ElementFilter(kind=ui.select, only_visible=True))


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


async def test_search_page_renders(user: User) -> None:
    """The search page loads without error and shows the heading."""
    await user.open('/search')
    await user.should_see('Search')


async def test_search_empty_returns_all_concerts(user: User) -> None:
    """Opening the search page with no filters returns all seeded concerts."""
    await user.open('/search')
    rows = _result_rows(user)
    assert rows, "Expected at least one result when no filters are applied"
    # The seeded concert should be present
    assert any('Münchner' in str(r.get('orchestra', '')) for r in rows)


async def test_search_by_piece_text_finds_match(user: User) -> None:
    """Filtering by piece text finds the seeded concert that contains the piece."""
    await user.open('/search')

    with user:
        inputs = list(ElementFilter(kind=ui.input, only_visible=True))
        # The third input is the piece text input (date_from, date_to, piece)
        piece_input = inputs[2]

    # The seeded piece is "Violinkonzert"
    fire_value_change(user, piece_input, 'Violin')

    rows = _result_rows(user)
    assert rows, "Expected a result when searching for 'Violin'"


async def test_search_by_piece_text_no_match_returns_empty(user: User) -> None:
    """A piece text with no match returns an empty result set."""
    await user.open('/search')

    with user:
        inputs = list(ElementFilter(kind=ui.input, only_visible=True))
        piece_input = inputs[2]

    fire_value_change(user, piece_input, 'XYZ_NO_SUCH_PIECE')
    # The piece input uses a 0.3 s debounce before calling load()
    await asyncio.sleep(0.5)

    rows = _result_rows(user)
    assert not rows, f"Expected no results for 'XYZ_NO_SUCH_PIECE', got: {rows}"


async def test_search_by_orchestra_dropdown(user: User) -> None:
    """Selecting an orchestra in the dropdown filters to matching concerts."""
    await user.open('/search')

    selects = _get_selects(user)
    # Layout: composer(0), conductor(1), orchestra(2), artist(3), venue(4)
    # (The "—" option is the default; the seeded orchestra is in the list)
    orchestra_sel = selects[2]

    _open_and_select(user, orchestra_sel, 'Münchner Philharmoniker')
    # Trigger the update:model-value event on the select
    with user:
        for listener in orchestra_sel._event_listeners.values():
            if listener.type in ('update:modelValue', 'update:model-value'):
                evt = events.ValueChangeEventArguments(
                    sender=orchestra_sel,
                    client=user._client,
                    value=orchestra_sel.value,
                    previous_value=None,
                )
                events.handle_event(listener.handler, evt)

    rows = _result_rows(user)
    assert rows, "Expected results when filtering by orchestra"
    assert all('Münchner' in str(r.get('orchestra', '')) for r in rows)


async def test_search_result_row_click_navigates_to_detail(user: User) -> None:
    """Clicking a row in the search results navigates to the concert detail."""
    await user.open('/search')

    rows = _result_rows(user)
    assert rows, "Need at least one result to test row navigation"

    first_id = rows[0]['id']
    with user:
        table = list(ElementFilter(kind=ui.table, only_visible=True))[0]

    # Simulate the rowClick event (args: [event, row, cols, colName, event])
    UserInteraction(user, {table}, None).trigger(
        'rowClick', args=[None, rows[0], None, None, None]
    )
    # Navigation is async (background task) – wait briefly for it to complete
    await asyncio.sleep(0.1)

    # The back-history should record the concert detail URL
    assert user.back_history[-1] == f'/concerts/{first_id}'


async def test_search_query_param_pre_fills_piece_input(user: User) -> None:
    """Navigating to /search?q=mozart pre-fills the piece search field."""
    await user.open('/search?q=Violinkonzert')

    with user:
        inputs = list(ElementFilter(kind=ui.input, only_visible=True))
        piece_input = inputs[2]
        assert piece_input.value == 'Violinkonzert', \
            f"Expected 'Violinkonzert' in piece input, got: {piece_input.value!r}"
