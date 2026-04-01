
from app.services.person_service import (
    create_artist,
    create_composer,
    create_conductor,
    list_artists,
    list_composers,
    list_conductors,
    search_artists,
    search_composers,
    search_conductors,
)


def test_create_and_list_conductor(session):
    create_conductor(session, first_name="Carlos", last_name="Kleiber")
    results = list_conductors(session)
    assert any(c.last_name == "Kleiber" for c in results)


def test_create_and_list_composer(session):
    create_composer(session, first_name="Johann Sebastian", last_name="Bach", birth_year=1685)
    results = list_composers(session)
    assert any(c.last_name == "Bach" for c in results)


def test_create_and_list_artist(session):
    create_artist(session, first_name="Yo-Yo", last_name="Ma", instrument="Cello")
    results = list_artists(session)
    assert any(a.last_name == "Ma" for a in results)


def test_search_conductors(session):
    create_conductor(session, first_name="Claudio", last_name="Abbado")
    create_conductor(session, first_name="Daniel", last_name="Barenboim")
    assert len(search_conductors(session, "Abbado")) == 1
    assert len(search_conductors(session, "xx")) == 0


def test_search_composers(session):
    create_composer(session, first_name="Franz", last_name="Schubert")
    assert len(search_composers(session, "Schu")) == 1


def test_search_artists(session):
    create_artist(session, first_name="Lang", last_name="Lang", instrument="Piano")
    assert len(search_artists(session, "lang")) == 1
