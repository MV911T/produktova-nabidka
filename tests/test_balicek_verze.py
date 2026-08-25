"""Shoda verze mezi balíčkem a modulem."""

import pathlib
import re

import nabidka

KOREN = pathlib.Path(__file__).resolve().parent.parent


def test_verze_v_pyproject_odpovida_modulu():
    """`pip list` hlásí verzi z pyproject, `nabidka --version` z modulu.

    Rozešly se: pyproject zůstal na 1.0.0, zatímco modul byl na 1.2.0.
    """
    pyproject = (KOREN / "pyproject.toml").read_text("utf-8")
    verze = re.search(r'^version = "([^"]+)"', pyproject, re.M).group(1)

    assert verze == nabidka.__version__
