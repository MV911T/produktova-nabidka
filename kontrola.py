"""Kontrola krátkých popisů proti Vodítkům SZPI 2024.

Hlásí:
  - riziková (léčebná) slova z přílohy 5
  - slovesa, která tvrzení zesilují nad rámec schváleného znění (příloha 6)
  - zmínky o symptomech, které schválená tvrzení neobsahují

Použití:
    python3 kontrola.py "text popisu" [látka ...]
"""

from __future__ import annotations

import json
import re
import unicodedata
from pathlib import Path

_ZDE = Path(__file__).parent

RIZIKOVA_SLOVA = json.loads((_ZDE / "rizikova_slova.json").read_text("utf-8"))
NEPRIPUSTNE = json.loads((_ZDE / "nepripustne.json").read_text("utf-8"))
SCHVALENA_ZT = json.loads((_ZDE / "schvalena_zt.json").read_text("utf-8"))
ON_HOLD = json.loads((_ZDE / "onhold.json").read_text("utf-8"))
SCHVALENA_VT = json.loads((_ZDE / "schvalena_vt.json").read_text("utf-8"))

# Slovesa, kterými se schválené "přispívá k…" mění na silnější tvrzení.
ZESILUJICI = [
    "zlepšuje", "posiluje", "stimuluje", "zvyšuje", "urychluje", "obnovuje",
    "odstraňuje", "potlačuje", "zabraňuje", "předchází", "chrání před",
    "léčí", "vyléčí", "zbaví", "uleví", "řeší", "napravuje", "hraje klíčovou roli",
]


def _norm(text: str) -> str:
    text = unicodedata.normalize("NFD", str(text).lower())
    return "".join(z for z in text if unicodedata.category(z) != "Mn")


# České koncovky, o které se hledané slovo smí lišit. Delší zbytek už znamená
# jiné slovo – „lecitinu“ není tvar slova „léčit“.
_KONCOVKY = {
    "", "a", "e", "i", "y", "u", "o", "ě", "í", "ý", "á", "é", "ů", "ou", "em",
    "im", "am", "om", "mi", "ch", "ech", "ich", "ám", "ým", "ých", "ové", "ový",
    "ová", "ové", "ně", "ný", "ná", "né", "ni", "te", "l", "la", "lo", "ly", "t",
    "ti", "m", "š", "me", "s", "ce", "ci", "ku", "ky", "ka", "ek", "ku",
}


def _obsahuje_slovo(text: str, hledane: str) -> bool:
    """Slovo se ve větě vyskytuje jako samostatné slovo (i v jiném pádu)."""
    cil = _norm(hledane)
    # víceslovné výrazy porovnáváme jako podřetězec
    if " " in cil:
        return cil in _norm(text)
    for token in re.findall(r"[a-zá-ž]+", _norm(text)):
        if token.startswith(cil) and token[len(cil):] in _KONCOVKY:
            return True
    return False


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
    """Slova, která se vyskytují ve zdravotních tvrzeních – signál, že jde o tvrzení."""
    slova: set[str] = set()
    for radek in SCHVALENA_ZT:
        if len(radek) > 2:
            slova.update(_norm(radek[2]).split())
    for radek in ON_HOLD:
        slova.update(_norm(radek["tvrzeni"]).split())
    # Názvy látek a rostlin nejsou tvrzení – samotná zmínka složení nic neporušuje.
    nazvy: set[str] = set()
    for radek in SCHVALENA_ZT:
        if len(radek) > 1:
            nazvy.update(_norm(radek[1]).split())
    for radek in ON_HOLD:
        nazvy.update(_norm(radek["cz"]).split())
        nazvy.update(_norm(radek["lat"]).split())

    # obecná slova, která samy o sobě nic neznamenají
    bezvyznamne = {
        "a", "i", "k", "o", "u", "v", "s", "z", "na", "po", "do", "ke", "se", "je",
        "the", "of", "and", "to", "in", "for", "prispiva", "podili", "prispiv",
        "normalni", "normalnimu", "normalnich", "udrzeni", "stavu", "funkce", "-",
        # názvy živin a složek – popis složení není zdravotní tvrzení
        "obsah", "obsahu", "obsahuji", "obsahuje", "obsahem", "zdrojem", "davce", "davku",
        "aminokyselin", "aminokyselina", "aminokyseliny", "bilkovin", "bilkoviny",
        "sacharid", "sacharidy", "vlaknina", "vlakniny", "vitamin", "vitaminu",
        "mineral", "mineraly", "extrakt", "extraktu", "polysacharid", "polysacharidu",
    }
    return {s for s in slova if len(s) > 4 and s not in bezvyznamne and s not in nazvy}


_SLOVNIK = _zdravotni_slovnik()

# Symptomy a stavy, které schválená tvrzení neznají – naznačují léčebný účinek.
SYMPTOMY = [
    "křeče", "křeč", "nespavost", "neklidný spánek", "nedostatek", "deficit",
    "bolest", "nadýmání", "nafouklé břicho", "vypadávání", "lámavost",
    "podrážděnost", "výkyvy nálad", "vyčerpaný", "unavený",
]


def zkontroluj(popis: str, latky: list[str] | None = None) -> list[str]:
    """Vrátí seznam nálezů. Prázdný seznam = popis prošel."""
    nalezy = []
    normovany = _norm(popis)

    for slovo in RIZIKOVA_SLOVA:
        if _obsahuje_slovo(popis, slovo):
            nalezy.append(f"rizikové (léčebné) slovo: „{slovo}“")

    for sloveso in ZESILUJICI:
        if _obsahuje_slovo(popis, sloveso):
            nalezy.append(f"zesilující sloveso: „{sloveso}“ – bude silnější než schválené znění")

    for symptom in SYMPTOMY:
        if re.search(r"\b%s" % re.escape(_norm(symptom)), normovany):
            nalezy.append(f"symptom mimo schválená tvrzení: „{symptom}“")

    # Věty, které se dotýkají zdraví, musí mít oporu ve schváleném nebo on-hold tvrzení.
    opory = [_norm(r[2]) for r in SCHVALENA_ZT if len(r) > 2]
    opory += [_norm(r[1]) for r in SCHVALENA_VT if len(r) > 1]
    if latky:
        for latka in latky:
            opory += [_norm(t) for t in tvrzeni_pro(latka, limit=99)["on_hold"]]

    for veta in re.split(r"(?<=[.!?])\s+", popis):
        n_veta = _norm(veta)
        temata = {s for s in _SLOVNIK if _obsahuje_slovo(veta, s)}
        if not temata:
            continue
        podepreno = any(
            sum(1 for slovo in opora.split() if len(slovo) > 4 and slovo in n_veta) >= 2
            for opora in opory
        )
        if not podepreno:
            nalezy.append(f"zdravotní téma bez opory v seznamu: „{veta.strip()[:70]}…“")

    return nalezy


if __name__ == "__main__":
    import sys

    popis = sys.argv[1]
    nalezy = zkontroluj(popis)
    if nalezy:
        print("NÁLEZY:")
        for nalez in nalezy:
            print("   ✗", nalez)
    else:
        print("✓ bez nálezů")

    for latka in sys.argv[2:]:
        dostupna = tvrzeni_pro(latka)
        print(f"\n-- tvrzení pro „{latka}“ --")
        for veta in dostupna["schvalena"]:
            print("   [schválené]", veta)
        for veta in dostupna["on_hold"]:
            print("   [on hold]  ", veta)
