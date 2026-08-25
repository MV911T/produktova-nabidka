# TODO

**6 zbývá · 24 hotovo · 3 vyřazeno**

Poslední změna: 25. 8. 2026

---

## Zbývá

### Dokončení nabídky

**1. Pustit zbylé tři kategorie**
Doplňky stravy jsou hotové (při běhu 364 produktů, dnes jich výpis hlásí 435). Muži a ženy jsou projeté a ověřené
(viz 16), LAUF proběhl jako zkouška po opravě 22 — výstup ale zatím nikde
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
už `ziskej_nabidku()` řeší (viz 26), takže stačí předat všechny čtyři URL
najednou a výstup uložit.

### Údržba

**3. Kontrola hlásí i doslovné znění schválených tvrzení**
Dvě příčiny, obě doložené na návrzích textů (viz 29):

*Riziková slova a zesilující slovesa se posuzují nad celým popisem*, bez
ohledu na to, že věta oporu má. Aktivní uhlí tak dostane nález za slovo
„plynatost“ ve větě, která je doslovným schváleným tvrzením č. 1, a kreatin
za „zvyšuje“ — přitom to sloveso je ve schváleném znění samo. Schválená
tvrzení používají „zvyšuje“ (kreatin, vitamín C, škrob) i „zlepšuje“
(laktáza), a „DNA“ v tvrzení o zinku spustí rizikové slovo „dna“.

*Krátká on-hold tvrzení nemohou být oporou.* „Normální trávení“ i
„Antioxidant“ mají po odečtení výplňových slov jediné významové slovo,
jenže `_podepira()` žádá dvě.

### Otevřené otázky

**4. Má výstup nést stabilní identifikátor?**
Stránka vystavuje `sku`, `productID` i `gtin13` (EAN) — ve vzorku 23 z 23.
Zahazujeme je a jediným klíčem záznamu zůstává URL, která se při
přejmenování produktu mění. Zadání ale žádá přesně pět polí a příklad
jich víc neukazuje, takže rozšíření je změna dohodnutého tvaru dat.

**5. Psyllium — semena vs. slupky**
On-hold tvrzení „normální funkce trávicího traktu a střev“ (ID 2510) je
vedené pro *semena* jitrocele. Náš produkt je z *slupek*. Použili jsme ho.

**6. Seznam symptomů je vlastní**
`tvrzeni.SYMPTOMY` (křeče, nespavost, nedostatek…) ve Vodítkách není —
příloha 5 obsahuje nemoci, ne symptomy. Bude potřeba ho doplňovat.
Totéž platí pro `tvrzeni.VZTAHOVA`: tvrzení naznačené bez slovesa
(„Pro zdravé klouby“) kontrola mine.

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
**14.** Kontrola tvrzení proti Vodítkům SZPI 2024 — tři vrstvy (dnes čtyři, viz 24):
riziková léčebná slova, zesilující slovesa, zdravotní téma bez opory
**15.** Vyhledávač schválených a on-hold tvrzení podle látky
**16.** Chybějící popisy v kategoriích muži a ženy — psát se nemusel žádný.
Ze 137 produktů nemá e-shop krátký popis u jediného (Performance Magnesium®)
a ten vlastní popis už má. Žádné prázdné pole, 10 balíčků vyřazeno.

### Projekt

