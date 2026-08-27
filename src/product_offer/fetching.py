"""Page downloads and the HTML helpers built on top of them.

The shop runs on Shoptet and exposes product data as schema.org microdata,
not as JSON-LD. The short description is not in the microdata at all — it
lives only in the HTML.
"""

from __future__ import annotations

import html
import re
import time

import requests

BASE_URL = "https://www.brainmarket.cz"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"
    )
}

REQUEST_DELAY = 0.3
"""Seconds between requests, so the shop is not hammered."""

TIMEOUT = 30

ATTEMPTS = 3
"""How many times a page is fetched before giving up."""

RETRY_DELAY = 1.0
"""Seconds after the first failure. Multiplied by each further attempt."""


def _worth_retrying(error: requests.RequestException) -> bool:
    """Retrying pays off for dropped connections and server-side errors.

    A 4xx response will not be fixed by asking again — that page simply
    is not there.
    """
    response = getattr(error, "response", None)
    return response is None or response.status_code >= 500


def fetch(url: str, attempts: int = ATTEMPTS) -> str:
    """Fetch a page, retrying a temporary outage.

    Raises `requests.RequestException` when even the last attempt fails.
    """
    last_error: requests.RequestException

    for attempt in range(1, attempts + 1):
        try:
            response = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
            response.raise_for_status()
            return response.text
        except requests.RequestException as error:
            last_error = error
            if not _worth_retrying(error):
                break

        if attempt < attempts:
            time.sleep(RETRY_DELAY * attempt)

    raise last_error


def pause() -> None:
    time.sleep(REQUEST_DELAY)


def clean(text: str) -> str:
    """Resolve entities and collapse whitespace into a single space."""
    return re.sub(r"\s+", " ", html.unescape(text)).strip()


def strip_tags(fragment: str) -> str:
    """Turn an HTML fragment into plain text."""
    fragment = re.sub(r"<(script|style)\b.*?</\1>", " ", fragment, flags=re.S | re.I)
    fragment = re.sub(r"<br\s*/?>", " ", fragment, flags=re.I)
    return clean(re.sub(r"<[^>]+>", " ", fragment))


def _content_from(page: str, opening_tag: re.Match[str] | None) -> str | None:
    """Contents of `<div>…</div>` from the given opening tag, nested divs included."""
    if not opening_tag:
        return None

    depth, end = 1, len(page)
    for tag in re.finditer(r"<(/?)div\b[^>]*>", page[opening_tag.end():]):
        depth += -1 if tag.group(1) else 1
        if depth == 0:
            end = opening_tag.end() + tag.start()
            break
    return page[opening_tag.end():end]


def block_by_class(page: str, class_name: str) -> str | None:
    name = re.escape(class_name)
    tag = re.search(rf'<div[^>]*class="[^"]*\b{name}\b[^"]*"[^>]*>', page)
    return _content_from(page, tag)


def block_by_id(page: str, element_id: str) -> str | None:
    tag = re.search(rf'<div[^>]*id="{re.escape(element_id)}"[^>]*>', page)
    return _content_from(page, tag)


def microdata(area: str, prop: str) -> str:
    """Value of an `itemprop` — from content/src/href, otherwise from the tag text."""
    name = re.escape(prop)
    pattern = (
        rf'<[^>]*itemprop="{name}"[^>]*?(?:content|src|href)="([^"]*)"'
        rf'|<[^>]*itemprop="{name}"[^>]*>([^<]*)<'
    )
    match = re.search(pattern, area)
    return clean(match.group(1) or match.group(2) or "") if match else ""
