#!/usr/bin/env python3
"""L'istruttoria di una proposta: un grafo LangGraph con sei nodi e un'interruzione.

  python3 scripts/istruttoria.py proposte/007-ce-marking.yaml                              chiede la decisione a tastiera
  python3 scripts/istruttoria.py proposte/007-ce-marking.yaml --solo-triage                 il triage: esito nel file (Actions)
  python3 scripts/istruttoria.py proposte/007-ce-marking.yaml --decidi approva --motivazione "..."   decisione gia' data (Actions)

  leggi -> controlla -> analizza -> decidi -> applica
              |             |          |        rifiuta
           rimanda       rimanda   (si ferma e aspetta l'editor)

Il codice controlla cio' che ha una risposta esatta; il modello legge; la persona
decide. Il grafo scrive solo due cose: la voce modificata (se approvata) e
l'esito nel file della proposta. Di git si occupa proposta.sh."""
import argparse, pathlib, re, sys
from typing import TypedDict
import yaml
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import interrupt, Command
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from pre_analisi import pre_analisi

CONCEPTS = pathlib.Path("data/concepts")
fonti = yaml.safe_load(pathlib.Path("data/sources.yaml").read_text(encoding="utf-8"))
CAMPI_TESTO = {"prefLabel.en", "prefLabel.it", "definition.en", "definition.it", "scopeNote.en", "scopeNote.it"}
CAMPI_LISTA = {"altLabel.en", "altLabel.it", "related", "broader"}


class Stato(TypedDict, total=False):
    file: str          # la proposta da istruire
    proposta: dict     # il suo contenuto
    voce: dict         # la voce che vuole modificare
    problemi: list     # cio' che manca, secondo il codice
    analisi: dict      # cio' che dice il modello: pertinente, perche', campo, valore, riassunto, dubbi
    decisione: dict    # esito e motivazione dell'editor
    solo_triage: bool  # su Actions: fermarsi a "pronta", la decisione arrivera' in un altro processo


# ---- scrivere YAML come nelle voci: testi lunghi a blocchi --------------------------
class Dumper(yaml.SafeDumper): pass
Dumper.add_representer(str, lambda d, s: d.represent_scalar("tag:yaml.org,2002:str", s, style=">" if len(s) > 80 else None))
def scrivi(path, dati):
    pathlib.Path(path).write_text(yaml.dump(dati, Dumper=Dumper, sort_keys=False, allow_unicode=True, width=100), encoding="utf-8")


# ---- i nodi -----------------------------------------------------------------------
def leggi(s):
    p = yaml.safe_load(pathlib.Path(s["file"]).read_text(encoding="utf-8"))
    f = CONCEPTS / f"{p.get('voce')}.yaml"
    return {"proposta": p, "voce": yaml.safe_load(f.read_text(encoding="utf-8")) if f.exists() else {}}

def controlla(s):
    """Le regole meccaniche. Chi propone deve dare: una voce che esiste, una richiesta,
    una motivazione di venti parole, una fonte del registro con il punto preciso."""
    p, problemi = s["proposta"], []
    if p.get("tipo") == "nuova-voce":
        if s["voce"]: problemi.append(f"la voce '{p.get('voce')}' esiste gia'")
        if not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", str(p.get("voce", ""))): problemi.append("l'id della voce nuova non e' nella forma giusta")
        for campo in ("prefLabel", "definition"):
            if not (p.get(campo) or {}).get("en"): problemi.append(f"manca {campo}.en")
        if not p.get("perspective"): problemi.append("manca la prospettiva")
    else:
        if not s["voce"]: problemi.append(f"la voce '{p.get('voce')}' non esiste")
        if not (p.get("richiesta") or p.get("campo")): problemi.append("manca la richiesta")
    if len(str(p.get("motivazione", "")).split()) < 20: problemi.append("motivazione sotto le venti parole")
    if not p.get("sources"): problemi.append("nessuna fonte")
    for f in p.get("sources") or []:
        if f.get("ref") not in fonti: problemi.append(f"fonte '{f.get('ref')}' non nel registro")
        elif not f.get("locator"): problemi.append(f"fonte '{f['ref']}' senza locatore")
    return {"problemi": problemi}

def analizza(s):
    """Il modello legge: e' pertinente? che cosa chiede, tradotto in campo e valore?"""
    a = pre_analisi(s["proposta"], s["voce"]) or {"pertinente": True, "riassunto": "assistente non disponibile: la richiesta va letta per intero"}
    if s["proposta"].get("campo"):                       # se il proponente e' stato preciso, vale quello che ha scritto
        a["campo"], a["valore"] = s["proposta"]["campo"], s["proposta"]["valore"]
    if a.get("campo") and a["campo"] not in CAMPI_TESTO | CAMPI_LISTA:
        a["pertinente"], a["perche"] = False, f"il campo '{a['campo']}' non si modifica con una proposta"
    return {"analisi": a}

def rimanda(s):
    """Torna a chi ha proposto, con il perche'. Resta aperta: nessuno la chiude."""
    p = s["proposta"]; p["stato"] = "rimandata"; p["nota"] = "; ".join(s["problemi"]) or s["analisi"]["perche"]
    scrivi(s["file"], p); print("rimandata:", p["nota"]); return {}

