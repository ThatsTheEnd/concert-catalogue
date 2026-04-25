# KonzertKatalog

**Your personal classical concert archive** – keep a lasting record of every concert
you have attended: programme, soloists, conductor, venue, and any attachments such as
tickets or programme booklets.

![KonzertKatalog concert list](docs/screenshot-concerts.png)
<!-- Replace the placeholder above with an actual screenshot once taken -->

---

## Download & Install

No Python or programming knowledge required. Simply grab the pre-built executable for
your platform from the **[Releases page](https://github.com/ThatsTheEnd/concert-catalogue/releases/latest)**.

| Platform | File to download |
|----------|-----------------|
| **Windows** | `KonzertKatalog.exe` |
| **macOS / Linux** | `KonzertKatalog` |

### Windows

1. Download `KonzertKatalog.exe`.
2. Double-click it to run.
3. If Windows SmartScreen shows a warning, click **"More info" → "Run anyway"**.  
   *(The app is not code-signed; this warning is expected.)*

### macOS

1. Download `KonzertKatalog`.
2. Open a Terminal in the download folder and make it executable:
   ```bash
   chmod +x KonzertKatalog
   ```
3. The first time you open it, macOS Gatekeeper will block it because the binary is not
   notarised. Right-click (or Control-click) the file and choose **Open**, then confirm
   in the dialog.
4. Alternatively, remove the quarantine flag from Terminal:
   ```bash
   xattr -d com.apple.quarantine KonzertKatalog
   ```
5. Double-click to launch. A browser window opens automatically.

---

## Where is my data?

KonzertKatalog stores everything in a single SQLite database file. The location depends
on your operating system:

| Platform | Default database path |
|----------|-----------------------|
| **Windows** | `%LOCALAPPDATA%\KonzertKatalog\konzert.db` |
| **macOS** | `~/Library/Application Support/KonzertKatalog/konzert.db` |

The folder is created automatically on first launch. You can **back up** your data at
any time by copying this file, and you can **move it** to another machine just by
copying it there.

> **Custom path:** Set the environment variable `KONZERT_DB_PATH=/path/to/konzert.db`
> before launching the app to use a different location (e.g. a network drive or a
> shared folder).

Uploaded attachments (tickets, programme booklets, etc.) are stored in an `uploads/`
subfolder next to the database file.

---

## Using the App

When the app launches it opens in your default web browser. You can also navigate to
`http://localhost:8080` manually.

### Concerts list

The home page shows all your concerts, newest first. Use the **search box** in the
navigation bar to filter across all data. Click any concert row to open its detail view.

### Adding a concert

Click **"Add concert"** (or the ➕ button) to open the concert form. Fill in:

- **Date** and **venue**
- **Orchestra** and **conductor**
- **Programme** – one or more pieces with composer, title, and catalogue number
- **Soloists** – performer and instrument
- **Choir** and choir director (optional)
- **Attachments** – upload a ticket scan, programme booklet PDF, or review

Save with the **Save** button. The concert appears immediately in the list.

### Editing or deleting a concert

Open a concert's detail view and click **Edit** to change any field, or **Delete** to
remove it permanently.

### Reference data

The **Reference** section (nav-bar) lets you manage the building blocks used across
concerts:

- **Orchestras** – name and home city
- **Venues** – name and city
- **Composers** – name, birth/death years, and catalogue prefix (e.g. "KV" for Mozart)
- **Conductors** and **Artists** (soloists) – name and nationality

Entries can be added, edited, and deleted here or inline while filling in a concert
form.

### Search

The search box in the navigation bar performs a full-text search across concerts,
composers, conductors, artists, orchestras, and venues. Results are grouped by type.

### Language & dark mode

Use the toggle in the top-right corner to switch between **English** and **German**, or
to enable **dark mode**. Your preference is remembered for the current browser session.

---

## Upgrading

Download the new executable from the
[Releases page](https://github.com/ThatsTheEnd/concert-catalogue/releases) and replace
the old one. **Your database is untouched** – it lives outside the executable and
carries forward automatically.

---

## For Developers

<details>
<summary>Tech stack & contributing</summary>

**Stack:** Python 3.13+, [NiceGUI](https://nicegui.io/), SQLAlchemy 2, SQLite, loguru,
packaged with PyInstaller via `nicegui-pack`.

```bash
# Install dependencies (requires uv)
uv sync

# Run in development mode
uv run python main.py

# Run tests
uv run pytest

# Lint
uv run ruff check .
```

Pull requests are welcome! Please open an issue first to discuss significant changes.

</details>
