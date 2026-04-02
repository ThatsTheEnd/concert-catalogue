from loguru import logger
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.setting import Setting

_DEFAULTS: dict[str, str] = {
    "lang": "en",
    "dark_mode": "false",
    "font_size": "16",
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
