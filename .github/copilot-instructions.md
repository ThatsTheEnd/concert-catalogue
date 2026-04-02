# KonzertKatalog — Workspace Instructions

Personal classical concert archive. Python 3.14+, NiceGUI, SQLAlchemy 2.0, SQLite, loguru.

## Quick Reference

```bash
uv sync                  # Install dependencies
uv run python main.py    # Start app (browser opens automatically)
uv run pytest            # Run tests (59 tests, in-memory SQLite)
uv run ruff check .      # Lint
uv run ruff check --fix . # Auto-fix lint
```

## Architecture

Service-layer pattern with clear separation:

```
main.py              → Routes (@ui.page), nav_bar(), entry point
app/models/          → SQLAlchemy ORM models (one file per entity)
app/services/        → Business logic, CRUD (one file per entity)
app/views/           → NiceGUI page functions (one file per feature)
app/database.py      → Engine, Base, session factory, platform-aware DB path
app/i18n.py          → EN/DE translations via t(key)
app/storage/         → File upload helpers
tests/               → pytest suite (models/, services/, views/)
```

## Conventions

### Models (`app/models/`)

- Always start with `from __future__ import annotations` (forward refs)
- Import `Base` from `app.database`
- Use `Mapped[T]` + `mapped_column()` for columns, `relationship()` for links
- Use `back_populates` for bidirectional relationships
- Junction tables use `cascade="all, delete-orphan"`
- Add `@property` helpers (`full_name`, `display_name`) and `__repr__`
- F821 is suppressed in ruff config for this directory

### Services (`app/services/`)

- First parameter is always `session: Session`
- Standard CRUD: `create_*`, `get_*`, `update_*`, `delete_*`, `list_*`, `search_*`
- Log every mutation with `logger.info()`; use `{}` placeholders (loguru format)
- Call `session.commit()` explicitly after changes
- Return the entity (or `None` for not-found)

### Views (`app/views/`)

- Export one function: `{feature}_page(**params) -> None`
- Acquire session with `get_session()`, close at end
- All UI strings: `t("key")` — never hardcoded text
- Log page loads with `logger.debug()`
- State pattern: `state = {"search": "", "page": 0}` dict captured by closures
- NiceGUI style: chain `.classes()` (Tailwind) → `.props()` (Quasar) → `.on()` (events)

### Routes (`main.py`)

- `@ui.page("/path")` decorator → call `nav_bar("/path")` → render in `ui.column()` container
- `nav_bar(current)` highlights the active tab

### i18n (`app/i18n.py`)

- `t(key)` returns translated string for current user language
- Keys are snake_case: `"add_concert"`, `"col_date"`, `"choir_director"`
- Always add both EN and DE entries when adding new keys
- Language stored in `app.storage.user["lang"]`

### Logging (loguru)

- `from loguru import logger`
- Services: `logger.info("Created X id={}", obj.id)`
- Views: `logger.debug("Loading page")`; `logger.debug("Search: {!r}", query)`
- Use `{}` placeholders (not f-strings) — loguru lazy formatting

### Testing

- Fixture `session` yields in-memory SQLite session (see `tests/conftest.py`)
- Tests import services/models directly, pass `session` fixture
- Create test data inline or via service functions; no shared fixtures across files
- Run: `uv run pytest` or `uv run pytest -q` for compact output

## Database

- Platform-aware path: macOS `~/Library/Application Support/KonzertKatalog/konzert.db`
- Override: `KONZERT_DB_PATH=/path/to/db`
- `Base.metadata.create_all()` auto-creates new tables on startup
- **Does not** alter existing tables — delete DB to reset schema during dev
- Uploads stored in `{db_dir}/uploads/`

## Deployment

- PyInstaller via `nicegui-pack`: `nicegui-pack --onefile --name KonzertKatalog main.py`
- `freeze_support()` is called in main guard (required for PyInstaller)
- `native.find_open_port()` for auto port selection
- DB lives outside the bundle (user data directory)
- See [DEPLOYMENT.md](../DEPLOYMENT.md) for full packaging details

## Pitfalls

- **Forward refs in models**: Without `from __future__ import annotations`, circular imports break
- **Session lifecycle**: Always close sessions in views; tests use fixture that auto-manages this
- **Orchestra is a FK**: `Concert.orchestra_id` → Orchestra table (not a string field)
- **Catalogue system**: Composer has `catalogue` prefix (e.g. "KV"), Piece has `catalogue_number` (e.g. "525") — `display_name` composites them
- **NiceGUI reload**: Must be `reload=False` for packaged apps and native mode
