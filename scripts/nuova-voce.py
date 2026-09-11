#!/usr/bin/env python3
"""Crea una voce nuova dal template.  python3 scripts/nuova-voce.py ai-puzzona

Copia data/voce.template.yaml in data/concepts/<id>.yaml con l'id gia'
scritto e il termine inglese abbozzato dall'id. Poi tocca a te: riempi i
campi, cancella le righe che non usi, e lancia python3 scripts/validate.py."""
import pathlib, re, sys

if len(sys.argv) != 2 or not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", sys.argv[1]):
    sys.exit("uso: python3 scripts/nuova-voce.py <id>   (minuscole, cifre e trattini: es. ai-literacy)")
cid = sys.argv[1]
dest = pathlib.Path("data/concepts") / f"{cid}.yaml"
if dest.exists():
    sys.exit(f"{dest} esiste gia': l'id e' per sempre, scegline un altro")

testo = pathlib.Path("data/voce.template.yaml").read_text(encoding="utf-8")
testo = re.sub(r"^id: .*$", f"id: {cid}", testo, count=1, flags=re.M)
testo = re.sub(r"^  en: Term as written in the source$", f"  en: {cid.replace('-', ' ').capitalize()}", testo, count=1, flags=re.M)
dest.write_text(testo, encoding="utf-8")
print(f"creata {dest}\n  1. apri il file e riempi i campi (cancella le righe che non usi)\n  2. python3 scripts/validate.py\n  3. python3 scripts/build.py && mkdocs build")
