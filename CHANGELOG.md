# Changelog

All notable changes to KonzertKatalog are documented here.

---

## [1.2.2] — 2026-04-26

### Fixed

- **PDF attachments openable** — clicking a PDF (or any non-image) attachment
  in the concert detail view now opens the file in a new browser tab instead of
  showing a blank lightbox dialog. Images continue to open in the in-page
  lightbox as before. Non-image thumbnails now display a document icon so users
  can recognise the file type at a glance. Resolves #10.

### Tests

- `test_is_image_returns_true_for_image_extensions` — parametrised over common
  image extensions (jpg, jpeg, png, gif, webp, bmp, svg) including mixed case.
- `test_is_image_returns_false_for_non_image_files` — parametrised over pdf,
  docx, txt, zip and extension-less filenames.
- `test_is_image_strips_path_components` — verifies path prefixes do not
  interfere with the extension check.
- `test_is_image_timestamped_pdf_filename` — exercises the real-world filename
  pattern produced by the upload handler.

---

## [1.2.1] — 2026-04-26

### Fixed

- **Quick filter wired up** — the text input on the concerts list was not
  triggering searches due to a wrong Vue event binding (`update:model-value`
  with `GenericEventArguments` instead of `on_change` with
  `ValueChangeEventArguments`). Typing in the field now actually filters the
  list.
- **Session not prematurely closed** — `session.close()` was called immediately
  after the initial page render, before any user interaction. Subsequent
  searches would silently fail. The session is now kept open for the lifetime
  of the page (closed on disconnect, as intended).

### Changed

- **Quick filter relabelled** — placeholder changed from "Search composers,
  artists, venues…" to "Quick filter…" (EN) / "Schnellfilter…" (DE) to reflect
  its narrower scope vs. the dedicated search page.
- **"Advanced search →" link** — a muted link next to the quick filter now
  points directly to `/search` for users who need date-range or per-entity
  filtering.

### Tests

- `test_concert_list_quick_filter_is_connected` — regression guard: proves the
  filter input is actually wired up by asserting a no-match term empties the
  table.
- `test_concert_list_has_advanced_search_link` — verifies the "Advanced search"
  link is present and href-targets `/search`.

---

## [1.2.0] — 2026-04-26

### Added

- **Werke editable** — pieces in the Reference Data → Werke tab can now be
  edited (title, key, catalogue number, composer) and deleted, matching the
  behaviour of all other reference data tabs. Resolves #11 / #19.
- **Back to concerts button** — a `← Concerts` button now appears in the
  concert detail header, allowing users to return to the concert list after
  viewing or creating a concert without having to use the nav bar.

### Fixed / Tests

- Added service-layer tests for `update_piece` and `delete_piece` to ensure
  both operations are covered.

---

## [1.1.1] — 2026-04-26

### Fixed

- **Reference data tables** — all columns (Werke, Komponisten, Künstler,
  Orchester, Spielorte) were right-aligned by default due to Quasar's table
  default. Explicit `align: left` added to every content column. (#12, #16)
- **Notes line breaks** — newlines entered in the Notizen textarea were
  collapsed to a single line on the concert detail view. Both concert-level
  and piece-level notes now render with `whitespace-pre-wrap`. (#13)


## [1.0.0] — 2026-04-25

### Breaking — Database schema change

This release consolidates the separate `Conductor` and `Artist` master-data
entities into a single `Artist` entity. If you are upgrading from an older
installation, **the application will automatically back up your existing
database** (renamed to `konzert_backup_<timestamp>.db` next to the original
file) and start fresh. No manual migration is required; you will be notified
with a dialog on first launch.

#### What changed in the schema

| Table | Change |
|---|---|
| `conductors` | **Dropped.** Conductors are now regular `Artist` records. |
| `artists.instrument` | **Renamed** to `artists.default_instrument` (nullable). Stores the artist's usual instrument as a suggestion; leave blank for pure conductors. |
| `concert_artists.instrument` | **Added** (nullable). Records the instrument the artist actually played at this specific concert, pre-filled from `default_instrument` but freely editable. |
| `concerts.conductor_id` | FK target changed from `conductors.id` → `artists.id`. |
| `concerts.choir_director_id` | FK target changed from `conductors.id` → `artists.id`. |

#### Why

Previously, a soloist who also conducted a concert had to be entered twice —
once as a Conductor and once as an Artist. The new design uses a single
`Artist` record for any person, with their role (conductor, soloist, etc.)
determined by context (the `conductor_id` FK or the `concert_artists.role`
field).

The instrument is now stored per-concert rather than per-person, so the same
pianist can be recorded playing harpsichord at a different event.

### Other changes in this release

- **Reference data:** Conductors tab removed from the Stammdaten page; artists
  who conduct appear in the Artists tab instead (with `Default instrument`
  left blank).
- **Concert form:** Conductor and choir-director selects now draw from the
  shared artist pool. The soloist section shows separate `Role` and
  `Instrument` fields; the instrument is pre-filled from the artist's default.
- **Startup guard:** If the on-disk database has an incompatible schema, it is
  automatically backed up and a fresh database is created. A dismissable dialog
  informs the user.
- **Tests:** Browser windows no longer open when running the test suite
  (`PYTEST_CURRENT_TEST` guard on `webbrowser.open`).

---

## [1.1.0] — 2026-04-25

### Added

- **Settings dialog** — a gear icon in the nav bar consolidates all user
  preferences into a single dialog, replacing the separate language and dark-
  mode buttons.
  - Language toggle (EN/DE).
  - Dark mode switch (takes effect immediately, no reload required).
  - Concert column configuration: control which columns are visible and in what
    order using checkboxes and up/down arrows. Preference is persisted in the
    database and survives restarts.
- **Soloists column** in the concert list — artists linked to a concert are now
  shown in a dedicated Soloists column.
- **Default column set** updated to match the requested layout: Date, Orchestra,
  Conductor, Soloists, Venue. Choir is hidden by default but can be re-enabled
  via the settings dialog.

### Changed

- `settings.value` column type widened from `VARCHAR(200)` to `TEXT` to
  accommodate JSON payloads (column config).

---

## [0.4.2] — 2026-04-02

- End-to-end tests using NiceGUI's user simulation framework.
- README rewritten for end users.

## [0.4.1] — 2026-04-02

- Database path moved outside the codebase to a platform-appropriate location:
  - macOS: `~/Library/Application Support/KonzertKatalog/konzert.db`
  - Windows: `%LOCALAPPDATA%\KonzertKatalog\konzert.db`
  - Linux: `~/.local/share/konzertkatalog/konzert.db`
- Override via `KONZERT_DB_PATH` environment variable.
- File uploads stored alongside the database in `{db_dir}/uploads/`.
- Composer catalogue-number prefix shown in the piece selection dropdown.
- Python requirement pinned to ≥ 3.13.

## [0.3.0] — earlier

- Filtering, search, and stop-button UX improvements.
- Reference-data filtering with per-column filter inputs.

## [0.2.0] — earlier

- Internationalisation (EN/DE).
- Choir support (`choir` name + `choir_director_id` on concerts).
- Venue entity and service layer.
- Attachment uploads (ticket, programme booklet, reviews).

## [0.1.0] — earlier

- Initial release.
- Core entities: Concert, Orchestra (as relation), Composer, Piece, Artist,
  Conductor, Venue.
- Service-layer architecture with SQLAlchemy ORM and NiceGUI front end.
