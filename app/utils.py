"""Shared utility helpers used across multiple modules."""


def filter_rows(all_rows: list[dict], query: str) -> list[dict]:
    """Return rows where any string value contains *query* (case-insensitive)."""
    q = query.strip().lower()
    if not q:
        return all_rows
    return [r for r in all_rows if any(q in str(v).lower() for v in r.values())]
