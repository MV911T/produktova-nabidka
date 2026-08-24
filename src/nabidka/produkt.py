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
    r"Vážení zákazníci[^.]*\.",
    r"Děkujeme za pochopení\.",
]
"""Provozní sdělení, která e-shop míchá do krátkého popisu."""


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
    """Pět polí produktu.

    Kategorie se předává zvenčí – na produktové stránce spolehlivá není,
    zhruba třetina produktů má drobečkovou navigaci jen dvouúrovňovou
    (`BrainMax® > Název`) a věcnou kategorii web u nich vůbec nevede.
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
    }