def pronta(s):
    """Il triage e' finito e la proposta merita un editor: l'esito resta nel file, con il riassunto."""
    p, a = s["proposta"], s["analisi"]
    p["stato"] = "pronta"; p["analisi"] = {k: a.get(k) for k in ("riassunto", "campo", "valore", "dubbi") if a.get(k) is not None}
    scrivi(s["file"], p); print("pronta per la decisione"); return {}

def decidi(s):
    """Il punto di controllo umano: se la decisione non c'e', il grafo si ferma e aspetta."""
    if s.get("decisione"): return {}
    a, p = s["analisi"], s["proposta"]
    cosa = f"voce nuova: {p['prefLabel']['en']}" if p.get("tipo") == "nuova-voce" else f"modifica: {a.get('campo')} = {a.get('valore')}"
    return {"decisione": interrupt(f"\n{s['file']}  voce {p['voce']}\n  {a.get('riassunto', '')}\n"
                                   f"  {cosa}\n  dubbi: {'; '.join(a.get('dubbi') or []) or 'nessuno'}\n")}

def applica(s):
    """Scrive la modifica nella voce (testo sostituito o elemento aggiunto a una lista), oppure crea la voce nuova."""
    a, p = s["analisi"], s["proposta"]
    if p.get("tipo") == "nuova-voce":                    # il file nasce dalla proposta, con lo stato "proposed"
        v = {"id": p["voce"], "status": "proposed", "perspective": p["perspective"], "prefLabel": p["prefLabel"]}
        for campo in ("altLabel", "definition", "scopeNote", "broader", "related", "sources", "alignments"):
            if p.get(campo): v[campo] = p[campo]
        scrivi(CONCEPTS / f"{p['voce']}.yaml", v)
        p["stato"] = "approvata"; p["motivazione_decisione"] = s["decisione"]["motivazione"]; scrivi(s["file"], p)
        print(f"creata: {p['voce']}"); return {}
    if not a.get("campo"): sys.exit("la modifica non ha campo e valore: scrivili nel file della proposta (campo: altLabel.it, valore: [...]) e rilancia")
    v = dict(s["voce"]); parti = a["campo"].split(".")
    if a["campo"] in CAMPI_LISTA:
        lista = v.setdefault(parti[0], {}).setdefault(parti[1], []) if len(parti) == 2 else v.setdefault(parti[0], [])
        lista += [x for x in a["valore"] if x not in lista]
    else:
        v.setdefault(parti[0], {})[parti[1]] = a["valore"]
    scrivi(CONCEPTS / f"{s['proposta']['voce']}.yaml", v)
    p = s["proposta"]; p["stato"] = "approvata"; p["motivazione_decisione"] = s["decisione"]["motivazione"]; scrivi(s["file"], p)
    print(f"applicata: {a['campo']} di {p['voce']}"); return {}

def rifiuta(s):
    p = s["proposta"]; p["stato"] = "rifiutata"; p["motivazione_decisione"] = s["decisione"]["motivazione"]
    scrivi(s["file"], p); print("rifiutata, con motivazione"); return {}


# ---- il grafo -----------------------------------------------------------------------
g = StateGraph(Stato)
for nome, fn in [("leggi", leggi), ("controlla", controlla), ("analizza", analizza), ("rimanda", rimanda), ("pronta", pronta),
                 ("decidi", decidi), ("applica", applica), ("rifiuta", rifiuta)]:
    g.add_node(nome, fn)
g.add_edge(START, "leggi")
g.add_edge("leggi", "controlla")
g.add_conditional_edges("controlla", lambda s: "rimanda" if s["problemi"] else "analizza")
g.add_conditional_edges("analizza", lambda s: "rimanda" if not s["analisi"]["pertinente"] else ("pronta" if s.get("solo_triage") else "decidi"))
g.add_conditional_edges("decidi", lambda s: "applica" if s["decisione"]["esito"] == "approvata" else "rifiuta")
for fine in ("applica", "rifiuta", "rimanda", "pronta"): g.add_edge(fine, END)
grafo = g.compile(checkpointer=MemorySaver())

if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("file"); ap.add_argument("--decidi", choices=["approva", "rifiuta"]); ap.add_argument("--motivazione", default="")
    ap.add_argument("--solo-triage", action="store_true", help="senza tastiera e senza decisione: si ferma a 'pronta'")
    a = ap.parse_args()
    stato = {"file": a.file, "solo_triage": a.solo_triage}
    if a.decidi:
        if len(a.motivazione.split()) < 5: sys.exit("la decisione vuole una motivazione: la leggera' chi ha proposto")
        stato["decisione"] = {"esito": "approvata" if a.decidi == "approva" else "rifiutata", "motivazione": a.motivazione}
    cfg = {"configurable": {"thread_id": a.file}}
    r = grafo.invoke(stato, cfg)
    if "__interrupt__" in r:                                  # a tastiera: il grafo si e' fermato a "decidi"
        print(r["__interrupt__"][0].value)
        esito = ""
        while esito not in ("approva", "rifiuta"): esito = input("approva / rifiuta? ").strip().lower()
        motivazione = ""
        while len(motivazione.split()) < 5: motivazione = input("motivazione (almeno cinque parole): ").strip()
        grafo.invoke(Command(resume={"esito": "approvata" if esito == "approva" else "rifiutata", "motivazione": motivazione}), cfg)
    p = yaml.safe_load(open(a.file, encoding="utf-8"))
    sys.exit(0 if p.get("stato") == "approvata" else 3)      # 0: c'e' una modifica da committare; 3: niente da committare
