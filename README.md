# Produktová nabídka

[![testy](https://github.com/MV911T/produktova-nabidka/actions/workflows/testy.yml/badge.svg)](https://github.com/MV911T/produktova-nabidka/actions/workflows/testy.yml)

Stáhne produkty z vybraných kategorií brainmarket.cz a vrátí je jako `list[dict]`
připravený k převodu do JSON. Součástí je kontrola krátkých popisů proti
Vodítkům SZPI k zdravotním a výživovým tvrzením.

## Instalace

```bash
pip install -e .
```

Jedinou závislostí je `requests`, zbytek je standardní knihovna.

## Použití

```python
from nabidka import ziskej_nabidku

produkty = ziskej_nabidku([
    "https://www.brainmarket.cz/brainmax-doplnky-stravy/",
    "https://www.brainmarket.cz/lauf/",
])
```

Z příkazové řádky:

```bash
nabidka https://www.brainmarket.cz/lauf/ > nabidka.json

nabidka --kontrola "text popisu" --latka hořčík
nabidka --tvrzeni hořčík psyllium
```

Průběžné hlášky jdou na stderr, na stdout je čistý JSON.

Když se některou stránku nepodaří stáhnout ani na třetí pokus, je nabídka
neúplná: `ziskej_nabidku()` vyhodí `NeuplnaNabidka` a příkaz skončí kódem 1,
místo aby zkrácený seznam vydával za úplný. Výjimka nese v `nabidka` to, co
se stáhnout povedlo, a v `nestazene` seznam URL, která se vzdala.

```python
from nabidka import NeuplnaNabidka, ziskej_nabidku

try:
    produkty = ziskej_nabidku(["https://www.brainmarket.cz/lauf/"])
except NeuplnaNabidka as chyba:
    produkty = chyba.nabidka        # co se stihlo
    print(chyba.nestazene)          # a co chybí
```

Z příkazové řádky totéž svolí `--dovol-neuplnou`.

## Pole

| Pole | Zdroj |
|---|---|
| `product_name` | poslední prvek drobečkové navigace |
| `product_url` | microdata `url` |
| `short_description` | blok `.p-short-description`, jinak vlastní popis |
| `image_url` | microdata `image` |
| `category` | nadpis výpisu, ze kterého se produkt stahoval |

## Rozvržení

```
src/nabidka/
├── __init__.py     ziskej_nabidku() – hlavní vstupní bod
├── stahovani.py    HTTP a práce s HTML
├── katalog.py      výpisy kategorií a stránkování
├── produkt.py      parsování pěti polí
├── balicky.py      rozpoznání sad
├── tvrzeni.py      kontrola proti Vodítkům SZPI
├── cli.py          příkazová řádka
└── data/           JSON zdroje
nastroje/tabule.py  přehled úkolů z TODO.md
tests/              84 testů, bez přístupu na síť
```

## Na co narazíte v datech

**Kategorie se bere z výpisu, ne z produktu.** Produktová stránka vlastní
kategorii nese: `itemprop="category"` je vyplněná vždy a obsahuje celou cestu.
Použitelná ale není. Končí názvem produktu, takže věcná kategorie je až
předposledním článkem – a ten u části produktů chybí:

| Vzorek 55 produktů z doplňků stravy | |
|---|---|
| cesta `Úvodní stránka > BrainMax® > název` – kategorie žádná | 7 (13 %) |
| věcná kategorie k dispozici | 48 (87 %) |
| kolik různých kategorií to je | 36 |

K tomu je to kategorie, kam produkt patří primárně, ne ta, o kterou jsme
požádali: `FUELIX DRINK` se ve výpisu doplňků stravy hlásí do „Zdravá výživa
a potraviny pro děti“. Kdyby o `category` rozhodovala, nabídka sestavená ze
čtyř kategorií by se roztříštila do desítek hodnot a u 13 % produktů by místo
kategorie stála značka.

Nadpis výpisu je proti tomu vyplněný vždy, drží se toho, oč bylo požádáno,
a při spojení víc kategorií zůstává srozumitelný. Produkt, který patří do
víc kategorií, dostane tu, ve které se objevil první.

**Název produktu je slepený.** `itemprop="name"` obsahuje název, podtitulek
a u variant i nadpisy zákaznických dotazů. Čistý název je posledním prvkem
drobečkové navigace.

**Krátký popis není v microdata.** Je jen v HTML bloku `.p-short-description`,
a bývá do něj přimíchané provozní sdělení („Vážení zákazníci, upozorňujeme…“),
které se odstraňuje.

**Zrušené produkty visí ve výpisu.** Web na jejich URL vrátí přesměrování
na kategorii. Poznají se podle chybějících microdata produktu.

**Balíčky nejsou nijak označené.** V Shoptetu jsou vedené jako běžný produkt.
Rozpoznávají se třemi signály – klíčové slovo v názvu, dva produkty s vlastním
balením v názvu, věta „Tento balíček…“ na stránce – a co jim unikne, je
v ručně odsouhlaseném `data/balicky_rucne.json`.

Znak `+` v názvu má přitom dva významy: složení jedné receptury
(*Hořčík + Vitamín B6*) versus dva samostatné produkty
(*Sleep Magnesium + BrainMax Glycin*).

## Kontrola zdravotních tvrzení

Podle čl. 10 nařízení (ES) č. 1924/2006 musí být každé tvrzení spojující
potravinu se zdravím na schváleném seznamu. Modul `tvrzeni` hlásí:

1. **riziková (léčebná) slova** – příloha 5 Vodítek
2. **zesilující slovesa** – formulace silnější než schválené znění, příloha 6
3. **zdravotní téma bez opory** – věta účinek tvrdí, ale neodpovídá
   žádnému schválenému, on-hold ani výživovému tvrzení
4. **opora jen pro jinou část rostliny** – tvrzení je vedené pro kořen,
   semena či listy; ověřte, že je výrobek opravdu obsahuje

Posuzují se jen věty, které vztah k účinku vyslovují — zmínka o zdraví
sama tvrzením není. Opora musí platit pro touž látku: „Kolagen přispívá
k normální funkci imunitního systému“ se o schválené znění pro vitamín C
opřít nemůže, byť je napsané stejně.

```python
from nabidka import tvrzeni_pro, zkontroluj

zkontroluj("Hořčík posiluje svaly.", ["hořčík"])
# ['zesilující sloveso: „posiluje“ – bude silnější než schválené znění', ...]

tvrzeni_pro("psyllium")["on_hold"]
# ['Jitrocel indický ( psyllium) - semena → Normální funkce trávicího traktu a střev', ...]
```

Zdroj dat: [Vodítka SZPI k problematice zdravotních a výživových tvrzení](https://www.szpi.gov.cz/clanek/voditka-k-problematice-zdravotnich-a-vyzivovych-tvrzeni.aspx),
verze 2024, přílohy převedené do JSON v `src/nabidka/data/`.

### Omezení

Seznam symptomů (`tvrzeni.SYMPTOMY`) je vlastní – ve Vodítkách takový výčet
není. Stejně tak seznam vztahových sloves (`tvrzeni.VZTAHOVA`): tvrzení
naznačené bez slovesa („Pro zdravé klouby“) nástroj minout může.

Na 165 popisech z e-shopu hlásí 26 vět bez opory, 3 zesilující slovesa,
2 riziková slova a 2 symptomy. Nástroj posouzení člověkem nenahrazuje,
jen upozorňuje na nejčastější prohřešky.

## Vývoj

```bash
pip install -e ".[dev]"
pytest
ruff check .
```

Stav úkolů vypíše `python3 nastroje/tabule.py`. Totéž po každé iteraci
ukáže `Stop` hook v `~/.claude/settings.json`; repozitář si najde sám
přes `git rev-parse`, takže mu přesun projektu nevadí.

Testy běží proti uloženým výřezům skutečných stránek v `tests/podklady/`,
takže nechodí na síť.
