"""Collecting URLs from a category listing."""

from product_offer.catalog import category_name, page_count, products_in_listing


def test_collects_products_from_the_listing(category_listing):
    paths = products_in_listing(category_listing)

    assert paths, "výpis musí obsahovat produkty"
    assert all(path.startswith("/") and path.endswith("/") for path in paths)


def test_paths_are_unique(category_listing):
    paths = products_in_listing(category_listing)

    assert len(paths) == len(set(paths))


def test_ignores_the_bestsellers_block():
    """Products outside `<div id="products">` do not belong to the category."""
    page = (
        '<div id="productsTop"><a href="/mimo-vypis/" class="image"></a></div>'
        '<div id="products"><a href="/ve-vypisu/" class="image"></a></div>'
    )

    assert products_in_listing(page) == ["/ve-vypisu/"]


def test_listing_without_products():
    assert products_in_listing("<html></html>") == []


def test_page_count_from_pagination():
    assert page_count("<p>Nacházíte se na straně 1 z 12.</p>") == 12


def test_single_page_when_pagination_is_missing():
    assert page_count("<html></html>") == 1


def test_category_name_from_the_heading():
    assert category_name("<h1 class='x'>BrainMax® doplňky stravy</h1>") == (
        "BrainMax® doplňky stravy"
    )
