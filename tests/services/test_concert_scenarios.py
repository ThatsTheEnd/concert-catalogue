"""
Integration tests covering the bug scenarios from the issue report:
- Concert without conductor (chamber orchestra)
- Concert with multiple soloists
- Concert with choir + choir director
- Conductor search returns correct results for autocomplete
- Concert update persists all fields correctly
"""
from datetime import date

from app.models import Artist, Composer, Piece
from app.services.concert_service import create_concert, get_concert, update_concert
from app.services.orchestra_service import create_orchestra
from app.services.person_service import create_conductor, search_conductors


def test_concert_without_conductor_chamber_orchestra(session):
    """A chamber orchestra plays without a conductor — conductor_id must be optional."""
    orch = create_orchestra(session, name="Artemis Quartett")
    concert = create_concert(
        session,
        date=date(2024, 2, 14),
        orchestra_id=orch.id,
        conductor_id=None,
    )
    fetched = get_concert(session, concert.id)
    assert fetched is not None
    assert fetched.conductor_id is None
    assert fetched.conductor is None


def test_concert_with_multiple_soloists(session):
    """Bug scenario: adding more than one soloist/artist to a concert."""
    a1 = Artist(first_name="Anne-Sophie", last_name="Mutter", instrument="Violin")
    a2 = Artist(first_name="Yo-Yo", last_name="Ma", instrument="Cello")
    a3 = Artist(first_name="Lang", last_name="Lang", instrument="Piano")
    session.add_all([a1, a2, a3])
    session.flush()

    orch = create_orchestra(session, name="Berliner Philharmoniker")
    concert = create_concert(
        session,
        date=date(2024, 3, 10),
        orchestra_id=orch.id,
        artists=[
            {"artist_id": a1.id, "role": "Soloist"},
            {"artist_id": a2.id, "role": "Soloist"},
            {"artist_id": a3.id, "role": "Soloist"},
        ],
    )
    fetched = get_concert(session, concert.id)
    assert fetched is not None
    assert len(fetched.artist_links) == 3
    names = {lnk.artist.full_name for lnk in fetched.artist_links}
    assert "Anne-Sophie Mutter" in names
    assert "Yo-Yo Ma" in names
    assert "Lang Lang" in names


def test_concert_with_choir_and_director(session):
    """Concert with choir name and a choir director (separate from main conductor)."""
    conductor = create_conductor(session, first_name="Simon", last_name="Rattle")
    choir_dir = create_conductor(session, first_name="Simon", last_name="Halsey")

    orch = create_orchestra(session, name="Berliner Philharmoniker")
    concert = create_concert(
        session,
        date=date(2024, 5, 1),
        orchestra_id=orch.id,
        conductor_id=conductor.id,
        choir="Rundfunkchor Berlin",
        choir_director_id=choir_dir.id,
    )
    fetched = get_concert(session, concert.id)
    assert fetched is not None
    assert fetched.choir == "Rundfunkchor Berlin"
    assert fetched.choir_director_id == choir_dir.id
    assert fetched.choir_director.full_name == "Simon Halsey"
    assert fetched.conductor.full_name == "Simon Rattle"


def test_concert_with_choir_no_director(session):
    """Choir director is optional — a choir name alone is valid."""
    orch = create_orchestra(session, name="Münchner Philharmoniker")
    concert = create_concert(
        session,
        date=date(2024, 6, 1),
        orchestra_id=orch.id,
        choir="Chor des Bayerischen Rundfunks",
        choir_director_id=None,
    )
    fetched = get_concert(session, concert.id)
    assert fetched is not None
    assert fetched.choir == "Chor des Bayerischen Rundfunks"
    assert fetched.choir_director is None


def test_conductor_search_for_autocomplete(session):
    """Bug scenario: conductor dropdown search returns filtered results."""
    create_conductor(session, first_name="Carlos", last_name="Kleiber")
    create_conductor(session, first_name="Carlos", last_name="Kleiber")  # duplicate ok
    create_conductor(session, first_name="Daniel", last_name="Barenboim")
    create_conductor(session, first_name="Claudio", last_name="Abbado")

    results = search_conductors(session, "Kleiber")
    assert len(results) == 2
    assert all(c.last_name == "Kleiber" for c in results)

    results = search_conductors(session, "bar")  # case-insensitive
    assert any(c.last_name == "Barenboim" for c in results)

    results = search_conductors(session, "xyz")
    assert len(results) == 0


def test_concert_update_persists_choir_and_soloists(session):
    """Updating a concert correctly replaces choir and soloist data."""
    conductor = create_conductor(session, first_name="Kent", last_name="Nagano")
    artist = Artist(first_name="Elina", last_name="Garanca", instrument="Mezzo-soprano")
    session.add(artist)
    session.flush()

    orch = create_orchestra(session, name="Orchestre de Paris")
    concert = create_concert(
        session,
        date=date(2022, 9, 1),
        orchestra_id=orch.id,
        conductor_id=conductor.id,
        artists=[{"artist_id": artist.id, "role": "Soloist"}],
    )
    assert concert.choir == ""
    assert len(concert.artist_links) == 1

    # Update: add choir
    updated = update_concert(session, concert.id, choir="Choeur de l'Orchestre de Paris")
    assert updated is not None
    assert updated.choir == "Choeur de l'Orchestre de Paris"
    # Soloists unchanged
    assert len(updated.artist_links) == 1


def test_program_piece_ordering_after_save(session):
    """Program pieces must be stored in user-defined performance order."""
    composer = Composer(first_name="Ludwig van", last_name="Beethoven")
    session.add(composer)
    session.flush()

    overture = Piece(composer_id=composer.id, title="Coriolan Overture")
    concerto = Piece(composer_id=composer.id, title="Piano Concerto No. 5")
    symphony = Piece(composer_id=composer.id, title="Symphony No. 7")
    session.add_all([overture, concerto, symphony])
    session.flush()

    orch = create_orchestra(session, name="Wiener Philharmoniker")
    concert = create_concert(
        session,
        date=date(2024, 7, 15),
        orchestra_id=orch.id,
        pieces=[
            {"piece_id": overture.id, "sort_order": 0},
            {"piece_id": concerto.id, "sort_order": 1},
            {"piece_id": symphony.id, "sort_order": 2},
        ],
    )
    fetched = get_concert(session, concert.id)
    assert fetched is not None
    program = [lnk.piece.title for lnk in fetched.piece_links]
    assert program == ["Coriolan Overture", "Piano Concerto No. 5", "Symphony No. 7"]
