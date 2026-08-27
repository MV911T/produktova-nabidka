"""Recognising bundles and sets."""

import pytest

from product_offer.bundles import MANUAL_LIST, is_bundle

BUNDLES = [
    "BrainMax Magnesium Trio, výhodný balíček",
    "BrainMax sada Trénink",
    "BrainMax Women Beauty Pack",
    "BrainMax Immunity Starter Pack",
    # two products, each with its own pack size
    "BrainMax Calcium D3 & K2, 90 rostlinných kapslí + BrainMax Pure® Collagen Drink, 300 g",
    # two products, each with its own brand
    "BrainMax Sleep magnesium + BrainMax Glycin 975 mg, 100 rostlinných kapslí",
]

CLOTHING_SETS = [
    "LAUF unisex cyklistický set, bílý dres a černé kraťasy se šlemi",
    "Brain unisex cyklistický set, dres a kraťasy, modrý",
    "BrainMax bavlněné oversized triko & kraťasy set, šedá",
]


@pytest.mark.parametrize("name", CLOTHING_SETS)
def test_a_clothing_set_is_a_bundle(name):
    """The jersey and the shorts sell separately, so the set is a bundle."""
    assert is_bundle(name)


SINGLES = [
    "BrainMax Glycin 975 mg, 100 rostlinných kapslí",
    "BrainMax Pure® MSM prášek, 500 g",
    "BrainMax IronZen",
    "BrainMax GlucoControl",
    # here „+“ separates the parts of one formula, not two products
    "Performance Magnesium®, 1000 mg, Hořčík 200 mg + Vitamín B6 P5P, 100 vegan kapslí",
    "BrainMax Silymarin Complex, Ostropestřec mariánský extrakt + dalších 5 bylin, 90 kapslí",
    "BrainMax Draslík Magnesium®, Draslík citrát + Hořčík malát, 200 rostlinných kapslí",
]


@pytest.mark.parametrize("name", BUNDLES)
def test_recognises_a_bundle(name):
    assert is_bundle(name)


@pytest.mark.parametrize("name", SINGLES)
def test_does_not_take_a_product_for_a_bundle(name):
    assert not is_bundle(name)


def test_marker_on_the_page():
    """A set without a keyword in its name is recognised by a sentence on the page."""
    name = "BrainMax Něco Nového"

    assert not is_bundle(name)
    assert is_bundle(name, "<p>Tento balíček obsahuje tři produkty.</p>")


def test_the_manual_list_wins():
    """Sets carrying no signal whatsoever are listed by hand."""
    assert "BrainMax Superhrdina" in MANUAL_LIST
    assert is_bundle("BrainMax Superhrdina")


def test_the_marker_has_to_introduce_a_list():
    """„Tento balíček“ in cross-selling marks no set.

    „Omega 3 skvěle doplní tento balíček“ used to drop Bacopa Monnieri, an
    ordinary single-ingredient product, from the offer.
    """
    cross_selling = (
        '<p><a href="/omega-3-oleje/">Omega 3</a> skvěle doplní tento balíček '
        "díky tomu, že podporují normální činnost mozku.</p>"
    )

    assert not is_bundle("BrainMax Enhanced Bacopa Monnieri, 60 kapslí", cross_selling)


def test_a_marker_introducing_a_list_takes_effect():
    for marker in ("Balíček obsahuje:", "Sada obsahuje:", "V balíčku najdete"):
        assert is_bundle("BrainMax Cokoliv, 60 kapslí", f"<p>{marker} tři produkty.</p>")
