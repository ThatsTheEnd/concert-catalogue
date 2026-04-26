"""E2E tests for concert management (add, view, delete).

Uses the seeded ``data/konzert.db`` which already contains one concert with
Münchner Philharmoniker / Herkulessaal / Nikolaus Harnoncourt so tests can
always verify data from a pre-populated database.
"""

from nicegui import ElementFilter, ui
from nicegui.testing import User, UserInteraction

from .helpers import fire_value_change

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _get_table_rows(user: User) -> list[dict]:
    """Return the rows of the first visible table on the current page."""
    with user:
        tables = list(ElementFilter(kind=ui.table, only_visible=True))
    return tables[0].rows if tables else []  # type: ignore[return-value]


def _select_option(user: User, select_el: ui.select, option_label: str) -> None:
    """Open a select widget and choose the option whose display text matches."""
    UserInteraction(user, {select_el}, None).click()          # open popup
    UserInteraction(user, {select_el}, option_label).click()  # pick option


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


async def test_seeded_concert_appears_in_list(user: User) -> None:
    """The seeded concert (2026-03-02, Münchner Philharmoniker) is listed."""
    await user.open('/concerts')
    rows = _get_table_rows(user)
    assert rows, "Concert list is empty"
    assert any('Münchner' in str(r.get('orchestra', '')) for r in rows)
    assert any('2026-03-02' in str(r.get('date', '')) for r in rows)


async def test_concert_detail_shows_correct_data(user: User) -> None:
    """Opening the seeded concert detail page shows orchestra, venue, conductor."""
    await user.open('/concerts/1')
    await user.should_see('Münchner Philharmoniker')
    await user.should_see('Herkulessaal')
    await user.should_see('Harnoncourt')


async def test_add_concert_minimal(user: User) -> None:
    """Adding a new concert with orchestra and venue persists it in the list."""
    await user.open('/concerts/new')
    await user.should_see('Add Concert')

    with user:
        selects = list(ElementFilter(kind=ui.select))
        # Order: Orchestra, Venue, Conductor (from the form layout)
        orch_sel = selects[0]
        venue_sel = selects[1]

    _select_option(user, orch_sel, 'Münchner Philharmoniker')
    _select_option(user, venue_sel, 'Herkulessaal, München')

    # Save
    user.find('Save').click()

    # Should redirect to the concerts list (or detail) – either way the concert exists
    await user.open('/concerts')
    rows = _get_table_rows(user)
    assert len(rows) >= 2, f"Expected at least 2 concerts after adding, got: {rows}"


async def test_add_concert_with_conductor(user: User) -> None:
    """Adding a concert with a conductor stores the conductor's name."""
    await user.open('/concerts/new')

    with user:
        selects = list(ElementFilter(kind=ui.select))
        orch_sel = selects[0]
        venue_sel = selects[1]
        conductor_sel = selects[2]

    _select_option(user, orch_sel, 'Münchner Philharmoniker')
    _select_option(user, venue_sel, 'Herkulessaal, München')
    _select_option(user, conductor_sel, 'Nikolaus Harnoncourt')

    user.find('Save').click()

    # Find the newly created concert (the last one in the list)
    await user.open('/concerts')
    rows = _get_table_rows(user)
    new_row = max(rows, key=lambda r: r['id'])
    assert new_row['conductor'] == 'Nikolaus Harnoncourt'


async def test_delete_concert(user: User) -> None:
    """Deleting a concert removes it from the concert list."""
    # First create a concert to delete
    await user.open('/concerts/new')

    with user:
        selects = list(ElementFilter(kind=ui.select))
        orch_sel = selects[0]

    _select_option(user, orch_sel, 'Münchner Philharmoniker')
    user.find('Save').click()

    # Verify it was created and navigate to its detail page
    await user.open('/concerts')
    rows = _get_table_rows(user)
    new_concert = max(rows, key=lambda r: r['id'])
    new_id = new_concert['id']

    await user.open(f'/concerts/{new_id}')
    await user.should_see('Münchner Philharmoniker')

    # Click Delete
    user.find('Delete').click()

    # Confirm deletion in the dialog
    user.find('Delete').click()

    # After deletion we should be back at the concert list
    await user.open('/concerts')
    rows = _get_table_rows(user)
    assert not any(r['id'] == new_id for r in rows), \
        f"Concert {new_id} should have been deleted"


async def test_concert_list_search_by_orchestra(user: User) -> None:
    """Searching the concert list by orchestra name filters the results."""
    await user.open('/concerts')

    with user:
        search_inputs = list(ElementFilter(kind=ui.input, only_visible=True))
        search_input = search_inputs[0]

    # A term that matches the seeded concert
    fire_value_change(user, search_input, 'Münchner')
    rows = _get_table_rows(user)
    assert rows, "Expected at least one result for 'Münchner'"
    assert all('Münchner' in str(r.get('orchestra', '')) for r in rows)

    # A term with no matches should return an empty list
    fire_value_change(user, search_input, 'XYZ_NO_MATCH')
    rows_no_match = _get_table_rows(user)
    assert not rows_no_match, f"Expected 0 results for 'XYZ_NO_MATCH', got: {rows_no_match}"


async def test_concert_list_quick_filter_is_connected(user: User) -> None:
    """Quick filter input is wired up: a no-match term empties the table."""
    await user.open('/concerts')
    rows_before = _get_table_rows(user)
    assert rows_before, "Seeded DB should have at least one concert"

    with user:
        search_inputs = list(ElementFilter(kind=ui.input, only_visible=True))
        search_input = search_inputs[0]

    fire_value_change(user, search_input, 'ZZZ_NOTHING_MATCHES_THIS')
    rows_after = _get_table_rows(user)
    assert not rows_after, (
        "Quick filter has no effect — event binding is likely broken "
        f"(got {len(rows_after)} rows, expected 0)"
    )


async def test_concert_list_has_advanced_search_link(user: User) -> None:
    """Concerts list shows an 'Advanced search' link pointing to /search."""
    await user.open('/concerts')
    await user.should_see('Advanced search →')

    with user:
        links = list(ElementFilter(kind=ui.link))
    search_links = [lnk for lnk in links if 'Advanced search' in (lnk.text or '')]
    assert search_links, "No ui.link with 'Advanced search' found"
    assert any(lnk._props.get('href') == '/search' for lnk in search_links), (
        f"Expected link href '/search', got: {[lnk._props.get('href') for lnk in search_links]}"
    )
