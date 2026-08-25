# TODO

**8 zbývá · 20 hotovo · 3 vyřazeno**

Poslední změna: 25. 8. 2026

---

## Zbývá

### Dokončení nabídky

**1. Pustit zbylé tři kategorie**
Doplňky stravy (364 produktů) jsou hotové. Muži a ženy jsou projeté a ověřené
(viz 18), LAUF proběhl jako zkouška po opravě 24 — výstup ale zatím nikde
uložený není. Chybí:

| Kategorie | URL | Produktů |
|---|---|---|
| BrainMax pro muže | `/brainmax-men/` | 91 URL → 85 produktů |
| BrainMax pro ženy | `/brainmax-pro-zeny/` | 104 URL → 51 nových |
| LAUF | `/lauf/` | 28 |

```bash
nabidka https://www.brainmarket.cz/brainmax-men/ > muzi.json
```

**2. Spojit výstupy všech čtyř kategorií do jedné nabídky**
Produkt může být ve víc kategoriích zároveň — duplicity i pořadí kategorií
už `ziskej_nabidku()` řeší (viz 27), takže stačí předat všechny čtyři URL
najednou a výstup uložit.

### Opravy

**3. `category` se bere z výpisu, ačkoli produkt vlastní kategorii nese**
README tvrdí, že web věcnou kategorii u produktu nevede, a proto se bere
nadpis výpisu. Vzorek 23 produktů to nepotvrdil: `itemprop="category"` byla
vyplněná u všech 23 a nese celou cestu (`Úvodní stránka > Muži > Doplňky
stravy pro muže`). Dvouúrovňové drobečky měl 1 produkt z 23, ne třetina.
Rozhodnout, který zdroj je správný, a srovnat README s tím, co data ukazují.

### Údržba

**4. Projet celý katalog kontrolou tvrzení**
Zatím prošly kontrolou jen naše vlastní popisy. Popisy stažené z webu
(350 kusů) zkontrolované nejsou — může tam být materiál pro SZPI.

**5. Doplnit ruční seznam balíčků**
`data/balicky_rucne.json` má 51 položek a platí k srpnu 2026. Až e-shop
přidá další sady, heuristika je nemusí zachytit.

### Otevřené otázky

**6. Má výstup nést stabilní identifikátor?**
Stránka vystavuje `sku`, `productID` i `gtin13` (EAN) — ve vzorku 23 z 23.
Zahazujeme je a jediným klíčem záznamu zůstává URL, která se při
přejmenování produktu mění. Zadání ale žádá přesně pět polí a příklad
jich víc neukazuje, takže rozšíření je změna dohodnutého tvaru dat.

**7. Psyllium — semena vs. slupky**
On-hold tvrzení „normální funkce trávicího traktu a střev“ (ID 2510) je
vedené pro *semena* jitrocele. Náš produkt je z *slupek*. Použili jsme ho.

**8. Seznam symptomů je vlastní**
`tvrzeni.SYMPTOMY` (křeče, nespavost, nedostatek…) ve Vodítkách není —
příloha 5 obsahuje nemoci, ne symptomy. Bude potřeba ho doplňovat.
Totéž platí pro `tvrzeni.VZTAHOVA`: tvrzení naznačené bez slovesa
(„Pro zdravé klouby“) kontrola mine.

---

## Hotovo

### Sběr dat

**9.** Parsování pěti polí z produktové stránky — microdata + `.p-short-description`
**10.** Sběr URL z výpisu kategorie včetně stránkování (`/strana-N/`)
**11.** `category` z nadpisu výpisu — na produktu spolehlivá není
**12.** Přeskakování zrušených produktů — web je přesměruje na kategorii
**13.** Rozpoznání a vyřazení balíčků — tři signály plus ruční seznam
**14.** Běh na kategorii doplňků stravy — 364 produktů, 0 prázdných polí

### Popisy a legislativa

