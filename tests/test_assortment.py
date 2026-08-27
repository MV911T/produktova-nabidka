"""Dropping goods that are not eaten."""

import pytest

from product_offer.assortment import category_path, is_edible


def _page(path: str) -> str:
    """A page cut-out with product microdata and the given category path."""
    return (
        '<div itemtype="https://schema.org/Product" itemscope>'
        f'<meta itemprop="category" content="{path}">'
        "</div>"
    )


INEDIBLE = [
    ("Brain dámské tričko z BIO bavlny, khaki",
     "Úvodní stránka &gt; Oblečení a doplňky &gt; Sportovní oblečení pro ženy &gt; Tričko"),
    ("BrainMax® Shower Gel Bergamot &amp; Orange, 200 ml",
     "Úvodní stránka &gt; Přírodní kosmetika &gt; Péče o tělo &gt; Gel"),
    ("BrainMax Pure® Skleněná láhev s křišťálem, 500 ml",
     "Úvodní stránka &gt; Domov &gt; Boxy na jídlo, lahve, šejkry, tašky &gt; Láhev"),
    # the trail leads to no branch, the name decides
    ("LAUF láhev na kolo a sport, bidon, 750 ml",
     "Úvodní stránka &gt; BrainMax® &gt; LAUF láhev na kolo a sport"),
]


@pytest.mark.parametrize(("name", "path"), INEDIBLE)
def test_goods_that_are_not_eaten_do_not_pass(name, path):
    assert not is_edible(name, _page(path))


EDIBLE = [
    ("BrainMax Pure® Almonda, Coconut Dream, Mandlový krém s kokosem, 30 g",
     "Úvodní stránka &gt; Potraviny &gt; Ořechové krémy, džemy a marmelády &gt; Almonda"),
    # „Pleť, vlasy, nehty“ is a goal, not cosmetics — supplements hang there
    ("BrainMax Women Beauty Fish Collagen, 250 g",
     "Úvodní stránka &gt; Cíle &gt; Pleť, vlasy, nehty &gt; Kolagen"),
    ("BrainMax Zinc Complex®, 50 rostlinných kapslí",
     "Úvodní stránka &gt; BrainMax® &gt; BrainMax Zinc Complex®"),
]


@pytest.mark.parametrize(("name", "path"), EDIBLE)
def test_supplements_pass(name, path):
    assert is_edible(name, _page(path))


def test_the_path_drops_its_leading_entry():
    path = category_path(_page("Úvodní stránka &gt; Potraviny &gt; Nápoje &gt; Limonáda"))

    assert path == ["Potraviny", "Nápoje", "Limonáda"]


def test_a_product_without_microdata_passes():
    """A missing category is no reason to drop a product on its own."""
    assert is_edible("BrainMax Cokoliv, 60 kapslí", "<html></html>")
