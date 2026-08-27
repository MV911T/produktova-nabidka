"""Checking short descriptions against the SZPI Guidelines 2024.

Under Article 10 of Regulation (EC) No 1924/2006 every claim linking a food
to health must appear on the approved list. This module looks for five kinds
of offence:

1. risky (medicinal) words — Annex 5 of the Guidelines
2. verbs that push a claim beyond its approved wording — Annex 6
3. wordings the Guidelines list as prohibited, reason included
4. sentences on a health topic with no support in an approved, on-hold
   or nutrition claim
5. sentences whose only support is tied to a different part of the plant
   than the product contains

Only sentences that actually state an effect are judged: merely mentioning
health is not a claim. The support must also hold for the same substance —
wording copied from another nutrient is no support at all.

A word is reported only when the claim the sentence leans on does not use it
too. Approved wordings themselves say „zvyšuje“ (creatine, vitamin C) and
„zlepšuje“ (lactase), „plynatost“ stands in the approved claim for activated
charcoal, and „DNA“ in the zinc claim matches the risky word „dna“ once the
diacritics are stripped.

This does not replace human judgement, it only flags the commonest mistakes.
"""

from __future__ import annotations

import json
import re
import unicodedata
from pathlib import Path

_DATA = Path(__file__).parent / "data"


def _load(name: str):
    return json.loads((_DATA / name).read_text("utf-8"))


RISK_WORDS: list[str] = _load("risk_words.json")
PROHIBITED: list[dict] = _load("prohibited_claims.json")
APPROVED_HEALTH: list[list[str]] = _load("approved_health_claims.json")
APPROVED_NUTRITION: list[list[str]] = _load("approved_nutrition_claims.json")
ON_HOLD: list[dict] = _load("on_hold_claims.json")

AMPLIFYING_VERBS = [
    "zlepšuje", "posiluje", "stimuluje", "zvyšuje", "urychluje", "obnovuje",
    "odstraňuje", "potlačuje", "zabraňuje", "předchází", "chrání před",
    "léčí", "vyléčí", "zbaví", "uleví", "řeší", "napravuje", "hraje klíčovou roli",
]
"""Verbs that turn the approved „přispívá k…“ into a stronger claim."""

SYMPTOMS_FROM_GUIDELINES = ["nedostatek", "výkyvy nálad"]
"""Symptoms whose wording stands in the Guidelines.

Both „Nedostatek X vede k poruchám zraku“ and „jejíž narušení způsobuje
poruchy a výkyvy nálad“ appear verbatim among the prohibited claims.
"""

SYMPTOMS_OWN = [
    "křeč", "neklidný spánek", "deficit", "nadýmání",
    "nafouklé břicho", "lámavost", "podrážděnost", "vyčerpaný", "unavený",
]
"""Symptoms we added ourselves.

Annex 5 of the Guidelines lists diseases, not symptoms — that is a gap in the
source, not in the code. The list is therefore a deliberate one and kept
short. Words such as „soustředění“ or „nálada“ are not in it: they occur
routinely in supplement descriptions in a harmless sense and would turn the
check into an alarm generator.

`nespavost`, `bolest` and `vypadávání vlasů` are absent because Annex 5
already carries them among the risky words — they would be reported twice.
"""

SYMPTOMS = SYMPTOMS_FROM_GUIDELINES + SYMPTOMS_OWN
"""Symptoms unknown to the approved claims — they hint at a medicinal effect."""

VOCABULARY_THRESHOLD = 2
"""How many words from the health vocabulary a sentence needs before it is judged."""

RELATIONAL = [
    # verbs
    "přispívá", "přispívají", "přispět", "podílí", "pomáhá", "pomáhají",
    "podporuje", "napomáhá", "napomáhají", "prospívá", "působí",
    "udržuje", "ovlivňuje", "snižuje", "zmírňuje",
    "doplňuje", "dodává", "je potřebný", "je nezbytný", "má vliv",
    # a noun instead of a verb — „pro podporu normální hladiny cholesterolu“
    "podpor", "ochran", "regenerac", "prospěšn",
    "posílení", "zvýšení", "snížení", "udržení", "účinek", "účinky", "péči o",
]
"""Expressions a sentence links a substance to health with.

A health claim under Article 2 of Regulation 1924/2006 has to state the
relationship between the food and health. „Vysoké koncentrace glycinu se
nacházejí ve svalech“ claims no effect — it describes where the substance
occurs in the body.

It need not be a verb that states it, though. The catalogue holds 60
sentences like „pro podporu normální hladiny cholesterolu“ or „pro udržení
energie“, which are claims, only carried by a noun. Short forms such as
`podpor` or `ochran` are stems — `_SUFFIXES` supplies the ending.
"""

