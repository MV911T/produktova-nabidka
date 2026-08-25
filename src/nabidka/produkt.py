"""Produktová stránka → slovník s pěti poli podle zadání."""

from __future__ import annotations

import json
import re
from pathlib import Path

from .stahovani import bez_tagu, blok_podle_tridy, microdata, uklid

_DATA = Path(__file__).parent / "data"

VLASTNI_POPISY: dict[str, str] = json.loads((_DATA / "popisy.json").read_text("utf-8"))
"""Ručně napsané popisy pro produkty, u nichž e-shop krátký popis nemá.

Klíčem je URL produktu. Všechny texty prošly kontrolou v modulu `tvrzeni`.
"""

BALAST = [
    r"Vážení zákazníci[^.!?]*[.!?]?",
    r"Děkujeme za pochopení[.!?]?",
]
"""Provozní sdělení, která e-shop míchá do krátkého popisu.

Věta smí končit tečkou, vykřičníkem, otazníkem i ničím: obě balení Energy
Magnesia® mají na konci „Vážení zákazníci, vylepšili jsme složení… formě!“
a s požadavkem na tečku tam ta věta zůstávala.
"""


def je_produktova_stranka(stranka: str) -> bool:
    """Zrušený produkt web přesměruje na kategorii – ta microdata produktu nemá."""
    return bool(re.search(r'itemtype="https?://schema\.org/Product"', stranka))


def _oblast_produktu(stranka: str) -> str:
    match = re.search(r'itemtype="https?://schema\.org/Product"', stranka)
    return stranka[match.start():] if match else stranka


def drobeckova_navigace(stranka: str) -> list[str]:
    """Cesta bez úvodní položky „Domů“.

    Poslední prvek je čistý název produktu – na rozdíl od `itemprop="name"`,
    kde je název slepený s podtitulkem a u variant i s nadpisy dotazů.
    """
    zacatek = re.search(r'itemtype="https?://schema\.org/BreadcrumbList"', stranka)
    if not zacatek:
        return []

    nazvy = []
    for polozka in re.split(r'itemprop="itemListElement"', stranka[zacatek.start():])[1:]:
        match = re.search(
            r'<[^>]*itemprop="name"[^>]*content="([^"]*)"'
            r'|<[^>]*itemprop="name"[^>]*>([^<]*)<',
            polozka,
        )
        if match:
            nazev = uklid(match.group(1) or match.group(2) or "")
            if nazev:
                nazvy.append(nazev)
    return nazvy[1:]


def kratky_popis(stranka: str, oblast: str) -> str:
    blok = blok_podle_tridy(stranka, "p-short-description")
    text = bez_tagu(blok) if blok else ""
    if not text:
        text = microdata(oblast, "description")

    for vzor in BALAST:
        text = re.sub(vzor, "", text)
    return uklid(text)


def parsuj(stranka: str, kategorie: str) -> dict[str, str]:
    """Pět polí ze zadání a k nim `sku` a `ean`.

    Kategorie se předává zvenčí – na produktové stránce spolehlivá není,
    u části produktů vede drobečková navigace jen ke značce a věcnou
    kategorii web nenese vůbec.

    `sku` a `ean` zadání nežádá, ale bez nich je jediným klíčem záznamu
    URL, a ta se s přejmenováním produktu mění. U variantního zboží nese
    `sku` příponu velikosti (`70423/XL`), takže určuje variantu; nadřazený
    produkt má microdata `productID`.
    """
    oblast = _oblast_produktu(stranka)
    cesta = drobeckova_navigace(stranka)
    url = microdata(oblast, "url")

    return {
        "product_name": cesta[-1] if cesta else microdata(oblast, "name"),
        "product_url": url,
        "short_description": VLASTNI_POPISY.get(url) or kratky_popis(stranka, oblast),
        "image_url": microdata(oblast, "image"),
        "category": kategorie,
        "sku": microdata(oblast, "sku"),
        "ean": microdata(oblast, "gtin13"),
    }
