# TODO

**5 zbývá · 26 hotovo · 3 vyřazeno**

Poslední změna: 25. 8. 2026

---

## Zbývá

### Dokončení nabídky

**1. Pustit zbylé tři kategorie**
Doplňky stravy jsou hotové (při běhu 364 produktů, dnes jich výpis hlásí 435). Muži a ženy jsou projeté a ověřené
(viz 15), LAUF proběhl jako zkouška po opravě 21 — výstup ale zatím nikde
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
už `ziskej_nabidku()` řeší (viz 25), takže stačí předat všechny čtyři URL
najednou a výstup uložit.

### Rozsah nabídky

**3. Odfiltrovat nepoživatelné zboží**
Kategorie `/brainmax-men/`, `/brainmax-pro-zeny/` a `/lauf/` nejsou rubriky
doplňků — z 539 produktů ve výpisech je 84 podle názvu oblečení nebo
kosmetika (44 u mužů, 25 u žen, 7 v LAUF). Čistá není ani kategorie doplňků
stravy: vede skleněné láhve a šejkr. Kategorie zůstávají, filtrovat se má
zboží. Podle názvu to nejde — „Mandlový krém s kokosem“ je potravina —,
použitelná je vlastní kategorijní cesta produktu (`itemprop="category"`),
kde jdou poznat větve `Oblečení a doplňky`, `Přírodní kosmetika`
a `Péče o tělo`. Cesty všech produktů jsou stažené.

### Otevřené otázky

**4. Psyllium — semena vs. slupky**
On-hold tvrzení „normální funkce trávicího traktu a střev“ (ID 2510) je
vedené pro *semena* jitrocele. Náš produkt je z *slupek*. Použili jsme ho.

**5. Seznam symptomů je vlastní**
`tvrzeni.SYMPTOMY` (křeče, nespavost, nedostatek…) ve Vodítkách není —
příloha 5 obsahuje nemoci, ne symptomy. Bude potřeba ho doplňovat.
Totéž platí pro `tvrzeni.VZTAHOVA`: tvrzení naznačené bez slovesa
(„Pro zdravé klouby“) kontrola mine.

---

## Hotovo

### Sběr dat

**6.** Parsování pěti polí z produktové stránky — microdata + `.p-short-description`
**7.** Sběr URL z výpisu kategorie včetně stránkování (`/strana-N/`)
**8.** `category` z nadpisu výpisu — na produktu spolehlivá není
**9.** Přeskakování zrušených produktů — web je přesměruje na kategorii
**10.** Rozpoznání a vyřazení balíčků — tři signály plus ruční seznam
**11.** Běh na kategorii doplňků stravy — 364 produktů, 0 prázdných polí

### Popisy a legislativa

**12.** 14 vlastních popisů pro produkty, u nichž e-shop krátký popis nemá
**13.** Kontrola tvrzení proti Vodítkům SZPI 2024 — tři vrstvy (dnes čtyři, viz 23):
riziková léčebná slova, zesilující slovesa, zdravotní téma bez opory
**14.** Vyhledávač schválených a on-hold tvrzení podle látky
**15.** Chybějící popisy v kategoriích muži a ženy — psát se nemusel žádný.
Ze 137 produktů nemá e-shop krátký popis u jediného (Performance Magnesium®)
a ten vlastní popis už má. Žádné prázdné pole, 10 balíčků vyřazeno.

### Projekt

