#!/usr/bin/env python3
"""Dal sorgente al sito. Legge le voci e il registro delle fonti, calcola NT e RT,
scrive in docs/ una pagina Markdown per voce, l'indice, le fonti. Poi MkDocs fa il sito.
Non valida: l'ordine valida-costruisci-pubblica lo garantisce pipeline.sh"""
import csv, json, pathlib, shutil, yaml
from jinja2 import Environment, FileSystemLoader

voci = {p.stem: yaml.safe_load(p.read_text(encoding="utf-8")) for p in pathlib.Path("data/concepts").glob("*.yaml")}
fonti = yaml.safe_load(pathlib.Path("data/sources.yaml").read_text(encoding="utf-8"))
meta = yaml.safe_load(pathlib.Path("tesauro.yaml").read_text(encoding="utf-8"))     # i metadati del tesauro

def nome(cid):
    return voci[cid]["prefLabel"]["en"]

# le relazioni si scrivono in una direzione sola: qui si completano
nt, rt = {}, {}
for cid, v in voci.items():
    for bt in v.get("broader", []):
        nt.setdefault(bt, []).append(cid)
    for r in v.get("related", []):
        rt.setdefault(cid, set()).add(r)
        rt.setdefault(r, set()).add(cid)
for cid, v in voci.items():
    v["nt"] = sorted(nt.get(cid, []), key=nome)
    v["rt"] = sorted(rt.get(cid, []), key=nome)
radici = sorted((c for c, v in voci.items() if not v.get("broader") and v["status"] != "deprecated"), key=nome)

docs = pathlib.Path("docs")
shutil.rmtree(docs, ignore_errors=True)
(docs / "voci").mkdir(parents=True)
env = Environment(loader=FileSystemLoader("templates"), autoescape=False, trim_blocks=True, lstrip_blocks=True)
env.filters["nome"] = nome
for cid, v in voci.items():
    (docs / "voci" / f"{cid}.md").write_text(env.get_template("voce.md.j2").render(v=v, voci=voci, fonti=fonti, meta=meta), encoding="utf-8")
# i dati che il filtro dell'indice usa nel browser: una riga per voce, solo cio' che serve a filtrare
dati = []
for cid, v in voci.items():
    testo = " ".join([v["prefLabel"]["en"], v["prefLabel"].get("it", ""), v["definition"]["en"], v["definition"].get("it", "")]
                     + [x for lista in v.get("altLabel", {}).values() for x in lista]).lower()
    dati.append({"id": cid, "en": v["prefLabel"]["en"], "it": v["prefLabel"].get("it", ""), "stato": v["status"],
                 "prospettiva": v["perspective"], "bt": bool(v.get("broader")), "nt": bool(v["nt"]), "rt": bool(v["rt"]),
                 "standard": [a["standard"] for a in v.get("alignments", [])], "testo": testo})
(docs / "index.md").write_text(env.get_template("index.md.j2").render(voci=voci, radici=radici, meta=meta, fonti=fonti, dati=dati), encoding="utf-8")
(docs / "assets").mkdir(exist_ok=True)
shutil.copy("templates/filtri.js", docs / "assets" / "filtri.js")
shutil.copy("templates/filtri.css", docs / "assets" / "filtri.css")

# la pagina delle fonti: per ogni fonte, quali voci la citano e quali si allineano
citata = {k: sorted((c for c, v in voci.items() if any(s["ref"] == k for s in v["sources"])), key=nome) for k in fonti}
allineata = {k: sorted((c for c, v in voci.items() if any(a["standard"] == k for a in v.get("alignments", []))), key=nome) for k in fonti}
(docs / "fonti.md").write_text(env.get_template("fonti.md.j2").render(fonti=fonti, citata=citata, allineata=allineata), encoding="utf-8")

# le pagine scritte a mano (pagine/): passano da Jinja solo per i collegamenti al repository
for f in pathlib.Path("pagine").glob("*.md"):
    (docs / f.name).write_text(env.from_string(f.read_text(encoding="utf-8")).render(meta=meta), encoding="utf-8")

# i moduli delle proposte per GitHub, generati dal registro e dalle voci: si versionano perche' GitHub li legge dal repository
moduli = pathlib.Path(".github/ISSUE_TEMPLATE"); moduli.mkdir(parents=True, exist_ok=True)
for modulo in ("modifica", "nuova-voce"):          # non "nome": e' la funzione che ordina le voci
    (moduli / f"{modulo}.yml").write_text(env.get_template(f"issue-{modulo}.yml.j2").render(voci=voci, fonti=fonti, meta=meta), encoding="utf-8")
print(f"{len(voci)} pagine in docs/")

# gli export: gli stessi dati, per chi li vuole in un programma (JSON) o in un foglio (CSV)
dati_dir = docs / "dati"; dati_dir.mkdir(exist_ok=True)
json.dump({"tesauro": meta, "voci": list(voci.values())}, open(dati_dir / "tesauro.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2, default=str)   # le date di YAML diventano testo
with open(dati_dir / "tesauro.csv", "w", newline="", encoding="utf-8-sig") as f:      # il BOM fa aprire bene il file a Excel
    w = csv.writer(f, delimiter=";")
    w.writerow(["id", "termine EN", "termine IT", "stato", "prospettive", "definizione EN", "definizione IT", "BT", "NT", "RT", "fonti", "standard"])
    for cid, v in sorted(voci.items(), key=lambda x: nome(x[0])):
        w.writerow([cid, v["prefLabel"]["en"], v["prefLabel"].get("it", ""), v["status"], ", ".join(v["perspective"]),
                    v["definition"]["en"], v["definition"].get("it", ""),
                    "; ".join(nome(x) for x in v.get("broader", [])), "; ".join(nome(x) for x in v["nt"]), "; ".join(nome(x) for x in v["rt"]),
                    "; ".join(fonti[s["ref"]].get("short") or fonti[s["ref"]]["title"] for s in v["sources"]),
                    "; ".join(fonti[a["standard"]].get("short") or fonti[a["standard"]]["title"] for a in v.get("alignments", []))])
print("export in docs/dati/: tesauro.json, tesauro.csv")

# il documento unico per la stampa: Pandoc e WeasyPrint lo trasformano in PDF (pipeline.sh)
# per il documento serve un ambiente Jinja che NON tolga le righe vuote: a Pandoc servono per separare i paragrafi
env_doc = Environment(loader=FileSystemLoader("templates"), autoescape=False)
env_doc.filters["nome"] = nome
(dati_dir / "tesauro.md").write_text(env_doc.get_template("tesauro.md.j2").render(voci=voci, fonti=fonti, meta=meta), encoding="utf-8")
shutil.copy("templates/stampa.css", dati_dir / "stampa.css")
