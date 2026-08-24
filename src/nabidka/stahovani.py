"""Stahování stránek a práce s jejich HTML.

Web běží na Shoptetu a produktová data vystavuje jako schema.org microdata,
ne jako JSON-LD. Krátký popis v microdata není vůbec – je jen v HTML.
"""

from __future__ import annotations

import html
import re
import time

import requests

BASE_URL = "https://www.brainmarket.cz"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"
    )
}

PAUZA_MEZI_DOTAZY = 0.3
"""Vteřiny mezi požadavky, ať web zbytečně nezatěžujeme."""

CASOVY_LIMIT = 30


def stahni(url: str) -> str:
    """Stáhne stránku. Vyhodí `requests.RequestException`, když se to nepovede."""
    odpoved = requests.get(url, headers=HEADERS, timeout=CASOVY_LIMIT)
    odpoved.raise_for_status()
    return odpoved.text


def pockej() -> None:
    time.sleep(PAUZA_MEZI_DOTAZY)


def uklid(text: str) -> str:
    """Zruší entity a sjednotí bílé znaky na jednu mezeru."""
    return re.sub(r"\s+", " ", html.unescape(text)).strip()


def bez_tagu(fragment: str) -> str:
    """HTML fragment převede na čistý text."""
    fragment = re.sub(r"<(script|style)\b.*?</\1>", " ", fragment, flags=re.S | re.I)
    fragment = re.sub(r"<br\s*/?>", " ", fragment, flags=re.I)
    return uklid(re.sub(r"<[^>]+>", " ", fragment))


def _obsah_od(stranka: str, otviraci_tag: re.Match[str] | None) -> str | None:
    """Obsah `<div>…</div>` od daného otevíracího tagu, včetně vnořených divů."""
    if not otviraci_tag:
        return None

    hloubka, konec = 1, len(stranka)
    for tag in re.finditer(r"<(/?)div\b[^>]*>", stranka[otviraci_tag.end():]):
        hloubka += -1 if tag.group(1) else 1
        if hloubka == 0:
            konec = otviraci_tag.end() + tag.start()
            break
    return stranka[otviraci_tag.end():konec]


def blok_podle_tridy(stranka: str, trida: str) -> str | None:
    nazev = re.escape(trida)
    tag = re.search(rf'<div[^>]*class="[^"]*\b{nazev}\b[^"]*"[^>]*>', stranka)
    return _obsah_od(stranka, tag)


def blok_podle_id(stranka: str, prvek_id: str) -> str | None:
    tag = re.search(rf'<div[^>]*id="{re.escape(prvek_id)}"[^>]*>', stranka)
    return _obsah_od(stranka, tag)


def microdata(oblast: str, vlastnost: str) -> str:
    """Hodnota `itemprop` – z atributu content/src/href, jinak z textu tagu."""
    nazev = re.escape(vlastnost)
    vzor = (
        rf'<[^>]*itemprop="{nazev}"[^>]*?(?:content|src|href)="([^"]*)"'
        rf'|<[^>]*itemprop="{nazev}"[^>]*>([^<]*)<'
    )
    match = re.search(vzor, oblast)
    return uklid(match.group(1) or match.group(2) or "") if match else ""
