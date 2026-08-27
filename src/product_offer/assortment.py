"""Dropping goods that are not eaten.

The `/brainmax-men/`, `/brainmax-pro-zeny/` and `/lauf/` categories are not
supplement sections — the shop lists clothing and cosmetics in them too. The
offer, though, is meant to hold only what goes into the mouth.

The name cannot decide it: „Mandlový krém s kokosem“ is food and „BrainMax®
Shower Gel“ is not, yet both would pass the same word filter. What decides is
the branch the product hangs in on the site.
"""

from __future__ import annotations

import html

from .fetching import microdata
from .product import product_area

INEDIBLE_BRANCHES = {
    # main branches
    "Oblečení a doplňky",
    "Přírodní kosmetika",
    "Domov",
    # sub-branches, in case the trail omits the main branch
    "Unisex sportovní oblečení a doplňky",
    "Sportovní oblečení pro ženy",
    "Sportovní oblečení pro muže",
    "Dámská sportovní trička a topy",
    "Dámské legíny, sportovní kalhoty a kraťasy",
    "Dámské spodní prádlo na sport",
    "Dámské cyklistické dresy",
    "Pánská sportovní trička a mikiny",
    "Boxy na jídlo, lahve, šejkry, tašky",
    "Péče o vlasy",
    "Péče o tělo",
    "Péče o pleť a rty",
    "Péče o ruce a nohy",
}
"""Catalogue branches whose goods are not eaten.

They match the names the site actually uses. Goals such as „Pleť, vlasy,
nehty“ are deliberately absent — food supplements hang there.
"""

INEDIBLE_NAME_WORDS = ("láhev", "lahev", "bidon", "šejkr", "shaker", "kšiltovka")
"""A safety net for goods whose trail leads to no branch at all.

`LAUF láhev na kolo a sport, bidon` hangs directly under the brand, so the
branch says nothing about it. The list is deliberately short — the longer it
gets, the greater the risk of dropping a food with a similar word in its name.
"""


def category_path(page: str) -> list[str]:
    """The catalogue trail from microdata `category`, without its leading entry.

    The last link is the product name, not a category.
    """
    path = microdata(product_area(page), "category")
    parts = [html.unescape(part).strip() for part in path.split(">") if part.strip()]
    return parts[1:]


def is_edible(name: str, page: str = "") -> bool:
    """Does the product belong in the supplement offer, or is it clothing or cosmetics?"""
    if any(word in name.lower() for word in INEDIBLE_NAME_WORDS):
        return False

    return not any(part in INEDIBLE_BRANCHES for part in category_path(page))
