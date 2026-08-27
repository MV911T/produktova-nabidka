"""Recognising bundles and sets that do not belong in the product offer.

The shop marks them in no way at all — in Shoptet they are ordinary products.
Hence three independent signals plus a manual list for the rest.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

_DATA = Path(__file__).parent / "data"

MANUAL_LIST: list[str] = json.loads((_DATA / "manual_bundles.json").read_text("utf-8"))
"""Sets carrying no recognisable mark in their name or on their page.

„BrainMax Superhrdina“ or „BrainMax Mužské zdraví“, for instance. The list is
reviewed by hand and extended as needed.
"""

_KEYWORD = re.compile(r"\bbal[íi]če?k\w*\b|\bsada\b|\bpack\b|\bset\b", re.I)
"""Words the shop names a set with.

`set` was added because of clothing sets („LAUF unisex cyklistický set, dres
a kraťasy“) — the jersey and the shorts are sold separately, so it is a set
just like „BrainMax sada Trénink“. Across the catalogue it hits only those.
"""

_PACKAGING = re.compile(
    r"\d+\s*(?:\w+\s+){0,2}"
    r"(?:kapsl\w+|kapsle|tablet\w*|tbl|dra[žz]é|bonb[óo]n\w*|g\b|ml\b|ks\b)",
    re.I,
)

_BRAND = re.compile(r"BrainMax|Performance", re.I)

_PAGE_MARKER = re.compile(
    r"Bal[íi]ček obsahuje|Sada obsahuje|V balíčku (?:najdete|naleznete)",
    re.I,
)
"""Sentences a page introduces the contents of a set with.

A bare „Tento balíček“ used to be here as well, but it hit cross-selling
instead — „Omega 3 skvěle doplní tento balíček“ dropped Bacopa Monnieri from
the offer. Across the whole catalogue that pattern matched exactly once, and
wrongly. The marker must therefore introduce a list, not merely mention the
word.
"""


def is_bundle(name: str, page: str = "") -> bool:
    """Is the product a set of several products?

    A `+` in the name has two meanings — either the composition of a single
    formula („Hořčík + Vitamín B6“) or two standalone products („Sleep
    Magnesium + BrainMax Glycin“). The two are told apart by whether both
    sides carry their own pack size or their own brand.
    """
    if name in MANUAL_LIST:
        return True

    if _KEYWORD.search(name):
        return True

    if " + " in name:
        before, _, after = name.partition(" + ")
        two_packages = bool(_PACKAGING.search(before) and _PACKAGING.search(after))
        two_brands = bool(_BRAND.search(before) and _BRAND.search(after))
        if two_packages or two_brands:
            return True

    return bool(_PAGE_MARKER.search(page))
