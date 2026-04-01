from nicegui import ui

from app.database import get_session
from app.services.person_service import (
    create_artist,
    create_composer,
    create_conductor,
    list_artists,
    list_composers,
    list_conductors,
)
from app.services.piece_service import create_piece, list_pieces


def reference_data_page() -> None:
    session = get_session()

    with ui.tabs() as tabs:
        tab_composers = ui.tab("Composers")
        tab_conductors = ui.tab("Conductors")
        tab_artists = ui.tab("Artists")
        tab_pieces = ui.tab("Pieces")

    with ui.tab_panels(tabs, value=tab_composers).classes("w-full"):
        with ui.tab_panel(tab_composers):
            _composers_panel(session)
        with ui.tab_panel(tab_conductors):
            _conductors_panel(session)
        with ui.tab_panel(tab_artists):
            _artists_panel(session)
        with ui.tab_panel(tab_pieces):
            _pieces_panel(session)


def _composers_panel(session) -> None:
    columns = [
        {"name": "last_name", "label": "Last Name", "field": "last_name", "sortable": True},
        {"name": "first_name", "label": "First Name", "field": "first_name"},
        {"name": "birth_year", "label": "Born", "field": "birth_year"},
        {"name": "death_year", "label": "Died", "field": "death_year"},
        {"name": "nationality", "label": "Nationality", "field": "nationality"},
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

    with ui.row().classes("mt-2 gap-2"):
        fn = ui.input("First name").classes("w-40")
        ln = ui.input("Last name").classes("w-40")
        by = ui.input("Birth year").classes("w-24")
        dy = ui.input("Death year").classes("w-24")
        nat = ui.input("Nationality").classes("w-32")

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

        ui.button("Add", on_click=add).props("color=primary")


def _conductors_panel(session) -> None:
    columns = [
        {"name": "last_name", "label": "Last Name", "field": "last_name", "sortable": True},
        {"name": "first_name", "label": "First Name", "field": "first_name"},
    ]

    def rows():
        return [
            {"id": c.id, "last_name": c.last_name, "first_name": c.first_name}
            for c in list_conductors(session)
        ]

    table = ui.table(columns=columns, rows=rows(), row_key="id").classes("w-full")

    with ui.row().classes("mt-2 gap-2"):
        fn = ui.input("First name").classes("w-40")
        ln = ui.input("Last name").classes("w-40")

        def add():
            create_conductor(session, first_name=fn.value, last_name=ln.value)
            table.rows = rows()
            fn.set_value("")
            ln.set_value("")

        ui.button("Add", on_click=add).props("color=primary")


def _artists_panel(session) -> None:
    columns = [
        {"name": "last_name", "label": "Last Name", "field": "last_name", "sortable": True},
        {"name": "first_name", "label": "First Name", "field": "first_name"},
        {"name": "instrument", "label": "Instrument", "field": "instrument"},
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
        fn = ui.input("First name").classes("w-40")
        ln = ui.input("Last name").classes("w-40")
        instr = ui.input("Instrument").classes("w-40")

        def add():
            create_artist(session, first_name=fn.value, last_name=ln.value, instrument=instr.value)
            table.rows = rows()
            for inp in [fn, ln, instr]:
                inp.set_value("")

        ui.button("Add", on_click=add).props("color=primary")


def _pieces_panel(session) -> None:
    columns = [
        {"name": "composer", "label": "Composer", "field": "composer", "sortable": True},
        {"name": "title", "label": "Title", "field": "title", "sortable": True},
        {"name": "opus_number", "label": "Opus", "field": "opus_number"},
        {"name": "key", "label": "Key", "field": "key"},
    ]

    def rows():
        return [
            {"id": p.id, "composer": p.composer.full_name, "title": p.title,
             "opus_number": p.opus_number, "key": p.key}
            for p in list_pieces(session)
        ]

    table = ui.table(columns=columns, rows=rows(), row_key="id").classes("w-full")

    composers = list_composers(session)
    composer_options = {c.id: c.full_name for c in composers}

    with ui.row().classes("mt-2 gap-2 items-center"):
        comp_sel = ui.select(composer_options, label="Composer").classes("w-48")
        title_inp = ui.input("Title").classes("w-60")
        opus_inp = ui.input("Opus number").classes("w-32")
        key_inp = ui.input("Key").classes("w-32")

        def add():
            if comp_sel.value and title_inp.value:
                create_piece(session, composer_id=comp_sel.value, title=title_inp.value,
                             opus_number=opus_inp.value, key=key_inp.value)
                table.rows = rows()
                for inp in [title_inp, opus_inp, key_inp]:
                    inp.set_value("")
                comp_sel.set_value(None)

        ui.button("Add", on_click=add).props("color=primary")
