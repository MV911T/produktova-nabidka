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
tests/              44 testů, bez přístupu na síť
```

## Na co narazíte v datech

**Kategorie není na produktu.** Zhruba třetina produktů má drobečkovou navigaci
jen dvouúrovňovou (`BrainMax® > Název produktu`) – věcnou kategorii web u nich
vůbec nevede. Proto se bere z nadpisu výpisu, ze kterého se produkt stahoval.

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
3. **zdravotní téma bez opory** – věta se dotýká zdraví, ale neodpovídá
   žádnému schválenému, on-hold ani výživovému tvrzení

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
není. Nástroj posouzení člověkem nenahrazuje, jen upozorňuje na nejčastější
prohřešky.

## Vývoj

```bash
pip install -e ".[dev]"
pytest
ruff check .
```

Testy běží proti uloženým výřezům skutečných stránek v `tests/podklady/`,
takže nechodí na síť.
