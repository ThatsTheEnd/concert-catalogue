import uuid
from pathlib import Path

from app.database import DB_PATH

UPLOADS_ROOT = DB_PATH.parent / "uploads"


def save_upload(concert_id: int, attachment_type: str, filename: str, content: bytes) -> str:
    """Save uploaded file and return the relative path (used as file_path in Attachment)."""
    dest_dir = UPLOADS_ROOT / str(concert_id) / attachment_type
    dest_dir.mkdir(parents=True, exist_ok=True)
    safe_name = Path(filename).name  # strip any directory component
    unique_name = f"{uuid.uuid4().hex}_{safe_name}"
    dest = dest_dir / unique_name
    dest.write_bytes(content)
    return str(dest.relative_to(UPLOADS_ROOT))


def delete_upload(file_path: str) -> None:
    """Delete a stored upload by its relative path (relative to UPLOADS_ROOT)."""
    full_path = UPLOADS_ROOT / file_path
    if full_path.exists():
        full_path.unlink()


def url_for_upload(file_path: str) -> str:
    """Convert a stored file_path to the URL served by NiceGUI static files."""
    return f"/uploads/{file_path}"
