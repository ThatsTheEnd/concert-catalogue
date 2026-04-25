"""E2E tests for the Reference Data page.

Covers add and delete for every entity type exposed by the
``/reference`` page: Orchestras, Composers, Artists, Pieces, and Venues.
Every test works against an isolated per-test copy of ``data/konzert.db``,
so mutations do not bleed between runs.
"""

from nicegui.testing import User

from .helpers import (
    PANEL_ARTISTS,
    PANEL_COMPOSERS,
    PANEL_ORCHESTRAS,
    PANEL_PIECES,
    PANEL_VENUES,
    click_add_in_panel,
    click_tab,
    confirm_delete,
    get_table_rows,
    trigger_delete_row,
    type_in_panel_input,
)

# ---------------------------------------------------------------------------
# Orchestras
# ---------------------------------------------------------------------------


async def test_add_orchestra(user: User) -> None:
    """Adding an orchestra via the add form persists it in the table."""
    await user.open('/reference')

    before = get_table_rows(user, PANEL_ORCHESTRAS)
    type_in_panel_input(user, PANEL_ORCHESTRAS, 'Orchestra', 'E2E Philharmoniker')
    click_add_in_panel(user, PANEL_ORCHESTRAS)

    after = get_table_rows(user, PANEL_ORCHESTRAS)
    assert len(after) == len(before) + 1
    assert any(r['name'] == 'E2E Philharmoniker' for r in after)


async def test_delete_orchestra(user: User) -> None:
    """Deleting an orchestra removes it from the table."""
    await user.open('/reference')

    # Add one first so we have something to delete
    type_in_panel_input(user, PANEL_ORCHESTRAS, 'Orchestra', 'Del Orch')
    click_add_in_panel(user, PANEL_ORCHESTRAS)

    before = get_table_rows(user, PANEL_ORCHESTRAS)
    row = next(r for r in before if r['name'] == 'Del Orch')

    trigger_delete_row(user, PANEL_ORCHESTRAS, row)
    confirm_delete(user)

    after = get_table_rows(user, PANEL_ORCHESTRAS)
    assert len(after) == len(before) - 1
    assert not any(r['name'] == 'Del Orch' for r in after)


# ---------------------------------------------------------------------------
# Composers
# ---------------------------------------------------------------------------


async def test_add_composer(user: User) -> None:
    """Adding a composer persists all provided fields."""
    await user.open('/reference')
    click_tab(user, 'Composers')

    before = get_table_rows(user, PANEL_COMPOSERS)
    type_in_panel_input(user, PANEL_COMPOSERS, 'First name', 'Johann')
    type_in_panel_input(user, PANEL_COMPOSERS, 'Last name', 'Brahms')
    click_add_in_panel(user, PANEL_COMPOSERS)

    after = get_table_rows(user, PANEL_COMPOSERS)
    assert len(after) == len(before) + 1
    assert any(r['last_name'] == 'Brahms' and r['first_name'] == 'Johann' for r in after)


async def test_delete_composer(user: User) -> None:
    """Deleting a composer removes it from the table."""
    await user.open('/reference')
    click_tab(user, 'Composers')

    type_in_panel_input(user, PANEL_COMPOSERS, 'First name', 'Del')
    type_in_panel_input(user, PANEL_COMPOSERS, 'Last name', 'Composer')
    click_add_in_panel(user, PANEL_COMPOSERS)

    before = get_table_rows(user, PANEL_COMPOSERS)
    row = next(r for r in before if r['last_name'] == 'Composer')

    trigger_delete_row(user, PANEL_COMPOSERS, row)
    confirm_delete(user)

    after = get_table_rows(user, PANEL_COMPOSERS)
    assert not any(r['last_name'] == 'Composer' for r in after)


# ---------------------------------------------------------------------------
# Artists
# ---------------------------------------------------------------------------


async def test_add_artist(user: User) -> None:
    """Adding an artist persists name and default instrument."""
    await user.open('/reference')
    click_tab(user, 'Artists')

    before = get_table_rows(user, PANEL_ARTISTS)
    type_in_panel_input(user, PANEL_ARTISTS, 'First name', 'Hilary')
    type_in_panel_input(user, PANEL_ARTISTS, 'Last name', 'Hahn')
    type_in_panel_input(user, PANEL_ARTISTS, 'Default instrument', 'Violin')
    click_add_in_panel(user, PANEL_ARTISTS)

    after = get_table_rows(user, PANEL_ARTISTS)
    assert len(after) == len(before) + 1
    assert any(r['last_name'] == 'Hahn' and r['default_instrument'] == 'Violin' for r in after)


async def test_delete_artist(user: User) -> None:
    """Deleting an artist removes it from the table."""
    await user.open('/reference')
    click_tab(user, 'Artists')

    type_in_panel_input(user, PANEL_ARTISTS, 'First name', 'Del')
    type_in_panel_input(user, PANEL_ARTISTS, 'Last name', 'Artist')
    type_in_panel_input(user, PANEL_ARTISTS, 'Default instrument', 'Piccolo')
    click_add_in_panel(user, PANEL_ARTISTS)

    before = get_table_rows(user, PANEL_ARTISTS)
    row = next(r for r in before if r['last_name'] == 'Artist')

    trigger_delete_row(user, PANEL_ARTISTS, row)
    confirm_delete(user)

    after = get_table_rows(user, PANEL_ARTISTS)
    assert not any(r['last_name'] == 'Artist' for r in after)


