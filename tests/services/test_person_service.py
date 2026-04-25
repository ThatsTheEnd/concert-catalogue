
from app.services.person_service import (
    create_artist,
    create_composer,
    list_artists,
    list_composers,
    search_artists,
    search_composers,
)


def test_create_and_list_composer(session):
    create_composer(session, first_name="Johann Sebastian", last_name="Bach", birth_year=1685)
    results = list_composers(session)
    assert any(c.last_name == "Bach" for c in results)


def test_create_and_list_artist(session):
    create_artist(session, first_name="Yo-Yo", last_name="Ma", default_instrument="Cello")
    results = list_artists(session)
    assert any(a.last_name == "Ma" for a in results)


def test_search_composers(session):
    create_composer(session, first_name="Franz", last_name="Schubert")
    assert len(search_composers(session, "Schu")) == 1


def test_search_artists(session):
    create_artist(session, first_name="Lang", last_name="Lang", default_instrument="Piano")
    assert len(search_artists(session, "lang")) == 1


def test_create_composer_with_catalogue(session):
    composer = create_composer(
        session, first_name="Wolfgang Amadeus", last_name="Mozart",
        birth_year=1756, death_year=1791, catalogue="KV",
    )
    results = list_composers(session)
    found = [c for c in results if c.id == composer.id][0]
    assert found.catalogue == "KV"
    assert found.birth_year == 1756
