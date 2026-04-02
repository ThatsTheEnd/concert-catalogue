from datetime import date

from app.models import (
    Artist,
    Composer,
    Concert,
    ConcertArtist,
    ConcertPiece,
    Conductor,
    Orchestra,
    Piece,
    Venue,
)


def test_venue_repr(session):
    venue = Venue(name="Elbphilharmonie", city="Hamburg", country="Germany")
    session.add(venue)
    session.commit()
    assert "Elbphilharmonie" in repr(venue)
    assert "Hamburg" in repr(venue)


def test_conductor_full_name(session):
    c = Conductor(first_name="Simon", last_name="Rattle")
    session.add(c)
    session.commit()
    assert c.full_name == "Simon Rattle"


def test_composer_full_name(session):
    c = Composer(
        first_name="Wolfgang Amadeus", last_name="Mozart", birth_year=1756, death_year=1791
    )
    session.add(c)
    session.commit()
    assert c.full_name == "Wolfgang Amadeus Mozart"
    assert c.birth_year == 1756


def test_piece_display_name_key_before_catalogue(session):
    """Key must appear before catalogue number in display name."""
    composer = Composer(first_name="Ludwig van", last_name="Beethoven", catalogue="Op.")
    session.add(composer)
    session.flush()
    piece = Piece(
        composer_id=composer.id, title="Symphony No. 9", key="D minor", catalogue_number="125"
    )
    session.add(piece)
    session.commit()
    assert "Symphony No. 9" in piece.display_name
    assert "Op. 125" in piece.display_name
    assert "D minor" in piece.display_name
    # key must come before catalogue number in the string
    assert piece.display_name.index("D minor") < piece.display_name.index("Op. 125")


def test_concert_without_title(session):
    """Concerts have no title — identified by date, orchestra, venue."""
    orch = Orchestra(name="Berliner Philharmoniker")
    session.add(orch)
    session.flush()
    concert = Concert(date=date(2024, 3, 1), orchestra_id=orch.id)
    session.add(concert)
    session.commit()
    assert concert.id is not None
    assert repr(concert)  # should not crash


def test_concert_without_conductor(session):
    """A chamber orchestra may perform without a conductor."""
    orch = Orchestra(name="Artemis Quartett")
    session.add(orch)
    session.flush()
    concert = Concert(date=date(2024, 3, 1), orchestra_id=orch.id)
    session.add(concert)
    session.commit()
    assert concert.conductor is None


def test_concert_with_choir(session):
    """Concert can have a choir name and choir director (both optional)."""
    director = Conductor(first_name="Simon", last_name="Halsey")
    session.add(director)
    session.flush()
    orch = Orchestra(name="Berliner Philharmoniker")
    session.add(orch)
    session.flush()
    concert = Concert(
        date=date(2024, 4, 10),
        orchestra_id=orch.id,
        choir="Rundfunkchor Berlin",
        choir_director_id=director.id,
    )
    session.add(concert)
    session.commit()
    assert concert.choir == "Rundfunkchor Berlin"
    assert concert.choir_director.full_name == "Simon Halsey"


def test_concert_with_multiple_soloists(session):
    """A concert can have more than one soloist."""
    a1 = Artist(first_name="Anne-Sophie", last_name="Mutter", instrument="Violin")
    a2 = Artist(first_name="Yo-Yo", last_name="Ma", instrument="Cello")
    session.add_all([a1, a2])
    session.flush()
    orch = Orchestra(name="Chamber Orchestra")
    session.add(orch)
    session.flush()
    concert = Concert(date=date(2024, 5, 1), orchestra_id=orch.id)
    session.add(concert)
    session.flush()
    session.add(ConcertArtist(concert_id=concert.id, artist_id=a1.id, role="Soloist"))
    session.add(ConcertArtist(concert_id=concert.id, artist_id=a2.id, role="Soloist"))
    session.commit()
    session.refresh(concert)
    assert len(concert.artist_links) == 2


def test_concert_with_all_relations(session):
    venue = Venue(name="Berliner Philharmonie", city="Berlin")
    conductor = Conductor(first_name="Herbert von", last_name="Karajan")
    composer = Composer(first_name="Johannes", last_name="Brahms")
    session.add_all([venue, conductor, composer])
    session.flush()

    piece = Piece(composer_id=composer.id, title="Symphony No. 4", key="E minor")
    artist = Artist(first_name="Anne-Sophie", last_name="Mutter", instrument="Violin")
    session.add_all([piece, artist])
    session.flush()

    orch = Orchestra(name="Berliner Philharmoniker")
    session.add(orch)
    session.flush()
    concert = Concert(
        date=date(2023, 11, 15),
        orchestra_id=orch.id,
        venue_id=venue.id,
        conductor_id=conductor.id,
    )
    session.add(concert)
    session.flush()

    session.add(ConcertArtist(concert_id=concert.id, artist_id=artist.id, role="Soloist"))
    session.add(ConcertPiece(concert_id=concert.id, piece_id=piece.id, sort_order=1))
    session.commit()

    assert concert.venue.name == "Berliner Philharmonie"
    assert concert.conductor.full_name == "Herbert von Karajan"
    assert len(concert.artist_links) == 1
    assert concert.artist_links[0].artist.full_name == "Anne-Sophie Mutter"
    assert len(concert.piece_links) == 1
    assert concert.piece_links[0].piece.title == "Symphony No. 4"


def test_concert_pieces_ordered_by_sort_order(session):
    composer = Composer(first_name="Ludwig van", last_name="Beethoven")
    session.add(composer)
    session.flush()

    piece1 = Piece(composer_id=composer.id, title="Overture")
    piece2 = Piece(composer_id=composer.id, title="Symphony No. 5")
    session.add_all([piece1, piece2])
    session.flush()

    orch = Orchestra(name="Festspielorchester")
    session.add(orch)
    session.flush()
    concert = Concert(date=date(2024, 1, 10), orchestra_id=orch.id)
    session.add(concert)
    session.flush()

    # Add in reverse order to verify sort_order, not insertion order
    session.add(ConcertPiece(concert_id=concert.id, piece_id=piece2.id, sort_order=2))
    session.add(ConcertPiece(concert_id=concert.id, piece_id=piece1.id, sort_order=1))
    session.commit()

    session.refresh(concert)
    titles = [cp.piece.title for cp in concert.piece_links]
    assert titles == ["Overture", "Symphony No. 5"]
