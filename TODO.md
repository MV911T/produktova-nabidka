# TODO

**3 zbývá · 30 hotovo · 3 vyřazeno**

Poslední změna: 25. 8. 2026

---

## Zbývá

### Dokončení nabídky

**1. Pustit zbylé tři kategorie**
Doplňky stravy jsou hotové (při běhu 364 produktů, dnes jich výpis hlásí 435). Muži a ženy jsou projeté a ověřené
(viz 13), LAUF proběhl jako zkouška po opravě 19 — výstup ale zatím nikde
uložený není. Chybí:

| Kategorie | URL | Produktů |
|---|---|---|
| BrainMax pro muže | `/brainmax-men/` | 91 URL → 9 doplňků |
| BrainMax pro ženy | `/brainmax-pro-zeny/` | 104 URL → 2 doplňky |
| LAUF | `/lauf/` | 28 URL → 5 doplňků |

```bash
nabidka https://www.brainmarket.cz/brainmax-men/ > muzi.json
```

**2. Spojit výstupy všech čtyř kategorií do jedné nabídky**
Produkt může být ve víc kategoriích zároveň — duplicity i pořadí kategorií
už `ziskej_nabidku()` řeší (viz 23), takže stačí předat všechny čtyři URL
najednou a výstup uložit.


### Otevřené otázky

**3. Seznam symptomů zůstává vlastní**
`tvrzeni.SYMPTOMY` je náš, ve Vodítkách takový výčet není — příloha 5
obsahuje nemoci, ne symptomy. Průchod katalogem k jeho rozšíření podklad
nedal (jediný nález), takže se doplní až podle nálezů z praxe.
Vztahové výrazy už rozšířené jsou (viz 33).

---

## Hotovo

### Sběr dat

**4.** Parsování pěti polí z produktové stránky — microdata + `.p-short-description`
**5.** Sběr URL z výpisu kategorie včetně stránkování (`/strana-N/`)
**6.** `category` z nadpisu výpisu — na produktu spolehlivá není
**7.** Přeskakování zrušených produktů — web je přesměruje na kategorii
**8.** Rozpoznání a vyřazení balíčků — tři signály plus ruční seznam
**9.** Běh na kategorii doplňků stravy — 364 produktů, 0 prázdných polí

### Popisy a legislativa

**10.** 14 vlastních popisů pro produkty, u nichž e-shop krátký popis nemá
**11.** Kontrola tvrzení proti Vodítkům SZPI 2024 — tři vrstvy (dnes pět, viz 21 a 32):
riziková léčebná slova, zesilující slovesa, zdravotní téma bez opory
**12.** Vyhledávač schválených a on-hold tvrzení podle látky
**13.** Chybějící popisy v kategoriích muži a ženy — psát se nemusel žádný.
Ze 137 produktů nemá e-shop krátký popis u jediného (Performance Magnesium®)
a ten vlastní popis už má. Žádné prázdné pole, 10 balíčků vyřazeno.

### Projekt

