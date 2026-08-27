"""Command line.

    nabidka https://www.brainmarket.cz/lauf/ > nabidka.json
    nabidka --kontrola "text popisu" --latka hořčík
    nabidka --tvrzeni hořčík psyllium

When a page cannot be fetched the offer is incomplete and the command exits
with an error, so that nobody mistakes a shortened JSON for a complete one.
Whoever can live with an incomplete offer adds `--dovol-neuplnou`.

The options stay Czech on purpose — they are part of the user interface the
Czech README documents. Their `dest` names carry the English identifiers.
"""

from __future__ import annotations

import argparse
import json
import sys

from . import IncompleteOffer, __version__, build_offer
from .claims import check, claims_for


def _print_offer(args: argparse.Namespace) -> int:
    try:
        products = build_offer(args.categories)
    except IncompleteOffer as error:
        print(f"\nCHYBA: {error}", file=sys.stderr)
        for url in error.failed_urls:
            print(f"   ✗ {url}", file=sys.stderr)

        if not args.allow_incomplete:
            print("Zkuste to znovu, nebo přidejte --dovol-neuplnou.", file=sys.stderr)
            return 1

        products = error.offer
        json.dump(products, sys.stdout, ensure_ascii=False, indent=2)
        sys.stdout.write("\n")
        print(f"\n{len(products)} produktů – NEÚPLNÁ NABÍDKA", file=sys.stderr)
        return 0

    json.dump(products, sys.stdout, ensure_ascii=False, indent=2)
    sys.stdout.write("\n")
    print(f"\n{len(products)} produktů", file=sys.stderr)
    return 0


def _print_check(args: argparse.Namespace) -> int:
    findings = check(args.description, args.substances)
    if not findings:
        print("✓ bez nálezů")
        return 0

    print("NÁLEZY:")
    for finding in findings:
        print(f"   ✗ {finding}")
    return 1


def _print_claims(args: argparse.Namespace) -> int:
    for substance in args.claims:
        available = claims_for(substance)
        print(f"\n-- {substance} --")
        for wording in available["approved"]:
            print(f"   [schválené] {wording}")
        for wording in available["on_hold"]:
            print(f"   [on hold]   {wording}")
        if not available["approved"] and not available["on_hold"]:
            print("   (žádné tvrzení není k dispozici)")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="nabidka",
        description="Produktová nabídka z brainmarket.cz.",
    )
    parser.add_argument(
        "categories",
        metavar="KATEGORIE",
        nargs="*",
        help="URL kategorií ke stažení",
    )
    parser.add_argument(
        "--kontrola",
        dest="description",
        metavar="TEXT",
        help="prověří popis proti Vodítkům SZPI",
    )
    parser.add_argument(
        "--latka",
        dest="substances",
        action="append",
        default=[],
        metavar="NÁZEV",
        help="látka, jejíž on-hold tvrzení smí popis použít (lze opakovat)",
    )
    parser.add_argument(
        "--tvrzeni",
        dest="claims",
        nargs="+",
        metavar="LÁTKA",
        help="vypíše dostupná tvrzení pro dané látky",
    )
    parser.add_argument(
        "--dovol-neuplnou",
        dest="allow_incomplete",
        action="store_true",
        help="vypsat nabídku i tehdy, když se něco nepodařilo stáhnout",
    )
    parser.add_argument("--version", action="version", version=f"nabidka {__version__}")

    args = parser.parse_args(argv)

    if args.description:
        return _print_check(args)
    if args.claims:
        return _print_claims(args)
    if args.categories:
        return _print_offer(args)

    parser.print_help()
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
