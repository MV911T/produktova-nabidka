# Zadání: Zobrazení produktové nabídky

Pro zobrazení produktové nabídky na stránce musí být pro každý produkt dostupná následující pole. Názvy atributů jsou v angličtině a používají formát `snake_case` vhodný pro Python:

- `product_name` – název produktu
- `product_url` – URL produktu
- `short_description` – krátký popis produktu
- `image_url` – URL obrázku produktu
- `category` – kategorie produktu

Algoritmus v Pythonu vrátí seznam slovníků (`list[dict]`), který lze převést do formátu JSON.

## Příklad JSON struktury

```json
[
  {
    "product_name": "Ukázkový produkt",
    "product_url": "https://example.com/produkty/ukazkovy-produkt",
    "short_description": "Stručný popis ukázkového produktu.",
    "image_url": "https://example.com/obrazky/ukazkovy-produkt.jpg",
    "category": "Ukázková kategorie"
  }
]
```
