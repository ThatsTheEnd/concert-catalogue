"""Recreate data/konzert.db with the current schema, reference data, and one sample concert."""

import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker

import app.models  # noqa: F401 — registers all models with Base.metadata
from app.database import Base
from app.models import Artist, Composer, Concert, Orchestra, Venue
from app.seeds import seed_reference_data

DB_PATH = ROOT / "data" / "konzert.db"
DB_PATH.parent.mkdir(parents=True, exist_ok=True)

if DB_PATH.exists():
    DB_PATH.unlink()

engine = create_engine(f"sqlite:///{DB_PATH}", echo=False)
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine, expire_on_commit=False)

with Session() as session:
    # --- Reference data (composers, pieces, artists) ---
    seed_reference_data(session)
    session.flush()

    # --- Sample concert ---
    harnoncourt = session.scalars(
        select(Artist).where(Artist.last_name == "Harnoncourt")
    ).first()
    fischer = session.scalars(
        select(Artist).where(Artist.last_name == "Fischer")
    ).first()
    mozart = session.scalars(
        select(Composer).where(Composer.last_name == "Mozart")
    ).first()

    orch = Orchestra(name="Münchner Philharmoniker")
    venue = Venue(name="Herkulessaal", city="München", country="Deutschland")
    session.add_all([orch, venue])
    session.flush()

    concert = Concert(
        date=date(2026, 3, 2),
        orchestra_id=orch.id,
        venue_id=venue.id,
        conductor_id=harnoncourt.id if harnoncourt else None,
        notes="Meine Notizen",
    )
    session.add(concert)
    session.commit()

    print(f"Seed DB created at {DB_PATH}")
    print(f"  Conductor: {harnoncourt} (id={harnoncourt.id if harnoncourt else '—'})")
    print(f"  Soloist:   {fischer} (id={fischer.id if fischer else '—'})")
    print(f"  Composer:  {mozart} (id={mozart.id if mozart else '—'})")
    print(f"  Orchestra: {orch.name} (id={orch.id})")
    print(f"  Venue:     {venue.name} (id={venue.id})")
    print(f"  Concert id={concert.id}")
