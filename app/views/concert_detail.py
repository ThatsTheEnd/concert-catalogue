from nicegui import ui

from app.database import get_session
from app.models import AttachmentType
from app.services.concert_service import delete_concert, get_concert
from app.storage.file_handler import url_for_upload


def concert_detail_page(concert_id: int) -> None:
    session = get_session()
    concert = get_concert(session, concert_id)

    if concert is None:
        ui.label("Concert not found.").classes("text-red-500")
        session.close()
        return

    # Header
    with ui.row().classes("w-full items-start justify-between mb-4"):
        with ui.column():
            ui.label(concert.title).classes("text-2xl font-bold")
            meta_parts = [str(concert.date)]
            if concert.orchestra:
                meta_parts.append(concert.orchestra)
            if concert.venue:
                meta_parts.append(str(concert.venue))
            ui.label(" · ".join(meta_parts)).classes("text-gray-500")
            if concert.conductor:
                ui.label(f"Conducted by {concert.conductor.full_name}").classes(
                    "text-gray-600 italic"
                )
        with ui.row().classes("gap-2"):
            ui.button(
                "Edit",
                on_click=lambda: ui.navigate.to(f"/concerts/{concert_id}/edit"),
            ).props("outline")
            ui.button(
                "Delete",
                on_click=lambda: _confirm_delete(concert_id, session),
            ).props("color=negative outline")

    # Soloists
    if concert.artist_links:
        ui.label("Soloists").classes("text-lg font-semibold mt-4 mb-1")
        for link in concert.artist_links:
            role = f" — {link.role}" if link.role else ""
            with ui.row().classes("items-center gap-2"):
                ui.icon("person").classes("text-gray-400")
                ui.label(f"{link.artist.full_name}{role} ({link.artist.instrument})")

    # Program (in performance order)
    if concert.piece_links:
        ui.label("Program").classes("text-lg font-semibold mt-4 mb-1")
        for i, link in enumerate(concert.piece_links, 1):
            piece = link.piece
            composer_name = piece.composer.full_name if piece.composer else ""
            with ui.row().classes("items-baseline gap-3"):
                ui.label(f"{i}.").classes("text-gray-400 w-6 text-right")
                with ui.column().classes("gap-0"):
                    ui.label(piece.display_name).classes("font-medium")
                    if composer_name:
                        ui.label(composer_name).classes("text-sm text-gray-500")

    if concert.notes:
        ui.label("Notes").classes("text-lg font-semibold mt-4 mb-1")
        ui.label(concert.notes).classes("text-gray-700")

    # Attachments
    attachments_by_type = {t.value: [] for t in AttachmentType}
    for a in concert.attachments:
        attachments_by_type.setdefault(a.type, []).append(a)

    if any(attachments_by_type.values()):
        ui.label("Attachments").classes("text-lg font-semibold mt-6 mb-2")
        with ui.tabs() as tabs:
            tab_ticket = ui.tab("Ticket")
            tab_program = ui.tab("Program")
            tab_reviews = ui.tab("Reviews")

        with ui.tab_panels(tabs, value=tab_ticket).classes("w-full"):
            tab_map = [(tab_ticket, "ticket"), (tab_program, "program"), (tab_reviews, "review")]
            for tab, atype in tab_map:
                with ui.tab_panel(tab):
                    items = attachments_by_type.get(atype, [])
                    if not items:
                        ui.label("No images attached.").classes("text-gray-400 text-sm")
                    else:
                        with ui.row().classes("flex-wrap gap-3"):
                            for att in items:
                                url = url_for_upload(att.file_path)
                                _image_thumbnail(url, att.original_filename)

    session.close()


def _image_thumbnail(url: str, label: str) -> None:
    with ui.card().classes("cursor-pointer").on(
        "click", lambda u=url, lbl=label: _open_lightbox(u, lbl)
    ):
        ui.image(url).classes("w-40 h-40 object-cover")
        ui.label(label).classes("text-xs text-gray-500 truncate max-w-40")


def _open_lightbox(url: str, label: str) -> None:
    with ui.dialog() as dlg, ui.card().classes("max-w-4xl"):
        ui.label(label).classes("font-medium mb-2")
        ui.image(url).classes("max-w-full max-h-screen")
        ui.button("Close", on_click=dlg.close).classes("mt-2")
    dlg.open()


def _confirm_delete(concert_id: int, session) -> None:
    with ui.dialog() as dlg, ui.card():
        ui.label("Delete this concert?").classes("font-medium")
        ui.label("This cannot be undone.").classes("text-sm text-gray-500")
        with ui.row().classes("gap-2 mt-4"):
            ui.button("Cancel", on_click=dlg.close).props("outline")
            def do_delete():
                delete_concert(session, concert_id)
                dlg.close()
                ui.navigate.to("/concerts")
            ui.button("Delete", on_click=do_delete).props("color=negative")
    dlg.open()
