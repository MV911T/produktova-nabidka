"""Kontrola krátkých popisů proti Vodítkům SZPI 2024.

Podle čl. 10 nařízení (ES) č. 1924/2006 musí být každé tvrzení spojující
potravinu se zdravím na schváleném seznamu. Modul hledá tři druhy prohřešků:

1. riziková (léčebná) slova – příloha 5 Vodítek
2. slovesa, která tvrzení zesilují nad schválené znění – příloha 6
3. věty se zdravotním tématem bez opory ve schváleném, on-hold
   nebo výživovém tvrzení

Nenahrazuje posouzení člověkem, jen upozorňuje na nejčastější chyby.
"""

from __future__ import annotations

import json
import re
import unicodedata
from pathlib import Path

_DATA = Path(__file__).parent / "data"


def _nacti(nazev: str):
    return json.loads((_DATA / nazev).read_text("utf-8"))


RIZIKOVA_SLOVA: list[str] = _nacti("rizikova_slova.json")
NEPRIPUSTNE: list[dict] = _nacti("nepripustne.json")
SCHVALENA_ZT: list[list[str]] = _nacti("schvalena_zt.json")
SCHVALENA_VT: list[list[str]] = _nacti("schvalena_vt.json")
ON_HOLD: list[dict] = _nacti("onhold.json")

ZESILUJICI = [
    "zlepšuje", "posiluje", "stimuluje", "zvyšuje", "urychluje", "obnovuje",
    "odstraňuje", "potlačuje", "zabraňuje", "předchází", "chrání před",
    "léčí", "vyléčí", "zbaví", "uleví", "řeší", "napravuje", "hraje klíčovou roli",
]
"""Slovesa, kterými se schválené „přispívá k…“ mění na silnější tvrzení."""

SYMPTOMY = [
    "křeče", "křeč", "nespavost", "neklidný spánek", "nedostatek", "deficit",
    "bolest", "nadýmání", "nafouklé břicho", "vypadávání", "lámavost",
    "podrážděnost", "výkyvy nálad", "vyčerpaný", "unavený",
]
"""Symptomy, které schválená tvrzení neznají – naznačují léčebný účinek.

Pozor: tenhle výčet je vlastní, ve Vodítkách takový seznam není.
"""

_KONCOVKY = {
    "", "a", "e", "i", "y", "u", "o", "ě", "í", "ý", "á", "é", "ů", "ou", "em",
    "im", "am", "om", "mi", "ch", "ech", "ich", "ám", "ým", "ých", "ové", "ový",
    "ová", "ně", "ný", "ná", "né", "ni", "te", "l", "la", "lo", "ly", "t",
    "ti", "m", "š", "me", "s", "ce", "ci", "ku", "ky", "ka", "ek",
}
"""Koncovky, o které se hledané slovo smí lišit.

Delší zbytek znamená jiné slovo – „lecitinu“ není tvar slova „léčit“.
"""

_NEVYZNAMNE = {
    "a", "i", "k", "o", "u", "v", "s", "z", "na", "po", "do", "ke", "se", "je",
    "the", "of", "and", "to", "in", "for", "prispiva", "podili", "prispiv",
    "normalni", "normalnimu", "normalnich", "udrzeni", "stavu", "funkce", "-",
    # názvy živin a složek – popis složení není zdravotní tvrzení
    "obsah", "obsahu", "obsahuji", "obsahuje", "obsahem", "zdrojem", "davce", "davku",
    "aminokyselin", "aminokyselina", "aminokyseliny", "bilkovin", "bilkoviny",
    "sacharid", "sacharidy", "vlaknina", "vlakniny", "vitamin", "vitaminu",
    "mineral", "mineraly", "extrakt", "extraktu", "polysacharid", "polysacharidu",
}


def _norm(text: str) -> str:
    """Malá písmena bez diakritiky."""
    text = unicodedata.normalize("NFD", str(text).lower())
    return "".join(znak for znak in text if unicodedata.category(znak) != "Mn")


