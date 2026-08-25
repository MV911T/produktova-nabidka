# TODO

**10 zbývá · 15 hotovo · 3 vyřazeno**

Poslední změna: 25. 8. 2026

---

## Zbývá

### Dokončení nabídky

**1. Pustit zbylé tři kategorie**
Doplňky stravy (364 produktů) jsou hotové. Muži a ženy jsou projeté a ověřené
(viz 20), ale výstup zatím nikde uložený není. Chybí:

| Kategorie | URL | Produktů |
|---|---|---|
| BrainMax pro muže | `/brainmax-men/` | 91 URL → 86 produktů |
| BrainMax pro ženy | `/brainmax-pro-zeny/` | 104 URL → 51 nových |
| LAUF | `/lauf/` | 28 |

```bash
nabidka https://www.brainmarket.cz/brainmax-men/ > muzi.json
```

**2. Spojit výstupy všech čtyř kategorií do jedné nabídky**
Produkt může být ve víc kategoriích zároveň — `ziskej_nabidku()` už duplicity
řeší přes `videne_url`, takže stačí předat všechny čtyři URL najednou.
Ověřit, že se první kategorie v pořadí propíše do `category`.

### Opravy nalezené při běhu na muže a ženy

**3. Provozní sdělení se z popisu neodstraní, když končí vykřičníkem**
Vzor `BALAST` v `produkt.py` je `Vážení zákazníci[^.]*\.` — vyžaduje tečku.
Obě balení Energy Magnesia® mají na konci popisu větu „Vážení zákazníci,
vylepšili jsme složení… v aktivní formě!“, která tak v datech zůstává.
Rozšířit ukončovací znak na `[.!?]`.

**4. Duplicita produktu ve výpisu jedné kategorie**
`BrainMax Men Multivitamin®` je v nabídce dvakrát. `videne_url` porovnává
URL z výpisu, jenže dvě různé cesty ve výpisu vedou na tentýž produkt —
teprve microdata `url` je shodné. Deduplikovat až podle `product_url`.

### Údržba

**5. Projet celý katalog kontrolou tvrzení**
Zatím prošly kontrolou jen naše vlastní popisy. Popisy stažené z webu
(350 kusů) zkontrolované nejsou — může tam být materiál pro SZPI.

**6. Doplnit ruční seznam balíčků**
`data/balicky_rucne.json` má 51 položek a platí k srpnu 2026. Až e-shop
přidá další sady, heuristika je nemusí zachytit.

### Otevřené otázky

**7. Psyllium — semena vs. slupky**
On-hold tvrzení „normální funkce trávicího traktu a střev“ (ID 2510) je
vedené pro *semena* jitrocele. Náš produkt je z *slupek*. Použili jsme ho.

**8. Ašvaganda Sensoril® — kořen vs. list**
On-hold „duševní zdraví, stres & spánek“ je vázané na *kořen*. Sensoril®
se vyrábí z kořene i listů, stránka to neupřesňuje.

**9. Seznam symptomů je vlastní**
`tvrzeni.SYMPTOMY` (křeče, nespavost, nedostatek…) ve Vodítkách není —
příloha 5 obsahuje nemoci, ne symptomy. Bude potřeba ho doplňovat.

**10. Kontrola má falešné poplachy i mezery**
Párování na podřetězec bylo nahrazeno tokenovým s českými koncovkami,
ale přesnost je omezená. Nástroj posouzení člověkem nenahrazuje.

---

## Hotovo

### Sběr dat

**11.** Parsování pěti polí z produktové stránky — microdata + `.p-short-description`
**12.** Sběr URL z výpisu kategorie včetně stránkování (`/strana-N/`)
**13.** `category` z nadpisu výpisu — na produktu spolehlivá není
**14.** Přeskakování zrušených produktů — web je přesměruje na kategorii
**15.** Rozpoznání a vyřazení balíčků — tři signály plus ruční seznam
**16.** Běh na kategorii doplňků stravy — 364 produktů, 0 prázdných polí

### Popisy a legislativa

**17.** 14 vlastních popisů pro produkty, u nichž e-shop krátký popis nemá
**18.** Kontrola tvrzení proti Vodítkům SZPI 2024 — tři vrstvy:
riziková léčebná slova, zesilující slovesa, zdravotní téma bez opory
**19.** Vyhledávač schválených a on-hold tvrzení podle látky
**20.** Chybějící popisy v kategoriích muži a ženy — psát se nemusel žádný.
Ze 137 produktů nemá e-shop krátký popis u jediného (Performance Magnesium®)
a ten vlastní popis už má. Žádné prázdné pole, 10 balíčků vyřazeno.

### Projekt

**21.** Repozitář na GitHubu — [MV911T/produktova-nabidka](https://github.com/MV911T/produktova-nabidka)
**22.** Hlášky na stderr místo do JSON výstupu
**23.** Rozdělení do modulů, `pyproject.toml`, CLI, GitHub Actions
**24.** 50 testů bez přístupu na síť, `ruff` bez nálezů
**25.** Tabule úkolů po každé iteraci — `nastroje/tabule.py` a `Stop` hook.
Předchozí hook měl natvrdo cestu na původní umístění projektu, a proto
po přesunu nikdy nevystřelil. Nový si repozitář najde přes `git rev-parse`,
takže přesun ani další klon už mu nevadí, a jinde než tady mlčí.

---

## Vyřazeno ze zadání

**26.** Doplňování z databáze prodspec — nahrazeno vlastními popisy
**27.** Cloudový scraper — krátký popis je jen v HTML, JSON-LD ho nemá
**28.** Fallback popisu z detailního textu — dával dávkování, výživové hodnoty
a doslovné „Popis produktu není dostupný“; použitelný byl 2krát z 19