**17.** Repozitář na GitHubu — [MV911T/produktova-nabidka](https://github.com/MV911T/produktova-nabidka)
**18.** Hlášky na stderr místo do JSON výstupu
**19.** Rozdělení do modulů, `pyproject.toml`, CLI, GitHub Actions
**20.** 79 testů bez přístupu na síť, `ruff` bez nálezů
**21.** Tabule úkolů po každé iteraci — `nastroje/tabule.py` a `Stop` hook.
Předchozí hook měl natvrdo cestu na původní umístění projektu, a proto
po přesunu nikdy nevystřelil. Nový si repozitář najde přes `git rev-parse`,
takže přesun ani další klon už mu nevadí, a jinde než tady mlčí.
**22.** Neúplná nabídka se pozná. Stahování opakuje pokus u výpadku spojení
a chyb 5xx (4xx ne, ta se opakováním nespraví), a co se ani napotřetí
nestáhne, propadne jako `NeuplnaNabidka` s dosud staženými produkty
a seznamem zbylých URL. CLI zkrácený JSON nevypíše a skončí kódem 1,
dokud nedostane `--dovol-neuplnou`.

**23.** Ašvaganda Sensoril® je z kořene **i listů** — technický list výrobce
(Kerry, majitel značky od převzetí Natreonu) ji vede jako „Premium Ashwagandha
Root & Leaf Extract“ a kombinaci obou částí uvádí jako svou přednost. On-hold
tvrzení 4194 „Duševní zdraví, stres & spánek“ je vázané na *kořen*, takže se
o ně opřít nelze. Popis Antistres komplexu proto stojí na tvrzení 2183
„Duševní zdraví a relaxace“, které část rostliny neomezuje.

**24.** Přesnost kontroly tvrzení. Na 165 popisech z e-shopu spadly
poplachy „bez opory“ z 223 na 26 a našich 14 popisů hlásí jediný nález —
ten věcný. Tři změny: věta se posuzuje, jen když účinek vysloví (samotná
zmínka o zdraví tvrzením není), opora musí platit pro touž látku, a když
je vedená jen pro určitou část rostliny, kontrola to řekne. Dřív prošlo
i „Kolagen přispívá k normální funkci imunitního systému“ — opřelo se
o znění pro vitamín C, protože se shodly na slovech „přispívá“
a „normální“.

**25.** Provozní sdělení zmizí z popisu, ať končí čímkoli. Vzor žádal
tečku, takže věta „Vážení zákazníci, vylepšili jsme složení… v aktivní
formě!“ v datech obou balení Energy Magnesia® zůstávala. Ověřeno na živých
stránkách i pěti testy.

**26.** Každý produkt je v nabídce jednou. E-shop vede `Men Multivitamin®`
ve výpisu i jako `…-kapsli-2`; adresy se liší, shodná je až microdata `url`,
a podle ní se teď duplicita pozná. Kategorie zůstává ta první v pořadí.
Kategorie mužů po opravě vrací 85 produktů místo 86, bez duplicit.

**27.** Zdroj `category` prověřen a ponechán u nadpisu výpisu. Produkt
vlastní kategorii nese, jenže `itemprop="category"` je celá cesta zakončená
názvem produktu a věcná kategorie je až předposledním článkem — ten u 7 z 55
produktů (13 %) chybí a zbývá značka. Navíc jde o primární zařazení, ne o to,
oč bylo požádáno: `FUELIX DRINK` se ve výpisu doplňků stravy hlásí do „Zdravá
výživa a potraviny pro děti“. README uvádělo třetinu, doloženo je 13 %.

**28.** Celý katalog projet kontrolou tvrzení — 466 produktů ze všech čtyř
kategorií, nic nestaženo nezůstalo, žádné prázdné pole ani duplicita.
Tvrdých nálezů 25 u 22 produktů; po ručním posouzení 14 k opravě,
2 k posouzení, 5 mimo rozsah (kosmetika) a 4 falešné. K tomu 123 vět bez
opory u 109 produktů — u bylin jich část oporu mít bude, seznam je
k posouzení. Zpráva zůstává mimo repozitář, ten je veřejný.

**29.** Náhradní znění pro texty, které kontrola označila. Deset míst
v katalogu, každé opřené o konkrétní schválené či on-hold tvrzení a projeté
kontrolou. Přitom se opravil i můj vlastní souhrn: ze 14 nálezů opravu
potřebuje 11. `Iron Complex®` cituje schválené tvrzení „vitamín C zvyšuje
vstřebávání železa“ doslova, u `Creatine®` chybí jen podmínka užití.
Návrhy jsou mimo repozitář, ten je veřejný.

**30.** Rozpoznávání balíčků prověřeno proti celému katalogu. Ruční seznam
je platný, všech 51 položek ve výpisech pořád je. Heuristika ale míjela
oděvní sady — klíčová slova znala „sada“ a „pack“, ne `set`, takže osm
cyklistických a jedna textilní sada procházely do nabídky, ačkoli se dres
i kraťasy prodávají samostatně. Opačným směrem marker `Tento balíček`
vyřazoval `Bacopu Monnieri` kvůli větě o křížovém prodeji („Omega 3 skvěle
doplní tento balíček“); v celém katalogu to byl jediný zásah toho vzoru,
a chybný. Marker teď musí uvozovat výčet. Nabídka má 459 produktů místo 466.

---

## Vyřazeno ze zadání

**31.** Doplňování z databáze prodspec — nahrazeno vlastními popisy
**32.** Cloudový scraper — krátký popis je jen v HTML, JSON-LD ho nemá
**33.** Fallback popisu z detailního textu — dával dávkování, výživové hodnoty
a doslovné „Popis produktu není dostupný“; použitelný byl 2krát z 19
