# KonzertKatalog

A personal classical concert archive built with [NiceGUI](https://nicegui.io/) and SQLite.

## Features

- **Concert list** – browse, search, and paginate your concert history
- **Concert detail** – view programme, soloists, conductor, venue, and attachments (ticket, programme booklet, reviews)
- **Concert form** – add or edit concerts with full programme, soloists, choir, and file-upload support
- **Reference data** – manage orchestras, venues, composers, conductors, and artists
- **Full-text search** – across all entities from the nav-bar search box
- **Dark mode & language toggle** – EN/DE, persisted per browser session

## Requirements

- Python 3.14+
- [uv](https://github.com/astral-sh/uv) (recommended) or `pip`

## Quick Start

```bash
# Install dependencies
uv sync

# Run the app
uv run python main.py
```

The app is available at <http://localhost:8080>.

## Project Layout

```
app/
  models/       SQLAlchemy ORM models
  services/     Business logic (CRUD operations)
  views/        NiceGUI page functions
  storage/      File-upload helpers
  i18n.py       EN/DE translations
  database.py   SQLite session factory
data/
  konzert.db    SQLite database (created on first run)
  uploads/      Uploaded attachments
tests/          Pytest test suite
main.py         Entry point & route definitions
```

## Running Tests

```bash
uv run pytest
```
