"""Vyřazení zboží, které se nejí.

Kategorie `/brainmax-men/`, `/brainmax-pro-zeny/` a `/lauf/` nejsou rubriky
doplňků – e-shop v nich vede i oblečení a kosmetiku. Nabídka má ale
obsahovat jen to, co se dává do pusy.

Podle názvu to rozhodnout nejde: „Mandlový krém s kokosem“ je potravina
a „BrainMax® Shower Gel“ ne, přitom obojí by prošlo stejným filtrem na
slovo. Rozhoduje proto větev, ve které produkt na webu visí.
"""

from __future__ import annotations

import html

from .produkt import oblast_produktu
from .stahovani import microdata

NEPOZIVATELNE_VETVE = {
    # hlavní větve
    "Oblečení a doplňky",
    "Přírodní kosmetika",
    "Domov",
    # podvětve pro případ, že cesta hlavní větev neuvádí
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
"""Větve katalogu, jejichž zboží se nejí.

Odpovídají názvům, které web skutečně používá. Cíle jako „Pleť, vlasy,
nehty“ mezi nimi schválně nejsou – tam visí doplňky stravy.
"""

NEPOZIVATELNE_NAZVY = ("láhev", "lahev", "bidon", "šejkr", "shaker", "kšiltovka")
"""Záchranná síť pro zboží, jehož cesta k žádné větvi nevede.

`LAUF láhev na kolo a sport, bidon` visí rovnou pod značkou, takže větev
o něm nic neříká. Výčet je schválně krátký – čím delší, tím větší riziko,
že vyřadí potravinu s podobným slovem v názvu.
"""


def kategorijni_cesta(stranka: str) -> list[str]:
    """Cesta katalogem z microdata `category`, bez úvodní položky.

    Poslední článek je název produktu, ne kategorie.
    """
    cesta = microdata(oblast_produktu(stranka), "category")
    clanky = [html.unescape(c).strip() for c in cesta.split(">") if c.strip()]
    return clanky[1:]


def je_pozivatelne(nazev: str, stranka: str = "") -> bool:
    """Patří produkt do nabídky doplňků, nebo je to oblečení či kosmetika?"""
    if any(slovo in nazev.lower() for slovo in NEPOZIVATELNE_NAZVY):
        return False

    return not any(clanek in NEPOZIVATELNE_VETVE for clanek in kategorijni_cesta(stranka))
