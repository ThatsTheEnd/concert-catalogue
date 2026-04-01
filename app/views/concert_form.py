from datetime import date

from loguru import logger
from nicegui import ui

from app.database import get_session
from app.i18n import t
from app.models.attachment import Attachment
from app.services.concert_service import create_concert, get_concert, update_concert
from app.services.orchestra_service import list_orchestras
from app.services.person_service import list_artists, list_conductors
from app.services.piece_service import search_pieces
from app.services.venue_service import list_venues
from app.storage.file_handler import save_upload


def concert_form_page(concert_id: int | None = None) -> None:
    session = get_session()
    existing = get_concert(session, concert_id) if concert_id else None
    is_edit = existing is not None

    # Pre-load reference data for autocomplete selects
    all_conductors = {c.id: c.full_name for c in list_conductors(session)}
    all_conductors_with_none = {None: "—", **all_conductors}
    all_artists = {a.id: f"{a.full_name} ({a.instrument})" for a in list_artists(session)}
    all_orchestras = {o.id: o.name for o in list_orchestras(session)}
    all_orchestras_with_none = {None: "—", **all_orchestras}
    all_venues = {v.id: str(v) for v in list_venues(session)}
    all_venues_with_none = {None: "—", **all_venues}

    form: dict = {
        "date": str(existing.date) if existing else str(date.today()),
        "orchestra_id": existing.orchestra_id if existing else None,
        "venue_id": existing.venue_id if existing else None,
        "conductor_id": existing.conductor_id if existing else None,
        "choir": existing.choir if existing else "",
        "choir_director_id": existing.choir_director_id if existing else None,
        "notes": existing.notes if existing else "",
        "pieces": [
            {
                "piece_id": lnk.piece_id,
                "sort_order": lnk.sort_order,
                "notes": lnk.notes,
                "_label": f"{lnk.piece.composer.full_name} — {lnk.piece.display_name}",
            }
            for lnk in (existing.piece_links if existing else [])
        ],
        "artists": [
            {"artist_id": lnk.artist_id, "role": lnk.role, "_label": lnk.artist.full_name}
            for lnk in (existing.artist_links if existing else [])
        ],
        "new_attachments": [],
    }

    heading = t("edit_concert_heading") if is_edit else t("add_concert_heading")
    ui.label(heading).classes("text-2xl font-bold mb-4")

    # ── Date picker ──────────────────────────────────────────────────────────
    ui.label(t("date")).classes("font-medium mt-2")
    date_picker = ui.date(value=form["date"]).classes("w-full")
    date_picker.on_value_change(lambda e: form.__setitem__("date", e.value))

    # ── Basic fields ─────────────────────────────────────────────────────────
    with ui.grid(columns=2).classes("w-full gap-4 mt-2"):
        orchestra_select = ui.select(
            options=all_orchestras_with_none,
            label=t("orchestra"),
            value=form["orchestra_id"],
            with_input=True,
        ).classes("w-full")
        orchestra_select.bind_value(form, "orchestra_id")

        venue_select = ui.select(
            options=all_venues_with_none,
            label=t("venue"),
            value=form["venue_id"],
            with_input=True,
        ).classes("w-full")
        venue_select.bind_value(form, "venue_id")

    # ── Conductor ────────────────────────────────────────────────────────────
    ui.label(t("conductor")).classes("font-medium mt-4")
    conductor_select = ui.select(
        options=all_conductors_with_none,
        label=t("search_conductor"),
        value=form["conductor_id"],
        with_input=True,
        clearable=True,
    ).classes("w-full")
    conductor_select.bind_value(form, "conductor_id")

    # ── Choir ────────────────────────────────────────────────────────────────
    with ui.expansion(t("choir"), icon="queue_music").classes("w-full mt-2"):
        with ui.grid(columns=2).classes("w-full gap-4"):
            ui.input(t("choir_name"), value=form["choir"]).bind_value(form, "choir")
            choir_dir_select = ui.select(
                options=all_conductors_with_none,
                label=t("choir_director_label"),
                value=form["choir_director_id"],
                with_input=True,
                clearable=True,
            ).classes("w-full")
            choir_dir_select.bind_value(form, "choir_director_id")

    # ── Program ──────────────────────────────────────────────────────────────
    ui.label(t("program")).classes("font-medium mt-4")
    piece_rows_container = ui.column().classes("w-full gap-2")

    def render_piece_rows():
        piece_rows_container.clear()
        with piece_rows_container:
            for i, item in enumerate(form["pieces"]):
                with ui.row().classes("items-center gap-2 w-full"):
                    ui.label(f"{i + 1}.").classes("text-gray-400 w-6 text-right shrink-0")
                    ui.label(item["_label"]).classes("flex-1 text-sm")
                    ui.input(t("piece_notes"), value=item["notes"]).classes("w-36").on(
                        "update:model-value",
                        lambda e, idx=i: form["pieces"][idx].__setitem__("notes", e.value),
                    )
                    ui.button(
                        icon="arrow_upward",
                        on_click=lambda _, idx=i: _move_piece(idx, -1),
                    ).props("flat dense")
                    ui.button(
                        icon="arrow_downward",
                        on_click=lambda _, idx=i: _move_piece(idx, 1),
                    ).props("flat dense")
                    ui.button(
                        icon="delete",
                        on_click=lambda _, idx=i: _remove_piece(idx),
                    ).props("flat dense color=negative")

    def _move_piece(idx: int, direction: int):
        new_idx = idx + direction
        if 0 <= new_idx < len(form["pieces"]):
            form["pieces"][idx], form["pieces"][new_idx] = (
                form["pieces"][new_idx], form["pieces"][idx]
            )
        render_piece_rows()

    def _remove_piece(idx: int):
        logger.debug("Removing piece at index {}", idx)
        form["pieces"].pop(idx)
        render_piece_rows()

    # Add piece — server-side filtered (pieces can be many)
    with ui.row().classes("items-center gap-2 mt-2"):
        piece_add_select = ui.select(
            options={}, label=t("search_piece"), with_input=True
        ).classes("flex-1")

        def on_piece_filter(e):
            query = e.args if isinstance(e.args, str) else ""
            results = search_pieces(session, query)
            piece_add_select.options = {
                p.id: f"{p.composer.full_name} — {p.display_name}" for p in results
            }
            piece_add_select.update()

        piece_add_select.on("filter", on_piece_filter)

        def add_piece():
            pid = piece_add_select.value
            label = (piece_add_select.options or {}).get(pid, "")
            if pid and label:
                logger.debug("Adding piece id={} to concert form", pid)
                form["pieces"].append({
                    "piece_id": pid,
                    "sort_order": len(form["pieces"]),
                    "notes": "",
                    "_label": label,
                })
                piece_add_select.set_value(None)
                render_piece_rows()

        ui.button(t("add_piece"), on_click=add_piece)

    render_piece_rows()

    # ── Soloists / Artists ───────────────────────────────────────────────────
    ui.label(t("soloists")).classes("font-medium mt-4")
    artist_rows_container = ui.column().classes("w-full gap-2")

    def render_artist_rows():
        artist_rows_container.clear()
        with artist_rows_container:
            for i, item in enumerate(form["artists"]):
                with ui.row().classes("items-center gap-2 w-full"):
                    ui.label(item["_label"]).classes("flex-1 text-sm")
                    ui.input(t("role_instrument"), value=item["role"]).classes("w-40").on(
                        "update:model-value",
                        lambda e, idx=i: form["artists"][idx].__setitem__("role", e.value),
                    )
                    ui.button(
                        icon="delete",
                        on_click=lambda _, idx=i: _remove_artist(idx),
                    ).props("flat dense color=negative")

    def _remove_artist(idx: int):
        logger.debug("Removing artist at index {}", idx)
        form["artists"].pop(idx)
        render_artist_rows()

    with ui.row().classes("items-center gap-2 mt-2"):
        artist_add_select = ui.select(
            options=all_artists,
            label=t("search_artist"),
            with_input=True,
        ).classes("flex-1")

        def add_artist():
            aid = artist_add_select.value
            label = all_artists.get(aid, "")
            if aid and label:
                logger.debug("Adding artist id={} to concert form", aid)
                # Show only name (strip instrument hint) in the row
                name_only = label.split(" (")[0]
                form["artists"].append({"artist_id": aid, "role": "", "_label": name_only})
                artist_add_select.set_value(None)
                render_artist_rows()

        ui.button(t("add_artist"), on_click=add_artist)

    render_artist_rows()

    # ── Attachments ──────────────────────────────────────────────────────────
    with ui.expansion(t("attachments"), icon="attach_file").classes("w-full mt-2"):
        for atype, label_key in [
            ("ticket", "upload_ticket"),
            ("program", "upload_program"),
            ("review", "upload_reviews"),
        ]:
            with ui.row().classes("items-center gap-2 mt-2"):
                ui.label(t(label_key)).classes("w-48 text-sm")
                uploader = (
                    ui.upload(
                        label=t(label_key),
                        multiple=(atype != "ticket"),
                        auto_upload=True,
                    )
                    .classes("flex-1")
                )

                def handle_upload(e, at=atype):
                    form["new_attachments"].append((at, e.name, e.content.read()))

                uploader.on_upload(handle_upload)

    # ── Notes ────────────────────────────────────────────────────────────────
    ui.label(t("notes")).classes("font-medium mt-4")
    ui.textarea(t("notes"), value=form["notes"]).classes("w-full").bind_value(form, "notes")

    # ── Save / Cancel ────────────────────────────────────────────────────────
    with ui.row().classes("gap-3 mt-6"):
        ui.button(t("cancel"), on_click=lambda: ui.navigate.to("/concerts")).props("outline")
        ui.button(
            t("save"), on_click=lambda: _save(form, concert_id, session, is_edit)
        ).props("color=primary")


