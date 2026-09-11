# Le voci del tesauro

Una voce è un file YAML, uno per concetto. **Il nome del file è l'identificativo** e non
cambia mai. Dentro ci sono solo i fatti che una persona decide: ciò che si può calcolare
(termini più specifici, date, storia, indirizzo web) non si scrive, lo ricava il build.

## I campi

| Campo | Obbligatorio | Valori | Che cosa dice |
|---|---|---|---|
| `id` | sì | slug in minuscolo con trattini, uguale al nome del file | l'identificativo, per sempre |
| `status` | sì | `approved`, `proposed`, `deprecated` | se il comitato l'ha approvata, se è in attesa, se è stata ritirata |
| `perspective` | sì, almeno una | `legal`, `technical`, `conceptual` | da quali prospettive il concetto è definito: normativa, tecnica, concettuale |
| `prefLabel` | sì | `en` e `it` | il termine preferito nelle due lingue; in italiano quello della versione ufficiale dell'atto |
| `altLabel` | no | liste per `en` e `it` | varianti non preferite: sigle, sinonimi (UF) |
| `definition` | sì | `en` e `it` | la definizione, citata dalla fonte, non parafrasata |
| `scopeNote` | no | `en` e `it` | quando usare questo termine e non un altro |
| `broader` | no | lista di `id` | i termini più generali (BT); i più specifici (NT) si calcolano |
| `related` | no | lista di `id` | i termini associati (RT); basta scriverli da una parte |
| `sources` | sì, almeno una | `ref` (chiave di `../sources.yaml`) e `locator` | dove sta la definizione: atto e articolo, standard e clausola |
| `alignments` | no | `standard`, `clause`, `term`, `relation`, `note` | come il termine giuridico corrisponde a uno standard tecnico |
| `replacedBy` | solo se `deprecated` | un `id` | la voce che sostituisce questa |

La `relation` di un allineamento è una delle cinque di SKOS: `exactMatch` (stesso concetto),
`closeMatch` (quasi), `broadMatch` (lo standard è più generale), `narrowMatch` (più specifico),
`relatedMatch` (associato). Chi scrive un allineamento ha letto la clausola: non c'è un campo per
dichiararlo. Se lo standard è a pagamento lo dice il registro (`access: paid`), e il sito e gli export
mostrano da soli l'avvertenza che l'allineamento non è verificabile sul testo.

## Le regole

1. Un file per voce.
2. L'`id` è per sempre; il termine può cambiare.
3. Le relazioni si scrivono in una direzione sola.
4. Nessun dato derivabile nel file.
5. Le fonti si citano per chiave, con il punto preciso nella voce.
6. I nomi dei campi sono quelli di SKOS.
7. Solo termini: niente categorie o titoli di sezione.
8. Una voce pubblicata non si cancella: si ritira con `status: deprecated` e `replacedBy`.

## Una voce minima

```yaml
id: ai-office
status: approved
perspective:
- legal
prefLabel:
  en: AI Office
  it: Ufficio per l'IA
definition:
  en: The Commission's function of contributing to the implementation, monitoring and supervision of AI systems and general-purpose AI models, and AI governance, provided for in Commission Decision of 24 January 2024.
  it: Funzione della Commissione volta a contribuire all'attuazione, al monitoraggio e alla supervisione dei sistemi di IA e dei modelli di IA per finalità generali e alla governance dell'IA, prevista dalla decisione della Commissione del 24 gennaio 2024.
related:
- scientific-panel-of-independent-experts
sources:
- ref: ai-act
  locator: Art. 3(47); Art. 64
```
