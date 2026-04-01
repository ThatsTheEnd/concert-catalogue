from datetime import date

from app.models import (
    Artist,
    Composer,
    Concert,
    ConcertArtist,
    ConcertPiece,
    Conductor,
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


def test_piece_display_name(session):
    composer = Composer(first_name="Ludwig van", last_name="Beethoven")
    session.add(composer)
    session.flush()
    piece = Piece(
        composer_id=composer.id, title="Symphony No. 9", opus_number="Op. 125", key="D minor"
    )
    session.add(piece)
    session.commit()
    assert "Symphony No. 9" in piece.display_name
    assert "Op. 125" in piece.display_name


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

    concert = Concert(
        date=date(2023, 11, 15),
        title="Brahms Evening",
        orchestra="Berliner Philharmoniker",
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

    concert = Concert(date=date(2024, 1, 10), title="Beethoven Night")
    session.add(concert)
    session.flush()

    # Add in reverse order to verify sort_order, not insertion order
    session.add(ConcertPiece(concert_id=concert.id, piece_id=piece2.id, sort_order=2))
    session.add(ConcertPiece(concert_id=concert.id, piece_id=piece1.id, sort_order=1))
    session.commit()

    session.refresh(concert)
    titles = [cp.piece.title for cp in concert.piece_links]
    assert titles == ["Overture", "Symphony No. 5"]
