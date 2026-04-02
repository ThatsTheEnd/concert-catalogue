import asyncio
from multiprocessing import freeze_support

from loguru import logger
from nicegui import app, native, ui

from app.database import DB_PATH, create_session_factory
from app.i18n import t, toggle_lang
from app.storage.file_handler import UPLOADS_ROOT
from app.version import get_version
from app.views.concert_detail import concert_detail_page
from app.views.concert_form import concert_form_page
from app.views.concerts_list import concerts_list_page
from app.views.reference_data import reference_data_page
from app.views.search import search_page

__version__ = get_version()

# Initialise DB and static file serving on startup
create_session_factory()
UPLOADS_ROOT.mkdir(parents=True, exist_ok=True)
app.add_static_files("/uploads", str(UPLOADS_ROOT))


_NAV_TAB_ACTIVE = (
    "bg-white/25 text-white border-b-2 border-white px-4 py-1.5 rounded-t text-sm font-medium"
)
_NAV_TAB_INACTIVE = (
    "text-white/70 hover:text-white hover:bg-white/10 px-4 py-1.5 rounded-t text-sm"
)


def nav_bar(current: str = "") -> None:
    # Dark mode controller — reads user preference stored in app.storage.user
    dark = ui.dark_mode(
        value=app.storage.user.get("dark_mode", False)
    )

    with ui.header().classes("px-6 py-3 flex items-center gap-6"):
        ui.label("KonzertKatalog").classes(
            "text-xl font-bold tracking-wide cursor-pointer"
        ).on("click", lambda: ui.navigate.to("/concerts"))

        with ui.row().classes("gap-1 flex-1"):
            for key, path in [("concerts", "/concerts"), ("reference_data", "/reference")]:
                ui.link(t(key), path).classes(
                    _NAV_TAB_ACTIVE if path == current else _NAV_TAB_INACTIVE
                )

        with ui.row().classes("ml-auto items-center gap-3"):
            search_box = (
                ui.input(placeholder=t("search_placeholder"))
                .classes("bg-white/10 text-white rounded px-2 py-1 text-sm w-44")
                .props("borderless dense")
            )
            search_box.on(
                "keydown.enter",
                lambda e: ui.navigate.to(f"/search?q={search_box.value}"),
            )

            # Language toggle — shows the language you'd switch TO
            def on_lang_toggle():
                toggle_lang()
                ui.navigate.reload()

            ui.button(
                t("language"),
                on_click=on_lang_toggle,
            ).props("flat dense color=white").classes("text-xs font-mono")

            # Dark/light mode toggle
            def on_dark_toggle():
                new_val = not app.storage.user.get("dark_mode", False)
                app.storage.user["dark_mode"] = new_val
                dark.set_value(new_val)

            ui.button(
                icon="dark_mode",
                on_click=on_dark_toggle,
            ).props("flat dense color=white").tooltip(
                t("dark_mode")
            )

            # Info button — shows version and database location
            def on_info_click():
                with ui.dialog() as dlg, ui.card().classes("min-w-[360px]"):
                    ui.label("KonzertKatalog").classes("text-lg font-bold")
                    with ui.grid(columns=2).classes("gap-x-4 gap-y-1 mt-2"):
                        ui.label(t("info_version")).classes("text-sm text-gray-500")
                        ui.label(__version__).classes("text-sm font-mono")
                        ui.label(t("info_database")).classes("text-sm text-gray-500")
                        ui.label(str(DB_PATH)).classes(
                            "text-sm font-mono break-all"
                        )
                    ui.button(t("close"), on_click=dlg.close).classes("mt-3")
                dlg.open()

            ui.button(
                icon="info_outline",
                on_click=on_info_click,
            ).props("flat dense color=white").tooltip(t("info"))

            # Stop application button
            async def on_stop_click():
                with ui.dialog() as dlg, ui.card():
                    logger.debug("Stop app dialog opened")
                    ui.label(t("stop_app_confirm")).classes("font-medium")
                    ui.label(t("stop_app_warning")).classes("text-sm text-gray-500")
                    with ui.row().classes("gap-2 mt-4"):
                        ui.button(t("cancel"), on_click=dlg.close).props("outline")

                        async def do_stop():
                            logger.info("Shutting down application by user request")
                            dlg.close()
                            ui.navigate.to("/stopped")
                            await asyncio.sleep(0.5)
                            app.shutdown()

                        ui.button(
                            t("stop_app"),
                            on_click=do_stop,
                        ).props("color=negative")
                dlg.open()

            ui.button(
                icon="power_settings_new",
                on_click=on_stop_click,
            ).props("flat dense color=white").tooltip(t("stop_app"))


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


@app.get("/stopped")
def page_stopped():
    from fastapi.responses import HTMLResponse

    return HTMLResponse(
        """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Application Stopped</title>
  <style>
    body {
      margin: 0;
      display: flex;
      align-items: center;
      justify-content: center;
      min-height: 100vh;
      font-family: sans-serif;
      background: #f9fafb;
      color: #111827;
    }
    .card {
      text-align: center;
      padding: 2rem 3rem;
      background: #fff;
      border-radius: 0.75rem;
      box-shadow: 0 4px 16px rgba(0,0,0,.08);
    }
    .icon { font-size: 3.5rem; margin-bottom: 1rem; }
    h1 { margin: 0 0 .5rem; font-size: 1.5rem; }
    p  { margin: 0; color: #6b7280; }
  </style>
</head>
<body>
  <div class="card">
    <div class="icon">&#x23FC;</div>
    <h1>Application Stopped</h1>
    <p>The server has been shut down. You can close this tab.</p>
  </div>
</body>
</html>"""
    )


if __name__ in ("__main__", "__mp_main__"):
    freeze_support()
    logger.info("Starting KonzertKatalog v{} — DB at {}", __version__, DB_PATH)
    ui.run(
        title="KonzertKatalog",
        port=native.find_open_port(),
        reload=False,
        native=True,
        storage_secret="konzert-katalog-secret",  # required for app.storage.user
    )
