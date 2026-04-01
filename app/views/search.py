from nicegui import ui

from app.database import get_session
from app.services.search_service import search_all


def search_page(query: str = "") -> None:
    session = get_session()

    ui.label("Search").classes("text-2xl font-bold mb-4")
    search_input = (
        ui.input("Search composers, conductors, artists, venues, pieces…", value=query)
        .classes("w-full text-lg")
    )

    results_container = ui.column().classes("w-full mt-4 gap-6")

    def run_search(q: str):
        results_container.clear()
        if not q.strip():
            return
        results = search_all(session, q.strip())
        with results_container:
            if results["concerts"]:
                ui.label(f"Concerts ({len(results['concerts'])})").classes("text-lg font-semibold")
                for c in results["concerts"]:
                    row_classes = "items-center gap-3 cursor-pointer hover:bg-gray-50 p-1 rounded"
                    with ui.row().classes(row_classes).on(
                        "click", lambda _, cid=c.id: ui.navigate.to(f"/concerts/{cid}")
                    ):
                        ui.label(str(c.date)).classes("text-gray-400 w-24 shrink-0")
                        with ui.column().classes("gap-0"):
                            ui.label(c.title).classes("font-medium")
                            sub = []
                            if c.conductor:
                                sub.append(c.conductor.full_name)
                            if c.venue:
                                sub.append(str(c.venue))
                            if sub:
                                ui.label(" · ".join(sub)).classes("text-sm text-gray-500")

            for key, label in [("conductors", "Conductors"), ("composers", "Composers"),
                                ("artists", "Artists"), ("venues", "Venues")]:
                items = results[key]
                if items:
                    ui.label(f"{label} ({len(items)})").classes("text-lg font-semibold")
                    for item in items:
                        ui.label(str(item)).classes("text-gray-700 ml-2")

    search_input.on("update:model-value", lambda e: run_search(e.value))

    if query:
        run_search(query)

    session.close()
