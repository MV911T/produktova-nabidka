# TODO

**10 zbývá · 14 hotovo · 3 vyřazeno**

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

### Projekt

**20.** Repozitář na GitHubu — [MV911T/produktova-nabidka](https://github.com/MV911T/produktova-nabidka)
**21.** Hlášky na stderr místo do JSON výstupu
**22.** Hook, který tenhle seznam vypíše po každé změně souboru v projektu
**23.** Rozdělení do modulů, `pyproject.toml`, CLI, GitHub Actions
**24.** 44 testů bez přístupu na síť, `ruff` bez nálezů

---

## Vyřazeno ze zadání

**25.** Doplňování z databáze prodspec — nahrazeno vlastními popisy
**26.** Cloudový scraper — krátký popis je jen v HTML, JSON-LD ho nemá
**27.** Fallback popisu z detailního textu — dával dávkování, výživové hodnoty
a doslovné „Popis produktu není dostupný“; použitelný byl 2krát z 19
