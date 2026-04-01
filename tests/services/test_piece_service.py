from app.models import Composer
from app.services.piece_service import create_piece, list_pieces, search_pieces


def test_create_and_list_piece(session):
    composer = Composer(first_name="Franz", last_name="Liszt")
    session.add(composer)
    session.flush()
    piece = create_piece(
        session, composer_id=composer.id, title="Piano Concerto No. 1", key="E-flat major"
    )
    pieces = list_pieces(session)
    assert any(p.id == piece.id for p in pieces)


def test_search_pieces_by_title(session):
    composer = Composer(first_name="Franz", last_name="Liszt")
    session.add(composer)
    session.flush()
    create_piece(session, composer_id=composer.id, title="Les Préludes")
    create_piece(session, composer_id=composer.id, title="Mephisto Waltz")
    assert len(search_pieces(session, "Préludes")) == 1


def test_search_pieces_by_composer_name(session):
    composer = Composer(first_name="Franz", last_name="Schubert")
    session.add(composer)
    session.flush()
    create_piece(session, composer_id=composer.id, title="Winterreise")
    assert len(search_pieces(session, "Schubert")) == 1
