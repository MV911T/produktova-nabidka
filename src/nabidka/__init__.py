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
    "je_balicek",
    "nacti_kategorii",
    "parsuj",
    "tvrzeni_pro",
    "zkontroluj",
]

__version__ = "1.0.0"


def ziskej_nabidku(kategorie: list[str]) -> list[dict[str, str]]:
    """Stáhne produkty ze zadaných kategorií a vrátí je jako `list[dict]`.

    Každý slovník má pole `product_name`, `product_url`, `short_description`,
    `image_url` a `category`.

    Vynechává zrušené produkty (web je přesměruje na kategorii) a balíčky.
    Průběžné hlášky jdou na stderr, aby nekazily JSON na stdout.
    """
    videne_url: set[str] = set()
    nabidka: list[dict[str, str]] = []

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
                continue

            if not je_produktova_stranka(stranka):
                print(f"  ! produkt už neexistuje: {url_produktu}", file=sys.stderr)
                continue

            produkt = parsuj(stranka, nazev)

            if je_balicek(produkt["product_name"], stranka):
                continue

            if not produkt["product_url"]:
                produkt["product_url"] = url_produktu
            nabidka.append(produkt)

    return nabidka
