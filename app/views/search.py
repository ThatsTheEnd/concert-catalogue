from loguru import logger
from nicegui import ui

from app.database import get_session
from app.i18n import t
from app.services.search_service import search_all


def search_page(query: str = "") -> None:
    session = get_session()
    ui.context.client.on_disconnect(session.close)

    ui.label(t("search_heading")).classes("text-2xl font-bold mb-4")
    search_input = (
        ui.input(t("search_all_placeholder"), value=query)
        .classes("w-full text-lg")
    )

    results_container = ui.column().classes("w-full mt-4 gap-6")

    entity_labels = {
        "concerts": t("results_concerts"),
        "conductors": t("results_conductors"),
        "composers": t("results_composers"),
        "artists": t("results_artists"),
        "venues": t("results_venues"),
    }

    def run_search(q: str):
        results_container.clear()
        if not q.strip():
            return
        logger.debug("Global search: {!r}", q.strip())
        results = search_all(session, q.strip())
        with results_container:
            if results["concerts"]:
                label_text = f"{entity_labels['concerts']} ({len(results['concerts'])})"
                ui.label(label_text).classes("text-lg font-semibold")
                for c in results["concerts"]:
                    row_classes = (
                        "items-center gap-3 cursor-pointer hover:bg-gray-50 p-1 rounded"
                    )
                    with ui.row().classes(row_classes).on(
                        "click", lambda _, cid=c.id: ui.navigate.to(f"/concerts/{cid}")
                    ):
                        ui.label(str(c.date)).classes("text-gray-400 w-24 shrink-0")
                        with ui.column().classes("gap-0"):
                            orch_name = c.orchestra.name if c.orchestra else "—"
                            ui.label(orch_name).classes("font-medium")
                            sub = []
                            if c.conductor:
                                sub.append(c.conductor.full_name)
                            if c.venue:
                                sub.append(str(c.venue))
                            if sub:
                                ui.label(" · ".join(sub)).classes("text-sm text-gray-500")

            for key in ["conductors", "composers", "artists", "venues"]:
                items = results[key]
                if items:
                    ui.label(
                        f"{entity_labels[key]} ({len(items)})"
                    ).classes("text-lg font-semibold")
                    for item in items:
                        ui.label(str(item)).classes("text-gray-700 ml-2")

    search_input.on("update:model-value", lambda e: run_search(e.value or ""))

    if query:
        run_search(query)

    session.close()
