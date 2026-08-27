"""Parsing a product page."""

import pytest

from product_offer.product import breadcrumbs, is_product_page, parse, short_description

BRIEF_FIELDS = ["product_name", "product_url", "short_description", "image_url", "category"]
"""The fields the brief asks for — in its order."""


def test_parses_all_five_fields_from_the_brief(product_page):
    product = parse(product_page, "Doplňky stravy")

    assert list(product)[:5] == BRIEF_FIELDS, "zadání žádá tahle pole v tomhle pořadí"
    assert all(product[field] for field in BRIEF_FIELDS), (
        "žádné pole zadání nesmí zůstat prázdné"
    )


def test_adds_stable_identifiers(product_page):
    """A URL changes when a product is renamed, a stock code does not."""
    product = parse(product_page, "Doplňky stravy")

    assert product["sku"]
    assert product["ean"].isdigit(), "EAN je číselný kód"
    assert len(product["ean"]) == 13


def test_name_carries_no_subtitle(product_page):
    """`itemprop="name"` glues the name to the subtitle, the breadcrumbs do not."""
    product = parse(product_page, "Doplňky stravy")

    assert product["product_name"] == "BrainMax Super Ashwagandha® KSM-66®, 100 rostlinných kapslí"
    assert "Patentovaný extrakt" not in product["product_name"]


def test_category_comes_from_the_outside(product_page):
    """The page says „Doplňky stravy a výživa“, yet the passed value must win."""
    product = parse(product_page, "LAUF")

    assert product["category"] == "LAUF"


def test_short_description_not_the_long_one(product_page):
    product = parse(product_page, "Doplňky stravy")

    assert product["short_description"].startswith("Promyšlená kombinace")
    assert "Prémiová verze Ashwagandhy" not in product["short_description"]


def test_short_description_without_the_operational_notice(product_page):
    product = parse(product_page, "Doplňky stravy")

    assert "Vážení zákazníci" not in product["short_description"]
    assert "Děkujeme za pochopení" not in product["short_description"]


NOTICES = [
    "Vážení zákazníci, upozorňujeme na změnu složení.",
    "Vážení zákazníci, vylepšili jsme složení Energy Magnesia® v aktivní formě!",
    "Vážení zákazníci, opravdu?",
    "Vážení zákazníci, sdělení bez tečky na konci",
    "Děkujeme za pochopení!",
]


@pytest.mark.parametrize("notice", NOTICES)
def test_the_notice_goes_however_it_ends(notice):
    """A sentence ending in an exclamation mark used to stay in the description."""
    page = f'<div class="p-short-description"><p>Popis výrobku. {notice}</p></div>'

    assert short_description(page, "") == "Popis výrobku."


def test_url_and_image_are_absolute(product_page):
    product = parse(product_page, "Doplňky stravy")

    assert product["product_url"].startswith("https://www.brainmarket.cz/")
    assert product["image_url"].startswith("https://")


def test_breadcrumbs_without_the_leading_entry(product_page):
    crumbs = breadcrumbs(product_page)

    assert crumbs[0] == "Doplňky stravy a výživa"
    assert "Domů" not in crumbs


def test_recognises_a_product_page(product_page):
    assert is_product_page(product_page)


def test_recognises_a_discontinued_page():
    """A discontinued product is redirected to its category — no product microdata there."""
    assert not is_product_page("<html><h1>BrainMax®</h1></html>")


def test_description_from_microdata_when_the_block_is_missing():
    page = '<meta itemprop="description" content="Náhradní popis." >'

    assert short_description(page, page) == "Náhradní popis."
