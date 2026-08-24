"""Rozpoznání balíčků a sad, které do produktové nabídky nepatří.

E-shop je nijak neoznačuje – v Shoptetu jsou vedené jako běžný produkt.
Proto tři nezávislé signály a ruční seznam pro zbytek.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

_DATA = Path(__file__).parent / "data"

RUCNI_SEZNAM: list[str] = json.loads((_DATA / "balicky_rucne.json").read_text("utf-8"))
"""Sady, které nemají v názvu ani na stránce žádný rozpoznatelný znak.

Například „BrainMax Superhrdina“ nebo „BrainMax Mužské zdraví“. Seznam je
ručně odsouhlasený a doplňuje se podle potřeby.
"""

_KLICOVE_SLOVO = re.compile(r"\bbal[íi]če?k\w*\b|\bsada\b|\bpack\b", re.I)

_BALENI = re.compile(
    r"\d+\s*(?:\w+\s+){0,2}"
    r"(?:kapsl\w+|kapsle|tablet\w*|tbl|dra[žz]é|bonb[óo]n\w*|g\b|ml\b|ks\b)",
    re.I,
)

_ZNACKA = re.compile(r"BrainMax|Performance", re.I)

_MARKER_NA_STRANCE = re.compile(
    r"Tento balíček|Bal[íi]ček obsahuje|Sada obsahuje|V balíčku (?:najdete|naleznete)",
    re.I,
)


def je_balicek(nazev: str, stranka: str = "") -> bool:
    """Je produkt sadou více produktů?

    Znak `+` v názvu má dva významy – buď složení jedné receptury
    („Hořčík + Vitamín B6“), nebo dva samostatné produkty
    („Sleep Magnesium + BrainMax Glycin“). Rozlišuje se podle toho,
    jestli obě strany nesou vlastní údaj o balení nebo vlastní značku.
    """
    if nazev in RUCNI_SEZNAM:
        return True

    if _KLICOVE_SLOVO.search(nazev):
        return True

    if " + " in nazev:
        pred, _, za = nazev.partition(" + ")
        dve_baleni = bool(_BALENI.search(pred) and _BALENI.search(za))
        dve_znacky = bool(_ZNACKA.search(pred) and _ZNACKA.search(za))
        if dve_baleni or dve_znacky:
            return True

    return bool(_MARKER_NA_STRANCE.search(stranka))
