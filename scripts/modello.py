#!/usr/bin/env python3
"""Una domanda a un modello linguistico, tramite Ollama. Legge chiave, endpoint e
modello da .env. Se la chiave manca o il servizio non risponde, restituisce None:
chi chiama va avanti senza modello. Temperatura zero: stessa domanda, stessa risposta."""
import json, os, pathlib, urllib.request

def env():
    """Le variabili di .env, se c'e', altrimenti quelle d'ambiente."""
    valori = dict(os.environ)
    f = pathlib.Path(__file__).resolve().parents[1] / ".env"
    if f.exists():
        for riga in f.read_text(encoding="utf-8").splitlines():
            if "=" in riga and not riga.startswith("#"):
                k, v = riga.split("=", 1); valori.setdefault(k.strip(), v.strip())
    return valori

def chiedi(sistema, domanda, modello=None, timeout=180):
    e = env()
    if not e.get("OLLAMA_API_KEY"): return None
    corpo = {"model": modello or e.get("OLLAMA_MODEL") or "gpt-oss:120b", "temperature": 0,
             "messages": [{"role": "system", "content": sistema}, {"role": "user", "content": domanda}]}
    req = urllib.request.Request(e.get("OLLAMA_ENDPOINT", "https://ollama.com/v1/chat/completions"),
                                 data=json.dumps(corpo).encode(), method="POST",
                                 headers={"Authorization": f"Bearer {e['OLLAMA_API_KEY']}", "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return json.load(r)["choices"][0]["message"]["content"]
    except Exception as errore:
        print(f"(modello non disponibile: {errore})"); return None

def json_dalla_risposta(testo):
    """I modelli a volte avvolgono il JSON in ``` o in una frase: si prende il primo oggetto."""
    if not testo: return None
    inizio, fine = testo.find("{"), testo.rfind("}")
    try: return json.loads(testo[inizio:fine + 1])
    except Exception: return None
