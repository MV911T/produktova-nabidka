# TODO

Stav: **13 / 15 hotovo**

## Hotovo

- [x] Parsování 5 polí z produktové stránky (microdata + `.p-short-description`)
- [x] Sběr URL z výpisu kategorie včetně stránkování
- [x] `category` z nadpisu výpisu — na produktu spolehlivá není
- [x] Přeskakování zrušených produktů (přesměrování na kategorii)
- [x] Rozpoznání a vyřazení balíčků (3 signály + ruční seznam)
- [x] 14 vlastních popisů pro produkty bez krátkého popisu
- [x] Kontrola tvrzení proti Vodítkům SZPI 2024
- [x] Repozitář na GitHubu
- [x] Hlášky na stderr místo do JSON výstupu
- [x] Hook, který tenhle seznam vypíše po každé změně souboru v projektu
- [x] Běh na kategorii *BrainMax® doplňky stravy* — 364 produktů, 0 prázdných polí
- [x] Rozdělení do modulů, `pyproject.toml`, CLI, CI
- [x] 44 testů (`pytest`), ruff bez nálezů

## Zbývá

- [ ] Pustit *BrainMax pro muže* (~108), *BrainMax pro ženy* (~108), *LAUF* (29)
- [ ] Spojit výstupy všech čtyř kategorií do jedné nabídky

## Otevřené otázky

- On-hold tvrzení pro psyllium je vedené pro *semena*, produkt je ze *slupek*
- Ašvaganda Sensoril® — on-hold „stres & spánek" je vázané na kořen,
  Sensoril se vyrábí z kořene i listů
- Seznam symptomů v `tvrzeni.py` je vlastní, ve Vodítkách takový výčet není
- Ruční seznam balíčků je nutné doplňovat, až e-shop přidá další sady

## Vyřazeno ze zadání

- Doplňování z databáze prodspec — nahrazeno vlastními popisy
- Cloudový scraper — krátký popis je jen v HTML, JSON-LD ho nemá
- Fallback popisu z detailního textu — dával nepoužitelné výsledky
  (dávkování, výživové hodnoty, „Popis produktu není dostupný")
