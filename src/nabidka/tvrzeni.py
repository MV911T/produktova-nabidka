"""Kontrola krátkých popisů proti Vodítkům SZPI 2024.

Podle čl. 10 nařízení (ES) č. 1924/2006 musí být každé tvrzení spojující
potravinu se zdravím na schváleném seznamu. Modul hledá pět druhů prohřešků:

1. riziková (léčebná) slova – příloha 5 Vodítek
2. slovesa, která tvrzení zesilují nad schválené znění – příloha 6
3. znění, která Vodítka vypisují jako nepřípustná, včetně důvodu
4. věty se zdravotním tématem bez opory ve schváleném, on-hold
   nebo výživovém tvrzení
5. věty, jejichž jediná opora je vedená pro jinou část rostliny,
   než jakou výrobek obsahuje

Posuzují se jen věty, které účinek vyslovují: samotná zmínka o zdraví
tvrzením není. Opora navíc musí platit pro touž látku – znění opsané
od jiné živiny oporou není.

Slovo se hlásí jen tehdy, když ho nemá i tvrzení, o které se věta opírá.
Schválená znění totiž sama používají „zvyšuje“ (kreatin, vitamín C)
i „zlepšuje“ (laktáza), „plynatost“ stojí ve schváleném tvrzení pro
aktivní uhlí a „DNA“ v tvrzení o zinku se bez diakritiky shoduje
s rizikovým slovem „dna“.

Nenahrazuje posouzení člověkem, jen upozorňuje na nejčastější chyby.
"""

from __future__ import annotations

import json
import re
import unicodedata
from pathlib import Path

_DATA = Path(__file__).parent / "data"


def _nacti(nazev: str):
    return json.loads((_DATA / nazev).read_text("utf-8"))


RIZIKOVA_SLOVA: list[str] = _nacti("rizikova_slova.json")
NEPRIPUSTNE: list[dict] = _nacti("nepripustne.json")
SCHVALENA_ZT: list[list[str]] = _nacti("schvalena_zt.json")
SCHVALENA_VT: list[list[str]] = _nacti("schvalena_vt.json")
ON_HOLD: list[dict] = _nacti("onhold.json")

ZESILUJICI = [
    "zlepšuje", "posiluje", "stimuluje", "zvyšuje", "urychluje", "obnovuje",
    "odstraňuje", "potlačuje", "zabraňuje", "předchází", "chrání před",
    "léčí", "vyléčí", "zbaví", "uleví", "řeší", "napravuje", "hraje klíčovou roli",
]
"""Slovesa, kterými se schválené „přispívá k…“ mění na silnější tvrzení."""

SYMPTOMY = [
    "křeče", "křeč", "nespavost", "neklidný spánek", "nedostatek", "deficit",
    "bolest", "nadýmání", "nafouklé břicho", "vypadávání", "lámavost",
    "podrážděnost", "výkyvy nálad", "vyčerpaný", "unavený",
]
"""Symptomy, které schválená tvrzení neznají – naznačují léčebný účinek.

Pozor: tenhle výčet je vlastní, ve Vodítkách takový seznam není.
"""

PRAH_SLOVNIKU = 2
"""Kolik slov ze zdravotního slovníku musí věta obsahovat, než se posuzuje."""

VZTAHOVA = [
    "přispívá", "přispívají", "podílí", "pomáhá", "pomáhají", "podporuje",
    "podporují", "napomáhá", "prospívá", "působí", "udržuje", "udržují",
    "ovlivňuje", "snižuje", "snižují", "zmírňuje", "doplňuje", "dodává",
    "je potřebný", "je nezbytný", "má vliv", "účinek", "účinky",
]
"""Slovesa, kterými věta spojuje látku se zdravím.

Zdravotní tvrzení podle čl. 2 nařízení 1924/2006 musí vztah mezi potravinou
a zdravím vyslovit. Věta „Vysoké koncentrace glycinu se nacházejí ve svalech“
žádný účinek netvrdí – popisuje, kde se látka v těle vyskytuje.
"""

_KONCOVKY = {
    "", "a", "e", "i", "y", "u", "o", "ě", "í", "ý", "á", "é", "ů", "ou", "em",
    "im", "am", "om", "mi", "ch", "ech", "ich", "ám", "ým", "ých", "ové", "ový",
    "ová", "ně", "ný", "ná", "né", "ni", "te", "l", "la", "lo", "ly", "t",
    "ti", "m", "š", "me", "s", "ce", "ci", "ku", "ky", "ka", "ek",
}
"""Koncovky, o které se hledané slovo smí lišit.

Delší zbytek znamená jiné slovo – „lecitinu“ není tvar slova „léčit“.
"""