**15.** 14 vlastních popisů pro produkty, u nichž e-shop krátký popis nemá
**16.** Kontrola tvrzení proti Vodítkům SZPI 2024 — tři vrstvy:
riziková léčebná slova, zesilující slovesa, zdravotní téma bez opory
**17.** Vyhledávač schválených a on-hold tvrzení podle látky
**18.** Chybějící popisy v kategoriích muži a ženy — psát se nemusel žádný.
Ze 137 produktů nemá e-shop krátký popis u jediného (Performance Magnesium®)
a ten vlastní popis už má. Žádné prázdné pole, 10 balíčků vyřazeno.

### Projekt

**19.** Repozitář na GitHubu — [MV911T/produktova-nabidka](https://github.com/MV911T/produktova-nabidka)
**20.** Hlášky na stderr místo do JSON výstupu
**21.** Rozdělení do modulů, `pyproject.toml`, CLI, GitHub Actions
**22.** 56 testů bez přístupu na síť, `ruff` bez nálezů
**23.** Tabule úkolů po každé iteraci — `nastroje/tabule.py` a `Stop` hook.
Předchozí hook měl natvrdo cestu na původní umístění projektu, a proto
po přesunu nikdy nevystřelil. Nový si repozitář najde přes `git rev-parse`,
takže přesun ani další klon už mu nevadí, a jinde než tady mlčí.
**24.** Neúplná nabídka se pozná. Stahování opakuje pokus u výpadku spojení
a chyb 5xx (4xx ne, ta se opakováním nespraví), a co se ani napotřetí
nestáhne, propadne jako `NeuplnaNabidka` s dosud staženými produkty
a seznamem zbylých URL. CLI zkrácený JSON nevypíše a skončí kódem 1,
dokud nedostane `--dovol-neuplnou`.

**25.** Ašvaganda Sensoril® je z kořene **i listů** — technický list výrobce
(Kerry, majitel značky od převzetí Natreonu) ji vede jako „Premium Ashwagandha
Root & Leaf Extract“ a kombinaci obou částí uvádí jako svou přednost. On-hold
tvrzení 4194 „Duševní zdraví, stres & spánek“ je vázané na *kořen*, takže se
o ně opřít nelze. Popis Antistres komplexu proto stojí na tvrzení 2183
„Duševní zdraví a relaxace“, které část rostliny neomezuje.

**26.** Přesnost kontroly tvrzení. Na 165 popisech z e-shopu spadly
poplachy „bez opory“ z 223 na 26 a našich 14 popisů hlásí jediný nález —
ten věcný. Tři změny: věta se posuzuje, jen když účinek vysloví (samotná
zmínka o zdraví tvrzením není), opora musí platit pro touž látku, a když
je vedená jen pro určitou část rostliny, kontrola to řekne. Dřív prošlo
i „Kolagen přispívá k normální funkci imunitního systému“ — opřelo se
o znění pro vitamín C, protože se shodly na slovech „přispívá“
a „normální“.

**27.** Provozní sdělení zmizí z popisu, ať končí čímkoli. Vzor žádal
tečku, takže věta „Vážení zákazníci, vylepšili jsme složení… v aktivní
formě!“ v datech obou balení Energy Magnesia® zůstávala. Ověřeno na živých
stránkách i pěti testy.

**28.** Každý produkt je v nabídce jednou. E-shop vede `Men Multivitamin®`
ve výpisu i jako `…-kapsli-2`; adresy se liší, shodná je až microdata `url`,
a podle ní se teď duplicita pozná. Kategorie zůstává ta první v pořadí.
Kategorie mužů po opravě vrací 85 produktů místo 86, bez duplicit.

---

## Vyřazeno ze zadání

**29.** Doplňování z databáze prodspec — nahrazeno vlastními popisy
**30.** Cloudový scraper — krátký popis je jen v HTML, JSON-LD ho nemá
**31.** Fallback popisu z detailního textu — dával dávkování, výživové hodnoty
a doslovné „Popis produktu není dostupný“; použitelný byl 2krát z 19
