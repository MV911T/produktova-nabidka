"""Assembling the offer — dropping duplicates and the order of categories."""

import re

import pytest

import product_offer
from product_offer import build_offer

CANONICAL = "https://www.brainmarket.cz/brainmax-men-multivitamin--90-kapsli/"
SECOND_PATH = "https://www.brainmarket.cz/brainmax-men-multivitamin--90-kapsli-2/"


@pytest.fixture
def no_waiting(monkeypatch):
    monkeypatch.setattr(product_offer, "pause", lambda: None)


def _page(product_page: str, url: str) -> str:
    """A cut-out of the real page with the microdata `url` swapped out."""
    return re.sub(
        r'(<[^>]*itemprop="url"[^>]*content=")[^"]*(")',
        rf"\g<1>{url}\g<2>",
        product_page,
        count=1,
    )


def test_two_paths_to_the_same_product_give_one_record(monkeypatch, no_waiting, product_page):
    """The shop lists the same product as „…-kapsli-2“ as well.

    The addresses from the listing differ, only the microdata `url` agrees —
    and that is what the duplicate is recognised by.
    """
    monkeypatch.setattr(
        product_offer, "load_category", lambda _: ("BrainMax pro muže", [CANONICAL, SECOND_PATH])
    )
    monkeypatch.setattr(
        product_offer, "fetch", lambda url, **_: _page(product_page, CANONICAL)
    )

    products = build_offer(["https://e.cz/brainmax-men/"])

    assert len(products) == 1
    assert products[0]["product_url"] == CANONICAL


def test_a_product_in_two_categories_gets_the_first_one(monkeypatch, no_waiting, product_page):
    listings = {
        "https://e.cz/muzi/": ("BrainMax pro muže", [CANONICAL]),
        "https://e.cz/zeny/": ("BrainMax pro ženy", [CANONICAL]),
    }
    monkeypatch.setattr(product_offer, "load_category", lambda url: listings[url])
    monkeypatch.setattr(
        product_offer, "fetch", lambda url, **_: _page(product_page, CANONICAL)
    )

    products = build_offer(["https://e.cz/muzi/", "https://e.cz/zeny/"])

    assert len(products) == 1
    assert products[0]["category"] == "BrainMax pro muže"


def test_different_products_stay(monkeypatch, no_waiting, product_page):
    """Only a match may be dropped, never two different products."""
    other = "https://www.brainmarket.cz/brainmax-jiny-produkt/"
    monkeypatch.setattr(
        product_offer, "load_category", lambda _: ("BrainMax pro muže", [CANONICAL, other])
    )
    monkeypatch.setattr(
        product_offer, "fetch", lambda url, **_: _page(product_page, url)
    )

    products = build_offer(["https://e.cz/brainmax-men/"])

    assert [p["product_url"] for p in products] == [CANONICAL, other]