_NEVYZNAMNE = {
    "a", "i", "k", "o", "u", "v", "s", "z", "na", "po", "do", "ke", "se", "je",
    "the", "of", "and", "to", "in", "for", "prispiva", "podili", "prispiv",
    "normalni", "normalnimu", "normalnich", "udrzeni", "stavu", "funkce", "-",
    # názvy živin a složek – popis složení není zdravotní tvrzení
    "obsah", "obsahu", "obsahuji", "obsahuje", "obsahem", "zdrojem", "davce", "davku",
    "aminokyselin", "aminokyselina", "aminokyseliny", "bilkovin", "bilkoviny",
    "sacharid", "sacharidy", "vlaknina", "vlakniny", "vitamin", "vitaminu",
    "mineral", "mineraly", "extrakt", "extraktu", "polysacharid", "polysacharidu",
    # slova, která se do slovníku dostala ze znění tvrzení, ale sama o zdraví
    # nevypovídají – „ideální během tréninku“ zdravotní tvrzení není
    "behem", "vysoce", "komfort", "zdroj", "latky", "kazdodenni", "trenink",
    "treninku", "organismu", "organismus", "ideal", "idealni", "vyzivove",
    "vyzivovy", "doplnek", "denni", "dennim", "davka", "forme", "forma",
    "slozeni", "produkt", "pripravek", "vyrobek", "kvality", "kvalita",
    "prirodni", "celkove", "dalsi",
}


def _norm(text: str) -> str:
    """Malá písmena bez diakritiky."""
    text = unicodedata.normalize("NFD", str(text).lower())
    return "".join(znak for znak in text if unicodedata.category(znak) != "Mn")


def _obsahuje_slovo(text: str, hledane: str) -> bool:
    """Vyskytuje se slovo v textu jako samostatné slovo, i v jiném pádu?"""
    cil = _norm(hledane)
    if " " in cil:
        return cil in _norm(text)

    return any(
        token.startswith(cil) and token[len(cil):] in _KONCOVKY
        for token in re.findall(r"[a-zá-ž]+", _norm(text))
    )


CASTI_ROSTLINY = {
    "kořen": ("root", "kořen"),
    "list": ("leaf", "leaves", "list"),
    "semeno": ("seed", "seeds", "semeno", "semena"),
    "plod": ("fruit", "plod"),
    "květ": ("flower", "květ"),
    "slupka": ("husk", "slupka"),
    "nať": ("herb", "nať"),
}
"""Části rostliny, na které bývá on-hold tvrzení vázané.

Čtvrtina záznamů některou uvádí a pak platí jen pro ni: „Duševní zdraví,
stres & spánek“ je vedené pro kořen vitánie, ne pro extrakt z kořene i listů.
"""


def cast_rostliny(text: str) -> str:
    """Část rostliny uvedená v záznamu, jinak prázdný řetězec."""
    for nazev, slova in CASTI_ROSTLINY.items():
        if any(_obsahuje_slovo(text, slovo) for slovo in slova):
            return nazev
    return ""


_VYPLN = {
    "prispiva", "prispivaji", "prispiv", "podili", "pomaha", "pomahaji",
    "pomahat", "udrzeni", "udrzet", "udrzovat", "udrzovani", "normalni",
    "normalniho", "normalnimu", "normalnich", "normalnim", "funkce", "funkci",
    "funkcim", "cinnost", "cinnosti", "stavu", "potrebna", "potrebny",
}
"""Spojovací slova, kterými je psané skoro každé schválené tvrzení.

Bez nich by „Ašvaganda přispívá k normální funkci jater“ vyšla jako
podepřená tvrzením o cholinu – shodly by se na „přispívá“ a „normální“.
"""


_SPOJKY = {
    "nebo", "anebo", "popr", "pripadne", "jine", "jiny", "ostatni", "vcetne",
    "kategorie", "potravin", "potraviny", "potravina", "latka", "latky",
}
"""Slova, která v názvu látky nesou jen skladbu věty, ne její totožnost."""


def _zminuje_latku(veta: str, latka: str) -> bool:
    """Mluví věta o té látce, pro kterou je tvrzení schválené?

    Bez téhle podmínky by „Kolagen přispívá k normální funkci imunitního
    systému“ vyšla jako podepřená tvrzením o vitamínu C – shodly by se na
    popisu účinku, ačkoli je schválený pro jinou látku.

    Výživová tvrzení se k látce nevážou, u nich se nezkoumá.
    """
    if not latka:
        return True

    # záměrně se nefiltruje přes _NEVYZNAMNE: „vitamin“ je tam kvůli slovníku,
    # jenže z názvu „vitamin A“ by pak nezbylo nic a kontrola by se přeskočila
    nazvy = [
        slovo for slovo in re.findall(r"[a-zá-ž0-9]+", _norm(latka))
        if len(slovo) > 2 and slovo not in _SPOJKY
    ]
    return not nazvy or any(_obsahuje_slovo(veta, nazev) for nazev in nazvy)


