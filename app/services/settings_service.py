import json

from loguru import logger
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.setting import Setting

_DEFAULT_CONCERT_COLUMNS: list[dict] = [
    {"name": "date", "visible": True},
    {"name": "orchestra", "visible": True},
    {"name": "conductor", "visible": True},
    {"name": "soloists", "visible": True},
    {"name": "venue", "visible": True},
    {"name": "choir", "visible": False},
]

_DEFAULTS: dict[str, str] = {
    "lang": "en",
    "dark_mode": "false",
    "font_size": "16",
    "concert_columns": json.dumps(_DEFAULT_CONCERT_COLUMNS),
}


def get_setting(session: Session, key: str) -> str:
    row = session.get(Setting, key)
    if row is not None:
        return row.value
    return _DEFAULTS.get(key, "")


def set_setting(session: Session, key: str, value: str) -> None:
    row = session.get(Setting, key)
    if row is not None:
        row.value = value
    else:
        session.add(Setting(key=key, value=value))
    session.commit()
    logger.info("Setting {}={}", key, value)


def get_all_settings(session: Session) -> dict[str, str]:
    """Return all settings, with defaults for any missing keys."""
    result = dict(_DEFAULTS)
    for row in session.scalars(select(Setting)):
        result[row.key] = row.value
    return result


def get_concert_columns(session: Session) -> list[dict]:
    """Return the ordered, annotated concert column config."""
    raw = get_setting(session, "concert_columns")
    try:
        return json.loads(raw)
    except (json.JSONDecodeError, TypeError):
        return [dict(c) for c in _DEFAULT_CONCERT_COLUMNS]


def set_concert_columns(session: Session, columns: list[dict]) -> None:
    set_setting(session, "concert_columns", json.dumps(columns))
    logger.info("Concert columns updated: {}", [c["name"] for c in columns if c["visible"]])
