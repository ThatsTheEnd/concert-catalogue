from nicegui import ui

from app.database import get_session
from app.i18n import t
from app.services.person_service import (
    create_artist,
    create_composer,
    create_conductor,
    list_artists,
    list_composers,
    list_conductors,
)
from app.services.piece_service import create_piece, list_pieces
from app.services.venue_service import create_venue, list_venues


def reference_data_page() -> None:
    session = get_session()

    with ui.tabs() as tabs:
        tab_composers = ui.tab(t("composers"))
        tab_conductors = ui.tab(t("conductors"))
        tab_artists = ui.tab(t("artists"))
        tab_pieces = ui.tab(t("pieces"))
        tab_venues = ui.tab(t("venue"))

    with ui.tab_panels(tabs, value=tab_composers).classes("w-full"):
        with ui.tab_panel(tab_composers):
            _composers_panel(session)
        with ui.tab_panel(tab_conductors):
            _conductors_panel(session)
        with ui.tab_panel(tab_artists):
            _artists_panel(session)
        with ui.tab_panel(tab_pieces):
            _pieces_panel(session)
        with ui.tab_panel(tab_venues):
            _venues_panel(session)


def _composers_panel(session) -> None:
    columns = [
        {"name": "last_name", "label": t("last_name"), "field": "last_name", "sortable": True},
        {"name": "first_name", "label": t("first_name"), "field": "first_name"},
        {"name": "birth_year", "label": t("birth_year"), "field": "birth_year"},
        {"name": "death_year", "label": t("death_year"), "field": "death_year"},
        {"name": "nationality", "label": t("nationality"), "field": "nationality"},
    ]

    def rows():
        return [
            {
                "id": c.id, "last_name": c.last_name, "first_name": c.first_name,
                "birth_year": c.birth_year or "", "death_year": c.death_year or "",
                "nationality": c.nationality,
            }
            for c in list_composers(session)
        ]

    table = ui.table(columns=columns, rows=rows(), row_key="id").classes("w-full")

    with ui.row().classes("mt-2 gap-2 flex-wrap"):
        fn = ui.input(t("first_name")).classes("w-40")
        ln = ui.input(t("last_name")).classes("w-40")
        by = ui.input(t("birth_year")).classes("w-24")
        dy = ui.input(t("death_year")).classes("w-24")
        nat = ui.input(t("nationality")).classes("w-32")

        def add():
            create_composer(
                session,
                first_name=fn.value, last_name=ln.value,
                birth_year=int(by.value) if by.value else None,
                death_year=int(dy.value) if dy.value else None,
                nationality=nat.value,
            )
            table.rows = rows()
            for inp in [fn, ln, by, dy, nat]:
                inp.set_value("")

        ui.button(t("add"), on_click=add).props("color=primary")


def _conductors_panel(session) -> None:
    columns = [
        {"name": "last_name", "label": t("last_name"), "field": "last_name", "sortable": True},
        {"name": "first_name", "label": t("first_name"), "field": "first_name"},
    ]

    def rows():
        return [
            {"id": c.id, "last_name": c.last_name, "first_name": c.first_name}
            for c in list_conductors(session)
        ]

    table = ui.table(columns=columns, rows=rows(), row_key="id").classes("w-full")

    with ui.row().classes("mt-2 gap-2"):
        fn = ui.input(t("first_name")).classes("w-40")
        ln = ui.input(t("last_name")).classes("w-40")

        def add():
            create_conductor(session, first_name=fn.value, last_name=ln.value)
            table.rows = rows()
            fn.set_value("")
            ln.set_value("")

        ui.button(t("add"), on_click=add).props("color=primary")


def _artists_panel(session) -> None:
    columns = [
        {"name": "last_name", "label": t("last_name"), "field": "last_name", "sortable": True},
        {"name": "first_name", "label": t("first_name"), "field": "first_name"},
        {"name": "instrument", "label": t("instrument"), "field": "instrument"},
    ]

    def rows():
        return [
            {
                "id": a.id, "last_name": a.last_name,
                "first_name": a.first_name, "instrument": a.instrument,
            }
            for a in list_artists(session)
        ]

    table = ui.table(columns=columns, rows=rows(), row_key="id").classes("w-full")

    with ui.row().classes("mt-2 gap-2"):
        fn = ui.input(t("first_name")).classes("w-40")
        ln = ui.input(t("last_name")).classes("w-40")
        instr = ui.input(t("instrument")).classes("w-40")

        def add():
            create_artist(session, first_name=fn.value, last_name=ln.value, instrument=instr.value)
            table.rows = rows()
            for inp in [fn, ln, instr]:
                inp.set_value("")

        ui.button(t("add"), on_click=add).props("color=primary")


def _pieces_panel(session) -> None:
    # Columns: composer, title, key, opus — key before opus per spec
    columns = [
        {"name": "composer", "label": t("composer"), "field": "composer", "sortable": True},
        {"name": "title", "label": t("piece_title"), "field": "title", "sortable": True},
        {"name": "key", "label": t("key"), "field": "key"},
        {"name": "opus_number", "label": t("opus"), "field": "opus_number"},
    ]

    def rows():
        return [
            {
                "id": p.id, "composer": p.composer.full_name,
                "title": p.title, "key": p.key, "opus_number": p.opus_number,
            }
            for p in list_pieces(session)
        ]

    table = ui.table(columns=columns, rows=rows(), row_key="id").classes("w-full")

    composers = list_composers(session)
    composer_options = {c.id: c.full_name for c in composers}

    with ui.row().classes("mt-2 gap-2 items-center flex-wrap"):
        comp_sel = ui.select(composer_options, label=t("composer"), with_input=True).classes("w-48")
        title_inp = ui.input(t("piece_title")).classes("w-60")
        key_inp = ui.input(t("key")).classes("w-32")
        opus_inp = ui.input(t("opus")).classes("w-32")

        def add():
            if comp_sel.value and title_inp.value:
                create_piece(
                    session,
                    composer_id=comp_sel.value,
                    title=title_inp.value,
                    key=key_inp.value,
                    opus_number=opus_inp.value,
                )
                table.rows = rows()
                for inp in [title_inp, key_inp, opus_inp]:
                    inp.set_value("")
                comp_sel.set_value(None)

        ui.button(t("add"), on_click=add).props("color=primary")


def _venues_panel(session) -> None:
    columns = [
        {"name": "name", "label": t("col_venue"), "field": "name", "sortable": True},
        {"name": "city", "label": "City", "field": "city"},
        {"name": "country", "label": "Country", "field": "country"},
    ]

    def rows():
        return [
            {"id": v.id, "name": v.name, "city": v.city, "country": v.country}
            for v in list_venues(session)
        ]

    table = ui.table(columns=columns, rows=rows(), row_key="id").classes("w-full")

    with ui.row().classes("mt-2 gap-2"):
        name_inp = ui.input("Name").classes("w-48")
        city_inp = ui.input("City").classes("w-32")
        country_inp = ui.input("Country").classes("w-32")

        def add():
            if name_inp.value:
                create_venue(session, name=name_inp.value, city=city_inp.value,
                             country=country_inp.value)
                table.rows = rows()
                for inp in [name_inp, city_inp, country_inp]:
                    inp.set_value("")

        ui.button(t("add"), on_click=add).props("color=primary")
