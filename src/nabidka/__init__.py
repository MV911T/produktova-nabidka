"""Produktová nabídka z brainmarket.cz.

    from nabidka import ziskej_nabidku

    produkty = ziskej_nabidku(["https://www.brainmarket.cz/lauf/"])
"""

from __future__ import annotations

import sys

import requests

from .balicky import je_balicek
from .katalog import nacti_kategorii
from .produkt import je_produktova_stranka, parsuj
from .stahovani import pockej, stahni
from .tvrzeni import tvrzeni_pro, zkontroluj

__all__ = [
    "ziskej_nabidku",
    "NeuplnaNabidka",
    "je_balicek",
    "nacti_kategorii",
    "parsuj",
    "tvrzeni_pro",
    "zkontroluj",
]

__version__ = "1.1.0"


class NeuplnaNabidka(RuntimeError):
    """Některé stránky se nepovedlo stáhnout ani na poslední pokus.

    Nese v `nabidka` to, co se stáhnout povedlo, a v `nestazene` seznam URL,
    která se vzdala. Volající se tak může rozhodnout sám, ale kratší seznam
    mlčky nedostane – výpadek sítě od zrušeného produktu nerozezná.
    """

    def __init__(self, nabidka: list[dict[str, str]], nestazene: list[str]) -> None:
        self.nabidka = nabidka
        self.nestazene = nestazene
        super().__init__(
            f"nabídka je NEÚPLNÁ – nestažené stránky: {len(nestazene)}, "
            f"stažené produkty: {len(nabidka)}"
        )


def ziskej_nabidku(kategorie: list[str]) -> list[dict[str, str]]:
    """Stáhne produkty ze zadaných kategorií a vrátí je jako `list[dict]`.

    Každý slovník má pole `product_name`, `product_url`, `short_description`,
    `image_url` a `category`.

    Vynechává zrušené produkty (web je přesměruje na kategorii) a balíčky.
    Průběžné hlášky jdou na stderr, aby nekazily JSON na stdout.

    Každý produkt je v nabídce jednou, i když na něj vede víc cest nebo
    patří do víc kategorií; totožnost určuje microdata `url`. Do `category`
    se propíše ta kategorie, ve které se produkt objevil první.

    Vyhodí `NeuplnaNabidka`, když se některou stránku nepodařilo stáhnout –
    kratší seznam by se od úplného nedal rozeznat. Nedostupný výpis celé
    kategorie propadne jako `requests.RequestException`.
    """
    videne_url: set[str] = set()
    videne_produkty: set[str] = set()
    nabidka: list[dict[str, str]] = []
    nestazene: list[str] = []

    for url_kategorie in kategorie:
        nazev, url_produktu_seznam = nacti_kategorii(url_kategorie)

        for url_produktu in url_produktu_seznam:
            if url_produktu in videne_url:
                continue
            videne_url.add(url_produktu)

            pockej()
            try:
                stranka = stahni(url_produktu)
            except requests.RequestException as chyba:
                print(f"  ! nestaženo {url_produktu}: {chyba}", file=sys.stderr)
                nestazene.append(url_produktu)
                continue

            if not je_produktova_stranka(stranka):
                print(f"  ! produkt už neexistuje: {url_produktu}", file=sys.stderr)
                continue

            produkt = parsuj(stranka, nazev)

            if je_balicek(produkt["product_name"], stranka):
                continue

            if not produkt["product_url"]:
                produkt["product_url"] = url_produktu

            # Výpis vede na tentýž produkt i dvěma cestami – „…-kapsli“
            # a „…-kapsli-2“ –, shodná je až microdata `url`. Rozhodne
            # proto ona, ne adresa, po které jsme přišli.
            if produkt["product_url"] in videne_produkty:
                continue
            videne_produkty.add(produkt["product_url"])

            nabidka.append(produkt)

    if nestazene:
        raise NeuplnaNabidka(nabidka, nestazene)

    return nabidka
