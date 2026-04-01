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
        orchestra="NDR Elbphilharmonie Orchester",
        venue_id=seed["venue"].id,
        conductor_id=seed["conductor"].id,
    )
    assert concert.id is not None
    assert concert.orchestra == "NDR Elbphilharmonie Orchester"
    assert concert.venue.name == "Elbphilharmonie"


def test_get_concert(session, seed):
    concert = create_concert(session, date=date(2022, 5, 20), orchestra="NDR")
    fetched = get_concert(session, concert.id)
    assert fetched is not None
    assert fetched.id == concert.id


def test_get_concert_not_found(session):
    assert get_concert(session, 9999) is None


def test_list_concerts_pagination(session):
    for i in range(5):
        create_concert(session, date=date(2023, 1, i + 1), orchestra=f"Orchestra {i}")
    page1 = list_concerts(session, limit=3, offset=0)
    page2 = list_concerts(session, limit=3, offset=3)
    assert len(page1) == 3
    assert len(page2) == 2


def test_list_concerts_filter_by_orchestra(session):
    create_concert(session, date=date(2023, 1, 1), orchestra="Berliner Philharmoniker")
    create_concert(session, date=date(2023, 2, 1), orchestra="Wiener Philharmoniker")
    results = list_concerts(session, search="Berliner")
    assert len(results) == 1
    assert results[0].orchestra == "Berliner Philharmoniker"


def test_update_concert(session, seed):
    concert = create_concert(session, date=date(2022, 5, 20), orchestra="Old Orchestra")
    updated = update_concert(session, concert.id, orchestra="New Orchestra")
    assert updated is not None
    assert updated.orchestra == "New Orchestra"


def test_delete_concert(session):
    concert = create_concert(session, date=date(2022, 5, 20), orchestra="To Delete")
    delete_concert(session, concert.id)
    assert get_concert(session, concert.id) is None


def test_create_concert_with_pieces_and_artists(session, seed):
    concert = create_concert(
        session,
        date=date(2022, 5, 20),
        orchestra="NDR",
        pieces=[{"piece_id": seed["piece"].id, "sort_order": 1}],
        artists=[{"artist_id": seed["artist"].id, "role": "Soloist"}],
    )
    assert len(concert.piece_links) == 1
    assert len(concert.artist_links) == 1
    assert concert.piece_links[0].sort_order == 1