_SUFFIXES = {
    "", "a", "e", "i", "y", "u", "o", "ě", "í", "ý", "á", "é", "ů", "ou", "em",
    "im", "am", "om", "mi", "ch", "ech", "ich", "ám", "ým", "ých", "ové", "ový",
    "ová", "ně", "ný", "ná", "né", "ni", "te", "l", "la", "lo", "ly", "t",
    "ti", "m", "š", "me", "s", "ce", "ci", "ku", "ky", "ka", "ek",
}
"""Endings a searched word is allowed to differ by.

A longer remainder means a different word — „lecitinu“ is no form of „léčit“.
"""

_INSIGNIFICANT = {
    "a", "i", "k", "o", "u", "v", "s", "z", "na", "po", "do", "ke", "se", "je",
    "the", "of", "and", "to", "in", "for", "prispiva", "podili", "prispiv",
    "normalni", "normalnimu", "normalnich", "udrzeni", "stavu", "funkce", "-",
    # names of nutrients and ingredients — describing composition is no health claim
    "obsah", "obsahu", "obsahuji", "obsahuje", "obsahem", "zdrojem", "davce", "davku",
    "aminokyselin", "aminokyselina", "aminokyseliny", "bilkovin", "bilkoviny",
    "sacharid", "sacharidy", "vlaknina", "vlakniny", "vitamin", "vitaminu",
    "mineral", "mineraly", "extrakt", "extraktu", "polysacharid", "polysacharidu",
    # words that reached the vocabulary from claim wordings but say nothing
    # about health on their own — „ideální během tréninku“ is no health claim
    "behem", "vysoce", "komfort", "zdroj", "latky", "kazdodenni", "trenink",
    "treninku", "organismu", "organismus", "ideal", "idealni", "vyzivove",
    "vyzivovy", "doplnek", "denni", "dennim", "davka", "forme", "forma",
    "slozeni", "produkt", "pripravek", "vyrobek", "kvality", "kvalita",
    "prirodni", "celkove", "dalsi",
}


def _norm(text: str) -> str:
    """Lower case without diacritics."""
    text = unicodedata.normalize("NFD", str(text).lower())
    return "".join(char for char in text if unicodedata.category(char) != "Mn")


def _search_stem(target: str) -> str:
    """The form a searched word is compared in.

    Words ending in a vowel are inflected by replacing it rather than by
    appending: „anorexie“ → „anorexií“, „nervozita“ → „nervozitu“. The form
    without that vowel is therefore compared, or such a word would only ever
    match in the nominative.

    Short stems are not shortened: „kolika“ would be left as „kolik“ and the
    sentence „podle toho, kolik odměrek nasypete“ would be reported.
    """
    return target[:-1] if len(target) > 6 and target[-1] in "aeo" else target


def _contains_word(text: str, needle: str) -> bool:
    """Does the word occur in the text as a word of its own, inflected forms included?"""
    target = _norm(needle)
    if " " in target:
        return target in _norm(text)

    stem = _search_stem(target)
    return any(
        token.startswith(stem) and token[len(stem):] in _SUFFIXES
        for token in re.findall(r"[a-zá-ž]+", _norm(text))
    )


PLANT_PARTS = {
    "kořen": ("root", "kořen"),
    "list": ("leaf", "leaves", "list"),
    "semeno": ("seed", "seeds", "semeno", "semena"),
    "plod": ("fruit", "plod"),
    "květ": ("flower", "květ"),
    "slupka": ("husk", "slupka"),
    "nať": ("herb", "nať"),
}
"""Plant parts an on-hold claim tends to be tied to.

A quarter of the records name one, and then the claim holds for it alone:
„Duševní zdraví, stres & spánek“ is tied to the root of ashwagandha, not to
an extract of root and leaf together.
"""


def plant_part(text: str) -> str:
    """The plant part named in the record, otherwise an empty string."""
    for name, words in PLANT_PARTS.items():
        if any(_contains_word(text, word) for word in words):
            return name
    return ""


_FILLER = {
    "prispiva", "prispivaji", "prispiv", "podili", "pomaha", "pomahaji",
    "pomahat", "udrzeni", "udrzet", "udrzovat", "udrzovani", "normalni",
    "normalniho", "normalnimu", "normalnich", "normalnim", "funkce", "funkci",
    "funkcim", "cinnost", "cinnosti", "stavu", "potrebna", "potrebny",
}
"""Connecting words nearly every approved claim is written with.

Without them „Ašvaganda přispívá k normální funkci jater“ would come out
supported by the choline claim — they would agree on „přispívá“ and
„normální“.
"""