**14.** Repozitář na GitHubu — [MV911T/produktova-nabidka](https://github.com/MV911T/produktova-nabidka)
**15.** Hlášky na stderr místo do JSON výstupu
**16.** Rozdělení do modulů, `pyproject.toml`, CLI, GitHub Actions
**17.** 79 testů bez přístupu na síť, `ruff` bez nálezů
**18.** Tabule úkolů po každé iteraci — `nastroje/tabule.py` a `Stop` hook.
Předchozí hook měl natvrdo cestu na původní umístění projektu, a proto
po přesunu nikdy nevystřelil. Nový si repozitář najde přes `git rev-parse`,
takže přesun ani další klon už mu nevadí, a jinde než tady mlčí.
**19.** Neúplná nabídka se pozná. Stahování opakuje pokus u výpadku spojení
a chyb 5xx (4xx ne, ta se opakováním nespraví), a co se ani napotřetí
nestáhne, propadne jako `NeuplnaNabidka` s dosud staženými produkty
a seznamem zbylých URL. CLI zkrácený JSON nevypíše a skončí kódem 1,
dokud nedostane `--dovol-neuplnou`.

**20.** Ašvaganda Sensoril® je z kořene **i listů** — technický list výrobce
(Kerry, majitel značky od převzetí Natreonu) ji vede jako „Premium Ashwagandha
Root & Leaf Extract“ a kombinaci obou částí uvádí jako svou přednost. On-hold
tvrzení 4194 „Duševní zdraví, stres & spánek“ je vázané na *kořen*, takže se
o ně opřít nelze. Popis Antistres komplexu proto stojí na tvrzení 2183
„Duševní zdraví a relaxace“, které část rostliny neomezuje.

**21.** Přesnost kontroly tvrzení. Na 165 popisech z e-shopu spadly
poplachy „bez opory“ z 223 na 26 a našich 14 popisů hlásí jediný nález —
ten věcný. Tři změny: věta se posuzuje, jen když účinek vysloví (samotná
zmínka o zdraví tvrzením není), opora musí platit pro touž látku, a když
je vedená jen pro určitou část rostliny, kontrola to řekne. Dřív prošlo
i „Kolagen přispívá k normální funkci imunitního systému“ — opřelo se
o znění pro vitamín C, protože se shodly na slovech „přispívá“
a „normální“.

**22.** Provozní sdělení zmizí z popisu, ať končí čímkoli. Vzor žádal
tečku, takže věta „Vážení zákazníci, vylepšili jsme složení… v aktivní
formě!“ v datech obou balení Energy Magnesia® zůstávala. Ověřeno na živých
stránkách i pěti testy.

**23.** Každý produkt je v nabídce jednou. E-shop vede `Men Multivitamin®`
ve výpisu i jako `…-kapsli-2`; adresy se liší, shodná je až microdata `url`,
a podle ní se teď duplicita pozná. Kategorie zůstává ta první v pořadí.
Kategorie mužů po opravě vrací 85 produktů místo 86, bez duplicit.

**24.** Zdroj `category` prověřen a ponechán u nadpisu výpisu. Produkt
vlastní kategorii nese, jenže `itemprop="category"` je celá cesta zakončená
názvem produktu a věcná kategorie je až předposledním článkem — ten u 7 z 55
produktů (13 %) chybí a zbývá značka. Navíc jde o primární zařazení, ne o to,
oč bylo požádáno: `FUELIX DRINK` se ve výpisu doplňků stravy hlásí do „Zdravá
výživa a potraviny pro děti“. README uvádělo třetinu, doloženo je 13 %.

**25.** Celý katalog projet kontrolou tvrzení — 466 produktů ze všech čtyř
kategorií, nic nestaženo nezůstalo, žádné prázdné pole ani duplicita.
Tvrdých nálezů 25 u 22 produktů; po ručním posouzení 14 k opravě,
2 k posouzení, 5 mimo rozsah (kosmetika) a 4 falešné. K tomu 123 vět bez
opory u 109 produktů — u bylin jich část oporu mít bude, seznam je
k posouzení. Zpráva zůstává mimo repozitář, ten je veřejný.

**26.** Náhradní znění pro texty, které kontrola označila. Deset míst
v katalogu, každé opřené o konkrétní schválené či on-hold tvrzení a projeté
kontrolou. Přitom se opravil i můj vlastní souhrn: ze 14 nálezů opravu
potřebuje 11. `Iron Complex®` cituje schválené tvrzení „vitamín C zvyšuje
vstřebávání železa“ doslova, u `Creatine®` chybí jen podmínka užití.
Návrhy jsou mimo repozitář, ten je veřejný.

**27.** Rozpoznávání balíčků prověřeno proti celému katalogu. Ruční seznam
je platný, všech 51 položek ve výpisech pořád je. Heuristika ale míjela
oděvní sady — klíčová slova znala „sada“ a „pack“, ne `set`, takže osm
cyklistických a jedna textilní sada procházely do nabídky, ačkoli se dres
i kraťasy prodávají samostatně. Opačným směrem marker `Tento balíček`
vyřazoval `Bacopu Monnieri` kvůli větě o křížovém prodeji („Omega 3 skvěle
doplní tento balíček“); v celém katalogu to byl jediný zásah toho vzoru,
a chybný. Marker teď musí uvozovat výčet. Nabídka má 459 produktů místo 466.

**28.** Kontrola mlčí tam, kde slovo má i samotná opora. Riziková slova
a zesilující slovesa se posuzovala nad celým popisem, takže doslovné
schválené tvrzení spadlo na vlastní slovník: aktivní uhlí na „plynatost“,
`Iron Complex®` na „zvyšuje“ ve větě „vitamín C zvyšuje vstřebávání
železa“, zinek by spadl na „DNA“. Nově se každé slovo posuzuje po větách
a hlásí se jen tehdy, když ho nemá i tvrzení, o které se věta opírá.
Zároveň krátká on-hold tvrzení („Antioxidant“, „Normální trávení“) mají
jediné významové slovo, a práh dvou je vyřazoval — u nich stačí jedno.
Na katalogu klesla riziková slova z 8 na 7 a zesilující slovesa ze 14 na 11;
kontrola je díky předpočítaným kmenům dvakrát rychlejší (22,3 s → 11,6 s).

**29.** Stabilní identifikátory ve výstupu. K pěti polím ze zadání přibylo
`sku` a `ean` (microdata `sku` a `gtin13`) — bez nich byla jediným klíčem
záznamu URL, která se s přejmenováním produktu mění, takže by týž produkt
vyšel při dalším běhu jako zmizelý a nově přidaný. U variantního zboží nese
`sku` příponu velikosti, určuje tedy variantu; nadřazený produkt má
`productID`.

**30.** Z nabídky vypadlo zboží, které se nejí. Kategorie mužů, žen a LAUF
nejsou rubriky doplňků — vedou i oblečení a kosmetiku. Filtrovat podle názvu
nešlo („Mandlový krém s kokosem“ je potravina), rozhoduje proto větev, ve
které produkt na webu visí: `Oblečení a doplňky`, `Přírodní kosmetika`,
`Domov` a jejich podvětve. Cíle jako „Pleť, vlasy, nehty“ mezi nimi
schválně nejsou, tam visí doplňky. Na produkty zavěšené rovnou pod značkou
větev neplatí, těm zbývá krátký výčet slov v názvu — týkal se jediného kusu
(`LAUF láhev na kolo a sport, bidon`). Vyřazeno 80 produktů: 62 oblečení,
13 kosmetika, 4 vybavení domácnosti, 1 podle názvu. Nabídka má 379 produktů
místo 459 a ze tří lifestylových kategorií v ní zbývá 16 doplňků, které
v hlavní kategorii nejsou.

**31.** Psyllium má vlastní on-hold tvrzení pro slupky, semena nebylo
třeba. Otázka stála na tom, že „Normální funkce trávicího traktu a střev“
(ID 2510) je vedené pro *semena* jitrocele, zatímco produkt je z *slupek*.
Seznam ale vede i `Plantago ovata/ispaghula (Common Name: Psyllium Husk)`
→ „Normální funkce střevního traktu“ (ID 3932 a 3933) a k tomu „Normální
hladina cholesterolu v krvi“ (ID 2106). Popis proto stojí na nich a mluví
o jitroceli vejčitém, jak ho seznam u slupek pojmenovává. Kontrola u té
věty dál upozorní na vazbu na část rostliny — správně, protože potvrdit,
že výrobek slupky obsahuje, může jen člověk.

**32.** Kontrola používá oficiální nepřípustná znění z Vodítek. Otázka
zněla, že seznam symptomů je vlastní výmysl — ukázalo se, že `nepripustne.json`
se od začátku načítal a nikde nepoužíval: 43 konkrétních vět, které Vodítka
vypisují jako nepoužitelné, každou i s důvodem. Shodovat se musí všechna
významová slova, protože Vodítka rozlišují věty lišící se jediným slovem
(„ochrana buněk před oxidativním *stresem*“ je schválená, „před oxidativním
*poškozením*“ nepřípustná). Na katalogu je nálezů zatím nula, což odpovídá —
je to síť na budoucí texty, ne na ty stávající.

**33.** Vztah k účinku se pozná i bez slovesa. Brána na slovesa míjela
věty typu „pro podporu normální hladiny cholesterolu“ nebo „Podpora
odolnosti a fyzické výkonnosti“ — tvrzení, která vztah nesou podstatným
jménem. Katalog jich měl 60. Do `VZTAHOVA` proto přibyly kmeny `podpor`,
`ochran`, `regenerac` a tvary `posílení`, `zvýšení`, `udržení`, `přispět`,
`napomáhají`. Vět k posouzení přibylo ze 111 na 154 a jsou to skutečná
tvrzení: „podporuje pevnou pokožku, krásné vlasy a zdravé klouby“,
„pro podporu imunity“, „chrání buňky před oxidačním stresem“.

---

## Vyřazeno ze zadání

**34.** Doplňování z databáze prodspec — nahrazeno vlastními popisy
**35.** Cloudový scraper — krátký popis je jen v HTML, JSON-LD ho nemá
**36.** Fallback popisu z detailního textu — dával dávkování, výživové hodnoty
a doslovné „Popis produktu není dostupný“; použitelný byl 2krát z 19
