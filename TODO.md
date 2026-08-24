# TODO

**13 hotovo · 6 zbývá · 4 otevřené otázky**

Poslední změna: 24. 8. 2026

---

## Zbývá

### Dokončení nabídky

**1. Pustit zbylé tři kategorie**
Doplňky stravy (364 produktů) jsou hotové. Chybí:

| Kategorie | URL | Produktů |
|---|---|---|
| BrainMax pro muže | `/brainmax-men/` | ~108 |
| BrainMax pro ženy | `/brainmax-pro-zeny/` | ~108 |
| LAUF | `/lauf/` | 28 |

```bash
nabidka https://www.brainmarket.cz/brainmax-men/ > muzi.json
```

**2. Spojit výstupy všech čtyř kategorií do jedné nabídky**
Produkt může být ve víc kategoriích zároveň — `ziskej_nabidku()` už duplicity
řeší přes `videne_url`, takže stačí předat všechny čtyři URL najednou.
Ověřit, že se první kategorie v pořadí propíše do `category`.

**3. Doplnit chybějící popisy v nových kategoriích**
Muži a ženy nebyly zatím projeté — pravděpodobně tam budou další produkty
bez krátkého popisu. Postup: vypsat je, napsat popis, projet `zkontroluj()`,
uložit do `data/popisy.json`.

### Údržba

**4. Projet celý katalog kontrolou tvrzení**
Zatím prošly kontrolou jen naše vlastní popisy. Popisy stažené z webu
(350 kusů) zkontrolované nejsou — může tam být materiál pro SZPI.

**5. Doplnit ruční seznam balíčků**
`data/balicky_rucne.json` má 51 položek a platí k srpnu 2026. Až e-shop
přidá další sady, heuristika je nemusí zachytit.

**6. Ověřit hook na TODO**
Zapsaný je, příkaz otestovaný, ale nevystřelil — Claude Code načítá hooky
při startu session. Otevřít jednou `/hooks` nebo restartovat.

---

## Hotovo

### Sběr dat

**7.** Parsování pěti polí z produktové stránky — microdata + `.p-short-description`
**8.** Sběr URL z výpisu kategorie včetně stránkování (`/strana-N/`)
**9.** `category` z nadpisu výpisu — na produktu spolehlivá není
**10.** Přeskakování zrušených produktů — web je přesměruje na kategorii
**11.** Rozpoznání a vyřazení balíčků — tři signály plus ruční seznam
**12.** Běh na kategorii doplňků stravy — 364 produktů, 0 prázdných polí

### Popisy a legislativa

**13.** 14 vlastních popisů pro produkty, u nichž e-shop krátký popis nemá
**14.** Kontrola tvrzení proti Vodítkům SZPI 2024 — tři vrstvy:
riziková léčebná slova, zesilující slovesa, zdravotní téma bez opory
**15.** Vyhledávač schválených a on-hold tvrzení podle látky

### Projekt

**16.** Repozitář na GitHubu — [MV911T/produktova-nabidka](https://github.com/MV911T/produktova-nabidka)
**17.** Hlášky na stderr místo do JSON výstupu
**18.** Hook, který tenhle seznam vypíše po každé změně souboru v projektu
**19.** Rozdělení do modulů, `pyproject.toml`, CLI, GitHub Actions
**20.** 44 testů bez přístupu na síť, `ruff` bez nálezů

---

## Otevřené otázky

**21. Psyllium — semena vs. slupky**
On-hold tvrzení „normální funkce trávicího traktu a střev“ (ID 2510) je
vedené pro *semena* jitrocele. Náš produkt je z *slupek*. Použili jsme ho.

**22. Ašvaganda Sensoril® — kořen vs. list**
On-hold „duševní zdraví, stres & spánek“ je vázané na *kořen*. Sensoril®
se vyrábí z kořene i listů, stránka to neupřesňuje.

**23. Seznam symptomů je vlastní**
`tvrzeni.SYMPTOMY` (křeče, nespavost, nedostatek…) ve Vodítkách není —
příloha 5 obsahuje nemoci, ne symptomy. Bude potřeba ho doplňovat.

**24. Kontrola má falešné poplachy i mezery**
Párování na podřetězec bylo nahrazeno tokenovým s českými koncovkami,
ale přesnost je omezená. Nástroj posouzení člověkem nenahrazuje.

---

## Vyřazeno ze zadání

**25.** Doplňování z databáze prodspec — nahrazeno vlastními popisy
**26.** Cloudový scraper — krátký popis je jen v HTML, JSON-LD ho nemá
**27.** Fallback popisu z detailního textu — dával dávkování, výživové hodnoty
a doslovné „Popis produktu není dostupný“; použitelný byl 2krát z 19
