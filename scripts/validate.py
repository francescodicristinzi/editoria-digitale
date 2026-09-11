#!/usr/bin/env python3
"""Controlla che il sorgente sia coerente, prima di costruire qualsiasi cosa.
Una regola, una funzione. Ogni funzione riceve una voce e aggiunge una riga a
`errori` (il build si ferma) o ad `avvisi` (il build va avanti).
Si lancia dalla radice:  python3 scripts/validate.py"""
import json, pathlib, sys, yaml
from jsonschema import Draft202012Validator

schema = json.loads(pathlib.Path("data/schema/voce.schema.json").read_text(encoding="utf-8"))
fonti = yaml.safe_load(pathlib.Path("data/sources.yaml").read_text(encoding="utf-8"))
errori, avvisi = [], []

# ---- 1. si leggono i file --------------------------------------------------
voci = {}
for file in sorted(pathlib.Path("data/concepts").glob("*.yaml")):
    try:
        voci[file.stem] = yaml.safe_load(file.read_text(encoding="utf-8"))
    except yaml.YAMLError as e:
        errori.append(f"{file.stem}: YAML non leggibile: {str(e).splitlines()[0]}")

# ---- 2. le regole, una per funzione ----------------------------------------
def forma(cid, v):
    """La voce rispetta lo schema: campi, valori ammessi, tipi, niente campi in piu'."""
    for problema in Draft202012Validator(schema).iter_errors(v):
        dove = ".".join(str(x) for x in problema.path) or "radice"
        errori.append(f"{cid}: schema, in {dove}: {problema.message}")

def id_uguale_al_file(cid, v):
    if v.get("id") != cid:
        errori.append(f"{cid}: id '{v.get('id')}' diverso dal nome del file")

def riferimenti_esistenti(cid, v):
    """Ogni broader e related punta a una voce che esiste, e non a se stessa."""
    for campo in ("broader", "related"):
        for altra in v.get(campo, []):
            if altra == cid:
                errori.append(f"{cid}: {campo} verso se stessa")
            elif altra not in voci:
                errori.append(f"{cid}: {campo} verso '{altra}', che non esiste")

def antenati(cid):
    """Tutti i termini sopra una voce, risalendo i broader. Si ferma se gira in tondo."""
    trovati, da_vedere = [], list(voci.get(cid, {}).get("broader", []))
    while da_vedere:
        x = da_vedere.pop()
        if x == cid:
            errori.append(f"{cid}: ciclo nella gerarchia"); break
        if x not in trovati:
            trovati.append(x)
            da_vedere += voci.get(x, {}).get("broader", [])
    return trovati

def niente_cicli(cid, v):
    antenati(cid)

def related_e_broader_disgiunti(cid, v):
    """SKOS: due voci legate da related non possono essere una sopra l'altra."""
    for altra in v.get("related", []):
        if altra in antenati(cid) or cid in antenati(altra):
            errori.append(f"{cid}: related e broader sulla stessa coppia con '{altra}': SKOS li vuole disgiunti")

def termine_preferito_unico(cid, v):
    for lingua, termine in v.get("prefLabel", {}).items():
        for altro_id, altra in voci.items():
            if altro_id != cid and altra.get("prefLabel", {}).get(lingua, "").lower() == termine.lower():
                errori.append(f"{cid}: prefLabel.{lingua} '{termine}' uguale a quello di '{altro_id}'")

def variante_diversa_dal_preferito(cid, v):
    for lingua, termine in v.get("prefLabel", {}).items():
        for variante in v.get("altLabel", {}).get(lingua, []):
            if variante.lower() == termine.lower():
                errori.append(f"{cid}: altLabel.{lingua} contiene il termine preferito '{termine}'")

def fonti_nel_registro(cid, v):
    """La fonte esiste nel registro; se e' un atto o uno standard, serve il punto preciso."""
    for s in v.get("sources", []):
        fonte = fonti.get(s["ref"])
        if fonte is None:
            errori.append(f"{cid}: fonte '{s['ref']}' non e' nel registro")
        elif fonte["type"] in ("legislation", "treaty", "standard", "soft-law") and not s.get("locator"):
            errori.append(f"{cid}: fonte '{s['ref']}' senza locatore (articolo, clausola)")

def allineamenti_a_standard(cid, v):
    """Lo standard esiste nel registro ed e' uno standard; se e' a pagamento, avviso."""
    for a in v.get("alignments", []):
        fonte = fonti.get(a["standard"])
        if fonte is None:
            errori.append(f"{cid}: standard '{a['standard']}' non e' nel registro")
        elif fonte["type"] not in ("standard", "framework"):
            errori.append(f"{cid}: '{a['standard']}' non e' uno standard ma '{fonte['type']}'")
        elif fonte.get("access") == "paid":
            avvisi.append(f"{cid}: allineamento a '{a['standard']}', standard a pagamento: non verificabile sul testo")

def approvata_completa(cid, v):
    if v.get("status") == "approved":
        for campo in ("prefLabel", "definition"):
            if not v.get(campo, {}).get("it"):
                errori.append(f"{cid}: approvata ma senza {campo}.it")

def ritirata_con_sostituta(cid, v):
    sostituta = v.get("replacedBy")
    if v.get("status") == "deprecated":
        if not sostituta:
            errori.append(f"{cid}: ritirata senza replacedBy")
        elif sostituta not in voci:
            errori.append(f"{cid}: replacedBy '{sostituta}' non esiste")
        elif voci[sostituta].get("status") == "deprecated":
            errori.append(f"{cid}: replacedBy '{sostituta}' e' a sua volta ritirata")
    elif sostituta:
        errori.append(f"{cid}: replacedBy ha senso solo in una voce ritirata")

def collegata_a_qualcosa(cid, v):
    """Una voce senza nessuna relazione, in nessuna direzione, e' sospetta: avviso."""
    citata = any(cid in w.get("broader", []) + w.get("related", []) for w in voci.values())
    if not v.get("broader") and not v.get("related") and not citata:
        avvisi.append(f"{cid}: nessuna relazione con altre voci")

REGOLE = [forma, id_uguale_al_file, riferimenti_esistenti, niente_cicli, related_e_broader_disgiunti,
          termine_preferito_unico, variante_diversa_dal_preferito, fonti_nel_registro,
          allineamenti_a_standard, approvata_completa, ritirata_con_sostituta, collegata_a_qualcosa]

# ---- 3. si applicano a ogni voce e si riferisce ----------------------------
for cid, v in voci.items():
    for regola in REGOLE:
        regola(cid, v)
for a in avvisi: print("AVVISO ", a)
for e in errori: print("ERRORE ", e)
print(f"{len(voci)} voci, {len(errori)} errori, {len(avvisi)} avvisi")
sys.exit(1 if errori else 0)
