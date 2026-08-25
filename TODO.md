# TODO

**12 zbývá · 16 hotovo · 3 vyřazeno**

Poslední změna: 25. 8. 2026

---

## Zbývá

### Dokončení nabídky

**1. Pustit zbylé tři kategorie**
Doplňky stravy (364 produktů) jsou hotové. Muži a ženy jsou projeté a ověřené
(viz 22), LAUF proběhl jako zkouška po opravě 28 — výstup ale zatím nikde
uložený není. Chybí:

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

### Opravy

**3. Provozní sdělení se z popisu neodstraní, když končí vykřičníkem**
Vzor `BALAST` v `produkt.py` je `Vážení zákazníci[^.]*\.` — vyžaduje tečku.
Obě balení Energy Magnesia® mají na konci popisu větu „Vážení zákazníci,
vylepšili jsme složení… v aktivní formě!“, která tak v datech zůstává.
Rozšířit ukončovací znak na `[.!?]`.

**4. Duplicita produktu ve výpisu jedné kategorie**
`BrainMax Men Multivitamin®` je v nabídce dvakrát. `videne_url` porovnává
URL z výpisu, jenže dvě různé cesty ve výpisu vedou na tentýž produkt —
teprve microdata `url` je shodné. Deduplikovat až podle `product_url`.

**5. `category` se bere z výpisu, ačkoli produkt vlastní kategorii nese**
README tvrdí, že web věcnou kategorii u produktu nevede, a proto se bere
nadpis výpisu. Vzorek 23 produktů to nepotvrdil: `itemprop="category"` byla
vyplněná u všech 23 a nese celou cestu (`Úvodní stránka > Muži > Doplňky
stravy pro muže`). Dvouúrovňové drobečky měl 1 produkt z 23, ne třetina.
Rozhodnout, který zdroj je správný, a srovnat README s tím, co data ukazují.

### Údržba

**6. Projet celý katalog kontrolou tvrzení**
Zatím prošly kontrolou jen naše vlastní popisy. Popisy stažené z webu
(350 kusů) zkontrolované nejsou — může tam být materiál pro SZPI.

**7. Doplnit ruční seznam balíčků**
`data/balicky_rucne.json` má 51 položek a platí k srpnu 2026. Až e-shop
přidá další sady, heuristika je nemusí zachytit.

### Otevřené otázky

**8. Má výstup nést stabilní identifikátor?**
Stránka vystavuje `sku`, `productID` i `gtin13` (EAN) — ve vzorku 23 z 23.
Zahazujeme je a jediným klíčem záznamu zůstává URL, která se při
přejmenování produktu mění. Zadání ale žádá přesně pět polí a příklad
jich víc neukazuje, takže rozšíření je změna dohodnutého tvaru dat.

**9. Psyllium — semena vs. slupky**
On-hold tvrzení „normální funkce trávicího traktu a střev“ (ID 2510) je
vedené pro *semena* jitrocele. Náš produkt je z *slupek*. Použili jsme ho.

**10. Ašvaganda Sensoril® — kořen vs. list**
On-hold „duševní zdraví, stres & spánek“ je vázané na *kořen*. Sensoril®
se vyrábí z kořene i listů, stránka to neupřesňuje.

**11. Seznam symptomů je vlastní**
`tvrzeni.SYMPTOMY` (křeče, nespavost, nedostatek…) ve Vodítkách není —
příloha 5 obsahuje nemoci, ne symptomy. Bude potřeba ho doplňovat.

**12. Kontrola má falešné poplachy i mezery**
Párování na podřetězec bylo nahrazeno tokenovým s českými koncovkami,
ale přesnost je omezená. Nástroj posouzení člověkem nenahrazuje.

---

## Hotovo

### Sběr dat

**13.** Parsování pěti polí z produktové stránky — microdata + `.p-short-description`
**14.** Sběr URL z výpisu kategorie včetně stránkování (`/strana-N/`)
**15.** `category` z nadpisu výpisu — na produktu spolehlivá není
**16.** Přeskakování zrušených produktů — web je přesměruje na kategorii
**17.** Rozpoznání a vyřazení balíčků — tři signály plus ruční seznam
**18.** Běh na kategorii doplňků stravy — 364 produktů, 0 prázdných polí

### Popisy a legislativa

**19.** 14 vlastních popisů pro produkty, u nichž e-shop krátký popis nemá
**20.** Kontrola tvrzení proti Vodítkům SZPI 2024 — tři vrstvy:
riziková léčebná slova, zesilující slovesa, zdravotní téma bez opory
**21.** Vyhledávač schválených a on-hold tvrzení podle látky
**22.** Chybějící popisy v kategoriích muži a ženy — psát se nemusel žádný.
Ze 137 produktů nemá e-shop krátký popis u jediného (Performance Magnesium®)
a ten vlastní popis už má. Žádné prázdné pole, 10 balíčků vyřazeno.

### Projekt

**23.** Repozitář na GitHubu — [MV911T/produktova-nabidka](https://github.com/MV911T/produktova-nabidka)
**24.** Hlášky na stderr místo do JSON výstupu
**25.** Rozdělení do modulů, `pyproject.toml`, CLI, GitHub Actions
**26.** 56 testů bez přístupu na síť, `ruff` bez nálezů
**27.** Tabule úkolů po každé iteraci — `nastroje/tabule.py` a `Stop` hook.
Předchozí hook měl natvrdo cestu na původní umístění projektu, a proto
po přesunu nikdy nevystřelil. Nový si repozitář najde přes `git rev-parse`,
takže přesun ani další klon už mu nevadí, a jinde než tady mlčí.
**28.** Neúplná nabídka se pozná. Stahování opakuje pokus u výpadku spojení
a chyb 5xx (4xx ne, ta se opakováním nespraví), a co se ani napotřetí
nestáhne, propadne jako `NeuplnaNabidka` s dosud staženými produkty
a seznamem zbylých URL. CLI zkrácený JSON nevypíše a skončí kódem 1,
dokud nedostane `--dovol-neuplnou`.

---

## Vyřazeno ze zadání

**29.** Doplňování z databáze prodspec — nahrazeno vlastními popisy
**30.** Cloudový scraper — krátký popis je jen v HTML, JSON-LD ho nemá
**31.** Fallback popisu z detailního textu — dával dávkování, výživové hodnoty
a doslovné „Popis produktu není dostupný“; použitelný byl 2krát z 19
