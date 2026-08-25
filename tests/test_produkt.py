"""Parsování produktové stránky."""

import pytest

from nabidka.produkt import drobeckova_navigace, je_produktova_stranka, kratky_popis, parsuj


def test_parsuje_vsech_pet_poli(produktova_stranka):
    produkt = parsuj(produktova_stranka, "Doplňky stravy")

    assert set(produkt) == {
        "product_name",
        "product_url",
        "short_description",
        "image_url",
        "category",
    }
    assert all(produkt.values()), "žádné pole nesmí zůstat prázdné"


def test_nazev_je_bez_podtitulku(produktova_stranka):
    """`itemprop="name"` má název slepený s podtitulkem, drobečky ne."""
    produkt = parsuj(produktova_stranka, "Doplňky stravy")

    assert produkt["product_name"] == "BrainMax Super Ashwagandha® KSM-66®, 100 rostlinných kapslí"
    assert "Patentovaný extrakt" not in produkt["product_name"]


def test_kategorie_se_bere_zvenci(produktova_stranka):
    """Na stránce je „Doplňky stravy a výživa“, přesto musí projít předaná hodnota."""
    produkt = parsuj(produktova_stranka, "LAUF")

    assert produkt["category"] == "LAUF"


def test_kratky_popis_ne_dlouhy(produktova_stranka):
    produkt = parsuj(produktova_stranka, "Doplňky stravy")

    assert produkt["short_description"].startswith("Promyšlená kombinace")
    assert "Prémiová verze Ashwagandhy" not in produkt["short_description"]


def test_kratky_popis_bez_provozniho_sdeleni(produktova_stranka):
    produkt = parsuj(produktova_stranka, "Doplňky stravy")

    assert "Vážení zákazníci" not in produkt["short_description"]
    assert "Děkujeme za pochopení" not in produkt["short_description"]


SDELENI = [
    "Vážení zákazníci, upozorňujeme na změnu složení.",
    "Vážení zákazníci, vylepšili jsme složení Energy Magnesia® v aktivní formě!",
    "Vážení zákazníci, opravdu?",
    "Vážení zákazníci, sdělení bez tečky na konci",
    "Děkujeme za pochopení!",
]


@pytest.mark.parametrize("sdeleni", SDELENI)
def test_provozni_sdeleni_zmizi_at_konci_cimkoli(sdeleni):
    """Vykřičníkem zakončená věta dřív v popisu zůstávala."""
    stranka = f'<div class="p-short-description"><p>Popis výrobku. {sdeleni}</p></div>'
    popis = kratky_popis(stranka, "")

    assert popis == "Popis výrobku."


def test_url_a_obrazek_jsou_absolutni(produktova_stranka):
    produkt = parsuj(produktova_stranka, "Doplňky stravy")

    assert produkt["product_url"].startswith("https://www.brainmarket.cz/")
    assert produkt["image_url"].startswith("https://")


def test_drobecky_bez_uvodni_polozky(produktova_stranka):
    cesta = drobeckova_navigace(produktova_stranka)

    assert cesta[0] == "Doplňky stravy a výživa"
    assert "Domů" not in cesta


def test_pozna_produktovou_stranku(produktova_stranka):
    assert je_produktova_stranka(produktova_stranka)


def test_pozna_zrusenou_stranku():
    """Zrušený produkt web přesměruje na kategorii – ta microdata produktu nemá."""
    assert not je_produktova_stranka("<html><h1>BrainMax®</h1></html>")


def test_popis_z_microdata_kdyz_blok_chybi():
    stranka = '<meta itemprop="description" content="Náhradní popis." >'
    assert kratky_popis(stranka, stranka) == "Náhradní popis."
