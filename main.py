from pathlib import Path

from nicegui import app, ui

from app.database import create_session_factory
from app.views.concert_detail import concert_detail_page
from app.views.concert_form import concert_form_page
from app.views.concerts_list import concerts_list_page
from app.views.reference_data import reference_data_page
from app.views.search import search_page

# Initialise DB on startup
create_session_factory()

# Serve uploaded images as static files
uploads_dir = Path(__file__).parent / "data" / "uploads"
uploads_dir.mkdir(parents=True, exist_ok=True)
app.add_static_files("/uploads", str(uploads_dir))


def nav_bar(current: str = "") -> None:
    with ui.header().classes("bg-gray-900 text-white px-6 py-3 flex items-center gap-6"):
        ui.label("KonzertKatalog").classes("text-xl font-bold tracking-wide cursor-pointer").on(
            "click", lambda: ui.navigate.to("/concerts")
        )
        with ui.row().classes("gap-4 flex-1"):
            for label, path in [("Concerts", "/concerts"), ("Reference Data", "/reference")]:
                active = "underline" if path == current else "opacity-70 hover:opacity-100"
                ui.link(label, path).classes(f"text-white {active}")
        with ui.row().classes("ml-auto items-center gap-2"):
            search_box = (
                ui.input(placeholder="Search…")
                .classes("bg-white/10 text-white rounded px-2 py-1 text-sm w-48")
            )
            search_box.on(
                "keydown.enter",
                lambda e: ui.navigate.to(f"/search?q={search_box.value}")
            )


@ui.page("/")
def root():
    ui.navigate.to("/concerts")


@ui.page("/concerts")
def page_concerts_list():
    nav_bar("/concerts")
    with ui.column().classes("w-full max-w-6xl mx-auto px-4 py-6"):
        concerts_list_page()


@ui.page("/concerts/new")
def page_concert_new():
    nav_bar()
    with ui.column().classes("w-full max-w-4xl mx-auto px-4 py-6"):
        concert_form_page(concert_id=None)


@ui.page("/concerts/{concert_id}")
def page_concert_detail(concert_id: int):
    nav_bar()
    with ui.column().classes("w-full max-w-4xl mx-auto px-4 py-6"):
        concert_detail_page(concert_id)


@ui.page("/concerts/{concert_id}/edit")
def page_concert_edit(concert_id: int):
    nav_bar()
    with ui.column().classes("w-full max-w-4xl mx-auto px-4 py-6"):
        concert_form_page(concert_id=concert_id)


@ui.page("/reference")
def page_reference():
    nav_bar("/reference")
    with ui.column().classes("w-full max-w-5xl mx-auto px-4 py-6"):
        reference_data_page()


@ui.page("/search")
def page_search(q: str = ""):
    nav_bar()
    with ui.column().classes("w-full max-w-4xl mx-auto px-4 py-6"):
        search_page(query=q)


if __name__ in ("__main__", "__mp_main__"):
    ui.run(title="KonzertKatalog", port=8080, reload=False)
