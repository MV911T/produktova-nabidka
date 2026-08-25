"""Sestavení nabídky – vyřazování duplicit a pořadí kategorií."""

import pytest

import nabidka
from nabidka import ziskej_nabidku

KANONICKA = "https://www.brainmarket.cz/brainmax-men-multivitamin--90-kapsli/"
DRUHA_CESTA = "https://www.brainmarket.cz/brainmax-men-multivitamin--90-kapsli-2/"


@pytest.fixture
def bez_cekani(monkeypatch):
    monkeypatch.setattr(nabidka, "pockej", lambda: None)


def _stranka(produktova_stranka: str, url: str) -> str:
    """Výřez skutečné stránky s podvrženou microdata `url`."""
    import re

    return re.sub(
        r'(<[^>]*itemprop="url"[^>]*content=")[^"]*(")',
        rf"\g<1>{url}\g<2>",
        produktova_stranka,
        count=1,
    )


def test_dve_cesty_na_tentyz_produkt_daji_jeden_zaznam(
    monkeypatch, bez_cekani, produktova_stranka
):
    """E-shop vede stejný produkt i jako „…-kapsli-2“.

    Adresy z výpisu se liší, shodná je až microdata `url` – podle ní
    se duplicita pozná.
    """
    monkeypatch.setattr(
        nabidka, "nacti_kategorii", lambda _: ("BrainMax pro muže", [KANONICKA, DRUHA_CESTA])
    )
    monkeypatch.setattr(
        nabidka, "stahni", lambda url, **_: _stranka(produktova_stranka, KANONICKA)
    )

    produkty = ziskej_nabidku(["https://e.cz/brainmax-men/"])

    assert len(produkty) == 1
    assert produkty[0]["product_url"] == KANONICKA


def test_produkt_ve_dvou_kategoriich_dostane_tu_prvni(
    monkeypatch, bez_cekani, produktova_stranka
):
    vypisy = {
        "https://e.cz/muzi/": ("BrainMax pro muže", [KANONICKA]),
        "https://e.cz/zeny/": ("BrainMax pro ženy", [KANONICKA]),
    }
    monkeypatch.setattr(nabidka, "nacti_kategorii", lambda url: vypisy[url])
    monkeypatch.setattr(
        nabidka, "stahni", lambda url, **_: _stranka(produktova_stranka, KANONICKA)
    )

    produkty = ziskej_nabidku(["https://e.cz/muzi/", "https://e.cz/zeny/"])

    assert len(produkty) == 1
    assert produkty[0]["category"] == "BrainMax pro muže"


def test_ruzne_produkty_zustanou(monkeypatch, bez_cekani, produktova_stranka):
    """Vyřazovat se smí jen shoda, ne dva různé produkty."""
    druhy = "https://www.brainmarket.cz/brainmax-jiny-produkt/"
    monkeypatch.setattr(
        nabidka, "nacti_kategorii", lambda _: ("BrainMax pro muže", [KANONICKA, druhy])
    )
    monkeypatch.setattr(
        nabidka, "stahni", lambda url, **_: _stranka(produktova_stranka, url)
    )

    produkty = ziskej_nabidku(["https://e.cz/brainmax-men/"])

    assert [p["product_url"] for p in produkty] == [KANONICKA, druhy]
