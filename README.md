# AI Governance Thesaurus

Tesauro bilingue, inglese e italiano, sulla governance dell'intelligenza artificiale.
Mette in dialogo tre prospettive, normativa-giuridica, tecnico-operativa e
concettuale-filosofica, a partire dalle fonti che le definiscono: l'AI Act, gli standard
ISO/IEC, il framework del NIST.

Parte da un primo nucleo di voci raccolte dal gruppo di lavoro e lo
riorganizza in un modello dove ogni voce ha una definizione citata dalla fonte, relazioni
con le altre voci e, dove esiste, l'allineamento con lo standard tecnico corrispondente.

## Com'è fatto

```
data/
  concepts/            una voce per file, in YAML (README.md spiega i campi)
  sources.yaml         il registro delle fonti: ogni voce le cita per chiave
  schema/voce.schema.json   il contratto del modello: campi, valori ammessi
  voce.template.yaml   il modello da copiare per una voce nuova
scripts/
  nuova-voce.py        crea una voce dal template
  validate.py          controlla che il sorgente sia coerente
  build.py             scrive le pagine Markdown in docs/
templates/             la forma delle pagine (una voce, l'indice)
pipeline.sh            la catena: valida, costruisce, genera il sito
mkdocs.yml             la configurazione del sito
```

Il sorgente è `data/`. Tutto il resto, `docs/` e `site/`, si rigenera da lì e non si versiona.

## Installazione

Serve Python 3. Le librerie sono elencate in `requirements.txt`:

```bash
pip install -r requirements.txt
```

## Costruire il sito

```bash
./pipeline.sh          # valida il sorgente, scrive le pagine, genera il sito in site/
./pipeline.sh serve    # come sopra, e apre il sito in locale su http://127.0.0.1:8000
```

La catena si ferma al primo passo che fallisce: un sorgente non valido non diventa mai un sito.

## Aggiungere o modificare una voce

1. Crea il file dal template, con l'identificativo scelto una volta per sempre:

   ```bash
   python3 scripts/nuova-voce.py ai-literacy
   ```

   Per modificare una voce esistente, apri direttamente `data/concepts/<id>.yaml`.

2. Riempi i campi seguendo la fonte: il termine come lo scrive l'atto, la definizione copiata
   e non parafrasata, l'articolo o la clausola nel `locator`. I campi sono spiegati in
   [`data/concepts/README.md`](data/concepts/README.md).

3. Controlla e guarda il risultato:

   ```bash
   ./pipeline.sh serve
   ```

   Il validatore dice in una riga che cosa non va: un riferimento a una voce che non esiste,
   un termine già usato, una fonte senza articolo, una voce approvata senza traduzione.

## Consultare il tesauro

- **L'indice** elenca le voci con traduzione, stato e prospettiva, e sotto la gerarchia:
  le radici e i loro termini più specifici.
- **La pagina di una voce** mostra le definizioni nelle due lingue, le varianti, le relazioni
  (BT più generale, NT più specifici, RT associati, tutte cliccabili), le fonti con il punto
  preciso e il collegamento al testo, e l'allineamento agli standard con il tipo di relazione
  SKOS e la nota che spiega la differenza. Se lo standard è a pagamento, la pagina lo dice.
- **Una voce ritirata** resta consultabile e rimanda alla voce che la sostituisce: nulla si
  cancella, così chi l'ha citata la ritrova.

## Le regole del modello

1. Un file per voce.
2. L'identificativo è per sempre; il termine può cambiare.
3. Le relazioni si scrivono in una direzione sola: BT e RT; NT e gli RT inversi li calcola il build.
4. Nessun dato derivabile nel file: date e storia le dà git.
5. Le fonti si citano per chiave dal registro, con il punto preciso nella voce.
6. I nomi dei campi sono quelli di SKOS.
7. Solo termini: niente categorie o titoli di sezione.
8. Una voce pubblicata non si cancella: si ritira con `status: deprecated` e `replacedBy`.

## Proporre e decidere

Il tesauro è aperto: chiunque può proporre, dai moduli del repository, una modifica a una voce o una
voce nuova; le regole complete sono in [`GOVERNANCE.md`](GOVERNANCE.md), e sul sito la pagina
"Come contribuire" le spiega a chi propone.

Il flusso, in breve:

1. La proposta arriva come issue dal modulo. Un workflow la trasforma in un file di `proposte/` e
   lancia l'istruttoria: il codice controlla motivazione e fonti, un modello linguistico giudica la
   pertinenza e traduce la richiesta nei campi della voce. L'esito torna sulla issue come commento.
2. Un editor scrive nella issue `/approva` o `/rifiuta`, seguito dalla motivazione.
3. Se accolta, la modifica viene applicata su un ramo, validata e committata con la motivazione nel
   messaggio; nasce una pull request, e il merge la pubblica. Se non accolta, la motivazione resta
   nella issue, che viene chiusa. Nessuna proposta viene chiusa in silenzio.

In locale si fa la stessa cosa senza GitHub, con un file in `proposte/` scritto sul modello di
`proposte/proposta.template.yaml` o `proposte/nuova-voce.template.yaml`:

```bash
./proposta.sh proposte/007-ce-marking.yaml                 # chiede la decisione a tastiera
./proposta.sh proposte/007-ce-marking.yaml approva "..."   # decisione già data
```

Il modello linguistico si configura in `.env` (vedi `.env.example`); senza, l'istruttoria funziona
lo stesso e passa ogni proposta completa all'editor.

## Pubblicazione

A ogni modifica su `main`, un workflow esegue `pipeline.sh` e pubblica `site/` su GitHub Pages:
<https://francescodicristinzi.github.io/editoria-digitale>. Le impostazioni che non stanno nei file:
Pages con sorgente "GitHub Actions"; in Actions → General → Workflow permissions, "Read and write" e
"Allow GitHub Actions to create and approve pull requests" (senza, il workflow della decisione non può
aprire la pull request); il segreto `OLLAMA_API_KEY` e la variabile `OLLAMA_MODEL`; la protezione del
ramo `main` con "Require a pull request before merging"; in General → Pull Requests, "Automatically
delete head branches", così il ramo della proposta sparisce dopo il merge. Le etichette delle issue le
crea il workflow, se mancano. Sulla pull request aperta dal workflow GitHub chiede a un editor di premere
"Approve workflows to run" prima di eseguire la validazione: la modifica è comunque già stata validata
prima del commit.
