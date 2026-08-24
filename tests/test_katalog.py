"""Sběr URL z výpisu kategorie."""

from nabidka.katalog import nazev_kategorie, pocet_stran, produkty_ve_vypisu


def test_sbira_produkty_z_vypisu(vypis_kategorie):
    cesty = produkty_ve_vypisu(vypis_kategorie)

    assert cesty, "výpis musí obsahovat produkty"
    assert all(cesta.startswith("/") and cesta.endswith("/") for cesta in cesty)


def test_cesty_jsou_unikatni(vypis_kategorie):
    cesty = produkty_ve_vypisu(vypis_kategorie)

    assert len(cesty) == len(set(cesty))


def test_ignoruje_blok_nejprodavanejsi():
    """Produkty mimo `<div id="products">` do kategorie nepatří."""
    stranka = (
        '<div id="productsTop"><a href="/mimo-vypis/" class="image"></a></div>'
        '<div id="products"><a href="/ve-vypisu/" class="image"></a></div>'
    )

    assert produkty_ve_vypisu(stranka) == ["/ve-vypisu/"]


def test_vypis_bez_produktu():
    assert produkty_ve_vypisu("<html></html>") == []


def test_pocet_stran_ze_strankovani():
    assert pocet_stran("<p>Nacházíte se na straně 1 z 12.</p>") == 12


def test_jedna_strana_kdyz_strankovani_chybi():
    assert pocet_stran("<html></html>") == 1


def test_nazev_kategorie_z_nadpisu():
    assert nazev_kategorie("<h1 class='x'>BrainMax® doplňky stravy</h1>") == (
        "BrainMax® doplňky stravy"
    )
