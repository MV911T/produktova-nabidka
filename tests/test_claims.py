"""Checking descriptions against the SZPI Guidelines."""

import pytest

from product_offer.claims import check, claims_for

PASSING = [
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
    # an on-hold claim for a plant we name among the substances
    (
        "Kořen ašvagandy přispívá k duševnímu zdraví a relaxaci, ke zvládání stresu a spánku.",
        ["vitánie"],
    ),
]


@pytest.mark.parametrize(("description", "substances"), PASSING)
def test_a_correct_description_passes(description, substances):
    assert check(description, substances) == []


def test_catches_a_medicinal_word():
    findings = check("Podporuje léčbu ekzému a snižuje zánět.")

    assert any("ekzém" in finding for finding in findings)
    assert any("zánět" in finding for finding in findings)


def test_catches_an_amplifying_verb():
    findings = check("Hořčík posiluje vaše svaly a zlepšuje spánek.", ["hořčík"])

    assert any("posiluje" in finding for finding in findings)
    assert any("zlepšuje" in finding for finding in findings)


def test_catches_a_symptom():
    findings = check("Vyčerpání a křeče ve svalech – za tím stojí nedostatek hořčíku.")

    assert any("křeč" in finding for finding in findings)
    assert any("nedostatek" in finding for finding in findings)


def test_a_symptom_is_reported_once():
    """The list carried both „křeč“ and „křeče“ — one sentence got two findings."""
    findings = [f for f in check("Zmírňuje křeče v nohou.") if "křeč" in f]

    assert len(findings) == 1, findings


def test_only_the_most_specific_risk_word_is_reported():
    """Annex 5 carries both „infekce“ and „plísňové infekce“."""
    findings = [f for f in check("Léčí plísňové infekce.") if "infekce" in f]

    assert findings == ["rizikové (léčebné) slovo: „plísňové infekce“"], findings


def test_catches_a_claim_without_support():
    findings = check("Ašvaganda podporuje duševní zdraví.")

    assert any("bez opory" in finding for finding in findings)


def test_an_on_hold_claim_has_to_be_asked_for():
    """Without naming the substance an on-hold claim is no support."""
    description = (
        "Kořen ašvagandy přispívá k duševnímu zdraví a relaxaci, ke zvládání stresu a spánku."
    )

    assert check(description, ["vitánie"]) == []
    assert check(description) != []


def test_lecitin_is_no_form_of_lecit():
    """Without diacritics „lecitin“ and „léčit“ agree on their first five characters."""
    findings = check("Fosfatidylserin ze slunečnicového lecitinu, 100 mg v kapsli.")

    assert not any("léčit" in finding for finding in findings)


def test_magnesium_has_approved_claims():
    available = claims_for("hořčík")

    assert "Hořčík přispívá ke snížení míry únavy a vyčerpání" in available["approved"]


def test_a_substance_without_claims():
    """Neither MSM nor chaga has an approved or on-hold claim."""
    for substance in ("methylsulfonylmethan", "chaga"):
        available = claims_for(substance)
        assert available["approved"] == []
        assert available["on_hold"] == []


NONEXISTENT_SUPPORT = [
    # the wording is copied from an approved claim, but for another substance
    "Kolagen přispívá k normální funkci imunitního systému.",
    "Kreatin přispívá k normální činnosti štítné žlázy.",
    "Spirulina přispívá k udržení normální hladiny cholesterolu v krvi.",
    "Ašvaganda přispívá k normální funkci jater.",
]


@pytest.mark.parametrize("description", NONEXISTENT_SUPPORT)
def test_support_has_to_hold_for_the_same_substance(description):
    """An approved wording for another substance is no support.

    It used to be enough that the sentence agreed with a claim on „přispívá“
    and „normální“ — anything written in the shape of an approved claim passed.
    """
    assert any("bez opory" in finding for finding in check(description))


REAL_CLAIMS = [
    "Vitamin C přispívá k normální funkci imunitního systému.",
    "Vitamín D přispívá k normální funkci imunitního systému.",
    "Železo přispívá k normální tvorbě červených krvinek a hemoglobinu.",
    "Zinek přispívá k udržení normální hladiny testosteronu v krvi.",
]


