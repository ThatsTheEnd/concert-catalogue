from collections.abc import Callable

from loguru import logger
from nicegui import ui
from sqlalchemy.exc import IntegrityError

from app.database import get_session
from app.i18n import t
from app.utils import filter_rows
from app.services.orchestra_service import (
    create_orchestra,
    delete_orchestra,
    list_orchestras,
    update_orchestra,
)
from app.services.person_service import (
    create_artist,
    create_composer,
    create_conductor,
    delete_artist,
    delete_composer,
    delete_conductor,
    list_artists,
    list_composers,
    list_conductors,
    update_artist,
    update_composer,
    update_conductor,
)
from app.services.piece_service import create_piece, delete_piece, list_pieces, update_piece
from app.services.venue_service import create_venue, delete_venue, list_venues, update_venue


def reference_data_page() -> None:
    session = get_session()

    # Shared list of hooks: pieces panel registers a callback so that composers
    # panel can refresh the composer drop-down after adding a new composer.
    comp_refresh_hooks: list = []

    with ui.tabs() as tabs:
        tab_orchestras = ui.tab(t("orchestras"))
        tab_composers = ui.tab(t("composers"))
        tab_conductors = ui.tab(t("conductors"))
        tab_artists = ui.tab(t("artists"))
        tab_pieces = ui.tab(t("pieces"))
        tab_venues = ui.tab(t("venue"))

    with ui.tab_panels(tabs, value=tab_orchestras).classes("w-full"):
        with ui.tab_panel(tab_orchestras):
            _orchestras_panel(session)
        with ui.tab_panel(tab_composers):
            _composers_panel(session, comp_refresh_hooks)
        with ui.tab_panel(tab_conductors):
            _conductors_panel(session)
        with ui.tab_panel(tab_artists):
            _artists_panel(session)
        with ui.tab_panel(tab_pieces):
            _pieces_panel(session, comp_refresh_hooks)
        with ui.tab_panel(tab_venues):
            _venues_panel(session)


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------

def _add_action_slot(table: ui.table) -> None:
    """Inject edit/delete icon buttons into a column named 'actions'."""
    table.add_slot(
        "body-cell-actions",
        r"""
        <q-td :props="props">
            <q-btn icon="edit" flat dense round size="sm"
                   @click="$parent.$emit('edit_row', props.row)" />
            <q-btn icon="delete" flat dense round size="sm" color="negative"
                   @click="$parent.$emit('delete_row', props.row)" />
        </q-td>
        """,
    )


def _delete_dialog(on_confirm: Callable[[], None]) -> ui.dialog:
    """Return a ready-made delete-confirmation dialog."""
    with ui.dialog() as dlg, ui.card():
        ui.label(t("delete_ref_confirm")).classes("text-base font-medium")
        ui.label(t("delete_warning")).classes("text-sm opacity-70")
        with ui.row().classes("mt-3 gap-2 justify-end"):
            ui.button(t("delete"), on_click=on_confirm).props("color=negative")
            ui.button(t("cancel"), on_click=dlg.close).props("flat")
    return dlg


# ---------------------------------------------------------------------------
# Orchestras
# ---------------------------------------------------------------------------

