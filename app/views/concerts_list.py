from loguru import logger
from nicegui import ui

from app.database import get_session
from app.i18n import t
from app.services.concert_service import count_concerts, list_concerts
from app.services.settings_service import get_concert_columns

_COL_SORTABLE = {"date", "orchestra"}


def concerts_list_page() -> None:
    logger.debug("Loading concerts list")
    session = get_session()
    ui.context.client.on_disconnect(session.close)

    col_config = get_concert_columns(session)
    columns = [
        {
            "name": cfg["name"],
            "label": t(f"col_{cfg['name']}"),
            "field": cfg["name"],
            **({"sortable": True} if cfg["name"] in _COL_SORTABLE else {}),
        }
        for cfg in col_config
        if cfg["visible"]
    ]

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
                "soloists": ", ".join(link.artist.full_name for link in c.artist_links),
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
        ui.input(placeholder=t("search_concerts"), on_change=on_search).classes("flex-1")
        ui.link(t("advanced_search"), "/search").classes("text-sm text-gray-500 whitespace-nowrap")
        pagination_label = ui.label("").classes("text-sm text-gray-500")
        ui.button(t("add_concert"), on_click=lambda: ui.navigate.to("/concerts/new")).props(
            "color=primary"
        )

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
