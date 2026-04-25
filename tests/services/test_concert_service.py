from datetime import date

import pytest

from app.models import Artist, Composer, Piece, Venue
from app.services.concert_service import (
    create_concert,
    delete_concert,
    get_concert,
    list_concerts,
    update_concert,
)
from app.services.orchestra_service import create_orchestra


@pytest.fixture
def seed(session):
    venue = Venue(name="Elbphilharmonie", city="Hamburg")
    conductor = Artist(first_name="Kent", last_name="Nagano")
    composer = Composer(first_name="Gustav", last_name="Mahler")
    session.add_all([venue, conductor, composer])
    session.flush()
    piece = Piece(composer_id=composer.id, title="Symphony No. 2")
    artist = Artist(first_name="Elina", last_name="Garanca", default_instrument="Mezzo-soprano")
    session.add_all([piece, artist])
    session.commit()
    return {
        "venue": venue, "conductor": conductor,
        "composer": composer, "piece": piece, "artist": artist,
    }


def test_create_concert(session, seed):
    orch = create_orchestra(session, name="NDR Elbphilharmonie Orchester")
    concert = create_concert(
        session,
        date=date(2022, 5, 20),
        orchestra_id=orch.id,
        venue_id=seed["venue"].id,
        conductor_id=seed["conductor"].id,
    )
    assert concert.id is not None
    assert concert.orchestra.name == "NDR Elbphilharmonie Orchester"
    assert concert.venue.name == "Elbphilharmonie"


def test_get_concert(session, seed):
    orch = create_orchestra(session, name="NDR")
    concert = create_concert(session, date=date(2022, 5, 20), orchestra_id=orch.id)
    fetched = get_concert(session, concert.id)
    assert fetched is not None
    assert fetched.id == concert.id


def test_get_concert_not_found(session):
    assert get_concert(session, 9999) is None


def test_list_concerts_pagination(session):
    for i in range(5):
        orch = create_orchestra(session, name=f"Orchestra {i}")
        create_concert(session, date=date(2023, 1, i + 1), orchestra_id=orch.id)
    page1 = list_concerts(session, limit=3, offset=0)
    page2 = list_concerts(session, limit=3, offset=3)
    assert len(page1) == 3
    assert len(page2) == 2


def test_list_concerts_filter_by_orchestra(session):
    orch1 = create_orchestra(session, name="Berliner Philharmoniker")
    orch2 = create_orchestra(session, name="Wiener Philharmoniker")
    create_concert(session, date=date(2023, 1, 1), orchestra_id=orch1.id)
    create_concert(session, date=date(2023, 2, 1), orchestra_id=orch2.id)
    results = list_concerts(session, search="Berliner")
    assert len(results) == 1
    assert results[0].orchestra.name == "Berliner Philharmoniker"


def test_update_concert(session, seed):
    orch_old = create_orchestra(session, name="Old Orchestra")
    concert = create_concert(session, date=date(2022, 5, 20), orchestra_id=orch_old.id)
    orch_new = create_orchestra(session, name="New Orchestra")
    updated = update_concert(session, concert.id, orchestra_id=orch_new.id)
    assert updated is not None
    assert updated.orchestra.name == "New Orchestra"


def test_delete_concert(session):
    orch = create_orchestra(session, name="To Delete")
    concert = create_concert(session, date=date(2022, 5, 20), orchestra_id=orch.id)
    delete_concert(session, concert.id)
    assert get_concert(session, concert.id) is None


def test_create_concert_with_pieces_and_artists(session, seed):
    orch = create_orchestra(session, name="NDR")
    concert = create_concert(
        session,
        date=date(2022, 5, 20),
        orchestra_id=orch.id,
        pieces=[{"piece_id": seed["piece"].id, "sort_order": 1}],
        artists=[{"artist_id": seed["artist"].id, "role": "Soloist"}],
    )
    assert len(concert.piece_links) == 1
    assert len(concert.artist_links) == 1
    assert concert.piece_links[0].sort_order == 1
