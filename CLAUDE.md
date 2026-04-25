# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
uv sync                        # Install dependencies
uv run python main.py          # Start app (browser opens automatically)
uv run pytest                  # Run all tests
uv run pytest tests/services/  # Run a specific test directory
uv run pytest tests/services/test_concert_service.py::test_name  # Single test
uv run pytest tests/e2e/       # End-to-end UI tests only
uv run ruff check .            # Lint
uv run ruff check --fix .      # Auto-fix lint issues
uv run ruff format .           # Format code
```

## Architecture

Service-layer pattern with strict separation:

```
main.py          → @ui.page routes, nav_bar(), entry point
app/models/      → SQLAlchemy ORM models (one file per entity)
app/services/    → Business logic & CRUD (one file per entity)
app/views/       → NiceGUI page functions (one file per feature)
app/database.py  → Engine, Base, session factory, platform-aware DB path
app/i18n.py      → EN/DE translations via t(key)
app/storage/     → File upload helpers
tests/           → pytest (models/, services/, views/ = unit; e2e/ = UI simulation)
```

**Data flow:** views call services → services query/mutate via SQLAlchemy session → models define schema. Views never touch ORM directly.

## Conventions

### Models (`app/models/`)
- Always start with `from __future__ import annotations` (required for forward refs; F821 is suppressed in ruff for this dir)
- Import `Base` from `app.database`
- Use `Mapped[T]` + `mapped_column()` for columns, `relationship()` with `back_populates` for links
- Junction tables use `cascade="all, delete-orphan"`
- Add `@property` helpers (`full_name`, `display_name`) and `__repr__`

### Services (`app/services/`)
- First parameter is always `session: Session`
- Standard naming: `create_*`, `get_*`, `update_*`, `delete_*`, `list_*`, `search_*`
- Call `session.commit()` explicitly after mutations; return the entity (or `None` for not-found)
- Log every mutation: `logger.info("Created X id={}", obj.id)` — use `{}` placeholders, not f-strings (loguru lazy formatting)

### Views (`app/views/`)
- Export one function: `{feature}_page(**params) -> None`
- Acquire session with `get_session()`, close at end
- All UI strings via `t("key")` — never hardcode text
- State pattern: `state = {"search": "", "page": 0}` dict captured by closures
- NiceGUI chaining: `.classes()` (Tailwind) → `.props()` (Quasar) → `.on()` (events)

### Routes (`main.py`)
- `@ui.page("/path")` → call `nav_bar("/path")` → render inside `ui.column()` container

### i18n (`app/i18n.py`)
- `t(key)` returns the translated string for the current user language
- Keys are snake_case: `"add_concert"`, `"col_date"`, `"choir_director"`
- Always add both EN and DE entries when adding a new key
- Language stored in `app.storage.user["lang"]`

### Logging (loguru)
- `from loguru import logger`
- Services: `logger.info(...)`, Views: `logger.debug(...)`
- Always use `{}` placeholders — never f-strings in log calls

## Testing

**Unit tests** (`tests/models/`, `tests/services/`, `tests/views/`): use the `session` fixture from `tests/conftest.py`, which provides an in-memory SQLite session. Create test data inline or via service functions; no shared fixtures across files.

**E2E tests** (`tests/e2e/`): use NiceGUI's `user_simulation` framework. Each test gets a fresh copy of `data/konzert.db` (the seeded sample database) in a `tmp_path`, with the module-level session factory monkeypatched to point at it. This means E2E tests run the full application against realistic data with full isolation between tests.

## Database

- Platform-aware default path: macOS `~/Library/Application Support/KonzertKatalog/konzert.db`, Windows `%LOCALAPPDATA%\KonzertKatalog\konzert.db`, Linux `~/.local/share/konzertkatalog/konzert.db`
- Override with `KONZERT_DB_PATH=/path/to/db`
- `Base.metadata.create_all()` auto-creates missing tables on startup — **does not alter existing tables**. Delete the DB file to reset schema during development.
- Uploads stored in `{db_dir}/uploads/<concert_id>/<type>/<uuid>_<filename>`

## Pitfalls

- **Forward refs in models**: `from __future__ import annotations` is mandatory — removing it causes circular import failures
- **Session lifecycle**: Always close sessions in views; the test fixture manages this automatically
- **Orchestra is a FK**: `Concert.orchestra_id` references the Orchestra table — it is not a plain string field
- **Catalogue system**: `Composer.catalogue` is the prefix (e.g. `"KV"`), `Piece.catalogue_number` is the value (e.g. `"525"`); `Piece.display_name` composites them
- **NiceGUI reload**: Must use `reload=False` for packaged apps and native window mode
