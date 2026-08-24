"""Vyhledávání ve schválených a on-hold zdravotních tvrzeních (Vodítka SZPI 2024)."""
import json, re, unicodedata

_ONHOLD = json.load(open('onhold.json', encoding='utf-8'))
_ZT = json.load(open('schvalena_zt.json', encoding='utf-8'))

def _norm(s):
    s = unicodedata.normalize('NFD', str(s).lower())
    return ''.join(c for c in s if unicodedata.category(c) != 'Mn')

def on_hold(vyraz, limit=12):
    v = _norm(vyraz)
    return [r for r in _ONHOLD if v in _norm(r['lat']) or v in _norm(r['cz'])][:limit]

def schvalena(vyraz, limit=12):
    v = _norm(vyraz)
    return [r for r in _ZT if len(r) > 2 and v in _norm(r[1])][:limit]

if __name__ == '__main__':
    import sys
    for q in sys.argv[1:]:
        print(f"\n########## {q} ##########")
        s = schvalena(q)
        print("-- SCHVÁLENÁ ZT --" if s else "-- schválená ZT: žádná --")
        for r in s: print(f"   [{r[1][:28]}] {r[2][:130]}")
        o = on_hold(q)
        print("-- ON HOLD --" if o else "-- on hold: nic --")
        for r in o: print(f"   ({r['id']}) {r['cz'][:38]} -> {r['tvrzeni'][:85]}")
