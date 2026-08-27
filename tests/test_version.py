"""Version agreement between the package metadata and the module."""

import pathlib
import re

import product_offer

ROOT = pathlib.Path(__file__).resolve().parent.parent


def test_pyproject_version_matches_the_module():
    """`pip list` reports the pyproject version, `nabidka --version` the module one.

    They drifted apart once: pyproject stayed on 1.0.0 while the module was
    already on 1.2.0.
    """
    pyproject = (ROOT / "pyproject.toml").read_text("utf-8")
    version = re.search(r'^version = "([^"]+)"', pyproject, re.M).group(1)

    assert version == product_offer.__version__
