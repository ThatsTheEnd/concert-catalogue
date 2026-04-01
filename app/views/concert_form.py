from datetime import date

from nicegui import ui

from app.database import get_session
from app.models.attachment import Attachment
from app.services.concert_service import create_concert, get_concert, update_concert
from app.services.person_service import search_artists, search_conductors
from app.services.piece_service import search_pieces
from app.storage.file_handler import save_upload


def concert_form_page(concert_id: int | None = None) -> None:
    session = get_session()
    existing = get_concert(session, concert_id) if concert_id else None
    is_edit = existing is not None

    # Form state
    form = {
        "date": str(existing.date) if existing else str(date.today()),
        "title": existing.title if existing else "",
        "orchestra": existing.orchestra if existing else "",
        "venue_id": existing.venue_id if existing else None,
        "conductor_id": existing.conductor_id if existing else None,
        "notes": existing.notes if existing else "",
        "pieces": [
            {
                "piece_id": lnk.piece_id, "sort_order": lnk.sort_order,
                "notes": lnk.notes, "_label": lnk.piece.display_name,
            }
            for lnk in (existing.piece_links if existing else [])
        ],
        "artists": [
            {"artist_id": lnk.artist_id, "role": lnk.role, "_label": lnk.artist.full_name}
            for lnk in (existing.artist_links if existing else [])
        ],
        "new_attachments": [],  # list of (type, filename, bytes)
    }

    ui.label("Edit Concert" if is_edit else "Add Concert").classes("text-2xl font-bold mb-4")

    # Basic fields
    with ui.grid(columns=2).classes("w-full gap-4"):
        ui.input("Date (YYYY-MM-DD)", value=form["date"]).bind_value(form, "date")
        ui.input("Title", value=form["title"]).bind_value(form, "title")
        ui.input("Orchestra", value=form["orchestra"]).bind_value(form, "orchestra")

    # Conductor autocomplete
    ui.label("Conductor").classes("font-medium mt-4")
    conductor_select = ui.select(
        options=[], label="Type to search conductors…", with_input=True, value=form["conductor_id"]
    ).classes("w-full")

    def search_cond(e):
        results = search_conductors(session, e.value or "")
        conductor_select.options = {c.id: c.full_name for c in results}
        conductor_select.update()

    conductor_select.on("filter", search_cond)
    conductor_select.bind_value(form, "conductor_id")

    # Program section
    ui.label("Program (in performance order)").classes("font-medium mt-4")
    piece_rows_container = ui.column().classes("w-full gap-2")

    def render_piece_rows():
        piece_rows_container.clear()
        with piece_rows_container:
            for i, item in enumerate(form["pieces"]):
                with ui.row().classes("items-center gap-2 w-full"):
                    ui.label(f"{i + 1}.").classes("text-gray-400 w-6")
                    ui.label(item["_label"]).classes("flex-1")
                    ui.input("Notes", value=item["notes"]).classes("w-40").on(
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
        form["pieces"].pop(idx)
        render_piece_rows()

    # Add piece
    with ui.row().classes("items-center gap-2 mt-2"):
        piece_add_select = ui.select(
            options=[], label="Search piece to add…", with_input=True
        ).classes("flex-1")

        def search_p(e):
            results = search_pieces(session, e.value or "")
            piece_add_select.options = {
                p.id: f"{p.composer.full_name} — {p.display_name}" for p in results
            }
            piece_add_select.update()

        piece_add_select.on("filter", search_p)

        def add_piece():
            pid = piece_add_select.value
            if pid:
                from app.services.piece_service import list_pieces
                all_pieces = {p.id: p for p in list_pieces(session)}
                if pid in all_pieces:
                    p = all_pieces[pid]
                    form["pieces"].append({
                        "piece_id": pid,
                        "sort_order": len(form["pieces"]),
                        "notes": "",
                        "_label": f"{p.composer.full_name} — {p.display_name}",
                    })
                    piece_add_select.set_value(None)
                    render_piece_rows()

        ui.button("Add piece", on_click=add_piece)

    render_piece_rows()

    # Soloists section
    ui.label("Soloists").classes("font-medium mt-4")
    artist_rows_container = ui.column().classes("w-full gap-2")

    def render_artist_rows():
        artist_rows_container.clear()
        with artist_rows_container:
            for i, item in enumerate(form["artists"]):
                with ui.row().classes("items-center gap-2 w-full"):
                    ui.label(item["_label"]).classes("flex-1")
                    ui.input("Role / instrument", value=item["role"]).classes("w-40").on(
                        "update:model-value",
                        lambda e, idx=i: form["artists"][idx].__setitem__("role", e.value),
                    )
                    ui.button(
                        icon="delete",
                        on_click=lambda _, idx=i: _remove_artist(idx),
                    ).props("flat dense color=negative")

    def _remove_artist(idx: int):
        form["artists"].pop(idx)
        render_artist_rows()

    with ui.row().classes("items-center gap-2 mt-2"):
        artist_add_select = ui.select(
            options=[], label="Search artist to add…", with_input=True
        ).classes("flex-1")

        def search_a(e):
            results = search_artists(session, e.value or "")
            artist_add_select.options = {a.id: a.full_name for a in results}
            artist_add_select.update()

        artist_add_select.on("filter", search_a)

        def add_artist():
            aid = artist_add_select.value
            if aid:
                from app.services.person_service import list_artists
                all_artists = {a.id: a for a in list_artists(session)}
                if aid in all_artists:
                    a = all_artists[aid]
                    form["artists"].append({"artist_id": aid, "role": "", "_label": a.full_name})
                    artist_add_select.set_value(None)
                    render_artist_rows()

        ui.button("Add artist", on_click=add_artist)

    render_artist_rows()

    # Attachments upload
    ui.label("Attachments").classes("font-medium mt-4")
    attachment_types = [
        ("ticket", "Ticket"), ("program", "Program booklet"), ("review", "Newspaper review(s)")
    ]
    for atype, label in attachment_types:
        with ui.row().classes("items-center gap-2 mt-2"):
            ui.label(label).classes("w-32")
            uploader = (
                ui.upload(label=f"Upload {label}", multiple=(atype != "ticket"), auto_upload=True)
                .classes("flex-1")
            )

            def handle_upload(e, t=atype):
                form["new_attachments"].append((t, e.name, e.content.read()))

            uploader.on_upload(handle_upload)

    # Notes
    ui.label("Notes").classes("font-medium mt-4")
    ui.textarea("Notes", value=form["notes"]).classes("w-full").bind_value(form, "notes")

    # Save / Cancel
    with ui.row().classes("gap-3 mt-6"):
        ui.button("Cancel", on_click=lambda: ui.navigate.to("/concerts")).props("outline")
        ui.button(
            "Save", on_click=lambda: _save(form, concert_id, session, is_edit)
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
    except ValueError:
        ui.notify("Invalid date format. Use YYYY-MM-DD.", type="negative")
        return

    if is_edit and concert_id:
        concert = get_concert(session, concert_id)
        if concert:
            # Clear existing links
            concert.piece_links.clear()
            concert.artist_links.clear()
            session.flush()
        update_concert(
            session, concert_id,
            date=concert_date,
            title=form["title"],
            orchestra=form["orchestra"],
            conductor_id=form["conductor_id"],
            notes=form["notes"],
        )
        # Re-add relations
        from app.models import ConcertArtist, ConcertPiece
        concert = get_concert(session, concert_id)
        for item in pieces:
            session.add(ConcertPiece(concert_id=concert_id, **{k: v for k, v in item.items()}))
        for item in artists:
            session.add(ConcertArtist(concert_id=concert_id, **item))
        session.commit()
        target_id = concert_id
    else:
        concert = create_concert(
            session,
            date=concert_date,
            title=form["title"],
            orchestra=form["orchestra"],
            conductor_id=form["conductor_id"],
            notes=form["notes"],
            pieces=pieces,
            artists=artists,
        )
        target_id = concert.id

    # Save new attachments
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

    ui.notify("Saved!", type="positive")
    ui.navigate.to(f"/concerts/{target_id}")