def _obsahuje_slovo(text: str, hledane: str) -> bool:
    """Vyskytuje se slovo v textu jako samostatné slovo, i v jiném pádu?"""
    cil = _norm(hledane)
    if " " in cil:
        return cil in _norm(text)

    return any(
        token.startswith(cil) and token[len(cil):] in _KONCOVKY
        for token in re.findall(r"[a-zá-ž]+", _norm(text))
    )


def tvrzeni_pro(latka: str, limit: int = 15) -> dict[str, list[str]]:
    """Schválená a on-hold tvrzení dostupná pro danou látku."""
    hledane = _norm(latka)

    schvalena = [
        radek[2] for radek in SCHVALENA_ZT
        if len(radek) > 2 and hledane in _norm(radek[1])
    ]
    onhold = [
        f"{radek['cz']} → {radek['tvrzeni']}" for radek in ON_HOLD
        if hledane in _norm(radek["lat"]) or hledane in _norm(radek["cz"])
    ]
    return {"schvalena": schvalena[:limit], "on_hold": onhold[:limit]}


def _zdravotni_slovnik() -> set[str]:
    """Slova z textů tvrzení – signál, že věta mluví o zdraví.

    Názvy látek a rostlin se vynechávají: zmínka složení tvrzením není.
    """
    slova: set[str] = set()
    for radek in SCHVALENA_ZT:
        if len(radek) > 2:
            slova.update(_norm(radek[2]).split())
    for radek in ON_HOLD:
        slova.update(_norm(radek["tvrzeni"]).split())

    nazvy: set[str] = set()
    for radek in SCHVALENA_ZT:
        if len(radek) > 1:
            nazvy.update(_norm(radek[1]).split())
    for radek in ON_HOLD:
        nazvy.update(_norm(radek["cz"]).split())
        nazvy.update(_norm(radek["lat"]).split())

    return {
        slovo for slovo in slova
        if len(slovo) > 4 and slovo not in _NEVYZNAMNE and slovo not in nazvy
    }


_SLOVNIK = _zdravotni_slovnik()


def zkontroluj(popis: str, latky: list[str] | None = None) -> list[str]:
    """Nálezy v popisu. Prázdný seznam znamená, že popis prošel.

    `latky` rozšiřují seznam přípustných opor o on-hold tvrzení pro
    konkrétní rostliny – bez nich projdou jen schválená tvrzení.
    """
    nalezy = []

    for slovo in RIZIKOVA_SLOVA:
        if _obsahuje_slovo(popis, slovo):
            nalezy.append(f"rizikové (léčebné) slovo: „{slovo}“")

    for sloveso in ZESILUJICI:
        if _obsahuje_slovo(popis, sloveso):
            nalezy.append(f"zesilující sloveso: „{sloveso}“ – bude silnější než schválené znění")

    for symptom in SYMPTOMY:
        if _obsahuje_slovo(popis, symptom):
            nalezy.append(f"symptom mimo schválená tvrzení: „{symptom}“")

    opory = [radek[2] for radek in SCHVALENA_ZT if len(radek) > 2]
    opory += [radek[1] for radek in SCHVALENA_VT if len(radek) > 1]
    for latka in latky or []:
        opory += tvrzeni_pro(latka, limit=99)["on_hold"]
    opory = [_norm(opora) for opora in opory]

    for veta in re.split(r"(?<=[.!?])\s+", popis):
        if not any(_obsahuje_slovo(veta, slovo) for slovo in _SLOVNIK):
            continue

        n_veta = _norm(veta)
        podepreno = any(
            sum(1 for slovo in opora.split() if len(slovo) > 4 and slovo in n_veta) >= 2
            for opora in opory
        )
        if not podepreno:
            nalezy.append(f"zdravotní téma bez opory v seznamu: „{veta.strip()[:70]}…“")

    return nalezy
