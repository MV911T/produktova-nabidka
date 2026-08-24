"""Výpisy kategorií – sběr produktových URL včetně stránkování."""

from __future__ import annotations

import re

from .stahovani import BASE_URL, bez_tagu, blok_podle_id, pockej, stahni


def pocet_stran(stranka: str) -> int:
    """Web uvádí počet stran větou „Nacházíte se na straně 1 z 12“."""
    match = re.search(r"Nacházíte se na straně \d+ z (\d+)", stranka)
    return int(match.group(1)) if match else 1


def nazev_kategorie(stranka: str) -> str:
    match = re.search(r"<h1[^>]*>(.*?)</h1>", stranka, re.S)
    return bez_tagu(match.group(1)) if match else ""


def produkty_ve_vypisu(stranka: str) -> list[str]:
    """Cesty k produktům z hlavního výpisu.

    Bere jen obsah `<div id="products">` – stránka obsahuje ještě blok
    „Nejprodávanější“, jehož produkty do kategorie nepatří.
    """
    vypis = blok_podle_id(stranka, "products")
    if vypis is None:
        return []

    odkazy = re.findall(r'<a href="(/[^"?#]+/)"[^>]*class="[^"]*\bimage\b', vypis)
    return list(dict.fromkeys(odkazy))


def nacti_kategorii(url_kategorie: str) -> tuple[str, list[str]]:
    """Vrátí `(název kategorie, absolutní URL všech jejích produktů)`."""
    url_kategorie = url_kategorie.rstrip("/")
    prvni = stahni(url_kategorie + "/")

    nazev = nazev_kategorie(prvni)
    cesty = produkty_ve_vypisu(prvni)

    for cislo_strany in range(2, pocet_stran(prvni) + 1):
        pockej()
        dalsi = stahni(f"{url_kategorie}/strana-{cislo_strany}/")
        cesty.extend(produkty_ve_vypisu(dalsi))

    return nazev, [BASE_URL + cesta for cesta in dict.fromkeys(cesty)]
