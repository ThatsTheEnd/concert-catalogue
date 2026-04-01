from datetime import date

import pytest

from app.models import Artist, Composer, Conductor, Piece, Venue
from app.services.concert_service import (
    create_concert,
    delete_concert,
    get_concert,
    list_concerts,
    update_concert,
)


@pytest.fixture
def seed(session):
    venue = Venue(name="Elbphilharmonie", city="Hamburg")
    conductor = Conductor(first_name="Kent", last_name="Nagano")
    composer = Composer(first_name="Gustav", last_name="Mahler")
    session.add_all([venue, conductor, composer])
    session.flush()
    piece = Piece(composer_id=composer.id, title="Symphony No. 2")
    artist = Artist(first_name="Elina", last_name="Garanca", instrument="Mezzo-soprano")
    session.add_all([piece, artist])
    session.commit()
    return {
        "venue": venue, "conductor": conductor,
        "composer": composer, "piece": piece, "artist": artist,
    }


def test_create_concert(session, seed):
    concert = create_concert(
        session,
        date=date(2022, 5, 20),
        title="Mahler 2",
        orchestra="NDR Elbphilharmonie Orchester",
        venue_id=seed["venue"].id,
        conductor_id=seed["conductor"].id,
    )
    assert concert.id is not None
    assert concert.title == "Mahler 2"
    assert concert.venue.name == "Elbphilharmonie"


def test_get_concert(session, seed):
    concert = create_concert(session, date=date(2022, 5, 20), title="Mahler 2")
    fetched = get_concert(session, concert.id)
    assert fetched is not None
    assert fetched.id == concert.id


def test_get_concert_not_found(session):
    assert get_concert(session, 9999) is None


def test_list_concerts_pagination(session):
    for i in range(5):
        create_concert(session, date=date(2023, 1, i + 1), title=f"Concert {i}")
    page1 = list_concerts(session, limit=3, offset=0)
    page2 = list_concerts(session, limit=3, offset=3)
    assert len(page1) == 3
    assert len(page2) == 2


def test_list_concerts_filter_by_title(session):
    create_concert(session, date=date(2023, 1, 1), title="Beethoven Night")
    create_concert(session, date=date(2023, 2, 1), title="Brahms Evening")
    results = list_concerts(session, search="Beethoven")
    assert len(results) == 1
    assert results[0].title == "Beethoven Night"


def test_update_concert(session, seed):
    concert = create_concert(session, date=date(2022, 5, 20), title="Old Title")
    updated = update_concert(session, concert.id, title="New Title")
    assert updated is not None
    assert updated.title == "New Title"


def test_delete_concert(session, seed):
    concert = create_concert(session, date=date(2022, 5, 20), title="To Delete")
    delete_concert(session, concert.id)
    assert get_concert(session, concert.id) is None


def test_create_concert_with_pieces_and_artists(session, seed):
    concert = create_concert(
        session,
        date=date(2022, 5, 20),
        title="Mahler 2",
        pieces=[{"piece_id": seed["piece"].id, "sort_order": 1}],
        artists=[{"artist_id": seed["artist"].id, "role": "Soloist"}],
    )
    assert len(concert.piece_links) == 1
    assert len(concert.artist_links) == 1
    assert concert.piece_links[0].sort_order == 1
