"""Rendering the task board from TODO.md.

The script in `tools/` is not part of the package, so it is loaded by path.
"""

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "tools" / "board.py"

SAMPLE = """# TODO

**2 zbývá · 3 hotovo · 1 vyřazeno**

## Zbývá

### Dokončení

**1. První úkol**
Podrobnosti, které do tabule nepatří.

**2. Druhý úkol s [odkazem](https://example.com) a `kódem`**

## Hotovo

**3.** Hotová věc
**4.** Další hotová věc
**5.** Třetí hotová věc

## Vyřazeno ze zadání

**6.** Zahozeno
"""


@pytest.fixture(scope="session")
def board():
    spec = importlib.util.spec_from_file_location("board", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def todo(tmp_path: Path) -> Path:
    path = tmp_path / "TODO.md"
    path.write_text(SAMPLE, "utf-8")
    return path


def test_reads_numbers_and_names(board, todo):
    items, counts = board.load(todo)

    assert counts == "2 zbývá · 3 hotovo · 1 vyřazeno"
    assert [(number, name) for _, _, number, name in items][:2] == [
        (1, "První úkol"),
        (2, "Druhý úkol s odkazem a kódem"),
    ]


def test_knows_both_heading_shapes(board, todo):
    """Remaining tasks carry the name in bold, finished ones after it."""
    items, _ = board.load(todo)
    sections = {number: section for section, _, number, _ in items}

    assert sections[1] == "Zbývá"
    assert sections[3] == "Hotovo"
    assert sections[6] == "Vyřazeno ze zadání"


def test_a_long_name_is_trimmed(board):
    trimmed = board.trim("x" * (board.WIDTH + 20))

    assert len(trimmed) == board.WIDTH
    assert trimmed.endswith("…")


def test_finished_items_are_only_a_span(board, todo):
    items, counts = board.load(todo)
    rendered = board.render(items, counts)

    assert "1  První úkol" in rendered
    assert "HOTOVO: 3–5 (3)" in rendered
    assert "Hotová věc" not in rendered


def test_the_hook_returns_json(board):
    """The hook reads stdout as JSON — broken output would take it down."""
    done = subprocess.run(
        [sys.executable, str(SCRIPT), "--hook"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=True,
    )

    assert json.loads(done.stdout)["systemMessage"].startswith("─")


def test_it_stays_silent_outside_the_project(tmp_path: Path):
    """Anywhere but in this repository the hook must print nothing."""
    done = subprocess.run(
        [sys.executable, str(SCRIPT), "--hook"],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        check=True,
    )

    assert done.stdout == ""
