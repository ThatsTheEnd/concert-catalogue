import uuid
from pathlib import Path

UPLOADS_ROOT = Path(__file__).parent.parent.parent / "data" / "uploads"


def save_upload(concert_id: int, attachment_type: str, filename: str, content: bytes) -> str:
    """Save uploaded file and return the relative path (used as file_path in Attachment)."""
    dest_dir = UPLOADS_ROOT / str(concert_id) / attachment_type
    dest_dir.mkdir(parents=True, exist_ok=True)
    safe_name = Path(filename).name  # strip any directory component
    unique_name = f"{uuid.uuid4().hex}_{safe_name}"
    dest = dest_dir / unique_name
    dest.write_bytes(content)
    return str(dest.relative_to(UPLOADS_ROOT.parent.parent))  # relative to project root


def delete_upload(file_path: str) -> None:
    """Delete a stored upload by its relative path."""
    full_path = Path(__file__).parent.parent.parent / file_path
    if full_path.exists():
        full_path.unlink()


def url_for_upload(file_path: str) -> str:
    """Convert a stored file_path to the URL served by NiceGUI static files."""
    # NiceGUI serves data/uploads/ as /uploads/
    relative = Path(file_path)
    # file_path is like data/uploads/1/ticket/abc_ticket.jpg
    # URL is /uploads/1/ticket/abc_ticket.jpg
    parts = relative.parts
    if "uploads" in parts:
        idx = list(parts).index("uploads")
        return "/" + "/".join(parts[idx:])
    return f"/{file_path}"
