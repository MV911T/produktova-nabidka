"""Vyřazení zboží, které se nejí."""

import pytest

from nabidka.sortiment import je_pozivatelne, kategorijni_cesta


def _stranka(cesta: str) -> str:
    """Výřez stránky s microdaty produktu a zadanou kategorijní cestou."""
    return (
        '<div itemtype="https://schema.org/Product" itemscope>'
        f'<meta itemprop="category" content="{cesta}">'
        "</div>"
    )


NEPOZIVATELNE = [
    ("Brain dámské tričko z BIO bavlny, khaki",
     "Úvodní stránka &gt; Oblečení a doplňky &gt; Sportovní oblečení pro ženy &gt; Tričko"),
    ("BrainMax® Shower Gel Bergamot &amp; Orange, 200 ml",
     "Úvodní stránka &gt; Přírodní kosmetika &gt; Péče o tělo &gt; Gel"),
    ("BrainMax Pure® Skleněná láhev s křišťálem, 500 ml",
     "Úvodní stránka &gt; Domov &gt; Boxy na jídlo, lahve, šejkry, tašky &gt; Láhev"),
    # cesta k větvi nevede, rozhodne název
    ("LAUF láhev na kolo a sport, bidon, 750 ml",
     "Úvodní stránka &gt; BrainMax® &gt; LAUF láhev na kolo a sport"),
]


@pytest.mark.parametrize(("nazev", "cesta"), NEPOZIVATELNE)
def test_zbozi_ktere_se_neji_neprojde(nazev, cesta):
    assert not je_pozivatelne(nazev, _stranka(cesta))


POZIVATELNE = [
    ("BrainMax Pure® Almonda, Coconut Dream, Mandlový krém s kokosem, 30 g",
     "Úvodní stránka &gt; Potraviny &gt; Ořechové krémy, džemy a marmelády &gt; Almonda"),
    # „Pleť, vlasy, nehty“ je cíl, ne kosmetika – visí tam doplňky stravy
    ("BrainMax Women Beauty Fish Collagen, 250 g",
     "Úvodní stránka &gt; Cíle &gt; Pleť, vlasy, nehty &gt; Kolagen"),
    ("BrainMax Zinc Complex®, 50 rostlinných kapslí",
     "Úvodní stránka &gt; BrainMax® &gt; BrainMax Zinc Complex®"),
]


@pytest.mark.parametrize(("nazev", "cesta"), POZIVATELNE)
def test_doplnky_projdou(nazev, cesta):
    assert je_pozivatelne(nazev, _stranka(cesta))


def test_cesta_vynecha_uvodni_polozku():
    cesta = kategorijni_cesta(_stranka("Úvodní stránka &gt; Potraviny &gt; Nápoje &gt; Limonáda"))

    assert cesta == ["Potraviny", "Nápoje", "Limonáda"]


def test_bez_microdat_produkt_projde():
    """Chybějící kategorie sama o sobě důvod k vyřazení není."""
    assert je_pozivatelne("BrainMax Cokoliv, 60 kapslí", "<html></html>")
