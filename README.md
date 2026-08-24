# Produktová nabídka

Stáhne produkty z vybraných kategorií brainmarket.cz a vrátí je jako `list[dict]`
připravený k převodu do JSON.

## Pole

| Pole | Zdroj |
|---|---|
| `product_name` | poslední prvek drobečkové navigace (bez podtitulků) |
| `product_url` | microdata `url` |
| `short_description` | blok `.p-short-description`, jinak vlastní popis z `popisy.json` |
| `image_url` | microdata `image` |
| `category` | nadpis výpisu, ze kterého se produkt stahoval |

## Použití

```python
from nabidka import ziskej_nabidku

produkty = ziskej_nabidku([
    "https://www.brainmarket.cz/brainmax-doplnky-stravy/",
    "https://www.brainmarket.cz/lauf/",
])
```

Nebo z příkazové řádky:

```bash
python3 nabidka.py https://www.brainmarket.cz/lauf/ > nabidka.json
```

Vyžaduje `requests`, zbytek je standardní knihovna.

## Co skript vyřazuje

- **Zrušené produkty** – web je přesměruje na kategorii, produktová data pak
  na stránce chybí.
- **Balíčky a sady** – e-shop je nijak neoznačuje, proto se rozpoznávají třemi
  nezávislými signály: klíčové slovo v názvu, dva produkty s vlastním balením
  v názvu, a věta „Tento balíček…“ na stránce. Co těmto signálům unikne, je
  v ručně odsouhlaseném seznamu `balicky_rucne.json`.

## Proč `category` nepochází z produktu

Zhruba třetina produktů má drobečkovou navigaci jen dvouúrovňovou
(`BrainMax® > Název produktu`) – věcnou kategorii web u nich vůbec nevede.
Kategorie se proto bere z nadpisu výpisu, ze kterého se produkt stahoval.

## Vlastní popisy

Část produktů nemá na webu krátký popis. Pro ty jsou v `popisy.json` ručně
napsané texty. Všechny prošly kontrolou v `kontrola.py`.

## Kontrola zdravotních tvrzení

`kontrola.py` prověřuje popis proti Vodítkům SZPI 2024 ve třech vrstvách:

1. **riziková (léčebná) slova** – příloha 5
2. **zesilující slovesa** – formulace silnější než schválené znění, příloha 6
3. **zdravotní téma bez opory** – věta se dotýká zdraví, ale neodpovídá
   žádnému schválenému, on-hold ani výživovému tvrzení

```bash
python3 kontrola.py "text popisu" hořčík
python3 tvrzeni.py hořčík psyllium     # jaká tvrzení jsou pro látku dostupná
```

Zdroj dat: [Vodítka SZPI k problematice zdravotních a výživových tvrzení](https://www.szpi.gov.cz/clanek/voditka-k-problematice-zdravotnich-a-vyzivovych-tvrzeni.aspx),
verze 2024. Přílohy jsou převedené do JSON v kořeni repozitáře.

### Omezení

Seznam symptomů v `kontrola.py` (`SYMPTOMY`) je vlastní – ve Vodítkách takový
výčet není. Nástroj kontrolu člověkem nenahrazuje, jen upozorňuje na nejčastější
prohřešky.
