"""Simple EN/DE translation module. Language is stored per-user in app.storage.user."""
from nicegui import app as _app

_TRANSLATIONS: dict[str, dict[str, str]] = {
    "en": {
        # Nav
        "concerts": "Concerts",
        "reference_data": "Reference Data",
        "search_placeholder": "Search…",
        # Concert list
        "add_concert": "+ Add Concert",
        "search_concerts": "Search composers, conductors, artists, venues…",
        "no_results": "No concerts found.",
        "of_concerts": "concert(s)",
        "prev": "←",
        "next": "→",
        # Columns
        "col_date": "Date",
        "col_orchestra": "Orchestra",
        "col_venue": "Venue",
        "col_conductor": "Conductor",
        # Concert detail
        "conducted_by": "Conducted by",
        "choir": "Choir",
        "choir_director": "Choir Director",
        "soloists": "Soloists",
        "program": "Program",
        "notes": "Notes",
        "attachments": "Attachments",
        "tab_ticket": "Ticket",
        "tab_program": "Program Booklet",
        "tab_reviews": "Reviews",
        "no_images": "No images attached.",
        "edit": "Edit",
        "delete": "Delete",
        "delete_confirm": "Delete this concert?",
        "delete_warning": "This cannot be undone.",
        "cancel": "Cancel",
        "close": "Close",
        "save": "Save",
        "saved": "Saved!",
        # Concert form
        "add_concert_heading": "Add Concert",
        "edit_concert_heading": "Edit Concert",
        "date": "Date",
        "orchestra": "Orchestra",
        "venue": "Venue",
        "conductor": "Conductor (optional)",
        "choir_name": "Choir name",
        "choir_director_label": "Choir director (optional)",
        "add_piece": "Add piece",
        "add_artist": "Add artist",
        "piece_notes": "Notes",
        "role_instrument": "Role / instrument",
        "search_conductor": "Type to search conductors…",
        "search_orchestra": "Type to search orchestras…",
        "search_piece": "Search piece to add…",
        "search_artist": "Search artist to add…",
        "search_venue": "Type to search venues…",
        "search_choir_director": "Type to search choir directors…",
        "upload_ticket": "Upload Ticket",
        "upload_program": "Upload Program Booklet",
        "upload_reviews": "Upload Review(s)",
        # Reference data
        "composers": "Composers",
        "conductors": "Conductors",
        "artists": "Artists",
        "orchestras": "Orchestras",
        "pieces": "Pieces",
        "first_name": "First name",
        "last_name": "Last name",
        "birth_year": "Birth year",
        "death_year": "Death year",
        "catalogue_label": "Catalogue prefix (e.g. KV, HWV, Hob.)",
        "instrument": "Instrument",
        "piece_title": "Title",
        "key": "Key",
        "catalogue_number": "Catalogue no.",
        "composer": "Composer",
        "add": "Add",
        # Search
        "search_heading": "Search",
        "search_all_placeholder": "Search composers, conductors, artists, venues, pieces…",
        "results_concerts": "Concerts",
        "results_conductors": "Conductors",
        "results_composers": "Composers",
        "results_artists": "Artists",
        "results_venues": "Venues",
        "results_orchestras": "Orchestras",
        # Dark mode
        "dark_mode": "Dark mode",
        "light_mode": "Light mode",
        "language": "DE",  # button shows what you'd switch TO
    },
    "de": {
        # Nav
        "concerts": "Konzerte",
        "reference_data": "Stammdaten",
        "search_placeholder": "Suchen…",
        # Concert list
        "add_concert": "+ Konzert hinzufügen",
        "search_concerts": "Komponisten, Dirigenten, Künstler, Spielstätten suchen…",
        "no_results": "Keine Konzerte gefunden.",
        "of_concerts": "Konzert(e)",
        "prev": "←",
        "next": "→",
        # Columns
        "col_date": "Datum",
        "col_orchestra": "Orchester",
        "col_venue": "Spielstätte",
        "col_conductor": "Dirigent",
        # Concert detail
        "conducted_by": "Dirigent",
        "choir": "Chor",
        "choir_director": "Chordirektor",
        "soloists": "Solisten",
        "program": "Programm",
        "notes": "Notizen",
        "attachments": "Anhänge",
        "tab_ticket": "Ticket",
        "tab_program": "Programmheft",
        "tab_reviews": "Kritiken",
        "no_images": "Keine Bilder angefügt.",
        "edit": "Bearbeiten",
        "delete": "Löschen",
        "delete_confirm": "Dieses Konzert löschen?",
        "delete_warning": "Diese Aktion kann nicht rückgängig gemacht werden.",
        "cancel": "Abbrechen",
        "close": "Schließen",
        "save": "Speichern",
        "saved": "Gespeichert!",
        # Concert form
        "add_concert_heading": "Konzert hinzufügen",
        "edit_concert_heading": "Konzert bearbeiten",
        "date": "Datum",
        "orchestra": "Orchester",
        "venue": "Spielstätte",
        "conductor": "Dirigent (optional)",
        "choir_name": "Chorname",
        "choir_director_label": "Chordirektor (optional)",
        "add_piece": "Werk hinzufügen",
        "add_artist": "Künstler hinzufügen",
        "piece_notes": "Notizen",
        "role_instrument": "Rolle / Instrument",
        "search_conductor": "Dirigenten suchen…",
        "search_orchestra": "Orchester suchen…",
        "search_piece": "Werk suchen…",
        "search_artist": "Künstler suchen…",
        "search_venue": "Spielstätte suchen…",
        "search_choir_director": "Chordirektor suchen…",
        "upload_ticket": "Ticket hochladen",
        "upload_program": "Programmheft hochladen",
        "upload_reviews": "Kritik(en) hochladen",
        # Reference data
        "composers": "Komponisten",
        "conductors": "Dirigenten",
        "artists": "Künstler",
        "orchestras": "Orchester",
        "pieces": "Werke",
        "first_name": "Vorname",
        "last_name": "Nachname",
        "birth_year": "Geburtsjahr",
        "death_year": "Todesjahr",
        "catalogue_label": "Verzeichnis-Kürzel (z.B. KV, HWV, Hob.)",
        "instrument": "Instrument",
        "piece_title": "Titel",
        "key": "Tonart",
        "catalogue_number": "Verz.-Nr.",
        "composer": "Komponist",
        "add": "Hinzufügen",
        # Search
        "search_heading": "Suche",
        "search_all_placeholder": "Komponisten, Dirigenten, Künstler, Spielstätten, Werke suchen…",
        "results_concerts": "Konzerte",
        "results_conductors": "Dirigenten",
        "results_composers": "Komponisten",
        "results_artists": "Künstler",
        "results_venues": "Spielstätten",
        "results_orchestras": "Orchester",
        # Dark mode
        "dark_mode": "Dunkelmodus",
        "light_mode": "Hellmodus",
        "language": "EN",  # button shows what you'd switch TO
    },
}


def t(key: str) -> str:
    """Translate a key using the current user's language preference."""
    try:
        lang = _app.storage.user.get("lang", "en")
    except Exception:
        lang = "en"
    return _TRANSLATIONS.get(lang, _TRANSLATIONS["en"]).get(key, key)


def current_lang() -> str:
    try:
        return _app.storage.user.get("lang", "en")
    except Exception:
        return "en"


def toggle_lang() -> None:
    try:
        lang = _app.storage.user.get("lang", "en")
        _app.storage.user["lang"] = "de" if lang == "en" else "en"
    except Exception:
        pass