def _save(form: dict, concert_id: int | None, session, is_edit: bool) -> None:
    pieces = [
        {"piece_id": item["piece_id"], "sort_order": i, "notes": item.get("notes", "")}
        for i, item in enumerate(form["pieces"])
    ]
    artists = [
        {"artist_id": item["artist_id"], "role": item.get("role", "")}
        for item in form["artists"]
    ]

    try:
        concert_date = date.fromisoformat(form["date"])
    except (ValueError, TypeError):
        ui.notify(t("date") + ": invalid format", type="negative")
        return

    logger.info("Saving concert (edit={}) date={}", is_edit, concert_date)

    if is_edit and concert_id:
        concert = get_concert(session, concert_id)
        if concert:
            concert.piece_links.clear()
            concert.artist_links.clear()
            session.flush()
        update_concert(
            session, concert_id,
            date=concert_date,
            orchestra_id=form["orchestra_id"],
            venue_id=form["venue_id"],
            conductor_id=form["conductor_id"],
            choir=form["choir"],
            choir_director_id=form["choir_director_id"],
            notes=form["notes"],
        )
        from app.models import ConcertArtist, ConcertPiece
        for item in pieces:
            session.add(ConcertPiece(concert_id=concert_id, **item))
        for item in artists:
            session.add(ConcertArtist(concert_id=concert_id, **item))
        session.commit()
        target_id = concert_id
    else:
        concert = create_concert(
            session,
            date=concert_date,
            orchestra_id=form["orchestra_id"],
            venue_id=form["venue_id"],
            conductor_id=form["conductor_id"],
            choir=form["choir"],
            choir_director_id=form["choir_director_id"],
            notes=form["notes"],
            pieces=pieces,
            artists=artists,
        )
        target_id = concert.id

    for atype, filename, content in form.get("new_attachments", []):
        file_path = save_upload(target_id, atype, filename, content)
        session.add(Attachment(
            concert_id=target_id,
            type=atype,
            file_path=file_path,
            original_filename=filename,
        ))
    session.commit()
    session.close()

    ui.notify(t("saved"), type="positive")
    ui.navigate.to(f"/concerts/{target_id}")
