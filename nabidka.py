"""Produktová nabídka z brainmarket.cz.

Vrací list[dict] s poli:
    product_name, product_url, short_description, image_url, category

Použití:
    from nabidka import ziskej_nabidku
    produkty = ziskej_nabidku(["https://www.brainmarket.cz/lauf/"])
"""

from __future__ import annotations

import html
import json
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

# Provozní sdělení, která nepatří do popisu produktu.
BALAST = [
    r"Vážení zákazníci[^.]*\.",
    r"Děkujeme za pochopení\.",
]

PAUZA_MEZI_DOTAZY = 0.3  # vteřiny, ať web zbytečně nezatěžujeme

# --- rozpoznání balíčků (sady více produktů), které do nabídky nepatří ---

# Klíčové slovo v názvu.
_BALICEK_SLOVO = re.compile(r"\bbal[íi]če?k\w*\b|\bsada\b|\bpack\b", re.I)
# Údaj o balení, např. "100 rostlinných kapslí", "500 g".
_BALENI = re.compile(
    r"\d+\s*(?:\w+\s+){0,2}"
    r"(?:kapsl\w+|kapsle|tablet\w*|tbl|dra[žz]é|bonb[óo]n\w*|g\b|ml\b|ks\b)",
    re.I,
)
_ZNACKA = re.compile(r"BrainMax|Performance", re.I)
# Věta, kterou e-shop uvádí obsah sady.
_BALICEK_MARKER = re.compile(
    r"Tento balíček|Bal[íi]ček obsahuje|Sada obsahuje|V balíčku (?:najdete|naleznete)", re.I
)

# Sady, které nemají v názvu ani na stránce žádný rozpoznatelný znak.
# Seznam je ručně odsouhlasený – doplňuje se podle potřeby.
BALICKY_RUCNE = json.loads(
    (__import__("pathlib").Path(__file__).parent / "balicky_rucne.json").read_text("utf-8")
)

# Ručně napsané popisy pro produkty, u nichž e-shop krátký popis nemá.
# Klíč je URL produktu. Všechny prošly kontrolou proti Vodítkům SZPI 2024.
VLASTNI_POPISY = json.loads(
    (__import__("pathlib").Path(__file__).parent / "popisy.json").read_text("utf-8")
)


# --------------------------------------------------------------------------
# Pomocné funkce pro práci s HTML
# --------------------------------------------------------------------------

def _uklid(text: str) -> str:
    return re.sub(r"\s+", " ", html.unescape(text)).strip()


def _bez_tagu(fragment: str) -> str:
    fragment = re.sub(r"<(script|style)\b.*?</\1>", " ", fragment, flags=re.S | re.I)
    fragment = re.sub(r"<br\s*/?>", " ", fragment, flags=re.I)
    return _uklid(re.sub(r"<[^>]+>", " ", fragment))


def _vnitrek_bloku(stranka: str, otviraci_tag: re.Match[str] | None) -> str | None:
    """Obsah <div>…</div> od daného otevíracího tagu, včetně vnořených divů."""
    if not otviraci_tag:
        return None
    hloubka, konec = 1, len(stranka)
    for tag in re.finditer(r"<(/?)div\b[^>]*>", stranka[otviraci_tag.end():]):
        hloubka += -1 if tag.group(1) else 1
        if hloubka == 0:
            konec = otviraci_tag.end() + tag.start()
            break
    return stranka[otviraci_tag.end():konec]


def _blok_podle_tridy(stranka: str, trida: str) -> str | None:
    tag = re.search(r'<div[^>]*class="[^"]*\b%s\b[^"]*"[^>]*>' % re.escape(trida), stranka)
    return _vnitrek_bloku(stranka, tag)


def _blok_podle_id(stranka: str, prvek_id: str) -> str | None:
    tag = re.search(r'<div[^>]*id="%s"[^>]*>' % re.escape(prvek_id), stranka)
    return _vnitrek_bloku(stranka, tag)


def _stahni(url: str) -> str:
    odpoved = requests.get(url, headers=HEADERS, timeout=30)
    odpoved.raise_for_status()
    return odpoved.text


# --------------------------------------------------------------------------
# Výpis kategorie -> seznam URL produktů
# --------------------------------------------------------------------------

def _pocet_stran(stranka: str) -> int:
    match = re.search(r"Nacházíte se na straně \d+ z (\d+)", stranka)
    return int(match.group(1)) if match else 1


def _produkty_ve_vypisu(stranka: str) -> list[str]:
    """URL produktů z hlavního výpisu (bez bloku 'Nejprodávanější')."""
    vypis = _blok_podle_id(stranka, "products")
    if vypis is None:
        return []
    odkazy = re.findall(r'<a href="(/[^"?#]+/)"[^>]*class="[^"]*\bimage\b', vypis)
    return list(dict.fromkeys(odkazy))


def _nazev_kategorie(stranka: str) -> str:
    """Název kategorie z nadpisu výpisu."""
    match = re.search(r"<h1[^>]*>(.*?)</h1>", stranka, re.S)
    return _bez_tagu(match.group(1)) if match else ""


def nacti_kategorii(url_kategorie: str) -> tuple[str, list[str]]:
    """Vrátí (název kategorie, absolutní URL všech jejích produktů)."""
    url_kategorie = url_kategorie.rstrip("/")
    prvni = _stahni(url_kategorie + "/")
    nazev = _nazev_kategorie(prvni)
    cesty = _produkty_ve_vypisu(prvni)

    for cislo_strany in range(2, _pocet_stran(prvni) + 1):
        time.sleep(PAUZA_MEZI_DOTAZY)
        dalsi = _stahni(f"{url_kategorie}/strana-{cislo_strany}/")
        cesty.extend(_produkty_ve_vypisu(dalsi))

    unikatni = list(dict.fromkeys(cesty))
    return nazev, [BASE_URL + cesta for cesta in unikatni]


