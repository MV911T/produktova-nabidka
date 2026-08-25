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

    assert any("křeč" in nalez for nalez in nalezy)
    assert any("nedostatek" in nalez for nalez in nalezy)


def test_symptom_se_hlasi_jednou():
    """Seznam vedl „křeč“ i „křeče“ – táž věta dostala dva nálezy."""
    nalezy = [n for n in zkontroluj("Zmírňuje křeče v nohou.") if "křeč" in n]

    assert len(nalezy) == 1, nalezy


def test_rizikove_slovo_se_hlasi_jen_nejurcitejsi():
    """Příloha 5 vede „infekce“ i „plísňové infekce“."""
    nalezy = [n for n in zkontroluj("Léčí plísňové infekce.") if "infekce" in n]

    assert nalezy == ["rizikové (léčebné) slovo: „plísňové infekce“"], nalezy


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


SLOVO_MA_I_OPORA = [
    # schválená znění sama používají slovesa ze seznamu zesilujících
    "Kreatin zvyšuje fyzickou výkonnost při po sobě jdoucích krátkodobých "
    "intervalech vysoce intenzivního fyzického výkonu.",
    "Vitamin C zvyšuje vstřebávání železa.",
    "Enzym laktáza zlepšuje trávení laktózy u osob, které laktózu špatně tráví.",
    # „plynatost“ je rizikové slovo, ale i součást schváleného tvrzení
    "Aktivní uhlí přispívá ke snižování nadměrné plynatosti po jídle.",
    # „DNA“ se bez diakritiky shoduje s rizikovým slovem „dna“
    "Zinek přispívá k normální syntéze DNA.",
]


@pytest.mark.parametrize("popis", SLOVO_MA_I_OPORA)
def test_slovo_ktere_ma_i_opora_se_nehlasi(popis):
    """Doslovné schválené tvrzení nesmí spadnout na vlastní slovník."""
    assert zkontroluj(popis) == []


SLOVO_BEZ_OPORY = [
    ("Hořčík posiluje svaly.", "posiluje"),
    ("Kolagen zvyšuje pružnost pokožky.", "zvyšuje"),
    ("Spirulina chrání buňky před poškozením volnými radikály.", "poškození"),
]


@pytest.mark.parametrize(("popis", "slovo"), SLOVO_BEZ_OPORY)
def test_slovo_bez_opory_se_hlasi(popis, slovo):
    """Stejné sloveso v jiné větě oporu nemá a hlásit se musí."""
    assert any(slovo in nalez for nalez in zkontroluj(popis))


def test_kratke_on_hold_tvrzeni_podepira():
    """„Normální trávení“ má jediné významové slovo – práh dvou ho vyřazoval."""
    assert zkontroluj("Hořec žlutý přispívá k normálnímu trávení.", ["hořec"]) == []
    assert zkontroluj("Hořec žlutý přispívá k normálnímu trávení.") != []


def test_kmeny_odpovidaji_hledani_slova():
    from nabidka.tvrzeni import _kmeny, _obsahuje, _obsahuje_slovo

    veta = "Popis zmiňuje lecitinu, plynatosti a zánětů."
    kmeny, n = _kmeny(veta), veta.lower()
    for slovo in ("plynatost", "zánět", "léčit", "nadýmání"):
        assert _obsahuje(kmeny, n, slovo) == _obsahuje_slovo(veta, slovo), slovo


NEPRIPUSTNA_ZNENI = [
    ("Biotin zlepšuje stav vašich vlasů.", "silnější"),
    ("Nedostatek zinku vede k poruchám imunity.", "poruch"),
    ("Vitamin C přispívá k ochraně buněk před oxidativním poškozením.", "silnější"),
    ("Hořčík zlepšuje funkci střev.", "silnější"),
]


@pytest.mark.parametrize(("popis", "cast_duvodu"), NEPRIPUSTNA_ZNENI)
def test_zachyti_nepripustne_zneni_z_voditek(popis, cast_duvodu):
    """Vodítka vedou 43 konkrétních vět, které použít nelze."""
    nalezy = [n for n in zkontroluj(popis) if "nepřípustné tvrzení" in n]

    assert nalezy, popis
    assert any(cast_duvodu in n for n in nalezy), nalezy