**16.** Repozitář na GitHubu — [MV911T/produktova-nabidka](https://github.com/MV911T/produktova-nabidka)
**17.** Hlášky na stderr místo do JSON výstupu
**18.** Rozdělení do modulů, `pyproject.toml`, CLI, GitHub Actions
**19.** 79 testů bez přístupu na síť, `ruff` bez nálezů
**20.** Tabule úkolů po každé iteraci — `nastroje/tabule.py` a `Stop` hook.
Předchozí hook měl natvrdo cestu na původní umístění projektu, a proto
po přesunu nikdy nevystřelil. Nový si repozitář najde přes `git rev-parse`,
takže přesun ani další klon už mu nevadí, a jinde než tady mlčí.
**21.** Neúplná nabídka se pozná. Stahování opakuje pokus u výpadku spojení
a chyb 5xx (4xx ne, ta se opakováním nespraví), a co se ani napotřetí
nestáhne, propadne jako `NeuplnaNabidka` s dosud staženými produkty
a seznamem zbylých URL. CLI zkrácený JSON nevypíše a skončí kódem 1,
dokud nedostane `--dovol-neuplnou`.

**22.** Ašvaganda Sensoril® je z kořene **i listů** — technický list výrobce
(Kerry, majitel značky od převzetí Natreonu) ji vede jako „Premium Ashwagandha
Root & Leaf Extract“ a kombinaci obou částí uvádí jako svou přednost. On-hold
tvrzení 4194 „Duševní zdraví, stres & spánek“ je vázané na *kořen*, takže se
o ně opřít nelze. Popis Antistres komplexu proto stojí na tvrzení 2183
„Duševní zdraví a relaxace“, které část rostliny neomezuje.

**23.** Přesnost kontroly tvrzení. Na 165 popisech z e-shopu spadly
poplachy „bez opory“ z 223 na 26 a našich 14 popisů hlásí jediný nález —
ten věcný. Tři změny: věta se posuzuje, jen když účinek vysloví (samotná
zmínka o zdraví tvrzením není), opora musí platit pro touž látku, a když
je vedená jen pro určitou část rostliny, kontrola to řekne. Dřív prošlo
i „Kolagen přispívá k normální funkci imunitního systému“ — opřelo se
o znění pro vitamín C, protože se shodly na slovech „přispívá“
a „normální“.

**24.** Provozní sdělení zmizí z popisu, ať končí čímkoli. Vzor žádal
tečku, takže věta „Vážení zákazníci, vylepšili jsme složení… v aktivní
formě!“ v datech obou balení Energy Magnesia® zůstávala. Ověřeno na živých
stránkách i pěti testy.

**25.** Každý produkt je v nabídce jednou. E-shop vede `Men Multivitamin®`
ve výpisu i jako `…-kapsli-2`; adresy se liší, shodná je až microdata `url`,
a podle ní se teď duplicita pozná. Kategorie zůstává ta první v pořadí.
Kategorie mužů po opravě vrací 85 produktů místo 86, bez duplicit.

**26.** Zdroj `category` prověřen a ponechán u nadpisu výpisu. Produkt
vlastní kategorii nese, jenže `itemprop="category"` je celá cesta zakončená
názvem produktu a věcná kategorie je až předposledním článkem — ten u 7 z 55
produktů (13 %) chybí a zbývá značka. Navíc jde o primární zařazení, ne o to,
oč bylo požádáno: `FUELIX DRINK` se ve výpisu doplňků stravy hlásí do „Zdravá
výživa a potraviny pro děti“. README uvádělo třetinu, doloženo je 13 %.

**27.** Celý katalog projet kontrolou tvrzení — 466 produktů ze všech čtyř
kategorií, nic nestaženo nezůstalo, žádné prázdné pole ani duplicita.
Tvrdých nálezů 25 u 22 produktů; po ručním posouzení 14 k opravě,
2 k posouzení, 5 mimo rozsah (kosmetika) a 4 falešné. K tomu 123 vět bez
opory u 109 produktů — u bylin jich část oporu mít bude, seznam je
k posouzení. Zpráva zůstává mimo repozitář, ten je veřejný.

**28.** Náhradní znění pro texty, které kontrola označila. Deset míst
v katalogu, každé opřené o konkrétní schválené či on-hold tvrzení a projeté
kontrolou. Přitom se opravil i můj vlastní souhrn: ze 14 nálezů opravu
potřebuje 11. `Iron Complex®` cituje schválené tvrzení „vitamín C zvyšuje
vstřebávání železa“ doslova, u `Creatine®` chybí jen podmínka užití.
Návrhy jsou mimo repozitář, ten je veřejný.

**29.** Rozpoznávání balíčků prověřeno proti celému katalogu. Ruční seznam
je platný, všech 51 položek ve výpisech pořád je. Heuristika ale míjela
oděvní sady — klíčová slova znala „sada“ a „pack“, ne `set`, takže osm
cyklistických a jedna textilní sada procházely do nabídky, ačkoli se dres
i kraťasy prodávají samostatně. Opačným směrem marker `Tento balíček`
vyřazoval `Bacopu Monnieri` kvůli větě o křížovém prodeji („Omega 3 skvěle
doplní tento balíček“); v celém katalogu to byl jediný zásah toho vzoru,
a chybný. Marker teď musí uvozovat výčet. Nabídka má 459 produktů místo 466.

**30.** Kontrola mlčí tam, kde slovo má i samotná opora. Riziková slova
a zesilující slovesa se posuzovala nad celým popisem, takže doslovné
schválené tvrzení spadlo na vlastní slovník: aktivní uhlí na „plynatost“,
`Iron Complex®` na „zvyšuje“ ve větě „vitamín C zvyšuje vstřebávání
železa“, zinek by spadl na „DNA“. Nově se každé slovo posuzuje po větách
a hlásí se jen tehdy, když ho nemá i tvrzení, o které se věta opírá.
Zároveň krátká on-hold tvrzení („Antioxidant“, „Normální trávení“) mají
jediné významové slovo, a práh dvou je vyřazoval — u nich stačí jedno.
Na katalogu klesla riziková slova z 8 na 7 a zesilující slovesa ze 14 na 11;
kontrola je díky předpočítaným kmenům dvakrát rychlejší (22,3 s → 11,6 s).

**31.** Stabilní identifikátory ve výstupu. K pěti polím ze zadání přibylo
`sku` a `ean` (microdata `sku` a `gtin13`) — bez nich byla jediným klíčem
záznamu URL, která se s přejmenováním produktu mění, takže by týž produkt
vyšel při dalším běhu jako zmizelý a nově přidaný. U variantního zboží nese
`sku` příponu velikosti, určuje tedy variantu; nadřazený produkt má
`productID`.

---

## Vyřazeno ze zadání

**32.** Doplňování z databáze prodspec — nahrazeno vlastními popisy
**33.** Cloudový scraper — krátký popis je jen v HTML, JSON-LD ho nemá
**34.** Fallback popisu z detailního textu — dával dávkování, výživové hodnoty
a doslovné „Popis produktu není dostupný“; použitelný byl 2krát z 19
