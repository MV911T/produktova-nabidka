"""Opakování pokusů při stahování a hlášení neúplné nabídky."""

import json

import pytest
import requests

import nabidka
from nabidka import NeuplnaNabidka, stahovani, ziskej_nabidku
from nabidka.cli import main


class Odpoved:
    """Náhrada za `requests.Response` – umí jen to, co `stahni()` potřebuje."""

    def __init__(self, text: str = "obsah", stav: int = 200) -> None:
        self.text = text
        self.status_code = stav

    def raise_for_status(self) -> None:
        if self.status_code >= 400:
            raise requests.HTTPError(f"HTTP {self.status_code}", response=self)


@pytest.fixture(autouse=True)
def bez_cekani(monkeypatch):
    """Testy nemají čekat na narůstající pauzu mezi pokusy."""
    monkeypatch.setattr(stahovani.time, "sleep", lambda _: None)


def _pokusy(monkeypatch, *odpovedi):
    """Nastaví `requests.get` tak, aby postupně vracel zadané odpovědi."""
    zbyva = list(odpovedi)
    volani = []

    def get(url, **_):
        volani.append(url)
        vysledek = zbyva.pop(0)
        if isinstance(vysledek, Exception):
            raise vysledek
        return vysledek

    monkeypatch.setattr(stahovani.requests, "get", get)
    return volani


def test_docasny_vypadek_se_zkusi_znovu(monkeypatch):
    volani = _pokusy(
        monkeypatch,
        requests.ConnectionError("spojení spadlo"),
        Odpoved(stav=503),
        Odpoved("povedlo se"),
    )

    assert stahovani.stahni("https://example.com/") == "povedlo se"
    assert len(volani) == 3


def test_vzdá_se_po_poslednim_pokusu(monkeypatch):
    volani = _pokusy(monkeypatch, *[requests.ConnectionError("spadlo")] * 3)

    with pytest.raises(requests.ConnectionError):
        stahovani.stahni("https://example.com/", pokusy=3)
    assert len(volani) == 3


def test_odpoved_4xx_se_neopakuje(monkeypatch):
    """Chybu na naší straně opakování nespraví, jen zdrží."""
    volani = _pokusy(monkeypatch, Odpoved(stav=404), Odpoved("nedosažitelné"))

    with pytest.raises(requests.HTTPError):
        stahovani.stahni("https://example.com/")
    assert len(volani) == 1


@pytest.fixture
def kategorie_o_dvou(monkeypatch, produktova_stranka):
    """Kategorie se dvěma produkty; druhý se nestáhne."""
    monkeypatch.setattr(
        nabidka,
        "nacti_kategorii",
        lambda _: ("Testovací kategorie", ["https://e.cz/a/", "https://e.cz/b/"]),
    )
    monkeypatch.setattr(nabidka, "pockej", lambda: None)

    def stahni(url, **_):
        if url.endswith("/b/"):
            raise requests.ConnectionError("spojení spadlo")
        return produktova_stranka

    monkeypatch.setattr(nabidka, "stahni", stahni)


def test_nestazena_stranka_nabidku_neztisi(kategorie_o_dvou):
    with pytest.raises(NeuplnaNabidka) as nalez:
        ziskej_nabidku(["https://e.cz/kategorie/"])

    assert nalez.value.nestazene == ["https://e.cz/b/"]
    assert len(nalez.value.nabidka) == 1


def test_cli_neuplnou_nabidku_nevypise(kategorie_o_dvou, capsys):
    """Zkrácený JSON nesmí projít na stdout jako by byl úplný."""
    navrat = main(["https://e.cz/kategorie/"])
    zachyceno = capsys.readouterr()

    assert navrat == 1
    assert zachyceno.out == ""
    assert "NEÚPLNÁ" in zachyceno.err.upper()


def test_cli_s_prepinacem_neuplnou_vypise(kategorie_o_dvou, capsys):
    navrat = main(["https://e.cz/kategorie/", "--dovol-neuplnou"])
    zachyceno = capsys.readouterr()

    assert navrat == 0
    assert len(json.loads(zachyceno.out)) == 1
    assert "NEÚPLNÁ NABÍDKA" in zachyceno.err
