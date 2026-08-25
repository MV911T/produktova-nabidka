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

SADY_OBLECENI = [
    "LAUF unisex cyklistický set, bílý dres a černé kraťasy se šlemi",
    "Brain unisex cyklistický set, dres a kraťasy, modrý",
    "BrainMax bavlněné oversized triko & kraťasy set, šedá",
]


@pytest.mark.parametrize("nazev", SADY_OBLECENI)
def test_oblecni_sada_je_balicek(nazev):
    """Dres i kraťasy se prodávají samostatně, sada je tedy balíček."""
    assert je_balicek(nazev)


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


def test_marker_musi_uvozovat_vycet():
    """„Tento balíček“ v křížovém prodeji sadu neoznačuje.

    Věta „Omega 3 skvěle doplní tento balíček“ vyřazovala z nabídky
    Bacopu Monnieri, běžný jednodruhový produkt.
    """
    krizovy_prodej = (
        '<p><a href="/omega-3-oleje/">Omega 3</a> skvěle doplní tento balíček '
        "díky tomu, že podporují normální činnost mozku.</p>"
    )

    assert not je_balicek("BrainMax Enhanced Bacopa Monnieri, 60 kapslí", krizovy_prodej)


def test_marker_vycet_zabere():
    for marker in ("Balíček obsahuje:", "Sada obsahuje:", "V balíčku najdete"):
        assert je_balicek("BrainMax Cokoliv, 60 kapslí", f"<p>{marker} tři produkty.</p>")