def _orchestras_panel(session) -> None:
    columns = [
        {"name": "name", "label": t("col_orchestra"), "field": "name", "sortable": True},
        {"name": "actions", "label": "", "field": "id", "align": "right"},
    ]

    def rows():
        return [{"id": o.id, "name": o.name} for o in list_orchestras(session)]

    all_rows = rows()

    filter_inp = ui.input(placeholder=t("filter_placeholder")).classes("w-64 mb-2")
    table = ui.table(columns=columns, rows=all_rows, row_key="id").classes("w-full")
    _add_action_slot(table)

    def refresh():
        nonlocal all_rows
        all_rows = rows()
        table.rows = filter_rows(all_rows, filter_inp.value)

    def on_filter(e):
        table.rows = filter_rows(all_rows, e.value)

    filter_inp.on_value_change(on_filter)

    # ---- Edit dialog ----
    edit_id: list[int] = [0]
    with ui.dialog() as edit_dlg, ui.card().classes("min-w-72"):
        ui.label(t("edit")).classes("text-base font-medium mb-2")
        e_name = ui.input(t("col_orchestra")).classes("w-full")

        def save_edit():
            update_orchestra(session, edit_id[0], name=e_name.value.strip())
            refresh()
            edit_dlg.close()

        with ui.row().classes("mt-3 gap-2 justify-end"):
            ui.button(t("save"), on_click=save_edit).props("color=primary")
            ui.button(t("cancel"), on_click=edit_dlg.close).props("flat")

    def on_edit(e):
        row = e.args
        edit_id[0] = row["id"]
        e_name.set_value(row["name"])
        edit_dlg.open()

    table.on("edit_row", on_edit)

    # ---- Delete dialog ----
    delete_id: list[int] = [0]

    def do_delete():
        try:
            delete_orchestra(session, delete_id[0])
            refresh()
            delete_dlg.close()
        except IntegrityError:
            session.rollback()
            delete_dlg.close()
            ui.notify(t("delete_ref_error"), type="negative")

    delete_dlg = _delete_dialog(do_delete)

    def on_delete(e):
        delete_id[0] = e.args["id"]
        delete_dlg.open()

    table.on("delete_row", on_delete)

    # ---- Add form ----
    with ui.row().classes("mt-2 gap-2"):
        name_inp = ui.input(t("col_orchestra")).classes("w-60")

        def add():
            if name_inp.value.strip():
                logger.info("UI: adding orchestra {!r}", name_inp.value)
                create_orchestra(session, name=name_inp.value.strip())
                name_inp.set_value("")
                refresh()

        ui.button(t("add"), on_click=add).props("color=primary")


# ---------------------------------------------------------------------------
# Composers
# ---------------------------------------------------------------------------

def _composers_panel(session, comp_refresh_hooks: list) -> None:
    columns = [
        {"name": "last_name", "label": t("last_name"), "field": "last_name", "sortable": True},
        {"name": "first_name", "label": t("first_name"), "field": "first_name"},
        {"name": "birth_year", "label": t("birth_year"), "field": "birth_year"},
        {"name": "death_year", "label": t("death_year"), "field": "death_year"},
        {"name": "catalogue", "label": t("catalogue_label"), "field": "catalogue"},
        {"name": "actions", "label": "", "field": "id", "align": "right"},
    ]

    def rows():
        return [
            {
                "id": c.id, "last_name": c.last_name, "first_name": c.first_name,
                "birth_year": c.birth_year or "", "death_year": c.death_year or "",
                "catalogue": c.catalogue,
            }
            for c in list_composers(session)
        ]

    all_rows = rows()

    filter_inp = ui.input(placeholder=t("filter_placeholder")).classes("w-64 mb-2")
    table = ui.table(columns=columns, rows=all_rows, row_key="id").classes("w-full")
    _add_action_slot(table)

    def refresh():
        nonlocal all_rows
        all_rows = rows()
        table.rows = filter_rows(all_rows, filter_inp.value)
        for hook in comp_refresh_hooks:
            hook()

    def on_filter(e):
        table.rows = filter_rows(all_rows, e.value)

    filter_inp.on_value_change(on_filter)

    # ---- Edit dialog ----
    edit_id: list[int] = [0]
    with ui.dialog() as edit_dlg, ui.card().classes("min-w-80"):
        ui.label(t("edit")).classes("text-base font-medium mb-2")
        e_fn = ui.input(t("first_name")).classes("w-full")
        e_ln = ui.input(t("last_name")).classes("w-full")
        e_by = ui.input(t("birth_year")).classes("w-full")
        e_dy = ui.input(t("death_year")).classes("w-full")
        e_cat = ui.input(t("catalogue_label")).classes("w-full")

        def save_edit():
            update_composer(
                session, edit_id[0],
                first_name=e_fn.value, last_name=e_ln.value,
                birth_year=int(e_by.value) if e_by.value else None,
                death_year=int(e_dy.value) if e_dy.value else None,
                catalogue=e_cat.value,
            )
            refresh()
            edit_dlg.close()

        with ui.row().classes("mt-3 gap-2 justify-end"):
            ui.button(t("save"), on_click=save_edit).props("color=primary")
            ui.button(t("cancel"), on_click=edit_dlg.close).props("flat")

    def on_edit(e):
        row = e.args
        edit_id[0] = row["id"]
        e_fn.set_value(row["first_name"])
        e_ln.set_value(row["last_name"])
        e_by.set_value(str(row["birth_year"]) if row["birth_year"] else "")
        e_dy.set_value(str(row["death_year"]) if row["death_year"] else "")
        e_cat.set_value(row["catalogue"])
        edit_dlg.open()

    table.on("edit_row", on_edit)

    # ---- Delete dialog ----
    delete_id: list[int] = [0]

    def do_delete():
        try:
            delete_composer(session, delete_id[0])
            refresh()
            delete_dlg.close()
        except IntegrityError:
            session.rollback()
            delete_dlg.close()
            ui.notify(t("delete_ref_error"), type="negative")

    delete_dlg = _delete_dialog(do_delete)

    def on_delete(e):
        delete_id[0] = e.args["id"]
        delete_dlg.open()

    table.on("delete_row", on_delete)

    # ---- Add form ----
    with ui.row().classes("mt-2 gap-2 flex-wrap"):
        fn = ui.input(t("first_name")).classes("w-40")
        ln = ui.input(t("last_name")).classes("w-40")
        by = ui.input(t("birth_year")).classes("w-24")
        dy = ui.input(t("death_year")).classes("w-24")
        cat = ui.input(t("catalogue_label")).classes("w-40")

        def add():
            logger.info("UI: adding composer {} {}", fn.value, ln.value)
            create_composer(
                session,
                first_name=fn.value, last_name=ln.value,
                birth_year=int(by.value) if by.value else None,
                death_year=int(dy.value) if dy.value else None,
                catalogue=cat.value,
            )
            for inp in [fn, ln, by, dy, cat]:
                inp.set_value("")
            refresh()

        ui.button(t("add"), on_click=add).props("color=primary")


