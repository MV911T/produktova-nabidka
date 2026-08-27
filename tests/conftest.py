from pathlib import Path

import pytest

FIXTURES = Path(__file__).parent / "fixtures"


@pytest.fixture(scope="session")
def product_page() -> str:
    """A cut-out of the BrainMax Super Ashwagandha® KSM-66® page."""
    return (FIXTURES / "product.html").read_text("utf-8")


@pytest.fixture(scope="session")
def category_listing() -> str:
    """A cut-out of the LAUF category listing."""
    return (FIXTURES / "listing.html").read_text("utf-8")