@pytest.mark.parametrize("description", REAL_CLAIMS)
def test_an_approved_claim_passes(description):
    assert check(description) == []


DESCRIPTIVE_SENTENCES = [
    "Neobsahuje žádné balastní látky (éčka).",
    "Ideální během tréninku, dlouhých pracovních dnů nebo po saunování.",
    "Adaptogenní bylina z ájurvédy, známá také jako indický ženšen.",
    "Vysoké koncentrace glycinu se nacházejí ve svalech a kůži.",
]


@pytest.mark.parametrize("sentence", DESCRIPTIVE_SENTENCES)
def test_a_sentence_without_a_stated_effect_is_no_claim(sentence):
    """Describing where a substance occurs or when to take it is no claim."""
    assert check(sentence) == []


def test_warns_about_a_plant_part_restriction():
    """An on-hold claim for seeds does not hold for a product made of husks."""
    description = "Jitrocel indický přispívá k normální funkci trávicího traktu a střev."
    findings = check(description, ["jitrocel"])

    assert any("část rostliny" in f and "semeno" in f for f in findings)


def test_a_claim_without_a_part_restriction_does_not_warn():
    """Ashwagandha also has claims that name no plant part."""
    description = "Ašvaganda přispívá k duševnímu zdraví a relaxaci."

    assert check(description, ["withania"]) == []


def test_recognises_a_plant_part():
    from product_offer.claims import plant_part

    assert plant_part("Withania somnifera ROOT") == "kořen"
    assert plant_part("Jitrocel indický ( psyllium) - semena") == "semeno"
    assert plant_part("Indický ženšen (Vitánie)") == ""
    # „plodnost“ is not „plod“
    assert plant_part("Normální plodnost a reprodukce") == ""


WORD_USED_BY_THE_SUPPORT = [
    # approved wordings themselves use verbs from the amplifying list
    "Kreatin zvyšuje fyzickou výkonnost při po sobě jdoucích krátkodobých "
    "intervalech vysoce intenzivního fyzického výkonu.",
    "Vitamin C zvyšuje vstřebávání železa.",
    "Enzym laktáza zlepšuje trávení laktózy u osob, které laktózu špatně tráví.",
    # „plynatost“ is a risky word, yet also part of an approved claim
    "Aktivní uhlí přispívá ke snižování nadměrné plynatosti po jídle.",
    # „DNA“ matches the risky word „dna“ once the diacritics are stripped
    "Zinek přispívá k normální syntéze DNA.",
]


@pytest.mark.parametrize("description", WORD_USED_BY_THE_SUPPORT)
def test_a_word_the_support_uses_too_is_not_reported(description):
    """A verbatim approved claim must not trip over our own word lists."""
    assert check(description) == []


WORD_WITHOUT_SUPPORT = [
    ("Hořčík posiluje svaly.", "posiluje"),
    ("Kolagen zvyšuje pružnost pokožky.", "zvyšuje"),
    ("Spirulina chrání buňky před poškozením volnými radikály.", "poškození"),
]


@pytest.mark.parametrize(("description", "word"), WORD_WITHOUT_SUPPORT)
def test_a_word_without_support_is_reported(description, word):
    """The same verb in another sentence has no support and has to be reported."""
    assert any(word in finding for finding in check(description))


def test_a_short_on_hold_claim_supports():
    """„Normální trávení“ has a single meaningful word — a threshold of two dropped it."""
    assert check("Hořec žlutý přispívá k normálnímu trávení.", ["hořec"]) == []
    assert check("Hořec žlutý přispívá k normálnímu trávení.") != []


def test_stems_agree_with_the_word_search():
    from product_offer.claims import _contains, _contains_word, _stems

    sentence = "Popis zmiňuje lecitinu, plynatosti a zánětů."
    stems, normalised = _stems(sentence), sentence.lower()
    for word in ("plynatost", "zánět", "léčit", "nadýmání"):
        assert _contains(stems, normalised, word) == _contains_word(sentence, word), word


PROHIBITED_WORDINGS = [
    ("Biotin zlepšuje stav vašich vlasů.", "silnější"),
    ("Nedostatek zinku vede k poruchám imunity.", "poruch"),
    ("Vitamin C přispívá k ochraně buněk před oxidativním poškozením.", "silnější"),
    ("Hořčík zlepšuje funkci střev.", "silnější"),
]


