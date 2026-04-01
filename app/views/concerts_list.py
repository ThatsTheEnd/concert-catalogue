from nicegui import ui

from app.database import get_session
from app.services.concert_service import count_concerts, list_concerts


def concerts_list_page() -> None:
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
                "title": c.title,
                "orchestra": c.orchestra,
                "venue": str(c.venue) if c.venue else "",
                "conductor": c.conductor.full_name if c.conductor else "",
            }
            for c in concerts
        ]
        pagination_label.set_text(f"{total} concert(s)")

    def on_search(e):
        state["search"] = e.value
        state["page"] = 0
        load()

    def on_row_click(e):
        concert_id = e.args["row"]["id"]
        ui.navigate.to(f"/concerts/{concert_id}")

    with ui.row().classes("w-full items-center gap-4 mb-4"):
        (
            ui.input(placeholder="Search composers, conductors, artists, venues…")
            .classes("flex-1")
            .on("update:model-value", on_search)
        )
        pagination_label = ui.label("").classes("text-sm text-gray-500")
        ui.button("+ Add Concert", on_click=lambda: ui.navigate.to("/concerts/new")).props(
            "color=primary"
        )

    columns = [
        {"name": "date", "label": "Date", "field": "date", "sortable": True},
        {"name": "title", "label": "Title", "field": "title", "sortable": True},
        {"name": "orchestra", "label": "Orchestra", "field": "orchestra"},
        {"name": "venue", "label": "Venue", "field": "venue"},
        {"name": "conductor", "label": "Conductor", "field": "conductor"},
    ]

    table = ui.table(columns=columns, rows=[], row_key="id").classes("w-full")
    table.on("rowClick", on_row_click)

    # Pagination controls
    with ui.row().classes("items-center gap-2 mt-2"):
        def prev_page():
            state["page"] = max(0, state["page"] - 1)
            load()

        def next_page():
            state["page"] += 1
            load()

        ui.button("←", on_click=prev_page)
        ui.button("→", on_click=next_page)

    load()
    session.close()