# ---------------------------------------------------------------------------
# Conductors
# ---------------------------------------------------------------------------

def _conductors_panel(session) -> None:
    columns = [
        {"name": "last_name", "label": t("last_name"), "field": "last_name", "sortable": True},
        {"name": "first_name", "label": t("first_name"), "field": "first_name"},
        {"name": "actions", "label": "", "field": "id", "align": "right"},
    ]

    def rows():
        return [
            {"id": c.id, "last_name": c.last_name, "first_name": c.first_name}
            for c in list_conductors(session)
        ]

    all_rows = rows()

    filter_inp = ui.input(placeholder=t("filter_placeholder")).classes("w-64 mb-2")
    table = ui.table(columns=columns, rows=all_rows, row_key="id").classes("w-full")
    _add_action_slot(table)

    def refresh():
        nonlocal all_rows
        all_rows = rows()
        table.rows = filter_rows(all_rows, filter_inp.value)

    def on_filter(e):
        table.rows = filter_rows(all_rows, e.value)

    filter_inp.on_value_change(on_filter)

    # ---- Edit dialog ----
    edit_id: list[int] = [0]
    with ui.dialog() as edit_dlg, ui.card().classes("min-w-72"):
        ui.label(t("edit")).classes("text-base font-medium mb-2")
        e_fn = ui.input(t("first_name")).classes("w-full")
        e_ln = ui.input(t("last_name")).classes("w-full")

        def save_edit():
            update_conductor(session, edit_id[0], first_name=e_fn.value, last_name=e_ln.value)
            refresh()
            edit_dlg.close()

        with ui.row().classes("mt-3 gap-2 justify-end"):
            ui.button(t("save"), on_click=save_edit).props("color=primary")
            ui.button(t("cancel"), on_click=edit_dlg.close).props("flat")

    def on_edit(e):
        row = e.args
        edit_id[0] = row["id"]
        e_fn.set_value(row["first_name"])
        e_ln.set_value(row["last_name"])
        edit_dlg.open()

    table.on("edit_row", on_edit)

    # ---- Delete dialog ----
    delete_id: list[int] = [0]

    def do_delete():
        try:
            delete_conductor(session, delete_id[0])
            refresh()
            delete_dlg.close()
        except IntegrityError:
            session.rollback()
            delete_dlg.close()
            ui.notify(t("delete_ref_error"), type="negative")

    delete_dlg = _delete_dialog(do_delete)

    def on_delete(e):
        delete_id[0] = e.args["id"]
        delete_dlg.open()

    table.on("delete_row", on_delete)

    # ---- Add form ----
    with ui.row().classes("mt-2 gap-2"):
        fn = ui.input(t("first_name")).classes("w-40")
        ln = ui.input(t("last_name")).classes("w-40")

        def add():
            logger.info("UI: adding conductor {} {}", fn.value, ln.value)
            create_conductor(session, first_name=fn.value, last_name=ln.value)
            fn.set_value("")
            ln.set_value("")
            refresh()

        ui.button(t("add"), on_click=add).props("color=primary")


