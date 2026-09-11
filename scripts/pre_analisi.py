#!/usr/bin/env python3
"""La pre-analisi di una proposta con un modello linguistico: e' pertinente? che cosa
chiede, tradotto nei campi della voce? Il modello non decide e non scrive nei file."""
import json, pathlib, yaml
from modello import chiedi, json_dalla_risposta

SISTEMA = """Sei l'assistente dell'istruttoria di un tesauro bilingue (inglese-italiano) sulla governance
dell'intelligenza artificiale. Ricevi una proposta e la voce attuale. Se la voce attuale e' vuota, la proposta e' una VOCE NUOVA: giudica
se il concetto riguarda la governance dell'IA e se termine, definizione e fonte sono seri e coerenti;
in quel caso "campo" e "valore" restano null.
Rispondi SOLO con un oggetto JSON con queste chiavi:
- "pertinente": true se la proposta riguarda davvero il contenuto della voce ed e' formulata in modo
  comprensibile e serio; false se e' vuota, scherzosa, offensiva, incoerente o non c'entra con la voce.
- "perche": una frase in italiano che spiega il giudizio, rivolta a chi ha proposto.
- "campo": se pertinente, il campo della voce da modificare, uno fra: prefLabel.en, prefLabel.it,
  definition.en, definition.it, scopeNote.en, scopeNote.it, altLabel.en, altLabel.it, related, broader.
- "valore": se pertinente, il nuovo valore: un testo per i campi di testo; una lista di stringhe per
  altLabel; una lista di identificativi di voci per related e broader.
- "riassunto": tre righe in italiano per l'editor: che cosa chiede, con quale motivazione, con quale fonte.
- "dubbi": lista di punti che l'editor dovrebbe verificare prima di decidere (anche vuota).
Regole: non inventare fonti, articoli o clausole; non aggiungere nulla che la proposta non dica;
non giudicare se la modifica sia giusta nel merito, solo se e' pertinente e che cosa chiede."""

def pre_analisi(proposta, voce, modello=None):
    domanda = "PROPOSTA:\n" + yaml.safe_dump(proposta, allow_unicode=True, sort_keys=False) + "\nVOCE ATTUALE:\n" + yaml.safe_dump(voce, allow_unicode=True, sort_keys=False)
    return json_dalla_risposta(chiedi(SISTEMA, domanda, modello))
