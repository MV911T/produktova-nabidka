#!/usr/bin/env python3
"""Render a readable task board from TODO.md.

Run from a hook after every iteration, so it has to be fast and must never
blow up — when something goes wrong it prints nothing instead.

    python3 tools/board.py            # board on stdout
    python3 tools/board.py --hook     # JSON with systemMessage for the hook
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

WIDTH = 64
"""How many characters task names are trimmed to."""

HEADING = re.compile(r"^\*\*(\d+)\.\s*(.*?)\*\*\s*$|^\*\*(\d+)\.\*\*\s+(.*?)\s*$")
SECTION = re.compile(r"^##\s+(.*?)\s*$")
SUBSECTION = re.compile(r"^###\s+(.*?)\s*$")


def load(path: Path) -> tuple[list[tuple[str, str, int, str]], str]:
    """Return `[(section, subsection, number, name)]` and the line with the counts."""
    items: list[tuple[str, str, int, str]] = []
    counts = ""
    section = subsection = ""

    for line in path.read_text("utf-8").splitlines():
        if not counts and line.startswith("**") and "zbývá" in line:
            counts = line.strip("* ")
            continue

        if match := SECTION.match(line):
            section, subsection = match.group(1), ""
            continue
        if match := SUBSECTION.match(line):
            subsection = match.group(1)
            continue
        if match := HEADING.match(line):
            number = match.group(1) or match.group(3)
            name = match.group(2) or match.group(4) or ""
            items.append((section, subsection, int(number), trim(name)))

    return items, counts


def trim(name: str) -> str:
    """Strip markdown and cut to the board width."""
    name = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", name)
    name = re.sub(r"[`*_]", "", name).strip()
    return name if len(name) <= WIDTH else name[: WIDTH - 1].rstrip() + "…"


def span(numbers: list[int]) -> str:
    return f"{min(numbers)}–{max(numbers)}" if len(numbers) > 1 else str(numbers[0])


def render(items: list[tuple[str, str, int, str]], counts: str) -> str:
    rule = "─" * (WIDTH + 6)
    lines = [rule, f"  TODO · produktová nabídka — {counts}" if counts else "  TODO", rule]

    remaining = [item for item in items if item[0] == "Zbývá"]
    subsection_order: list[str] = []
    for _, subsection, _, _ in remaining:
        if subsection not in subsection_order:
            subsection_order.append(subsection)

    for subsection in subsection_order:
        lines.append(f"\n  {subsection.upper()}")
        for _, own_subsection, number, name in remaining:
            if own_subsection == subsection:
                lines.append(f"   {number:>2}  {name}")

    for section in ("Hotovo", "Vyřazeno ze zadání"):
        numbers = [number for own_section, _, number, _ in items if own_section == section]
        if numbers:
            lines.append(f"\n  {section.upper()}: {span(numbers)} ({len(numbers)})")

    lines.append(rule)
    return "\n".join(lines)


def find_todo() -> Path | None:
    """TODO.md in the current directory or in one of its parents."""
    for directory in [Path.cwd(), *Path.cwd().parents]:
        candidate = directory / "TODO.md"
        if candidate.is_file() and (directory / "src" / "product_offer").is_dir():
            return candidate
    return None


def main(argv: list[str]) -> int:
    path = find_todo()
    if path is None:
        return 0

    items, counts = load(path)
    if not items:
        return 0

    board = render(items, counts)

    if "--hook" in argv:
        json.dump({"systemMessage": board, "suppressOutput": True}, sys.stdout)
    else:
        print(board)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main(sys.argv[1:]))
    except SystemExit:
        raise
    except Exception:
        raise SystemExit(0) from None
