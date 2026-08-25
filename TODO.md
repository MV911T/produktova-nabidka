# TODO

**7 zbývá · 22 hotovo · 3 vyřazeno**

Poslední změna: 25. 8. 2026

---

## Zbývá

### Dokončení nabídky

**1. Pustit zbylé tři kategorie**
Doplňky stravy jsou hotové (při běhu 364 produktů, dnes jich výpis hlásí 435). Muži a ženy jsou projeté a ověřené
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

### Údržba

**3. Opravit texty, které kontrola označila**
Průchod katalogem (viz 29) našel 14 nálezů u 13 produktů, které stojí za
přepsání — 11× zesilující sloveso („zvyšuje“, „zlepšuje“, „posiluje“,
„řeší“, „hraje klíčovou roli“), 2× symptom, 1× riziková formulace
o ochraně buněk u spiruliny. Texty jsou na e-shopu, ne u nás v datech,
takže je to úkol pro obsah, ne pro kód.

**4. Riziková slova hlásí i doslovné znění schváleného tvrzení**
Aktivní uhlí má v popisu větu „přispívá ke snižování nadměrné plynatosti
po jídle“ — doslovné schválené tvrzení č. 1 —, a kontrola ji nahlásí kvůli
slovu „plynatost“. Riziková slova se posuzují nad celým popisem, nezávisle
na tom, že věta oporu má. Falešné byly 4 z 25 tvrdých nálezů.

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

**29.** Parsování pěti polí z produktové stránky — microdata + `.p-short-description`
**29.** Sběr URL z výpisu kategorie včetně stránkování (`/strana-N/`)
**29.** `category` z nadpisu výpisu — na produktu spolehlivá není
**29.** Přeskakování zrušených produktů — web je přesměruje na kategorii
**29.** Rozpoznání a vyřazení balíčků — tři signály plus ruční seznam
**29.** Běh na kategorii doplňků stravy — 364 produktů, 0 prázdných polí

### Popisy a legislativa

**29.** 14 vlastních popisů pro produkty, u nichž e-shop krátký popis nemá
**29.** Kontrola tvrzení proti Vodítkům SZPI 2024 — tři vrstvy:
riziková léčebná slova, zesilující slovesa, zdravotní téma bez opory
**29.** Vyhledávač schválených a on-hold tvrzení podle látky
**29.** Chybějící popisy v kategoriích muži a ženy — psát se nemusel žádný.
Ze 137 produktů nemá e-shop krátký popis u jediného (Performance Magnesium®)
a ten vlastní popis už má. Žádné prázdné pole, 10 balíčků vyřazeno.

### Projekt

**29.** Repozitář na GitHubu — [MV911T/produktova-nabidka](https://github.com/MV911T/produktova-nabidka)
**29.** Hlášky na stderr místo do JSON výstupu
**29.** Rozdělení do modulů, `pyproject.toml`, CLI, GitHub Actions
**29.** 56 testů bez přístupu na síť, `ruff` bez nálezů
**29.** Tabule úkolů po každé iteraci — `nastroje/tabule.py` a `Stop` hook.
Předchozí hook měl natvrdo cestu na původní umístění projektu, a proto
po přesunu nikdy nevystřelil. Nový si repozitář najde přes `git rev-parse`,
takže přesun ani další klon už mu nevadí, a jinde než tady mlčí.
**29.** Neúplná nabídka se pozná. Stahování opakuje pokus u výpadku spojení
a chyb 5xx (4xx ne, ta se opakováním nespraví), a co se ani napotřetí
nestáhne, propadne jako `NeuplnaNabidka` s dosud staženými produkty
a seznamem zbylých URL. CLI zkrácený JSON nevypíše a skončí kódem 1,
dokud nedostane `--dovol-neuplnou`.

**29.** Ašvaganda Sensoril® je z kořene **i listů** — technický list výrobce
(Kerry, majitel značky od převzetí Natreonu) ji vede jako „Premium Ashwagandha
Root & Leaf Extract“ a kombinaci obou částí uvádí jako svou přednost. On-hold
tvrzení 4194 „Duševní zdraví, stres & spánek“ je vázané na *kořen*, takže se
o ně opřít nelze. Popis Antistres komplexu proto stojí na tvrzení 2183
„Duševní zdraví a relaxace“, které část rostliny neomezuje.

**29.** Přesnost kontroly tvrzení. Na 165 popisech z e-shopu spadly
poplachy „bez opory“ z 223 na 26 a našich 14 popisů hlásí jediný nález —
ten věcný. Tři změny: věta se posuzuje, jen když účinek vysloví (samotná
zmínka o zdraví tvrzením není), opora musí platit pro touž látku, a když
je vedená jen pro určitou část rostliny, kontrola to řekne. Dřív prošlo
i „Kolagen přispívá k normální funkci imunitního systému“ — opřelo se
o znění pro vitamín C, protože se shodly na slovech „přispívá“
a „normální“.

**29.** Provozní sdělení zmizí z popisu, ať končí čímkoli. Vzor žádal
tečku, takže věta „Vážení zákazníci, vylepšili jsme složení… v aktivní
formě!“ v datech obou balení Energy Magnesia® zůstávala. Ověřeno na živých
stránkách i pěti testy.

**29.** Každý produkt je v nabídce jednou. E-shop vede `Men Multivitamin®`
ve výpisu i jako `…-kapsli-2`; adresy se liší, shodná je až microdata `url`,
a podle ní se teď duplicita pozná. Kategorie zůstává ta první v pořadí.
Kategorie mužů po opravě vrací 85 produktů místo 86, bez duplicit.

**29.** Zdroj `category` prověřen a ponechán u nadpisu výpisu. Produkt
vlastní kategorii nese, jenže `itemprop="category"` je celá cesta zakončená
názvem produktu a věcná kategorie je až předposledním článkem — ten u 7 z 55
produktů (13 %) chybí a zbývá značka. Navíc jde o primární zařazení, ne o to,
oč bylo požádáno: `FUELIX DRINK` se ve výpisu doplňků stravy hlásí do „Zdravá
výživa a potraviny pro děti“. README uvádělo třetinu, doloženo je 13 %.

**29.** Celý katalog projet kontrolou tvrzení — 466 produktů ze všech čtyř
kategorií, nic nestaženo nezůstalo, žádné prázdné pole ani duplicita.
Tvrdých nálezů 25 u 22 produktů; po ručním posouzení 14 k opravě,
2 k posouzení, 5 mimo rozsah (kosmetika) a 4 falešné. K tomu 123 vět bez
opory u 109 produktů — u bylin jich část oporu mít bude, seznam je
k posouzení. Zpráva zůstává mimo repozitář, ten je veřejný.

---

## Vyřazeno ze zadání

**29.** Doplňování z databáze prodspec — nahrazeno vlastními popisy
**30.** Cloudový scraper — krátký popis je jen v HTML, JSON-LD ho nemá
**31.** Fallback popisu z detailního textu — dával dávkování, výživové hodnoty
a doslovné „Popis produktu není dostupný“; použitelný byl 2krát z 19
