from pathlib import Path

import pytest

PODKLADY = Path(__file__).parent / "podklady"


@pytest.fixture(scope="session")
def produktova_stranka() -> str:
    """Výřez stránky BrainMax Super Ashwagandha® KSM-66®."""
    return (PODKLADY / "produkt.html").read_text("utf-8")


@pytest.fixture(scope="session")
def vypis_kategorie() -> str:
    """Výřez výpisu kategorie LAUF."""
    return (PODKLADY / "vypis.html").read_text("utf-8")
