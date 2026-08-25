"""Kontrola popisů proti Vodítkům SZPI."""

import pytest

from nabidka.tvrzeni import tvrzeni_pro, zkontroluj

PROJDE = [
    (
        "Hořčík v chelátové formě bisglycinátu s aktivní formou vitamínu B6. "
        "Hořčík přispívá ke snížení míry únavy a vyčerpání a k normální psychické činnosti.",
        ["hořčík"],
    ),
    (
        "Methylsulfonylmethan (MSM) v čistotě 100 %. MSM je organická sloučenina síry, "
        "která se přirozeně vyskytuje v rostlinách i v lidském těle.",
        [],
    ),
    (
        "Glycin je nejmenší a nejjednodušší aminokyselina. Vysoké koncentrace glycinu "
        "se nacházejí ve svalech, kůži a dalších pojivových tkáních.",
        ["glycin"],
    ),
    # on-hold tvrzení pro rostlinu, kterou uvedeme mezi látkami
    (
        "Kořen ašvagandy přispívá k duševnímu zdraví a relaxaci, ke zvládání stresu a spánku.",
        ["vitánie"],
    ),
]


@pytest.mark.parametrize(("popis", "latky"), PROJDE)
def test_spravny_popis_projde(popis, latky):
    assert zkontroluj(popis, latky) == []


def test_zachyti_lecebne_slovo():
    nalezy = zkontroluj("Podporuje léčbu ekzému a snižuje zánět.")

    assert any("ekzém" in nalez for nalez in nalezy)
    assert any("zánět" in nalez for nalez in nalezy)


def test_zachyti_zesilujici_sloveso():
    nalezy = zkontroluj("Hořčík posiluje vaše svaly a zlepšuje spánek.", ["hořčík"])

    assert any("posiluje" in nalez for nalez in nalezy)
    assert any("zlepšuje" in nalez for nalez in nalezy)


def test_zachyti_symptom():
    nalezy = zkontroluj("Vyčerpání a křeče ve svalech – za tím stojí nedostatek hořčíku.")

    assert any("křeče" in nalez for nalez in nalezy)
    assert any("nedostatek" in nalez for nalez in nalezy)


def test_zachyti_tvrzeni_bez_opory():
    nalezy = zkontroluj("Ašvaganda podporuje duševní zdraví.")

    assert any("bez opory" in nalez for nalez in nalezy)


def test_on_hold_musi_byt_vyzadano():
    """Bez uvedení látky nemá on-hold tvrzení oporu."""
    popis = "Kořen ašvagandy přispívá k duševnímu zdraví a relaxaci, ke zvládání stresu a spánku."

    assert zkontroluj(popis, ["vitánie"]) == []
    assert zkontroluj(popis) != []


def test_lecitin_neni_tvar_slova_lecit():
    """Bez diakritiky se „lecitin“ a „léčit“ shodují na prvních pěti znacích."""
    nalezy = zkontroluj("Fosfatidylserin ze slunečnicového lecitinu, 100 mg v kapsli.")

    assert not any("léčit" in nalez for nalez in nalezy)


def test_horcik_ma_schvalena_tvrzeni():
    dostupna = tvrzeni_pro("hořčík")

    assert "Hořčík přispívá ke snížení míry únavy a vyčerpání" in dostupna["schvalena"]


def test_latka_bez_tvrzeni():
    """MSM ani čaga nemají schválené ani on-hold tvrzení."""
    for latka in ("methylsulfonylmethan", "chaga"):
        dostupna = tvrzeni_pro(latka)
        assert dostupna["schvalena"] == []
        assert dostupna["on_hold"] == []


NEEXISTUJICI_OPORA = [
    # znění je opsané ze schváleného tvrzení, ale pro jinou látku
    "Kolagen přispívá k normální funkci imunitního systému.",
    "Kreatin přispívá k normální činnosti štítné žlázy.",
    "Spirulina přispívá k udržení normální hladiny cholesterolu v krvi.",
    "Ašvaganda přispívá k normální funkci jater.",
]


@pytest.mark.parametrize("popis", NEEXISTUJICI_OPORA)
def test_opora_musi_platit_pro_tutez_latku(popis):
    """Schválené znění pro jinou látku oporou není.

    Dřív stačilo, že se věta s tvrzením shodla na slovech „přispívá“
    a „normální“ – tím prošlo cokoli napsaného ve tvaru schváleného tvrzení.
    """
    assert any("bez opory" in nalez for nalez in zkontroluj(popis))


SKUTECNA_TVRZENI = [
    "Vitamin C přispívá k normální funkci imunitního systému.",
    "Vitamín D přispívá k normální funkci imunitního systému.",
    "Železo přispívá k normální tvorbě červených krvinek a hemoglobinu.",
    "Zinek přispívá k udržení normální hladiny testosteronu v krvi.",
]


@pytest.mark.parametrize("popis", SKUTECNA_TVRZENI)
def test_schvalene_tvrzeni_projde(popis):
    assert zkontroluj(popis) == []


POPISNE_VETY = [
    "Neobsahuje žádné balastní látky (éčka).",
    "Ideální během tréninku, dlouhých pracovních dnů nebo po saunování.",
    "Adaptogenní bylina z ájurvédy, známá také jako indický ženšen.",
    "Vysoké koncentrace glycinu se nacházejí ve svalech a kůži.",
]


@pytest.mark.parametrize("veta", POPISNE_VETY)
def test_veta_bez_vysloveneho_ucinku_neni_tvrzeni(veta):
    """Popis místa výskytu ani vhodné chvíle k užití tvrzením není."""
    assert zkontroluj(veta) == []


def test_upozorni_na_omezeni_castí_rostliny():
    """On-hold pro semena neplatí pro výrobek ze slupek."""
    popis = "Jitrocel indický přispívá k normální funkci trávicího traktu a střev."
    nalezy = zkontroluj(popis, ["jitrocel"])

    assert any("část rostliny" in nalez and "semeno" in nalez for nalez in nalezy)


def test_tvrzeni_bez_omezeni_casti_neupozornuje():
    """Vitánie má i tvrzení, která část rostliny neuvádějí."""
    popis = "Ašvaganda přispívá k duševnímu zdraví a relaxaci."

    assert zkontroluj(popis, ["withania"]) == []


def test_rozpozna_cast_rostliny():
    from nabidka.tvrzeni import cast_rostliny

    assert cast_rostliny("Withania somnifera ROOT") == "kořen"
    assert cast_rostliny("Jitrocel indický ( psyllium) - semena") == "semeno"
    assert cast_rostliny("Indický ženšen (Vitánie)") == ""
    # „plodnost“ není „plod“
    assert cast_rostliny("Normální plodnost a reprodukce") == ""