SCHVALENA_PODOBNA = [
    # od nepřípustného znění se liší jediným slovem
    "Vitamin C přispívá k ochraně buněk před oxidativním stresem.",
    "Biotin přispívá k udržení normálního stavu vlasů.",
    "Zinek přispívá k normální funkci imunitního systému.",
]


@pytest.mark.parametrize("popis", SCHVALENA_PODOBNA)
def test_schvalene_zneni_se_za_nepripustne_nepovazuje(popis):
    """„oxidativním stresem“ je schválené, „oxidativním poškozením“ ne."""
    assert not [n for n in zkontroluj(popis) if "nepřípustné tvrzení" in n]


TVRZENI_JMENEM = [
    "Kombinace 16 látek pro podporu normální funkce prostaty a močových cest.",
    "Podpora odolnosti a fyzické výkonnosti s pomocí pokladů Ájurvédy.",
    "Ideální volba pro každodenní vitalitu a ochranu před oxidačním stresem.",
    "Zázvor je součástí tradičních směsí pro udržení energie během dne.",
]


@pytest.mark.parametrize("popis", TVRZENI_JMENEM)
def test_tvrzeni_nesene_jmenem_se_posoudi(popis):
    """Vztah k účinku nemusí vyslovit sloveso.

    Katalog má desítky vět typu „pro podporu normální hladiny cholesterolu“.
    Brána na slovesa je míjela, ačkoli tvrzením jsou.
    """
    assert zkontroluj(popis), popis


def test_popis_slozeni_jmenem_neprojde_jako_tvrzeni():
    """Samotné jméno bez zdravotního tématu tvrzení nedělá."""
    assert zkontroluj("Balení obsahuje 200 ml a vystačí na 20 dávek.") == []


NEMOCI_Z_VODITEK = [
    ("X snižuje riziko hypertenze.", "hypertenze"),
    ("Nedostatek vitamínu A může vést k šerosleposti.", "šeroslepost"),
    ("Pomáhá při dyslipidemii.", "dyslipidemie"),
    ("Zmírňuje nervozitu.", "nervozita"),
]


@pytest.mark.parametrize(("popis", "slovo"), NEMOCI_Z_VODITEK)
def test_nemoci_jmenovane_voditky_jsou_rizikove(popis, slovo):
    """Vodítka je jmenují ve svých nepřípustných tvrzeních, příloha 5 je neměla."""
    assert any(slovo in nalez for nalez in zkontroluj(popis)), popis


def test_priznak_z_prilohy_5_se_nehlasi_dvakrat():
    """Nespavost je mezi rizikovými slovy, mezi symptomy už být nemusí."""
    nalezy = [n for n in zkontroluj("Pomáhá při nespavosti.") if "nespavost" in n]

    assert len(nalezy) == 1, nalezy


def test_symptomy_maji_uvedeny_puvod():
    from nabidka.tvrzeni import SYMPTOMY, SYMPTOMY_VLASTNI, SYMPTOMY_Z_VODITEK

    assert SYMPTOMY == SYMPTOMY_Z_VODITEK + SYMPTOMY_VLASTNI
    assert not set(SYMPTOMY_Z_VODITEK) & set(SYMPTOMY_VLASTNI)


def test_kratke_slovo_se_nezkracuje():
    """Z „kolika“ by zbylo „kolik“ a chytalo by běžné věty.

    Daň za to je, že se krátká slova trefí jen v tvarech s přílepkem:
    „kolika“ ano, „kolice“ ne.
    """
    assert zkontroluj("Podle toho, kolik odměrek nasypete, namícháte nápoj.") == []
    assert any("kolika" in n for n in zkontroluj("Přípravek pomáhá při kolika."))


def test_dlouhe_slovo_se_trefi_i_ve_skloneni():
    """U delších slov záměna koncové samohlásky funguje."""
    for popis, slovo in (
        ("Zmírňuje nervozitu.", "nervozita"),
        ("Pomáhá při dyslipidemii.", "dyslipidemie"),
        ("Používá se při anorexii.", "anorexie"),
    ):
        assert any(slovo in n for n in zkontroluj(popis)), popis