def _kmeny(text: str) -> set[str]:
    """Kmeny slov věty – co všechno mohlo být hledaným slovem.

    Předpočítá se jednou za větu, aby se 230 rizikových slov nehledalo
    každé zvlášť procházením textu.
    """
    kmeny: set[str] = set()
    for token in re.findall(r"[a-zá-ž]+", _norm(text)):
        for koncovka in _KONCOVKY:
            if not koncovka:
                kmeny.add(token)
            elif token.endswith(koncovka):
                kmeny.add(token[: -len(koncovka)])
    return kmeny


def _obsahuje(kmeny: set[str], n_text: str, hledane: str) -> bool:
    """Totéž co `_obsahuje_slovo`, jen nad předpočítanými kmeny."""
    cil = _norm(hledane)
    return cil in n_text if " " in cil else cil in kmeny


def _podepira(opora: str, n_veta: str) -> bool:
    """Opírá se věta o tohle tvrzení?

    Rozhodují jen slova nesoucí význam a musí se shodnout dvě, aby náhodné
    setkání jednoho slova za oporu neplatilo. Krátká on-hold tvrzení jako
    „Antioxidant“ nebo „Normální trávení“ ale víc než jedno významové slovo
    nemají – u nich stačí to jediné, jinak by nemohla podepřít nic.
    """
    vyznamova = [
        slovo for slovo in opora.split()
        if len(slovo) > 4 and slovo not in _VYPLN
    ]
    if not vyznamova:
        return False

    prah = min(2, len(vyznamova))
    return sum(1 for slovo in vyznamova if slovo in n_veta) >= prah


def tvrzeni_pro(latka: str, limit: int = 15) -> dict[str, list[str]]:
    """Schválená a on-hold tvrzení dostupná pro danou látku."""
    hledane = _norm(latka)

    schvalena = [
        radek[2] for radek in SCHVALENA_ZT
        if len(radek) > 2 and hledane in _norm(radek[1])
    ]
    onhold = [
        f"{radek['cz']} → {radek['tvrzeni']}" for radek in ON_HOLD
        if hledane in _norm(radek["lat"]) or hledane in _norm(radek["cz"])
    ]
    return {"schvalena": schvalena[:limit], "on_hold": onhold[:limit]}


def _zdravotni_slovnik() -> set[str]:
    """Slova z textů tvrzení – signál, že věta mluví o zdraví.

    Názvy látek a rostlin se vynechávají: zmínka složení tvrzením není.
    """
    slova: set[str] = set()
    for radek in SCHVALENA_ZT:
        if len(radek) > 2:
            slova.update(_norm(radek[2]).split())
    for radek in ON_HOLD:
        slova.update(_norm(radek["tvrzeni"]).split())

    nazvy: set[str] = set()
    for radek in SCHVALENA_ZT:
        if len(radek) > 1:
            nazvy.update(_norm(radek[1]).split())
    for radek in ON_HOLD:
        nazvy.update(_norm(radek["cz"]).split())
        nazvy.update(_norm(radek["lat"]).split())

    return {
        slovo for slovo in slova
        if len(slovo) > 4 and slovo not in _NEVYZNAMNE and slovo not in nazvy
    }


_SLOVNIK = _zdravotni_slovnik()


_VYNECHAT_VE_VZORU = {
    "díky", "jako", "např", "tedy", "tím", "této", "která", "které", "který",
    "jehož", "jejíž", "jejichž", "jsou", "aby", "pro", "vaše", "vašich",
    "vašeho", "vašim", "přičemž", "další", "dalšími", "například",
}
"""Slova, která ve vzoru nepřípustného tvrzení nenesou jeho podstatu."""


def _vzory_nepripustnych() -> list[tuple[list[str], str, str]]:
    """Vzory jako (významová slova, znění, důvod).

    Shodovat se musí všechna slova. Vodítka totiž učí rozlišovat věty lišící
    se jediným slovem: „ochrana buněk před oxidativním stresem“ je schválená,
    „před oxidativním poškozením“ nepřípustná.
    """
    vzory = []
    for radek in NEPRIPUSTNE:
        slova = [
            slovo for slovo in re.findall(r"[a-zá-ž]+", radek["nepripustne"].lower())
            if len(slovo) > 3 and slovo not in _VYNECHAT_VE_VZORU
        ]
        if slova:
            vzory.append((slova, radek["nepripustne"].strip(), radek["duvod"].strip()))
    return vzory