_CONNECTIVES = {
    "nebo", "anebo", "popr", "pripadne", "jine", "jiny", "ostatni", "vcetne",
    "kategorie", "potravin", "potraviny", "potravina", "latka", "latky",
}
"""Words that carry only sentence structure in a substance name, not its identity."""


def _mentions_substance(sentence: str, substance: str) -> bool:
    """Does the sentence speak of the substance the claim is approved for?

    Without this condition „Kolagen přispívá k normální funkci imunitního
    systému“ would come out supported by the vitamin C claim — they would
    agree on the description of the effect although it is approved for a
    different substance.

    Nutrition claims are tied to no substance, so they are not examined.
    """
    if not substance:
        return True

    # deliberately not filtered through _INSIGNIFICANT: „vitamin“ is in there for
    # the vocabulary's sake, but the name „vitamin A“ would then be left with
    # nothing and the check would be skipped
    names = [
        word for word in re.findall(r"[a-zá-ž0-9]+", _norm(substance))
        if len(word) > 2 and word not in _CONNECTIVES
    ]
    return not names or any(_contains_word(sentence, name) for name in names)


def _stems(text: str) -> set[str]:
    """Stems of the sentence's words — everything the searched word could have been.

    Computed once per sentence so that 230 risky words are not each searched
    for by walking the text again.
    """
    stems: set[str] = set()
    for token in re.findall(r"[a-zá-ž]+", _norm(text)):
        for suffix in _SUFFIXES:
            if not suffix:
                stems.add(token)
            elif token.endswith(suffix):
                stems.add(token[: -len(suffix)])
    return stems


def _contains(stems: set[str], normalised: str, needle: str) -> bool:
    """The same as `_contains_word`, only over precomputed stems."""
    target = _norm(needle)
    return target in normalised if " " in target else _search_stem(target) in stems


def _supports(claim: str, normalised_sentence: str) -> bool:
    """Does the sentence lean on this claim?

    Only words carrying meaning decide, and two of them have to agree so that
    a chance meeting of a single word does not count as support. Short on-hold
    claims such as „Antioxidant“ or „Normální trávení“ have no more than one
    meaningful word, though — for those the single one is enough, or they
    could support nothing at all.
    """
    meaningful = [
        word for word in claim.split()
        if len(word) > 4 and word not in _FILLER
    ]
    if not meaningful:
        return False

    threshold = min(2, len(meaningful))
    return sum(1 for word in meaningful if word in normalised_sentence) >= threshold


def claims_for(substance: str, limit: int = 15) -> dict[str, list[str]]:
    """Approved and on-hold claims available for the given substance."""
    needle = _norm(substance)

    approved = [
        row[2] for row in APPROVED_HEALTH
        if len(row) > 2 and needle in _norm(row[1])
    ]
    on_hold = [
        f"{row['cz']} → {row['claim']}" for row in ON_HOLD
        if needle in _norm(row["lat"]) or needle in _norm(row["cz"])
    ]
    return {"approved": approved[:limit], "on_hold": on_hold[:limit]}


def _health_vocabulary() -> set[str]:
    """Words from claim texts — a signal that a sentence speaks of health.

    Substance and plant names are left out: mentioning composition is no claim.
    """
    words: set[str] = set()
    for row in APPROVED_HEALTH:
        if len(row) > 2:
            words.update(_norm(row[2]).split())
    for row in ON_HOLD:
        words.update(_norm(row["claim"]).split())

    names: set[str] = set()
    for row in APPROVED_HEALTH:
        if len(row) > 1:
            names.update(_norm(row[1]).split())
    for row in ON_HOLD:
        names.update(_norm(row["cz"]).split())
        names.update(_norm(row["lat"]).split())

    return {
        word for word in words
        if len(word) > 4 and word not in _INSIGNIFICANT and word not in names
    }


_VOCABULARY = _health_vocabulary()


_SKIP_IN_PATTERN = {
    "díky", "jako", "např", "tedy", "tím", "této", "která", "které", "který",
    "jehož", "jejíž", "jejichž", "jsou", "aby", "pro", "vaše", "vašich",
    "vašeho", "vašim", "přičemž", "další", "dalšími", "například",
}
"""Words that do not carry the substance of a prohibited claim's pattern."""


