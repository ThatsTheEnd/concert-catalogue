"""Tests for the filter_rows helper used in the reference-data tabs."""

import pytest

from app.utils import filter_rows


# ---------------------------------------------------------------------------
# Basic behaviour
# ---------------------------------------------------------------------------

def test_empty_query_returns_all_rows():
    rows = [{"id": 1, "name": "Alice"}, {"id": 2, "name": "Bob"}]
    assert filter_rows(rows, "") == rows


def test_whitespace_only_query_returns_all_rows():
    rows = [{"id": 1, "name": "Alice"}]
    assert filter_rows(rows, "   ") == rows


def test_matching_query_returns_only_matching_rows():
    rows = [
        {"id": 1, "name": "Berlin Philharmonic"},
        {"id": 2, "name": "Vienna Symphony"},
        {"id": 3, "name": "Royal Concertgebouw"},
    ]
    result = filter_rows(rows, "Vienna")
    assert len(result) == 1
    assert result[0]["id"] == 2


def test_no_match_returns_empty_list():
    rows = [{"id": 1, "name": "Berlin Philharmonic"}]
    assert filter_rows(rows, "zzz_no_match") == []


def test_filter_is_case_insensitive():
    rows = [{"id": 1, "name": "Mozart"}, {"id": 2, "name": "Bach"}]
    assert filter_rows(rows, "MOZART") == [{"id": 1, "name": "Mozart"}]
    assert filter_rows(rows, "mozart") == [{"id": 1, "name": "Mozart"}]
    assert filter_rows(rows, "MoZaRt") == [{"id": 1, "name": "Mozart"}]


def test_filter_matches_substring():
    rows = [{"id": 1, "name": "Berlin Philharmonic"}]
    assert filter_rows(rows, "Phil") == rows
    assert filter_rows(rows, "phil") == rows


def test_filter_searches_all_fields():
    rows = [
        {"id": 1, "first_name": "Ludwig", "last_name": "van Beethoven"},
        {"id": 2, "first_name": "Wolfgang", "last_name": "Mozart"},
    ]
    # Match on first_name
    assert filter_rows(rows, "Ludwig") == [rows[0]]
    # Match on last_name
    assert filter_rows(rows, "Beethoven") == [rows[0]]
    # No match
    assert filter_rows(rows, "Brahms") == []


def test_filter_matches_numeric_field_as_string():
    rows = [
        {"id": 1, "name": "Bach", "birth_year": 1685},
        {"id": 2, "name": "Mozart", "birth_year": 1756},
    ]
    result = filter_rows(rows, "1685")
    assert len(result) == 1
    assert result[0]["name"] == "Bach"


def test_filter_returns_multiple_matches():
    rows = [
        {"id": 1, "name": "Berlin Philharmonic"},
        {"id": 2, "name": "Berlin Symphony"},
        {"id": 3, "name": "Vienna Philharmonic"},
    ]
    result = filter_rows(rows, "Berlin")
    assert len(result) == 2
    ids = {r["id"] for r in result}
    assert ids == {1, 2}


def test_filter_query_is_stripped():
    rows = [{"id": 1, "name": "Mozart"}]
    # Leading/trailing spaces should not prevent a match
    assert filter_rows(rows, "  Mozart  ") == rows


def test_filter_with_none_value_in_row():
    """None values are converted to the string 'None'; query 'none' should match."""
    rows = [{"id": 1, "name": "Composer", "death_year": None}]
    # None becomes "None" — querying for "none" (case-insensitive) matches
    result = filter_rows(rows, "none")
    assert result == rows


# ---------------------------------------------------------------------------
# Realistic reference-data row shapes
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("query,expected_ids", [
    ("Wagner",  {1}),
    ("Brahms",  {2}),
    ("1813",    {1}),   # birth_year of Wagner
    ("ner",     {1}),   # substring of "Wagner"
    ("",        {1, 2}),
])
def test_composers_tab_filtering(query, expected_ids):
    rows = [
        {"id": 1, "last_name": "Wagner", "first_name": "Richard",
         "birth_year": 1813, "death_year": 1883, "catalogue": "WWV"},
        {"id": 2, "last_name": "Brahms", "first_name": "Johannes",
         "birth_year": 1833, "death_year": 1897, "catalogue": ""},
    ]
    result = filter_rows(rows, query)
    assert {r["id"] for r in result} == expected_ids


@pytest.mark.parametrize("query,expected_ids", [
    ("Carnegie",    {1}),
    ("Berlin",      {2}),
    ("Germany",     {2}),
    ("hall",        {1}),    # "Hall" appears only in Carnegie Hall
    ("xyz_no_match", set()),
])
def test_venues_tab_filtering(query, expected_ids):
    rows = [
        {"id": 1, "name": "Carnegie Hall", "city": "New York", "country": "USA"},
        {"id": 2, "name": "Berliner Philharmonie", "city": "Berlin", "country": "Germany"},
    ]
    result = filter_rows(rows, query)
    assert {r["id"] for r in result} == expected_ids
