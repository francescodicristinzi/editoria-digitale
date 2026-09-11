#!/usr/bin/env python3
"""Da una issue del modulo a un file in proposte/. Legge ISSUE_NUMBER, ISSUE_TITLE e ISSUE_BODY
dall'ambiente (cosi' li passa GitHub Actions) e stampa il percorso del file scritto.

Il modulo scrive ogni campo come "### Etichetta" seguita dal valore: qui si rilegge cosi'.
Le tendine portano "id — descrizione": si tiene la parte prima del trattino."""
import os, pathlib, re, yaml

def campi(corpo):
    """{etichetta: valore} dal corpo della issue."""
    out = {}
    for blocco in re.split(r"^### ", corpo, flags=re.M)[1:]:
        titolo, _, valore = blocco.partition("\n")
        valore = valore.strip()
        out[titolo.strip()] = "" if valore in ("_No response_", "None") else valore
    return out

def prima_del_trattino(s): return s.split(" — ")[0].strip()
def slug(s): return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")

def proposta_da_issue(numero, titolo, corpo):
    c = campi(corpo)
    fonte = {"ref": prima_del_trattino(c.get("Fonte", "")), "locator": c.get("Punto preciso della fonte", "")}
    if "Termine (EN)" in c:                                   # il modulo della voce nuova
        p = {"tipo": "nuova-voce", "voce": slug(c["Termine (EN)"]),
             "prefLabel": {"en": c["Termine (EN)"], "it": c.get("Termine (IT)", "")},
             "definition": {k: v for k, v in (("en", c.get("Definizione (EN)", "")), ("it", c.get("Definizione (IT)", ""))) if v},
             "perspective": [x.strip() for x in c.get("Prospettive", "").split(",") if x.strip()]}
        for riga in c.get("Relazioni con voci esistenti", "").splitlines():
            if ":" in riga:
                tipo, ids = riga.split(":", 1); tipo = tipo.strip().upper()
                lista = [x.strip() for x in ids.split(",") if x.strip()]
                if tipo == "BT": p["broader"] = lista
                if tipo == "RT": p["related"] = lista
    else:                                                     # il modulo della modifica
        p = {"tipo": "modifica", "voce": prima_del_trattino(c.get("Voce", "")), "richiesta": c.get("Che cosa cambieresti", "")}
    p["sources"] = [fonte]; p["motivazione"] = c.get("Motivazione", ""); p["issue"] = int(numero)
    return p

if __name__ == "__main__":
    numero, titolo, corpo = os.environ["ISSUE_NUMBER"], os.environ.get("ISSUE_TITLE", ""), os.environ.get("ISSUE_BODY", "")
    p = proposta_da_issue(numero, titolo, corpo)
    dest = pathlib.Path("proposte") / f"{int(numero):03d}-{p['voce'] or 'senza-voce'}.yaml"
    dest.write_text(yaml.dump(p, sort_keys=False, allow_unicode=True, width=100), encoding="utf-8")
    print(dest)
