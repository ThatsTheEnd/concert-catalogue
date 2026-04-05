"""Shared helpers for e2e tests.

The reference-data page uses ``ui.tab_panel`` containers for each entity type.
All six panels are rendered in the DOM at all times (NiceGUI's tab panels do not
set ``visible=False`` on inactive panels), so we must scope ``ElementFilter``
queries to the specific panel index rather than relying on ``only_visible=True``.

Panel order (matches the order in ``reference_data_page()``):
  0 – Orchestras
  1 – Composers
  2 – Conductors
  3 – Artists
  4 – Pieces
  5 – Venues
"""

from __future__ import annotations

from typing import Any

from nicegui import ElementFilter, events, ui
from nicegui.testing import User, UserInteraction

# ---------------------------------------------------------------------------
# Panel index constants
# ---------------------------------------------------------------------------

PANEL_ORCHESTRAS = 0
PANEL_COMPOSERS = 1
PANEL_CONDUCTORS = 2
PANEL_ARTISTS = 3
PANEL_PIECES = 4
PANEL_VENUES = 5


# ---------------------------------------------------------------------------
# Generic helpers
# ---------------------------------------------------------------------------


def get_panel(user: User, panel_index: int) -> ui.tab_panel:
    """Return the tab panel at *panel_index* (0-based) on the reference page."""
    with user:
        panels = list(ElementFilter(kind=ui.tab_panel))
    return panels[panel_index]


def get_table(user: User, panel_index: int) -> ui.table:
    """Return the single ``ui.table`` inside the given panel."""
    with user:
        panels = list(ElementFilter(kind=ui.tab_panel))
        panel = panels[panel_index]
        tables = list(ElementFilter(kind=ui.table).within(instance=panel))
    return tables[0]


def get_table_rows(user: User, panel_index: int) -> list[dict]:
    """Return a snapshot of the current table rows for the given panel."""
    return get_table(user, panel_index).rows  # type: ignore[return-value]


def click_add_in_panel(user: User, panel_index: int) -> None:
    """Click the *Add* button inside the given reference-data panel."""
    with user:
        panels = list(ElementFilter(kind=ui.tab_panel))
        panel = panels[panel_index]
        btn = list(ElementFilter(kind=ui.button, content="Add").within(instance=panel))[0]
    UserInteraction(user, {btn}, "Add").click()


def type_in_panel_input(user: User, panel_index: int, label: str, text: str) -> None:
    """Type *text* into the first ``ui.input`` with *label* inside *panel_index*."""
    with user:
        panels = list(ElementFilter(kind=ui.tab_panel))
        panel = panels[panel_index]
        inputs = [
            inp
            for inp in ElementFilter(kind=ui.input).within(instance=panel)
            if inp.props.get("label") == label
        ]
    assert inputs, f"No input labelled {label!r} found in panel {panel_index}"
    UserInteraction(user, {inputs[0]}, label).type(text)


def trigger_delete_row(user: User, panel_index: int, row: dict[str, Any]) -> None:
    """Trigger the *delete_row* custom event on the table in *panel_index*."""
    with user:
        panels = list(ElementFilter(kind=ui.tab_panel))
        panel = panels[panel_index]
        table = list(ElementFilter(kind=ui.table).within(instance=panel))[0]
    UserInteraction(user, {table}, "delete_row").trigger("delete_row", args=row)


def confirm_delete(user: User) -> None:
    """Click the *Delete* button inside the open confirmation dialog."""
    user.find("Delete").click()


def click_tab(user: User, tab_label: str) -> None:
    """Click the tab whose visible label matches *tab_label*."""
    user.find(ui.tab, content=tab_label).click()


def fire_value_change(user: User, element: ui.input, value: str) -> None:
    """Set an input's value and fire the ``update:modelValue`` event.

    NiceGUI stores event listeners with camelCase type names.  This helper
    updates the element's Python value and dispatches a
    ``ValueChangeEventArguments`` to all matching listeners, simulating what
    the browser would do when the user types in an input.
    """
    with user:
        element.value = value
        evt = events.ValueChangeEventArguments(
            sender=element,
            client=user._client,
            value=value,
            previous_value="",
        )
        for listener in element._event_listeners.values():
            if listener.type in ("update:modelValue", "update:model-value"):
                events.handle_event(listener.handler, evt)
