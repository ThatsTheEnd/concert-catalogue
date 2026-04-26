"""Tests for concert detail view helpers."""

import pytest

from app.views.concert_detail import _is_image


# ---------------------------------------------------------------------------
# _is_image — pure helper that drives the image vs. document rendering path
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("filename", [
    "photo.jpg",
    "photo.JPG",
    "scan.jpeg",
    "scan.JPEG",
    "screenshot.png",
    "screenshot.PNG",
    "animation.gif",
    "animation.GIF",
    "thumbnail.webp",
    "thumbnail.WEBP",
    "image.bmp",
    "vector.svg",
])
def test_is_image_returns_true_for_image_extensions(filename):
    assert _is_image(filename) is True


@pytest.mark.parametrize("filename", [
    "review.pdf",
    "review.PDF",
    "programme.PDF",
    "ticket.docx",
    "notes.txt",
    "archive.zip",
    "noextension",
    "",
])
def test_is_image_returns_false_for_non_image_files(filename):
    assert _is_image(filename) is False


def test_is_image_strips_path_components():
    """Only the file extension matters — path prefixes must not interfere."""
    assert _is_image("2024/ticket/abc123_scan.jpg") is True
    assert _is_image("2024/review/abc123_notes.pdf") is False


def test_is_image_timestamped_pdf_filename():
    """Realistic stored filename from a concert attachment upload."""
    assert _is_image("2025-05-12T14_35_15Z 849_RHB_EN.pdf") is False