# ---------------------------------------------------------------------------
# Artists
# ---------------------------------------------------------------------------

def _artists_panel(session) -> None:
    columns = [
        {"name": "last_name", "label": t("last_name"), "field": "last_name", "sortable": True},
        {"name": "first_name", "label": t("first_name"), "field": "first_name"},
        {"name": "instrument", "label": t("instrument"), "field": "instrument"},
        {"name": "actions", "label": "", "field": "id", "align": "right"},
    ]

    def rows():
        return [
            {
                "id": a.id, "last_name": a.last_name,
                "first_name": a.first_name, "instrument": a.instrument,
            }
            for a in list_artists(session)
        ]

    all_rows = rows()

    filter_inp = ui.input(placeholder=t("filter_placeholder")).classes("w-64 mb-2")
    table = ui.table(columns=columns, rows=all_rows, row_key="id").classes("w-full")
    _add_action_slot(table)

    def refresh():
        nonlocal all_rows
        all_rows = rows()
        table.rows = filter_rows(all_rows, filter_inp.value)

    def on_filter(e):
        table.rows = filter_rows(all_rows, e.value)

    filter_inp.on_value_change(on_filter)

    # ---- Edit dialog ----
    edit_id: list[int] = [0]
    with ui.dialog() as edit_dlg, ui.card().classes("min-w-72"):
        ui.label(t("edit")).classes("text-base font-medium mb-2")
        e_fn = ui.input(t("first_name")).classes("w-full")
        e_ln = ui.input(t("last_name")).classes("w-full")
        e_instr = ui.input(t("instrument")).classes("w-full")

        def save_edit():
            update_artist(
                session, edit_id[0],
                first_name=e_fn.value, last_name=e_ln.value, instrument=e_instr.value,
            )
            refresh()
            edit_dlg.close()

        with ui.row().classes("mt-3 gap-2 justify-end"):
            ui.button(t("save"), on_click=save_edit).props("color=primary")
            ui.button(t("cancel"), on_click=edit_dlg.close).props("flat")

    def on_edit(e):
        row = e.args
        edit_id[0] = row["id"]
        e_fn.set_value(row["first_name"])
        e_ln.set_value(row["last_name"])
        e_instr.set_value(row["instrument"])
        edit_dlg.open()

    table.on("edit_row", on_edit)

    # ---- Delete dialog ----
    delete_id: list[int] = [0]

    def do_delete():
        try:
            delete_artist(session, delete_id[0])
            refresh()
            delete_dlg.close()
        except IntegrityError:
            session.rollback()
            delete_dlg.close()
            ui.notify(t("delete_ref_error"), type="negative")

    delete_dlg = _delete_dialog(do_delete)

    def on_delete(e):
        delete_id[0] = e.args["id"]
        delete_dlg.open()

    table.on("delete_row", on_delete)

    # ---- Add form ----
    with ui.row().classes("mt-2 gap-2"):
        fn = ui.input(t("first_name")).classes("w-40")
        ln = ui.input(t("last_name")).classes("w-40")
        instr = ui.input(t("instrument")).classes("w-40")

        def add():
            logger.info("UI: adding artist {} {} ({})", fn.value, ln.value, instr.value)
            create_artist(session, first_name=fn.value, last_name=ln.value, instrument=instr.value)
            for inp in [fn, ln, instr]:
                inp.set_value("")
            refresh()

        ui.button(t("add"), on_click=add).props("color=primary")