def _prohibited_patterns() -> list[tuple[list[str], str, str]]:
    """Patterns as (meaningful words, wording, reason).

    All the words have to agree. The Guidelines teach one to tell apart
    sentences differing in a single word: „ochrana buněk před oxidativním
    stresem“ is approved, „před oxidativním poškozením“ is prohibited.
    """
    patterns = []
    for row in PROHIBITED:
        words = [
            word for word in re.findall(r"[a-zá-ž]+", row["prohibited"].lower())
            if len(word) > 3 and word not in _SKIP_IN_PATTERN
        ]
        if words:
            patterns.append((words, row["prohibited"].strip(), row["reason"].strip()))
    return patterns


_PROHIBITED_PATTERNS = _prohibited_patterns()


def _collect_support(substances: list[str] | None) -> list[tuple[str, str, str]]:
    """Support as triples (substance, wording, plant part).

    An empty substance means the name is not to be looked for in the sentence:
    for nutrition claims because they are tied to no substance, for on-hold
    ones because the caller asked for them — and a plant goes by several names
    („ašvaganda“ = „indický ženšen“ = vitánie).
    """
    support: list[tuple[str, str, str]] = [
        (row[1], _norm(row[2]), "") for row in APPROVED_HEALTH if len(row) > 2
    ]
    support += [("", _norm(row[1]), "") for row in APPROVED_NUTRITION if len(row) > 1]

    for substance in substances or []:
        needle = _norm(substance)
        for row in ON_HOLD:
            if needle in _norm(row["lat"]) or needle in _norm(row["cz"]):
                support.append((
                    "",
                    _norm(row["claim"]),
                    plant_part(f"{row['lat']} {row['cz']}"),
                ))
    return support


def check(description: str, substances: list[str] | None = None) -> list[str]:
    """Findings in the description. An empty list means it passed.

    `substances` widen the set of admissible support by the on-hold claims for
    particular plants — without them only approved claims get through.

    A word is reported only when the claim the sentence leans on does not use
    it too. Approved wordings themselves say „zvyšuje“ (creatine, vitamin C)
    and „zlepšuje“ (lactase), „plynatost“ stands in the approved claim for
    activated charcoal, and „DNA“ in the zinc claim matches the risky word
    „dna“.
    """
    findings: list[str] = []
    support = _collect_support(substances)
    reported: set[str] = set()

    for sentence in re.split(r"(?<=[.!?])\s+", description):
        normalised = _norm(sentence)
        stems = _stems(sentence)

        supporting = [
            (wording, part) for claim_substance, wording, part in support
            if _mentions_substance(sentence, claim_substance) and _supports(wording, normalised)
        ]

        def _report(word: str, message: str, supporting=supporting) -> None:
            if word in reported:
                return
            if any(_contains(_stems(w), w, word) for w, _ in supporting):
                return
            reported.add(word)
            findings.append(message)

        # Annex 5 carries both „nemoc“ and „Alzheimerova nemoc“. Both would hit
        # the same sentence, so only the more specific match is reported.
        hits = [word for word in RISK_WORDS if _contains(stems, normalised, word)]
        for word in hits:
            if any(other != word and _contains_word(other, word) for other in hits):
                continue
            _report(word, f"rizikové (léčebné) slovo: „{word}“")

        for verb in AMPLIFYING_VERBS:
            if _contains(stems, normalised, verb):
                _report(
                    verb,
                    f"zesilující sloveso: „{verb}“ – bude silnější než schválené znění",
                )

        for symptom in SYMPTOMS:
            if _contains(stems, normalised, symptom):
                _report(symptom, f"symptom mimo schválená tvrzení: „{symptom}“")

        for words, wording, reason in _PROHIBITED_PATTERNS:
            if wording not in reported and all(
                _contains(stems, normalised, word) for word in words
            ):
                reported.add(wording)
                findings.append(f"nepřípustné tvrzení podle Vodítek: „{wording}“ – {reason}")

        # a single vocabulary word does not make a sentence about health —
        # „ideální během tréninku“ hits „během“ and nothing more, so at least
        # two are required
        if sum(1 for word in _VOCABULARY if word in stems) < VOCABULARY_THRESHOLD:
            continue

        # and without a stated relation to an effect it is no claim, only a description
        if not any(_contains(stems, normalised, word) for word in RELATIONAL + AMPLIFYING_VERBS):
            continue

        parts = [part for _, part in supporting]
        if not parts:
            findings.append(f"zdravotní téma bez opory v seznamu: „{sentence.strip()[:70]}…“")
        elif all(parts):
            listed = ", ".join(sorted(set(parts)))
            findings.append(
                f"opora je vedená jen pro část rostliny ({listed}) – ověřte, "
                f"že ji produkt obsahuje: „{sentence.strip()[:70]}…“"
            )

    return findings
