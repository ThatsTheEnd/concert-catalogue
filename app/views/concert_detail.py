from pathlib import Path

from loguru import logger
from nicegui import ui

from app.database import get_session
from app.i18n import t
from app.models import AttachmentType
from app.services.concert_service import delete_concert, get_concert
from app.storage.file_handler import url_for_upload

_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp", ".svg"}


def _is_image(filename: str) -> bool:
    """Return True if *filename* has a recognised image extension."""
    return Path(filename).suffix.lower() in _IMAGE_EXTENSIONS


def concert_detail_page(concert_id: int) -> None:
    logger.debug("Viewing concert id={}", concert_id)
    session = get_session()
    ui.context.client.on_disconnect(session.close)
    concert = get_concert(session, concert_id)

    if concert is None:
        ui.label("Concert not found.").classes("text-red-500")
        session.close()
        return

    # ── Header ───────────────────────────────────────────────────────────────
    with ui.row().classes("w-full items-start justify-between mb-4"):
        with ui.column().classes("gap-1"):
            meta_parts = [str(concert.date)]
            if concert.orchestra:
                meta_parts.append(concert.orchestra.name)
            if concert.venue:
                meta_parts.append(str(concert.venue))
            ui.label(" · ".join(meta_parts)).classes("text-2xl font-bold")

            if concert.conductor:
                ui.label(
                    f"{t('conducted_by')}: {concert.conductor.full_name}"
                ).classes("text-gray-500")
            if concert.choir:
                choir_line = f"{t('choir')}: {concert.choir}"
                if concert.choir_director:
                    choir_line += f" ({t('choir_director')}: {concert.choir_director.full_name})"
                ui.label(choir_line).classes("text-gray-500")

        with ui.row().classes("gap-2 shrink-0"):
            ui.button(
                t("back_to_concerts"),
                on_click=lambda: ui.navigate.to("/concerts"),
            ).props("flat")
            ui.button(
                t("edit"),
                on_click=lambda: ui.navigate.to(f"/concerts/{concert_id}/edit"),
            ).props("outline")
            ui.button(
                t("delete"),
                on_click=lambda: _confirm_delete(concert_id, session),
            ).props("color=negative outline")

    # ── Soloists ─────────────────────────────────────────────────────────────
    if concert.artist_links:
        ui.label(t("soloists")).classes("text-lg font-semibold mt-4 mb-1")
        for link in concert.artist_links:
            role = f" — {link.role}" if link.role else ""
            instr = f" ({link.instrument})" if link.instrument else ""
            with ui.row().classes("items-center gap-2"):
                ui.icon("person").classes("text-gray-400 text-base")
                ui.label(f"{link.artist.full_name}{role}{instr}")

    # ── Program ──────────────────────────────────────────────────────────────
    if concert.piece_links:
        ui.label(t("program")).classes("text-lg font-semibold mt-4 mb-1")
        for i, link in enumerate(concert.piece_links, 1):
            piece = link.piece
            composer_name = piece.composer.full_name if piece.composer else ""
            with ui.row().classes("items-baseline gap-3"):
                ui.label(f"{i}.").classes("text-gray-400 w-6 text-right shrink-0")
                with ui.column().classes("gap-0"):
                    ui.label(piece.display_name).classes("font-medium")
                    if composer_name:
                        ui.label(composer_name).classes("text-sm text-gray-500")
                    if link.notes:
                        ui.label(link.notes).classes("text-xs text-gray-400 italic whitespace-pre-wrap")

    # ── Notes ────────────────────────────────────────────────────────────────
    if concert.notes:
        ui.label(t("notes")).classes("text-lg font-semibold mt-4 mb-1")
        ui.label(concert.notes).classes("text-gray-700 whitespace-pre-wrap")

    # ── Attachments ──────────────────────────────────────────────────────────
    attachments_by_type: dict[str, list] = {t_val: [] for t_val in AttachmentType}
    for a in concert.attachments:
        attachments_by_type.setdefault(a.type, []).append(a)

    if any(attachments_by_type.values()):
        ui.label(t("attachments")).classes("text-lg font-semibold mt-6 mb-2")
        with ui.tabs() as tabs:
            tab_ticket = ui.tab(t("tab_ticket"))
            tab_program = ui.tab(t("tab_program"))
            tab_reviews = ui.tab(t("tab_reviews"))

        with ui.tab_panels(tabs, value=tab_ticket).classes("w-full"):
            tab_map = [
                (tab_ticket, "ticket"),
                (tab_program, "program"),
                (tab_reviews, "review"),
            ]
            for tab, atype in tab_map:
                with ui.tab_panel(tab):
                    items = attachments_by_type.get(atype, [])
                    if not items:
                        ui.label(t("no_images")).classes("text-gray-400 text-sm")
                    else:
                        with ui.row().classes("flex-wrap gap-3"):
                            for att in items:
                                url = url_for_upload(att.file_path)
                                _image_thumbnail(url, att.original_filename)

    session.close()


def _image_thumbnail(url: str, label: str) -> None:
    if _is_image(label):
        with ui.card().classes("cursor-pointer").on(
            "click", lambda u=url, lbl=label: _open_lightbox(u, lbl)
        ):
            ui.image(url).classes("w-40 h-40 object-cover")
            ui.label(label).classes("text-xs text-gray-500 truncate max-w-40")
    else:
        with ui.card().classes("cursor-pointer").on(
            "click", lambda u=url: ui.navigate.to(u, new_tab=True)
        ):
            with ui.element("div").classes("w-40 h-40 flex items-center justify-center"):
                ui.icon("description").classes("text-6xl text-gray-400")
            ui.label(label).classes("text-xs text-gray-500 truncate max-w-40")


def _open_lightbox(url: str, label: str) -> None:
    with ui.dialog() as dlg, ui.card().classes("max-w-4xl"):
        ui.label(label).classes("font-medium mb-2")
        ui.image(url).classes("max-w-full max-h-screen")
        ui.button(t("close"), on_click=dlg.close).classes("mt-2")
    dlg.open()


def _confirm_delete(concert_id: int, session) -> None:
    with ui.dialog() as dlg, ui.card():
        ui.label(t("delete_confirm")).classes("font-medium")
        ui.label(t("delete_warning")).classes("text-sm text-gray-500")
        with ui.row().classes("gap-2 mt-4"):
            ui.button(t("cancel"), on_click=dlg.close).props("outline")

            def do_delete():
                delete_concert(session, concert_id)
                dlg.close()
                ui.navigate.to("/concerts")

            ui.button(t("delete"), on_click=do_delete).props("color=negative")
    dlg.open()
