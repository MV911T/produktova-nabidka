"""Product page → a dictionary with the five fields the brief asks for."""

from __future__ import annotations

import json
import re
from pathlib import Path

from .fetching import block_by_class, clean, microdata, strip_tags

_DATA = Path(__file__).parent / "data"

CUSTOM_DESCRIPTIONS: dict[str, str] = json.loads(
    (_DATA / "custom_descriptions.json").read_text("utf-8")
)
"""Hand-written descriptions for products the shop has no short description for.

Keyed by product URL. Every text has passed the check in the `claims` module.
"""

BOILERPLATE = [
    r"Vážení zákazníci[^.!?]*[.!?]?",
    r"Děkujeme za pochopení[.!?]?",
]
"""Operational notices the shop mixes into the short description.

The sentence may end with a period, an exclamation mark, a question mark or
nothing at all: both Energy Magnesia® pack sizes end with „Vážení zákazníci,
vylepšili jsme složení… formě!“ and requiring a period left it in place.
"""


def is_product_page(page: str) -> bool:
    """A discontinued product is redirected to its category — no product microdata there."""
    return bool(re.search(r'itemtype="https?://schema\.org/Product"', page))


def product_area(page: str) -> str:
    """The part of the page from where the product microdata start — searched from there on."""
    match = re.search(r'itemtype="https?://schema\.org/Product"', page)
    return page[match.start():] if match else page


def breadcrumbs(page: str) -> list[str]:
    """The trail without its leading „Domů“ entry.

    The last item is the clean product name — unlike `itemprop="name"`, where
    the name is glued to the subtitle and, on variants, to question headings.
    """
    start = re.search(r'itemtype="https?://schema\.org/BreadcrumbList"', page)
    if not start:
        return []

    names = []
    for item in re.split(r'itemprop="itemListElement"', page[start.start():])[1:]:
        match = re.search(
            r'<[^>]*itemprop="name"[^>]*content="([^"]*)"'
            r'|<[^>]*itemprop="name"[^>]*>([^<]*)<',
            item,
        )
        if match:
            name = clean(match.group(1) or match.group(2) or "")
            if name:
                names.append(name)
    return names[1:]


def short_description(page: str, area: str) -> str:
    block = block_by_class(page, "p-short-description")
    text = strip_tags(block) if block else ""
    if not text:
        text = microdata(area, "description")

    for pattern in BOILERPLATE:
        text = re.sub(pattern, "", text)
    return clean(text)


def parse(page: str, category: str) -> dict[str, str]:
    """The five fields from the brief plus `sku` and `ean`.

    The category is passed in from the outside — on the product page it is not
    reliable: for some products the breadcrumb trail leads only to the brand
    and the shop carries no subject category at all.

    The brief does not ask for `sku` and `ean`, but without them the only key
    of a record is its URL, and that changes when a product is renamed. On
    variant goods `sku` carries a size suffix (`70423/XL`) and so identifies
    the variant; the parent product has microdata `productID`.
    """
    area = product_area(page)
    crumbs = breadcrumbs(page)
    url = microdata(area, "url")

    return {
        "product_name": crumbs[-1] if crumbs else microdata(area, "name"),
        "product_url": url,
        "short_description": CUSTOM_DESCRIPTIONS.get(url) or short_description(page, area),
        "image_url": microdata(area, "image"),
        "category": category,
        "sku": microdata(area, "sku"),
        "ean": microdata(area, "gtin13"),
    }
