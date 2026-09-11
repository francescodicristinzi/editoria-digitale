#!/usr/bin/env python3
"""Riporta sulla issue l'esito scritto nel file della proposta: un commento e un'etichetta.
  python3 scripts/esito_issue.py proposte/007-ce-marking.yaml 7 [url-della-pull-request]
Usa `gh`, presente sui runner di GitHub, con GH_TOKEN nell'ambiente."""
import subprocess, sys, yaml

file, numero = sys.argv[1], sys.argv[2]; pr = sys.argv[3] if len(sys.argv) > 3 else ""
p = yaml.safe_load(open(file, encoding="utf-8")); stato = p.get("stato", "")
a = p.get("analisi") or {}

testi = {
    "rimandata": f"Grazie per la proposta. Prima di passarla a un editor serve una cosa:\n\n> {p.get('nota', '')}\n\n"
                 "Puoi modificare la proposta: il controllo si riesegue da solo. Finche' resta cosi', rimane aperta e nessuno la chiude.",
    "pronta": "Controllo superato: la proposta passa a un editor.\n\n" + (f"**Riassunto.** {a.get('riassunto', '')}\n\n" if a.get("riassunto") else "")
              + (f"**Modifica letta dalla richiesta:** `{a.get('campo')}` = {a.get('valore')}\n\n" if a.get("campo") else "")
              + (("**Da verificare prima di decidere:**\n" + "\n".join(f"- {d}" for d in a.get("dubbi", []))) if a.get("dubbi") else ""),
    "approvata": f"**Accolta.** {p.get('motivazione_decisione', '')}\n\n" + (f"La modifica e' nella pull request {pr}: entra nel tesauro quando viene unita." if pr else ""),
    "rifiutata": f"**Non accolta.** {p.get('motivazione_decisione', '')}\n\nLa motivazione resta qui, pubblica: anche un no e' informazione.",
}
etichette = {"rimandata": "da-integrare", "pronta": "in-istruttoria", "approvata": "decisa", "rifiutata": "decisa"}
if stato not in testi: sys.exit(f"stato '{stato}' senza esito da riportare")
for nome, colore in (("proposta", "0e8a16"), ("modifica", "1d76db"), ("nuova-voce", "5319e7"),
                     ("da-integrare", "fbca04"), ("in-istruttoria", "c5def5"), ("decisa", "6f42c1")):
    subprocess.run(["gh", "label", "create", nome, "--color", colore, "--force"], capture_output=True)   # se manca, nasce

subprocess.run(["gh", "issue", "comment", numero, "--body", testi[stato]], check=True)
for vecchia in set(etichette.values()) - {etichette[stato]}:
    subprocess.run(["gh", "issue", "edit", numero, "--remove-label", vecchia], capture_output=True)
subprocess.run(["gh", "issue", "edit", numero, "--add-label", ",".join(x for x in ("proposta", p.get("tipo", ""), etichette[stato]) if x)], capture_output=True)
if stato == "rifiutata":
    subprocess.run(["gh", "issue", "close", numero, "--reason", "not planned"], check=True)
print(f"issue #{numero}: {stato}")