_VZORY_NEPRIPUSTNYCH = _vzory_nepripustnych()


def _sestav_opory(latky: list[str] | None) -> list[tuple[str, str, str]]:
    """Opory jako trojice (látka, znění, část rostliny).

    Prázdná látka znamená, že se název ve větě hledat nemá: u výživových
    tvrzení proto, že se k žádné látce nevážou, u on-hold proto, že si je
    vyžádal volající – a rostlina má jmen víc („ašvaganda“ = „indický
    ženšen“ = vitánie).
    """
    opory: list[tuple[str, str, str]] = [
        (radek[1], _norm(radek[2]), "") for radek in SCHVALENA_ZT if len(radek) > 2
    ]
    opory += [("", _norm(radek[1]), "") for radek in SCHVALENA_VT if len(radek) > 1]

    for latka in latky or []:
        hledane = _norm(latka)
        for radek in ON_HOLD:
            if hledane in _norm(radek["lat"]) or hledane in _norm(radek["cz"]):
                opory.append((
                    "",
                    _norm(radek["tvrzeni"]),
                    cast_rostliny(f"{radek['lat']} {radek['cz']}"),
                ))
    return opory


def zkontroluj(popis: str, latky: list[str] | None = None) -> list[str]:
    """Nálezy v popisu. Prázdný seznam znamená, že popis prošel.

    `latky` rozšiřují seznam přípustných opor o on-hold tvrzení pro
    konkrétní rostliny – bez nich projdou jen schválená tvrzení.

    Slovo se hlásí jen tehdy, když ho nemá i tvrzení, o které se věta
    opírá. Schválená znění totiž sama používají „zvyšuje“ (kreatin,
    vitamín C) i „zlepšuje“ (laktáza), „plynatost“ stojí ve schváleném
    tvrzení pro aktivní uhlí a „DNA“ v tvrzení o zinku se shoduje
    s rizikovým slovem „dna“.
    """
    nalezy: list[str] = []
    opory = _sestav_opory(latky)
    ohlasene: set[str] = set()

    for veta in re.split(r"(?<=[.!?])\s+", popis):
        n_veta = _norm(veta)
        kmeny = _kmeny(veta)

        podpurne = [
            (znění, cast) for latka_opory, znění, cast in opory
            if _zminuje_latku(veta, latka_opory) and _podepira(znění, n_veta)
        ]

        def _ohlas(slovo: str, hlaska: str, podpurne=podpurne) -> None:
            if slovo in ohlasene:
                return
            if any(_obsahuje(_kmeny(o), o, slovo) for o, _ in podpurne):
                return
            ohlasene.add(slovo)
            nalezy.append(hlaska)

        for slovo in RIZIKOVA_SLOVA:
            if _obsahuje(kmeny, n_veta, slovo):
                _ohlas(slovo, f"rizikové (léčebné) slovo: „{slovo}“")

        for sloveso in ZESILUJICI:
            if _obsahuje(kmeny, n_veta, sloveso):
                _ohlas(
                    sloveso,
                    f"zesilující sloveso: „{sloveso}“ – bude silnější než schválené znění",
                )

        for symptom in SYMPTOMY:
            if _obsahuje(kmeny, n_veta, symptom):
                _ohlas(symptom, f"symptom mimo schválená tvrzení: „{symptom}“")

        for slova, zneni, duvod in _VZORY_NEPRIPUSTNYCH:
            if all(_obsahuje(kmeny, n_veta, slovo) for slovo in slova):
                if zneni not in ohlasene:
                    ohlasene.add(zneni)
                    nalezy.append(
                        f"nepřípustné tvrzení podle Vodítek: „{zneni}“ – {duvod}"
                    )

        # jediné slovo ze slovníku větu o zdraví nedělá – „ideální během
        # tréninku“ trefí „během“ a nic víc, proto se žádají aspoň dvě
        if sum(1 for slovo in _SLOVNIK if slovo in kmeny) < PRAH_SLOVNIKU:
            continue

        # a bez vysloveného vztahu k účinku nejde o tvrzení, jen o popis
        if not any(_obsahuje(kmeny, n_veta, slovo) for slovo in VZTAHOVA + ZESILUJICI):
            continue

        casti = [cast for _, cast in podpurne]
        if not casti:
            nalezy.append(f"zdravotní téma bez opory v seznamu: „{veta.strip()[:70]}…“")
        elif all(casti):
            vypis = ", ".join(sorted(set(casti)))
            nalezy.append(
                f"opora je vedená jen pro část rostliny ({vypis}) – ověřte, "
                f"že ji produkt obsahuje: „{veta.strip()[:70]}…“"
            )

    return nalezy