@pytest.mark.parametrize(("description", "part_of_reason"), PROHIBITED_WORDINGS)
def test_catches_a_prohibited_wording_from_the_guidelines(description, part_of_reason):
    """The Guidelines carry 43 concrete sentences that cannot be used."""
    findings = [f for f in check(description) if "nepřípustné tvrzení" in f]

    assert findings, description
    assert any(part_of_reason in f for f in findings), findings


APPROVED_LOOKALIKES = [
    # differing from a prohibited wording by a single word
    "Vitamin C přispívá k ochraně buněk před oxidativním stresem.",
    "Biotin přispívá k udržení normálního stavu vlasů.",
    "Zinek přispívá k normální funkci imunitního systému.",
]


@pytest.mark.parametrize("description", APPROVED_LOOKALIKES)
def test_an_approved_wording_is_not_taken_for_a_prohibited_one(description):
    """„oxidativním stresem“ is approved, „oxidativním poškozením“ is not."""
    assert not [f for f in check(description) if "nepřípustné tvrzení" in f]


CLAIMS_CARRIED_BY_A_NOUN = [
    "Kombinace 16 látek pro podporu normální funkce prostaty a močových cest.",
    "Podpora odolnosti a fyzické výkonnosti s pomocí pokladů Ájurvédy.",
    "Ideální volba pro každodenní vitalitu a ochranu před oxidačním stresem.",
    "Zázvor je součástí tradičních směsí pro udržení energie během dne.",
]


@pytest.mark.parametrize("description", CLAIMS_CARRIED_BY_A_NOUN)
def test_a_claim_carried_by_a_noun_is_judged(description):
    """It need not be a verb that states the relation to an effect.

    The catalogue holds dozens of sentences like „pro podporu normální hladiny
    cholesterolu“. A verb-only gate missed them although they are claims.
    """
    assert check(description), description


def test_a_composition_note_does_not_pass_as_a_claim():
    """A bare noun without a health topic makes no claim."""
    assert check("Balení obsahuje 200 ml a vystačí na 20 dávek.") == []


DISEASES_FROM_THE_GUIDELINES = [
    ("X snižuje riziko hypertenze.", "hypertenze"),
    ("Nedostatek vitamínu A může vést k šerosleposti.", "šeroslepost"),
    ("Pomáhá při dyslipidemii.", "dyslipidemie"),
    ("Zmírňuje nervozitu.", "nervozita"),
]


@pytest.mark.parametrize(("description", "word"), DISEASES_FROM_THE_GUIDELINES)
def test_diseases_named_by_the_guidelines_are_risky(description, word):
    """The Guidelines name them in their prohibited claims, Annex 5 did not."""
    assert any(word in finding for finding in check(description)), description


def test_a_symptom_from_annex_5_is_not_reported_twice():
    """Insomnia sits among the risky words, it need not sit among the symptoms too."""
    findings = [f for f in check("Pomáhá při nespavosti.") if "nespavost" in f]

    assert len(findings) == 1, findings


def test_the_symptoms_state_their_origin():
    from product_offer.claims import SYMPTOMS, SYMPTOMS_FROM_GUIDELINES, SYMPTOMS_OWN

    assert SYMPTOMS == SYMPTOMS_FROM_GUIDELINES + SYMPTOMS_OWN
    assert not set(SYMPTOMS_FROM_GUIDELINES) & set(SYMPTOMS_OWN)


def test_a_short_word_is_not_shortened():
    """„kolika“ would be left as „kolik“ and would catch ordinary sentences.

    The price for that is that short words only match in forms with an
    appended ending: „kolika“ yes, „kolice“ no.
    """
    assert check("Podle toho, kolik odměrek nasypete, namícháte nápoj.") == []
    assert any("kolika" in f for f in check("Přípravek pomáhá při kolika."))


def test_a_long_word_matches_when_inflected():
    """For longer words swapping the final vowel works."""
    for description, word in (
        ("Zmírňuje nervozitu.", "nervozita"),
        ("Pomáhá při dyslipidemii.", "dyslipidemie"),
        ("Používá se při anorexii.", "anorexie"),
    ):
        assert any(word in f for f in check(description)), description
