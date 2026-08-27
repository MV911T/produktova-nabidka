"""Retrying downloads and reporting an incomplete offer."""

import json

import pytest
import requests

import product_offer
from product_offer import IncompleteOffer, build_offer, fetching
from product_offer.cli import main


class Response:
    """A stand-in for `requests.Response` — does only what `fetch()` needs."""

    def __init__(self, text: str = "obsah", status: int = 200) -> None:
        self.text = text
        self.status_code = status

    def raise_for_status(self) -> None:
        if self.status_code >= 400:
            raise requests.HTTPError(f"HTTP {self.status_code}", response=self)


@pytest.fixture(autouse=True)
def no_waiting(monkeypatch):
    """Tests are not to sit through the growing pause between attempts."""
    monkeypatch.setattr(fetching.time, "sleep", lambda _: None)


def _attempts(monkeypatch, *responses):
    """Make `requests.get` return the given responses one after another."""
    remaining = list(responses)
    calls = []

    def get(url, **_):
        calls.append(url)
        result = remaining.pop(0)
        if isinstance(result, Exception):
            raise result
        return result

    monkeypatch.setattr(fetching.requests, "get", get)
    return calls


def test_temporary_outage_is_retried(monkeypatch):
    calls = _attempts(
        monkeypatch,
        requests.ConnectionError("spojení spadlo"),
        Response(status=503),
        Response("povedlo se"),
    )

    assert fetching.fetch("https://example.com/") == "povedlo se"
    assert len(calls) == 3


def test_gives_up_after_the_last_attempt(monkeypatch):
    calls = _attempts(monkeypatch, *[requests.ConnectionError("spadlo")] * 3)

    with pytest.raises(requests.ConnectionError):
        fetching.fetch("https://example.com/", attempts=3)
    assert len(calls) == 3


def test_4xx_response_is_not_retried(monkeypatch):
    """An error on our side is not fixed by asking again, it only costs time."""
    calls = _attempts(monkeypatch, Response(status=404), Response("nedosažitelné"))

    with pytest.raises(requests.HTTPError):
        fetching.fetch("https://example.com/")
    assert len(calls) == 1


@pytest.fixture
def category_of_two(monkeypatch, product_page):
    """A category with two products; the second one fails to download."""
    monkeypatch.setattr(
        product_offer,
        "load_category",
        lambda _: ("Testovací kategorie", ["https://e.cz/a/", "https://e.cz/b/"]),
    )
    monkeypatch.setattr(product_offer, "pause", lambda: None)

    def fetch(url, **_):
        if url.endswith("/b/"):
            raise requests.ConnectionError("spojení spadlo")
        return product_page

    monkeypatch.setattr(product_offer, "fetch", fetch)


def test_a_failed_page_does_not_quietly_shrink_the_offer(category_of_two):
    with pytest.raises(IncompleteOffer) as found:
        build_offer(["https://e.cz/kategorie/"])

    assert found.value.failed_urls == ["https://e.cz/b/"]
    assert len(found.value.offer) == 1


def test_cli_withholds_an_incomplete_offer(category_of_two, capsys):
    """A shortened JSON must not reach stdout as if it were complete."""
    exit_code = main(["https://e.cz/kategorie/"])
    captured = capsys.readouterr()

    assert exit_code == 1
    assert captured.out == ""
    assert "NEÚPLNÁ" in captured.err.upper()


def test_cli_prints_an_incomplete_offer_when_told_to(category_of_two, capsys):
    exit_code = main(["https://e.cz/kategorie/", "--dovol-neuplnou"])
    captured = capsys.readouterr()

    assert exit_code == 0
    assert len(json.loads(captured.out)) == 1
    assert "NEÚPLNÁ NABÍDKA" in captured.err
