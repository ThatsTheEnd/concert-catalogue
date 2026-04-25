import asyncio
from datetime import date

from nicegui import ui

from app.database import get_session
from app.i18n import t
from app.services.concert_service import filter_concerts
from app.services.orchestra_service import list_orchestras
from app.services.person_service import list_artists, list_composers
from app.services.venue_service import list_venues


def _parse_date(value: str) -> date | None:
    try:
        return date.fromisoformat(value) if value else None
    except ValueError:
        return None


def search_page(query: str = "") -> None:
    session = get_session()
    ui.context.client.on_disconnect(session.close)

    composers = {None: "—", **{c.id: c.full_name for c in list_composers(session)}}
    _all_artists = list_artists(session)
    conductors = {None: "—", **{a.id: a.full_name for a in _all_artists}}
    artists = {
        None: "—",
        **{
            a.id: f"{a.full_name} ({a.default_instrument})" if a.default_instrument else a.full_name
            for a in _all_artists
        },
    }
    orchestras = {None: "—", **{o.id: o.name for o in list_orchestras(session)}}
    venues = {None: "—", **{v.id: str(v) for v in list_venues(session)}}

    ui.label(t("search_heading")).classes("text-2xl font-bold mb-4")

    with ui.card().classes("w-full mb-2 p-4"):
        with ui.grid(columns=3).classes("w-full gap-4"):
            date_from_input = ui.input(t("search_date_from")).props("type=date").classes("w-full")
            date_to_input = ui.input(t("search_date_to")).props("type=date").classes("w-full")
            piece_input = ui.input(t("search_piece_label"), value=query).classes("w-full")
        with ui.grid(columns=3).classes("w-full gap-4 mt-2"):
            composer_sel = ui.select(composers, label=t("composer"), value=None, with_input=True).classes("w-full")
            conductor_sel = (
                ui.select(conductors, label=t("conductor_label"), value=None, with_input=True)
                .classes("w-full")
            )
            orchestra_sel = ui.select(orchestras, label=t("orchestra"), value=None, with_input=True).classes("w-full")
        with ui.grid(columns=2).classes("w-full gap-4 mt-2"):
            artist_sel = ui.select(artists, label=t("artist"), value=None, with_input=True).classes("w-full")
            venue_sel = ui.select(venues, label=t("venue"), value=None, with_input=True).classes("w-full")

    count_label = ui.label("").classes("text-sm text-gray-500 mb-2")

    columns = [
        {"name": "date", "label": t("col_date"), "field": "date", "sortable": True},
        {"name": "orchestra", "label": t("col_orchestra"), "field": "orchestra"},
        {"name": "conductor", "label": t("col_conductor"), "field": "conductor"},
        {"name": "venue", "label": t("col_venue"), "field": "venue"},
    ]
    table = ui.table(columns=columns, rows=[], row_key="id").classes("w-full cursor-pointer")
    table.on("rowClick", lambda e: ui.navigate.to(f"/concerts/{e.args[1]['id']}"))

    _debounce: list[asyncio.TimerHandle | None] = [None]

    def load():
        concerts = filter_concerts(
            session,
            date_from=_parse_date(date_from_input.value),
            date_to=_parse_date(date_to_input.value),
            piece_text=piece_input.value.strip(),
            composer_id=composer_sel.value,
            conductor_id=conductor_sel.value,
            artist_id=artist_sel.value,
            orchestra_id=orchestra_sel.value,
            venue_id=venue_sel.value,
        )
        table.rows = [
            {
                "id": c.id,
                "date": str(c.date),
                "orchestra": c.orchestra.name if c.orchestra else "—",
                "conductor": c.conductor.full_name if c.conductor else "—",
                "venue": str(c.venue) if c.venue else "—",
            }
            for c in concerts
        ]
        count_label.set_text(f"{len(table.rows)} {t('of_concerts')}")

    def schedule_load(_=None):
        if _debounce[0] is not None:
            _debounce[0].cancel()
        _debounce[0] = asyncio.get_event_loop().call_later(0.3, load)

    for widget in [date_from_input, date_to_input, composer_sel, conductor_sel, orchestra_sel, artist_sel, venue_sel]:
        widget.on("update:model-value", lambda _: load())
    piece_input.on("update:model-value", schedule_load)

    load()