# ---------------------------------------------------------------------------
# Pieces
# ---------------------------------------------------------------------------

def _pieces_panel(session, comp_refresh_hooks: list) -> None:
    columns = [
        {"name": "composer", "label": t("composer"), "field": "composer", "sortable": True},
        {"name": "title", "label": t("piece_title"), "field": "title", "sortable": True},
        {"name": "key", "label": t("key"), "field": "key"},
        {"name": "catalogue_number", "label": t("catalogue_number"), "field": "catalogue_number"},
        {"name": "actions", "label": "", "field": "id", "align": "right"},
    ]

    def rows():
        return [
            {
                "id": p.id, "composer": p.composer.full_name, "composer_id": p.composer_id,
                "title": p.title, "key": p.key, "catalogue_number": p.catalogue_number,
            }
            for p in list_pieces(session)
        ]

    def composer_options():
        return {c.id: c.full_name for c in list_composers(session)}

    all_rows = rows()
    current_comp_opts = composer_options()

    filter_inp = ui.input(placeholder=t("filter_placeholder")).classes("w-64 mb-2")
    table = ui.table(columns=columns, rows=all_rows, row_key="id").classes("w-full")
    _add_action_slot(table)

    def refresh():
        nonlocal all_rows, current_comp_opts
        all_rows = rows()
        current_comp_opts = composer_options()
        table.rows = filter_rows(all_rows, filter_inp.value)
        comp_sel.options = current_comp_opts
        comp_sel.update()

    # Register with the shared hook list so composers panel can trigger a refresh.
    comp_refresh_hooks.append(refresh)

    def on_filter(e):
        table.rows = filter_rows(all_rows, e.value)

    filter_inp.on_value_change(on_filter)

    # ---- Edit dialog ----
    edit_id: list[int] = [0]
    with ui.dialog() as edit_dlg, ui.card().classes("min-w-80"):
        ui.label(t("edit")).classes("text-base font-medium mb-2")
        e_comp = (
            ui.select(current_comp_opts, label=t("composer"), with_input=True).classes("w-full")
        )
        e_title = ui.input(t("piece_title")).classes("w-full")
        e_key = ui.input(t("key")).classes("w-full")
        e_cat = ui.input(t("catalogue_number")).classes("w-full")

        def save_edit():
            update_piece(
                session, edit_id[0],
                composer_id=e_comp.value, title=e_title.value,
                key=e_key.value, catalogue_number=e_cat.value,
            )
            refresh()
            edit_dlg.close()

        with ui.row().classes("mt-3 gap-2 justify-end"):
            ui.button(t("save"), on_click=save_edit).props("color=primary")
            ui.button(t("cancel"), on_click=edit_dlg.close).props("flat")

    def on_edit(e):
        row = e.args
        edit_id[0] = row["id"]
        e_comp.options = current_comp_opts
        e_comp.set_value(row["composer_id"])
        e_title.set_value(row["title"])
        e_key.set_value(row["key"])
        e_cat.set_value(row["catalogue_number"])
        edit_dlg.open()

    table.on("edit_row", on_edit)

    # ---- Delete dialog ----
    delete_id: list[int] = [0]

    def do_delete():
        try:
            delete_piece(session, delete_id[0])
            refresh()
            delete_dlg.close()
        except IntegrityError:
            session.rollback()
            delete_dlg.close()
            ui.notify(t("delete_ref_error"), type="negative")

    delete_dlg = _delete_dialog(do_delete)

    def on_delete(e):
        delete_id[0] = e.args["id"]
        delete_dlg.open()

    table.on("delete_row", on_delete)

    # ---- Add form ----
    with ui.row().classes("mt-2 gap-2 items-center flex-wrap"):
        comp_sel = (
            ui.select(current_comp_opts, label=t("composer"), with_input=True).classes("w-48")
        )
        title_inp = ui.input(t("piece_title")).classes("w-60")
        key_inp = ui.input(t("key")).classes("w-32")
        cat_inp = ui.input(t("catalogue_number")).classes("w-32")

        def add():
            if comp_sel.value and title_inp.value:
                logger.info(
                    "UI: adding piece {!r} (composer_id={})", title_inp.value, comp_sel.value
                )
                create_piece(
                    session,
                    composer_id=comp_sel.value,
                    title=title_inp.value,
                    key=key_inp.value,
                    catalogue_number=cat_inp.value,
                )
                for inp in [title_inp, key_inp, cat_inp]:
                    inp.set_value("")
                comp_sel.set_value(None)
                refresh()

        ui.button(t("add"), on_click=add).props("color=primary")


