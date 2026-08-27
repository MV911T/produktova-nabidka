"""Category listings — collecting product URLs, pagination included."""

from __future__ import annotations

import re

from .fetching import BASE_URL, block_by_id, fetch, pause, strip_tags


def page_count(page: str) -> int:
    """The shop states the number of pages as „Nacházíte se na straně 1 z 12“."""
    match = re.search(r"Nacházíte se na straně \d+ z (\d+)", page)
    return int(match.group(1)) if match else 1


def category_name(page: str) -> str:
    match = re.search(r"<h1[^>]*>(.*?)</h1>", page, re.S)
    return strip_tags(match.group(1)) if match else ""


def products_in_listing(page: str) -> list[str]:
    """Product paths from the main listing.

    Only the contents of `<div id="products">` count — the page also carries
    a „Nejprodávanější“ block whose products do not belong to the category.
    """
    listing = block_by_id(page, "products")
    if listing is None:
        return []

    links = re.findall(r'<a href="(/[^"?#]+/)"[^>]*class="[^"]*\bimage\b', listing)
    return list(dict.fromkeys(links))


def load_category(category_url: str) -> tuple[str, list[str]]:
    """Return `(category name, absolute URLs of all its products)`."""
    category_url = category_url.rstrip("/")
    first = fetch(category_url + "/")

    name = category_name(first)
    paths = products_in_listing(first)

    for page_number in range(2, page_count(first) + 1):
        pause()
        further = fetch(f"{category_url}/strana-{page_number}/")
        paths.extend(products_in_listing(further))

    return name, [BASE_URL + path for path in dict.fromkeys(paths)]
