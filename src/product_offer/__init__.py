"""Product offer from brainmarket.cz.

    from product_offer import build_offer

    products = build_offer(["https://www.brainmarket.cz/lauf/"])
"""

from __future__ import annotations

import sys

import requests

from .assortment import is_edible
from .bundles import is_bundle
from .catalog import load_category
from .claims import check, claims_for
from .fetching import fetch, pause
from .product import is_product_page, parse

__all__ = [
    "build_offer",
    "IncompleteOffer",
    "is_bundle",
    "is_edible",
    "load_category",
    "parse",
    "claims_for",
    "check",
]

__version__ = "2.0.0"


class IncompleteOffer(RuntimeError):
    """Some pages could not be fetched even on the last attempt.

    Carries what was fetched in `offer` and the URLs it gave up on in
    `failed_urls`. The caller can then decide for itself, but it never gets a
    shorter list in silence — a network outage is indistinguishable from a
    discontinued product.
    """

    def __init__(self, offer: list[dict[str, str]], failed_urls: list[str]) -> None:
        self.offer = offer
        self.failed_urls = failed_urls
        super().__init__(
            f"nabídka je NEÚPLNÁ – nestažené stránky: {len(failed_urls)}, "
            f"stažené produkty: {len(offer)}"
        )


def build_offer(categories: list[str]) -> list[dict[str, str]]:
    """Fetch the products of the given categories and return them as `list[dict]`.

    Every dictionary holds the `product_name`, `product_url`,
    `short_description`, `image_url` and `category` fields from the brief, plus
    `sku` and `ean` as stable identifiers — a URL changes when a product is
    renamed, a stock code does not.

    Discontinued products (the shop redirects them to a category), bundles and
    goods that are not eaten are left out — the men's, women's and LAUF
    categories carry clothing and cosmetics alongside supplements.
    Progress messages go to stderr so they do not spoil the JSON on stdout.

    Every product appears once even when several paths lead to it or it belongs
    to several categories; identity is decided by microdata `url`. The category
    a product first showed up in is the one written into `category`.

    Raises `IncompleteOffer` when a page could not be fetched — a shorter list
    would be indistinguishable from a complete one. An unreachable listing of a
    whole category comes out as `requests.RequestException`.
    """
    seen_urls: set[str] = set()
    seen_products: set[str] = set()
    offer: list[dict[str, str]] = []
    failed_urls: list[str] = []

    for category_url in categories:
        name, product_urls = load_category(category_url)

        for product_url in product_urls:
            if product_url in seen_urls:
                continue
            seen_urls.add(product_url)

            pause()
            try:
                page = fetch(product_url)
            except requests.RequestException as error:
                print(f"  ! nestaženo {product_url}: {error}", file=sys.stderr)
                failed_urls.append(product_url)
                continue

            if not is_product_page(page):
                print(f"  ! produkt už neexistuje: {product_url}", file=sys.stderr)
                continue

            product = parse(page, name)

            if is_bundle(product["product_name"], page):
                continue

            if not is_edible(product["product_name"], page):
                continue

            if not product["product_url"]:
                product["product_url"] = product_url

            # The listing leads to the same product by two paths as well —
            # „…-kapsli“ and „…-kapsli-2“ — and only the microdata `url` agrees.
            # It decides, then, not the address we arrived by.
            if product["product_url"] in seen_products:
                continue
            seen_products.add(product["product_url"])

            offer.append(product)

    if failed_urls:
        raise IncompleteOffer(offer, failed_urls)

    return offer
