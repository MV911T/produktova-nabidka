#!/usr/bin/env python3
"""Vykreslí přehlednou tabuli úkolů z TODO.md.

Spouští se z hooku po každé iteraci, takže musí být rychlá a nesmí
nikdy spadnout — když se něco nepovede, radši nevypíše nic.

    python3 nastroje/tabule.py            # tabule na stdout
    python3 nastroje/tabule.py --hook     # JSON se systemMessage pro hook
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

SIRKA = 64
"""Na kolik znaků se ořezávají názvy úkolů."""

NADPIS = re.compile(r"^\*\*(\d+)\.\s*(.*?)\*\*\s*$|^\*\*(\d+)\.\*\*\s+(.*?)\s*$")
SEKCE = re.compile(r"^##\s+(.*?)\s*$")
PODSEKCE = re.compile(r"^###\s+(.*?)\s*$")


def nacti(cesta: Path) -> tuple[list[tuple[str, str, int, str]], str]:
    """Vrátí `[(sekce, podsekce, číslo, název)]` a řádek s počty."""
    polozky: list[tuple[str, str, int, str]] = []
    pocty = ""
    sekce = podsekce = ""

    for radek in cesta.read_text("utf-8").splitlines():
        if not pocty and radek.startswith("**") and "zbývá" in radek:
            pocty = radek.strip("* ")
            continue

        if match := SEKCE.match(radek):
            sekce, podsekce = match.group(1), ""
            continue
        if match := PODSEKCE.match(radek):
            podsekce = match.group(1)
            continue
        if match := NADPIS.match(radek):
            cislo = match.group(1) or match.group(3)
            nazev = match.group(2) or match.group(4) or ""
            polozky.append((sekce, podsekce, int(cislo), zkrat(nazev)))

    return polozky, pocty


def zkrat(nazev: str) -> str:
    """Odstraní markdown a ořízne na šířku tabule."""
    nazev = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", nazev)
    nazev = re.sub(r"[`*_]", "", nazev).strip()
    return nazev if len(nazev) <= SIRKA else nazev[: SIRKA - 1].rstrip() + "…"


def rozsah(cisla: list[int]) -> str:
    return f"{min(cisla)}–{max(cisla)}" if len(cisla) > 1 else str(cisla[0])


def vykresli(polozky: list[tuple[str, str, int, str]], pocty: str) -> str:
    cara = "─" * (SIRKA + 6)
    radky = [cara, f"  TODO · produktová nabídka — {pocty}" if pocty else "  TODO", cara]

    zbyva = [p for p in polozky if p[0] == "Zbývá"]
    podsekce_poradi: list[str] = []
    for _, podsekce, _, _ in zbyva:
        if podsekce not in podsekce_poradi:
            podsekce_poradi.append(podsekce)

    for podsekce in podsekce_poradi:
        radky.append(f"\n  {podsekce.upper()}")
        for _, psek, cislo, nazev in zbyva:
            if psek == podsekce:
                radky.append(f"   {cislo:>2}  {nazev}")

    for sekce in ("Hotovo", "Vyřazeno ze zadání"):
        cisla = [c for s, _, c, _ in polozky if s == sekce]
        if cisla:
            radky.append(f"\n  {sekce.upper()}: {rozsah(cisla)} ({len(cisla)})")

    radky.append(cara)
    return "\n".join(radky)


def najdi_todo() -> Path | None:
    """TODO.md v aktuálním adresáři nebo v některém z nadřazených."""
    for adresar in [Path.cwd(), *Path.cwd().parents]:
        soubor = adresar / "TODO.md"
        if soubor.is_file() and (adresar / "src" / "nabidka").is_dir():
            return soubor
    return None


def main(argv: list[str]) -> int:
    cesta = najdi_todo()
    if cesta is None:
        return 0

    polozky, pocty = nacti(cesta)
    if not polozky:
        return 0

    tabule = vykresli(polozky, pocty)

    if "--hook" in argv:
        json.dump({"systemMessage": tabule, "suppressOutput": True}, sys.stdout)
    else:
        print(tabule)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main(sys.argv[1:]))
    except SystemExit:
        raise
    except Exception:
        raise SystemExit(0) from None
