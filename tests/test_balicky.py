"""Rozpoznání balíčků a sad."""

import pytest

from nabidka.balicky import RUCNI_SEZNAM, je_balicek

BALICKY = [
    "BrainMax Magnesium Trio, výhodný balíček",
    "BrainMax sada Trénink",
    "BrainMax Women Beauty Pack",
    "BrainMax Immunity Starter Pack",
    # dva produkty, každý s vlastním balením
    "BrainMax Calcium D3 & K2, 90 rostlinných kapslí + BrainMax Pure® Collagen Drink, 300 g",
    # dva produkty, každý s vlastní značkou
    "BrainMax Sleep magnesium + BrainMax Glycin 975 mg, 100 rostlinných kapslí",
]

JEDNOTLIVE = [
    "BrainMax Glycin 975 mg, 100 rostlinných kapslí",
    "BrainMax Pure® MSM prášek, 500 g",
    "BrainMax IronZen",
    "BrainMax GlucoControl",
    # „+“ tu odděluje složky jedné receptury, ne dva produkty
    "Performance Magnesium®, 1000 mg, Hořčík 200 mg + Vitamín B6 P5P, 100 vegan kapslí",
    "BrainMax Silymarin Complex, Ostropestřec mariánský extrakt + dalších 5 bylin, 90 kapslí",
    "BrainMax Draslík Magnesium®, Draslík citrát + Hořčík malát, 200 rostlinných kapslí",
]


@pytest.mark.parametrize("nazev", BALICKY)
def test_pozna_balicek(nazev):
    assert je_balicek(nazev)


@pytest.mark.parametrize("nazev", JEDNOTLIVE)
def test_nepovazuje_produkt_za_balicek(nazev):
    assert not je_balicek(nazev)


def test_marker_na_strance():
    """Sada bez klíčového slova v názvu se pozná podle věty na stránce."""
    nazev = "BrainMax Něco Nového"

    assert not je_balicek(nazev)
    assert je_balicek(nazev, "<p>Tento balíček obsahuje tři produkty.</p>")


def test_rucni_seznam_ma_prednost():
    """Sady bez jakéhokoli signálu jsou vyjmenované ručně."""
    assert "BrainMax Superhrdina" in RUCNI_SEZNAM
    assert je_balicek("BrainMax Superhrdina")