# --------------------------------------------------------------------------
# Produktová stránka -> slovník s pěti poli
# --------------------------------------------------------------------------

def je_balicek(nazev: str, stranka: str) -> bool:
    """Sada více produktů. E-shop je nijak neoznačuje, proto tři nezávislé signály."""
    if nazev in BALICKY_RUCNE:
        return True
    if _BALICEK_SLOVO.search(nazev):
        return True
    if " + " in nazev:
        pred, _, za = nazev.partition(" + ")
        dve_baleni = bool(_BALENI.search(pred) and _BALENI.search(za))
        dve_znacky = bool(_ZNACKA.search(pred) and _ZNACKA.search(za))
        if dve_baleni or dve_znacky:
            return True
    return bool(_BALICEK_MARKER.search(stranka))


def je_produktova_stranka(stranka: str) -> bool:
    """Zrušené produkty web přesměruje na kategorii – ta produktová data nemá."""
    return bool(re.search(r'itemtype="https?://schema\.org/Product"', stranka))


def _oblast_produktu(stranka: str) -> str:
    match = re.search(r'itemtype="https?://schema\.org/Product"', stranka)
    return stranka[match.start():] if match else stranka


def _vlastnost(oblast: str, nazev: str) -> str:
    vzor = (
        r'<[^>]*itemprop="%s"[^>]*?(?:content|src|href)="([^"]*)"'
        r'|<[^>]*itemprop="%s"[^>]*>([^<]*)<' % (re.escape(nazev), re.escape(nazev))
    )
    match = re.search(vzor, oblast)
    return _uklid(match.group(1) or match.group(2) or "") if match else ""


def _drobeckova_navigace(stranka: str) -> list[str]:
    """['Doplňky stravy a výživa', 'Adaptogeny', …, 'Název produktu'] – bez 'Domů'."""
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
            nazev = _uklid(match.group(1) or match.group(2) or "")
            if nazev:
                nazvy.append(nazev)
    return nazvy[1:]


def _zacatek_dlouheho_popisu(stranka: str, limit: int = 300) -> str:
    """Náhradní popis: první věty z detailního popisu produktu."""
    blok = _blok_podle_tridy(stranka, "basic-description")
    if not blok:
        return ""

    text = _bez_tagu(blok)
    text = re.sub(r"^\s*Detailní popis produktu\s*", "", text)

    vety, delka = [], 0
    for veta in re.findall(r"[^.!?]+[.!?]+|\S[^.!?]*$", text):
        veta = veta.strip()
        if not veta:
            continue
        vety.append(veta)
        delka += len(veta)
        if delka >= limit:
            break
    return _uklid(" ".join(vety))


def _kratky_popis(stranka: str, oblast: str) -> str:
    blok = _blok_podle_tridy(stranka, "p-short-description")
    text = _bez_tagu(blok) if blok else ""
    if not text:
        text = _vlastnost(oblast, "description")

    for vzor in BALAST:
        text = re.sub(vzor, "", text)
    return _uklid(text)


def parsuj_produkt(stranka: str, kategorie: str) -> dict[str, str]:
    """Pět polí produktu. Kategorie se předává z výpisu, na stránce spolehlivá není."""
    oblast = _oblast_produktu(stranka)
    cesta = _drobeckova_navigace(stranka)
    url = _vlastnost(oblast, "url")

    return {
        "product_name": cesta[-1] if cesta else _vlastnost(oblast, "name"),
        "product_url": url,
        "short_description": VLASTNI_POPISY.get(url) or _kratky_popis(stranka, oblast),
        "image_url": _vlastnost(oblast, "image"),
        "category": kategorie,
    }


# --------------------------------------------------------------------------
# Hlavní vstupní bod
# --------------------------------------------------------------------------

def ziskej_nabidku(kategorie: list[str]) -> list[dict[str, str]]:
    """Stáhne produkty ze zadaných kategorií a vrátí je jako list[dict]."""
    videne_url: set[str] = set()
    nabidka: list[dict[str, str]] = []

    for url_kategorie in kategorie:
        nazev, url_produktu_seznam = nacti_kategorii(url_kategorie)

        for url_produktu in url_produktu_seznam:
            if url_produktu in videne_url:
                continue
            videne_url.add(url_produktu)

            time.sleep(PAUZA_MEZI_DOTAZY)
            try:
                stranka = _stahni(url_produktu)
            except requests.RequestException as chyba:
                print(f"  ! nestaženo {url_produktu}: {chyba}")
                continue

            if not je_produktova_stranka(stranka):
                print(f"  ! produkt už neexistuje: {url_produktu}")
                continue

            produkt = parsuj_produkt(stranka, nazev)

            if je_balicek(produkt["product_name"], stranka):
                continue

            if not produkt["product_url"]:
                produkt["product_url"] = url_produktu
            nabidka.append(produkt)

    return nabidka


if __name__ == "__main__":
    import sys

    vstup = sys.argv[1:] or ["https://www.brainmarket.cz/lauf/"]
    vysledek = ziskej_nabidku(vstup)
    print(json.dumps(vysledek, ensure_ascii=False, indent=2))
