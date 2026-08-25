# TODO

**11 zbývá · 15 hotovo · 3 vyřazeno**

Poslední změna: 25. 8. 2026

---

## Zbývá

### Dokončení nabídky

**1. Pustit zbylé tři kategorie**
Doplňky stravy (364 produktů) jsou hotové. Muži a ženy jsou projeté a ověřené
(viz 14), ale výstup zatím nikde uložený není. Chybí:

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

**7. Ověřit hook na TODO**
Zapsaný je, příkaz otestovaný, ale nevystřelil — Claude Code načítá hooky
při startu session. Otevřít jednou `/hooks` nebo restartovat.

### Otevřené otázky

**8. Psyllium — semena vs. slupky**
On-hold tvrzení „normální funkce trávicího traktu a střev“ (ID 2510) je
vedené pro *semena* jitrocele. Náš produkt je z *slupek*. Použili jsme ho.

**9. Ašvaganda Sensoril® — kořen vs. list**
On-hold „duševní zdraví, stres & spánek“ je vázané na *kořen*. Sensoril®
se vyrábí z kořene i listů, stránka to neupřesňuje.

**10. Seznam symptomů je vlastní**
`tvrzeni.SYMPTOMY` (křeče, nespavost, nedostatek…) ve Vodítkách není —
příloha 5 obsahuje nemoci, ne symptomy. Bude potřeba ho doplňovat.

**11. Kontrola má falešné poplachy i mezery**
Párování na podřetězec bylo nahrazeno tokenovým s českými koncovkami,
ale přesnost je omezená. Nástroj posouzení člověkem nenahrazuje.

---

## Hotovo

### Sběr dat

**12.** Parsování pěti polí z produktové stránky — microdata + `.p-short-description`
**13.** Sběr URL z výpisu kategorie včetně stránkování (`/strana-N/`)
**14.** `category` z nadpisu výpisu — na produktu spolehlivá není
**15.** Přeskakování zrušených produktů — web je přesměruje na kategorii
**16.** Rozpoznání a vyřazení balíčků — tři signály plus ruční seznam
**17.** Běh na kategorii doplňků stravy — 364 produktů, 0 prázdných polí

### Popisy a legislativa

**18.** 14 vlastních popisů pro produkty, u nichž e-shop krátký popis nemá
**19.** Kontrola tvrzení proti Vodítkům SZPI 2024 — tři vrstvy:
riziková léčebná slova, zesilující slovesa, zdravotní téma bez opory
**20.** Vyhledávač schválených a on-hold tvrzení podle látky
**21.** Chybějící popisy v kategoriích muži a ženy — psát se nemusel žádný.
Ze 137 produktů nemá e-shop krátký popis u jediného (Performance Magnesium®)
a ten vlastní popis už má. Žádné prázdné pole, 10 balíčků vyřazeno.

### Projekt

**22.** Repozitář na GitHubu — [MV911T/produktova-nabidka](https://github.com/MV911T/produktova-nabidka)
**23.** Hlášky na stderr místo do JSON výstupu
**24.** Hook, který tenhle seznam vypíše po každé změně souboru v projektu
**25.** Rozdělení do modulů, `pyproject.toml`, CLI, GitHub Actions
**26.** 44 testů bez přístupu na síť, `ruff` bez nálezů

---

## Vyřazeno ze zadání

**27.** Doplňování z databáze prodspec — nahrazeno vlastními popisy
**28.** Cloudový scraper — krátký popis je jen v HTML, JSON-LD ho nemá
**29.** Fallback popisu z detailního textu — dával dávkování, výživové hodnoty
a doslovné „Popis produktu není dostupný“; použitelný byl 2krát z 19