# ---------------------------------------------------------------------------
# Pieces  (require a composer – the seeded DB already has Mozart)
# ---------------------------------------------------------------------------


async def test_add_piece(user: User) -> None:
    """Adding a piece for the existing seeded composer persists it."""
    await user.open('/reference')
    click_tab(user, 'Pieces')

    before = get_table_rows(user, PANEL_PIECES)

    # Select the seeded composer via the select widget.
    # The options dict maps {composer_id: full_name}.  Open the popup then
    # click the option whose display text matches the seeded composer.
    from nicegui import ElementFilter, ui
    from nicegui.testing import UserInteraction

    with user:
        panels = list(ElementFilter(kind=ui.tab_panel))
        panel = panels[PANEL_PIECES]
        selects = list(ElementFilter(kind=ui.select).within(instance=panel))
        title_inputs = [
            inp
            for inp in ElementFilter(kind=ui.input).within(instance=panel)
            if inp.props.get('label') == 'Title'
        ]
    assert selects, "Composer select not found in Pieces panel"
    assert title_inputs, "Title input not found in Pieces panel"

    # Open the popup, then click the full composer name to select it
    composer_sel = selects[0]
    UserInteraction(user, {composer_sel}, None).click()  # open popup
    UserInteraction(user, {composer_sel}, 'Wolfgang Amadeus Mozart').click()  # select

    UserInteraction(user, {title_inputs[0]}, 'Title').type('Piano Sonata in C')
    click_add_in_panel(user, PANEL_PIECES)

    after = get_table_rows(user, PANEL_PIECES)
    assert len(after) == len(before) + 1
    assert any(r['title'] == 'Piano Sonata in C' for r in after)


async def test_delete_piece(user: User) -> None:
    """Deleting a piece removes it from the table."""
    await user.open('/reference')
    click_tab(user, 'Pieces')

    # Add a piece to delete
    from nicegui import ElementFilter, ui
    from nicegui.testing import UserInteraction

    with user:
        panels = list(ElementFilter(kind=ui.tab_panel))
        panel = panels[PANEL_PIECES]
        selects = list(ElementFilter(kind=ui.select).within(instance=panel))
        title_inputs = [
            inp
            for inp in ElementFilter(kind=ui.input).within(instance=panel)
            if inp.props.get('label') == 'Title'
        ]

    composer_sel = selects[0]
    UserInteraction(user, {composer_sel}, None).click()
    UserInteraction(user, {composer_sel}, 'Wolfgang Amadeus Mozart').click()
    UserInteraction(user, {title_inputs[0]}, 'Title').type('Del Piece')
    click_add_in_panel(user, PANEL_PIECES)

    before = get_table_rows(user, PANEL_PIECES)
    row = next(r for r in before if r['title'] == 'Del Piece')

    trigger_delete_row(user, PANEL_PIECES, row)
    confirm_delete(user)

    after = get_table_rows(user, PANEL_PIECES)
    assert not any(r['title'] == 'Del Piece' for r in after)


# ---------------------------------------------------------------------------
# Venues
# ---------------------------------------------------------------------------


async def test_add_venue(user: User) -> None:
    """Adding a venue persists name, city and country."""
    await user.open('/reference')
    click_tab(user, 'Venue')

    before = get_table_rows(user, PANEL_VENUES)
    type_in_panel_input(user, PANEL_VENUES, 'Venue', 'Elbphilharmonie')
    type_in_panel_input(user, PANEL_VENUES, 'City', 'Hamburg')
    type_in_panel_input(user, PANEL_VENUES, 'Country', 'Germany')
    click_add_in_panel(user, PANEL_VENUES)

    after = get_table_rows(user, PANEL_VENUES)
    assert len(after) == len(before) + 1
    assert any(r['name'] == 'Elbphilharmonie' and r['city'] == 'Hamburg' for r in after)


async def test_delete_venue(user: User) -> None:
    """Deleting a venue removes it from the table."""
    await user.open('/reference')
    click_tab(user, 'Venue')

    type_in_panel_input(user, PANEL_VENUES, 'Venue', 'Del Venue')
    type_in_panel_input(user, PANEL_VENUES, 'City', 'Nowhere')
    type_in_panel_input(user, PANEL_VENUES, 'Country', 'Neverland')
    click_add_in_panel(user, PANEL_VENUES)

    before = get_table_rows(user, PANEL_VENUES)
    row = next(r for r in before if r['name'] == 'Del Venue')

    trigger_delete_row(user, PANEL_VENUES, row)
    confirm_delete(user)

    after = get_table_rows(user, PANEL_VENUES)
    assert not any(r['name'] == 'Del Venue' for r in after)
