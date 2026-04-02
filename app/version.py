"""Read the project version from pyproject.toml (dev) or frozen fallback (PyInstaller)."""

import sys
import tomllib
from pathlib import Path

_FALLBACK = "0.0.0"


def get_version() -> str:
    # In a PyInstaller bundle, __file__ is inside the temp extraction dir.
    # Try the directory containing the main script first, then the source tree.
    candidates = [
        Path(sys.argv[0]).resolve().parent / "pyproject.toml",
        Path(__file__).resolve().parent.parent / "pyproject.toml",
    ]
    for path in candidates:
        if path.is_file():
            with open(path, "rb") as f:
                data = tomllib.load(f)
            return data.get("project", {}).get("version", _FALLBACK)
    return _FALLBACK
