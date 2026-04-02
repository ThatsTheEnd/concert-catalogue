# Deployment Plan – KonzertKatalog Standalone Distribution

## Goal

Distribute KonzertKatalog as a **self-contained executable** that runs on Windows and
macOS without requiring Python, pip, or any other tooling to be installed.
Released artefacts are uploaded to the GitHub Releases page so users can simply
download and run them.

---

## Design question: SQLite database outside the application

**Yes, keeping the database outside the bundled application is fully supported and
recommended.**

The app reads the database path from the environment variable `KONZERT_DB_PATH` (with a
sensible default). Because the database file is *not* bundled inside the executable,
users can:

- Keep a single database file across multiple app upgrades.
- Back up or move the database independently.
- Share the database on a network drive.

Suggested default paths (applied when `KONZERT_DB_PATH` is not set):

| Platform | Default path |
|----------|-------------|
| Windows  | `%LOCALAPPDATA%\KonzertKatalog\konzert.db` |
| macOS    | `~/Library/Application Support/KonzertKatalog/konzert.db` |
| Linux    | `~/.local/share/konzertkatalog/konzert.db` |

Change `app/database.py` to honour `KONZERT_DB_PATH` before falling back to the
platform default. Distribute the database file separately (e.g., as a second asset on
the Releases page) or let the app create a fresh one on first run.

---

## Option 1 – PyInstaller (recommended)

[PyInstaller](https://pyinstaller.org) bundles the Python interpreter, all dependencies,
and the app's own code into a single folder or a single file (`--onefile`). It is the
most widely used tool for this purpose and has explicit NiceGUI support.

### How it works

```
pip install pyinstaller
pyinstaller --onefile \
    --name KonzertKatalog \
    --add-data "app/static:app/static" \       # include any static assets
    main.py
```

The resulting `dist/KonzertKatalog` (macOS/Linux) or `dist/KonzertKatalog.exe`
(Windows) is a fully self-contained executable.

### NiceGUI-specific notes

NiceGUI bundles its own Vue/Quasar frontend assets; you must tell PyInstaller to include
them:

```python
# konzert.spec  (auto-generated, then customised)
import nicegui, pathlib

nicegui_dir = pathlib.Path(nicegui.__file__).parent
a = Analysis(
    ["main.py"],
    datas=[
        (str(nicegui_dir / "web"), "nicegui/web"),   # NiceGUI frontend assets
    ],
    ...
)
```

NiceGUI's own documentation provides a ready-made PyInstaller spec file example.

### GitHub Actions build matrix

```yaml
# .github/workflows/release.yml
jobs:
  build:
    strategy:
      matrix:
        os: [windows-latest, macos-latest]
    runs-on: ${{ matrix.os }}
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: "3.12" }
      - run: pip install pyinstaller nicegui sqlalchemy loguru
      - run: pyinstaller konzert.spec
      - uses: actions/upload-artifact@v4
        with:
          name: KonzertKatalog-${{ runner.os }}
          path: dist/
```

On release, upload both artefacts to the GitHub Release.

### Pros / cons

| ✅ Pros | ⚠️ Cons |
|---------|---------|
| Single `.exe` / binary, no install | Antivirus false-positives on Windows |
| Well-documented NiceGUI integration | Large binary (~60–100 MB) |
| Free, open source | Must build separately per platform |

---

## Option 2 – Nuitka

[Nuitka](https://nuitka.net) compiles Python to C and then to a native binary. The
result is typically smaller and starts faster than a PyInstaller bundle.

```bash
pip install nuitka
python -m nuitka \
    --standalone \
    --onefile \
    --include-package=nicegui \
    --include-data-dir=path/to/nicegui/web=nicegui/web \
    main.py
```

### Pros / cons

| ✅ Pros | ⚠️ Cons |
|---------|---------|
| Smaller binary, faster startup | More complex build configuration |
| True native compilation | Longer build time |
| Good macOS + Windows support | Less NiceGUI-specific documentation |

---

## Option 3 – uv + zipapp (lightweight, Python required)

If requiring Python on the target machine is acceptable, `uv` can export a locked
virtual environment that travels with the source:

```bash
uv export --no-dev > requirements.txt
python -m zipapp . -m main:app -o KonzertKatalog.pyz
```

This creates a single `.pyz` archive. On the target machine:

```bash
# macOS / Linux
python3 KonzertKatalog.pyz

# Windows
py KonzertKatalog.pyz
```

**Not truly standalone** (Python must be installed), but produces the smallest artefact
and avoids cross-platform compiler issues.

---

## Recommended release artefacts on GitHub Releases

```
KonzertKatalog-windows-x64.exe   ← PyInstaller --onefile Windows build
KonzertKatalog-macos-universal.zip ← PyInstaller macOS app bundle (zipped)
konzert.db                         ← Blank starter database (optional)
RELEASE_NOTES.md
```

Users on macOS must run `xattr -d com.apple.quarantine KonzertKatalog` (or right-click →
Open) the first time because the binary is not notarised.

---

## macOS-specific considerations

| Topic | Action |
|-------|--------|
| Notarisation | Not required for personal use, but Gatekeeper will warn. Instruct users to right-click → Open the first time. |
| Universal binary | Build on `macos-latest` (ARM) *and* `macos-13` (Intel) or use `lipo` to merge into a universal binary. |
| App bundle | Wrap with `--windowed` and a `.icns` icon for a proper `.app` package. |

---

## Windows-specific considerations

| Topic | Action |
|-------|--------|
| Code signing | Not required, but Windows SmartScreen will warn. Advise users to click "More info → Run anyway". |
| Antivirus | PyInstaller binaries are occasionally flagged. Submitting to Microsoft/vendors resolves false positives. |
| Installer | For wider distribution consider wrapping the `.exe` with [Inno Setup](https://jrsoftware.org/isinfo.php) (free). |

---

## Configuring the database path

In `app/database.py`, replace the hard-coded path with:

```python
import os
from pathlib import Path
from platformdirs import user_data_dir   # pip install platformdirs

def _default_db_path() -> Path:
    return Path(user_data_dir("KonzertKatalog")) / "konzert.db"

DB_PATH = Path(os.environ.get("KONZERT_DB_PATH", _default_db_path()))
DB_PATH.parent.mkdir(parents=True, exist_ok=True)
DATABASE_URL = f"sqlite:///{DB_PATH}"
```

This means:
- Power users set `KONZERT_DB_PATH=/path/to/my/konzert.db` before launching.
- Regular users get a sensible per-user location automatically.
- The database is **never** embedded in the executable.
