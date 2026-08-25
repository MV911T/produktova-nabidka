"""Vykreslení tabule úkolů z TODO.md.

Skript v `nastroje/` není součástí balíčku, načítá se proto podle cesty.
"""

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest

KOREN = Path(__file__).resolve().parent.parent
SKRIPT = KOREN / "nastroje" / "tabule.py"

UKAZKA = """# TODO

**2 zbývá · 3 hotovo · 1 vyřazeno**

## Zbývá

### Dokončení

**1. První úkol**
Podrobnosti, které do tabule nepatří.

**2. Druhý úkol s [odkazem](https://example.com) a `kódem`**

## Hotovo

**3.** Hotová věc
**4.** Další hotová věc
**5.** Třetí hotová věc

## Vyřazeno ze zadání

**6.** Zahozeno
"""


@pytest.fixture(scope="session")
def tabule():
    zadani = importlib.util.spec_from_file_location("tabule", SKRIPT)
    modul = importlib.util.module_from_spec(zadani)
    zadani.loader.exec_module(modul)
    return modul


@pytest.fixture
def todo(tmp_path: Path) -> Path:
    soubor = tmp_path / "TODO.md"
    soubor.write_text(UKAZKA, "utf-8")
    return soubor


def test_nacte_cisla_a_nazvy(tabule, todo):
    polozky, pocty = tabule.nacti(todo)

    assert pocty == "2 zbývá · 3 hotovo · 1 vyřazeno"
    assert [(cislo, nazev) for _, _, cislo, nazev in polozky][:2] == [
        (1, "První úkol"),
        (2, "Druhý úkol s odkazem a kódem"),
    ]


def test_zna_obe_podoby_nadpisu(tabule, todo):
    """Zbývající úkoly mají název v tučném, hotové až za ním."""
    polozky, _ = tabule.nacti(todo)
    sekce = {cislo: sekce for sekce, _, cislo, _ in polozky}

    assert sekce[1] == "Zbývá"
    assert sekce[3] == "Hotovo"
    assert sekce[6] == "Vyřazeno ze zadání"


def test_dlouhy_nazev_se_orizne(tabule):
    orezany = tabule.zkrat("x" * (tabule.SIRKA + 20))

    assert len(orezany) == tabule.SIRKA
    assert orezany.endswith("…")


def test_hotove_polozky_jsou_jen_rozsah(tabule, todo):
    polozky, pocty = tabule.nacti(todo)
    vykres = tabule.vykresli(polozky, pocty)

    assert "1  První úkol" in vykres
    assert "HOTOVO: 3–5 (3)" in vykres
    assert "Hotová věc" not in vykres


def test_hook_vraci_json(tabule):
    """Hook čte stdout jako JSON – rozbitý výstup by ho shodil."""
    hotovo = subprocess.run(
        [sys.executable, str(SKRIPT), "--hook"],
        cwd=KOREN,
        capture_output=True,
        text=True,
        check=True,
    )

    assert json.loads(hotovo.stdout)["systemMessage"].startswith("─")


def test_mimo_projekt_mlci(tmp_path: Path):
    """Jinde než v tomhle repozitáři nesmí hook vypsat nic."""
    hotovo = subprocess.run(
        [sys.executable, str(SKRIPT), "--hook"],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        check=True,
    )

    assert hotovo.stdout == ""
