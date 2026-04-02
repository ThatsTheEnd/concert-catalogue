from loguru import logger
from nicegui import ui

from app.database import get_session
from app.i18n import t
from app.services.concert_service import count_concerts, list_concerts


def concerts_list_page() -> None:
    logger.debug("Loading concerts list")
    session = get_session()
    state = {"search": "", "page": 0, "page_size": 50}

    def load():
        total = count_concerts(session, state["search"])
        concerts = list_concerts(
            session,
            search=state["search"],
            limit=state["page_size"],
            offset=state["page"] * state["page_size"],
        )
        table.rows = [
            {
                "id": c.id,
                "date": str(c.date),
                "orchestra": c.orchestra.name if c.orchestra else "",
                "choir": c.choir,
                "venue": str(c.venue) if c.venue else "",
                "conductor": c.conductor.full_name if c.conductor else "",
            }
            for c in concerts
        ]
        pagination_label.set_text(f"{total} {t('of_concerts')}")

    def on_search(e):
        state["search"] = e.value or ""
        state["page"] = 0
        logger.debug("Concert search: {!r}", state["search"])
        load()

    def on_row_click(e):
        concert_id = e.args[1]["id"]
        logger.debug("Navigating to concert id={}", concert_id)
        ui.navigate.to(f"/concerts/{concert_id}")

    with ui.row().classes("w-full items-center gap-4 mb-4"):
        (
            ui.input(placeholder=t("search_concerts"))
            .classes("flex-1")
            .on("update:model-value", on_search)
        )
        pagination_label = ui.label("").classes("text-sm text-gray-500")
        ui.button(t("add_concert"), on_click=lambda: ui.navigate.to("/concerts/new")).props(
            "color=primary"
        )

    columns = [
        {"name": "date", "label": t("col_date"), "field": "date", "sortable": True},
        {"name": "orchestra", "label": t("col_orchestra"), "field": "orchestra", "sortable": True},
        {"name": "choir", "label": t("choir"), "field": "choir"},
        {"name": "venue", "label": t("col_venue"), "field": "venue"},
        {"name": "conductor", "label": t("col_conductor"), "field": "conductor"},
    ]

    table = ui.table(columns=columns, rows=[], row_key="id").classes("w-full cursor-pointer")
    table.on("rowClick", on_row_click)

    with ui.row().classes("items-center gap-2 mt-2"):
        def prev_page():
            state["page"] = max(0, state["page"] - 1)
            load()

        def next_page():
            state["page"] += 1
            load()

        ui.button(t("prev"), on_click=prev_page).props("flat")
        ui.button(t("next"), on_click=next_page).props("flat")

    load()
    session.close()