# ---------------------------------------------------------------------------
# Venues
# ---------------------------------------------------------------------------

def _venues_panel(session) -> None:
    columns = [
        {"name": "name", "label": t("col_venue"), "field": "name", "sortable": True},
        {"name": "city", "label": t("city"), "field": "city"},
        {"name": "country", "label": t("country"), "field": "country"},
        {"name": "actions", "label": "", "field": "id", "align": "right"},
    ]

    def rows():
        return [
            {"id": v.id, "name": v.name, "city": v.city, "country": v.country}
            for v in list_venues(session)
        ]

    all_rows = rows()

    filter_inp = ui.input(placeholder=t("filter_placeholder")).classes("w-64 mb-2")
    table = ui.table(columns=columns, rows=all_rows, row_key="id").classes("w-full")
    _add_action_slot(table)

    def refresh():
        nonlocal all_rows
        all_rows = rows()
        table.rows = filter_rows(all_rows, filter_inp.value)

    def on_filter(e):
        table.rows = filter_rows(all_rows, e.value)

    filter_inp.on_value_change(on_filter)

    # ---- Edit dialog ----
    edit_id: list[int] = [0]
    with ui.dialog() as edit_dlg, ui.card().classes("min-w-72"):
        ui.label(t("edit")).classes("text-base font-medium mb-2")
        e_name = ui.input(t("col_venue")).classes("w-full")
        e_city = ui.input(t("city")).classes("w-full")
        e_country = ui.input(t("country")).classes("w-full")

        def save_edit():
            update_venue(
                session, edit_id[0],
                name=e_name.value, city=e_city.value, country=e_country.value,
            )
            refresh()
            edit_dlg.close()

        with ui.row().classes("mt-3 gap-2 justify-end"):
            ui.button(t("save"), on_click=save_edit).props("color=primary")
            ui.button(t("cancel"), on_click=edit_dlg.close).props("flat")

    def on_edit(e):
        row = e.args
        edit_id[0] = row["id"]
        e_name.set_value(row["name"])
        e_city.set_value(row["city"])
        e_country.set_value(row["country"])
        edit_dlg.open()

    table.on("edit_row", on_edit)

    # ---- Delete dialog ----
    delete_id: list[int] = [0]

    def do_delete():
        try:
            delete_venue(session, delete_id[0])
            refresh()
            delete_dlg.close()
        except IntegrityError:
            session.rollback()
            delete_dlg.close()
            ui.notify(t("delete_ref_error"), type="negative")

    delete_dlg = _delete_dialog(do_delete)

    def on_delete(e):
        delete_id[0] = e.args["id"]
        delete_dlg.open()

    table.on("delete_row", on_delete)

    # ---- Add form ----
    with ui.row().classes("mt-2 gap-2"):
        name_inp = ui.input(t("col_venue")).classes("w-48")
        city_inp = ui.input(t("city")).classes("w-32")
        country_inp = ui.input(t("country")).classes("w-32")

        def add():
            if name_inp.value:
                logger.info("UI: adding venue {!r}, {}", name_inp.value, city_inp.value)
                create_venue(session, name=name_inp.value, city=city_inp.value,
                             country=country_inp.value)
                for inp in [name_inp, city_inp, country_inp]:
                    inp.set_value("")
                refresh()

        ui.button(t("add"), on_click=add).props("color=primary")

