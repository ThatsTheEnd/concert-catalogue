from datetime import date

from app.models import Piece
from app.services.concert_service import create_concert
from app.services.person_service import create_composer, create_conductor
from app.services.search_service import search_all


def test_search_finds_concert_by_composer(session):
    composer = create_composer(session, first_name="Wolfgang Amadeus", last_name="Mozart")
    piece = Piece(composer_id=composer.id, title="Symphony No. 40")
    session.add(piece)
    session.flush()
    concert = create_concert(
        session,
        date=date(2023, 3, 10),
        title="Mozart Evening",
        pieces=[{"piece_id": piece.id, "sort_order": 1}],
    )
    results = search_all(session, "Mozart")
    concert_ids = [c.id for c in results["concerts"]]
    assert concert.id in concert_ids


def test_search_finds_concert_by_conductor(session):
    conductor = create_conductor(session, first_name="Valery", last_name="Gergiev")
    concert = create_concert(
        session,
        date=date(2023, 4, 1),
        title="Russian Night",
        conductor_id=conductor.id,
    )
    results = search_all(session, "Gergiev")
    assert concert.id in [c.id for c in results["concerts"]]


def test_search_returns_grouped_results(session):
    create_conductor(session, first_name="Simon", last_name="Rattle")
    results = search_all(session, "Rattle")
    assert "concerts" in results
    assert "conductors" in results
    assert any(c.last_name == "Rattle" for c in results["conductors"])
