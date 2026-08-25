"""Příkazová řádka.

    nabidka https://www.brainmarket.cz/lauf/ > nabidka.json
    nabidka --kontrola "text popisu" --latka hořčík
    nabidka --tvrzeni hořčík psyllium

Když se některou stránku nepodaří stáhnout, nabídka je neúplná a příkaz
skončí chybou, aby zkrácený JSON nikdo omylem nepovažoval za úplný.
Kdo si s neúplnou nabídkou vystačí, přidá `--dovol-neuplnou`.
"""

from __future__ import annotations

import argparse
import json
import sys

from . import NeuplnaNabidka, __version__, ziskej_nabidku
from .tvrzeni import tvrzeni_pro, zkontroluj


def _vypis_nabidku(argumenty: argparse.Namespace) -> int:
    try:
        produkty = ziskej_nabidku(argumenty.kategorie)
    except NeuplnaNabidka as chyba:
        print(f"\nCHYBA: {chyba}", file=sys.stderr)
        for url in chyba.nestazene:
            print(f"   ✗ {url}", file=sys.stderr)

        if not argumenty.dovol_neuplnou:
            print("Zkuste to znovu, nebo přidejte --dovol-neuplnou.", file=sys.stderr)
            return 1

        produkty = chyba.nabidka
        json.dump(produkty, sys.stdout, ensure_ascii=False, indent=2)
        sys.stdout.write("\n")
        print(f"\n{len(produkty)} produktů – NEÚPLNÁ NABÍDKA", file=sys.stderr)
        return 0

    json.dump(produkty, sys.stdout, ensure_ascii=False, indent=2)
    sys.stdout.write("\n")
    print(f"\n{len(produkty)} produktů", file=sys.stderr)
    return 0


def _vypis_kontrolu(argumenty: argparse.Namespace) -> int:
    nalezy = zkontroluj(argumenty.kontrola, argumenty.latka)
    if not nalezy:
        print("✓ bez nálezů")
        return 0

    print("NÁLEZY:")
    for nalez in nalezy:
        print(f"   ✗ {nalez}")
    return 1


def _vypis_tvrzeni(argumenty: argparse.Namespace) -> int:
    for latka in argumenty.tvrzeni:
        dostupna = tvrzeni_pro(latka)
        print(f"\n-- {latka} --")
        for veta in dostupna["schvalena"]:
            print(f"   [schválené] {veta}")
        for veta in dostupna["on_hold"]:
            print(f"   [on hold]   {veta}")
        if not dostupna["schvalena"] and not dostupna["on_hold"]:
            print("   (žádné tvrzení není k dispozici)")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="nabidka",
        description="Produktová nabídka z brainmarket.cz.",
    )
    parser.add_argument("kategorie", nargs="*", help="URL kategorií ke stažení")
    parser.add_argument("--kontrola", metavar="TEXT", help="prověří popis proti Vodítkům SZPI")
    parser.add_argument(
        "--latka",
        action="append",
        default=[],
        metavar="NÁZEV",
        help="látka, jejíž on-hold tvrzení smí popis použít (lze opakovat)",
    )
    parser.add_argument(
        "--tvrzeni",
        nargs="+",
        metavar="LÁTKA",
        help="vypíše dostupná tvrzení pro dané látky",
    )
    parser.add_argument(
        "--dovol-neuplnou",
        action="store_true",
        help="vypsat nabídku i tehdy, když se něco nepodařilo stáhnout",
    )
    parser.add_argument("--version", action="version", version=f"nabidka {__version__}")

    argumenty = parser.parse_args(argv)

    if argumenty.kontrola:
        return _vypis_kontrolu(argumenty)
    if argumenty.tvrzeni:
        return _vypis_tvrzeni(argumenty)
    if argumenty.kategorie:
        return _vypis_nabidku(argumenty)

    parser.print_help()
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
