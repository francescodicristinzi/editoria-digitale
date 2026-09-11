# Come si lavora

Chiunque può leggere, proporre e discutere, in pubblico. Pochi possono decidere e unire, e
devono scrivere il perché. Le tre prospettive del tesauro, giuridica, tecnica e concettuale, sono
una proprietà delle voci, non un ruolo: nessuno ha un diritto di veto su un'area.

## Chi fa che cosa

| Chi | Che cosa può fare |
|---|---|
| chiunque | consultare il sito; proporre una voce nuova o una modifica dai moduli; commentare le proposte degli altri |
| editor | tutto quanto sopra, più: decidere una proposta, modificare le voci direttamente, unire le pull request |

Gli editor sono le persone con diritto di scrittura sul repository. Sono almeno due, così
nessuno è indispensabile. Chi ha avuto tre proposte accolte può essere invitato a diventare editor.

## Come si propone

Dai due moduli, **Proponi una modifica a una voce** e **Proponi una voce nuova**. Chiedono sempre
una motivazione e una fonte con il punto preciso, articolo o clausola. Non serve conoscere il
formato dei dati: si scrive che cosa si vorrebbe cambiare, e il resto lo fa l'istruttoria.

## L'istruttoria

Ogni proposta passa da tre passaggi, nell'ordine.

1. **Il controllo automatico** verifica che ci siano la richiesta, una motivazione di almeno venti
   parole e una fonte del registro con il punto preciso. Se manca qualcosa, la proposta torna a
   chi l'ha scritta con la lista, e resta aperta.
2. **La lettura assistita** da un modello linguistico giudica se la proposta è pertinente e la
   traduce nei campi della voce: quale campo, quale valore. Una proposta fuori tema o incomprensibile
   torna a chi l'ha scritta, con il perché, e resta aperta. Il modello non decide mai: legge,
   riassume, segnala i dubbi. Se il modello non risponde, la proposta passa all'editor senza filtro.
3. **La decisione** è di un editor, che scrive nel commento della proposta `/approva` oppure
   `/rifiuta`, seguito dalla motivazione. Senza motivazione il comando non fa niente.

## La decisione, e dove resta scritta

Se accolta, la modifica viene applicata su un ramo, validata, e committata con la motivazione, la
proposta e la fonte nel messaggio. Da quel ramo nasce una **pull request**: è il diff visibile della
decisione. Un editor la unisce; il merge rigenera il sito e chiude la proposta. Il messaggio di commit
è il record della decisione: ha data, autore, identificativo stabile, e resta nella storia della
voce.

Se non accolta, la motivazione viene scritta nella proposta, che viene chiusa. Nessuna proposta viene
chiusa senza una ragione leggibile.

## Le modifiche di iniziativa dell'editor

Un editor può modificare le voci senza una proposta: su un ramo, con una pull request compilata
secondo il template, motivazione e fonte comprese. Nessuno scrive direttamente su `main`, nemmeno
gli editor: la protezione del ramo lo impedisce.

## Due livelli di modifica

| Livello | Che cosa comprende | Che cosa richiede |
|---|---|---|
| formale | refusi, collegamenti, formattazione: nulla che cambi il significato | una pull request, con il messaggio che dice cosa |
| di merito | definizione, traduzione, nota d'ambito, varianti, relazioni, stato di una voce | una pull request con motivazione e fonte |

Le voci non si cancellano: si ritirano, con il rimando alla voce che le sostituisce.

## Che cosa fa la macchina, e che cosa no

La macchina controlla la forma delle voci, i riferimenti, le fonti, la coerenza delle relazioni;
rimanda indietro le proposte incomplete o fuori tema; applica le decisioni prese; costruisce e
pubblica il sito a ogni modifica unita; riporta ogni esito a chi ha proposto. Non decide mai se una
proposta è giusta: quello è il giudizio, ed è delle persone.

## Limiti dichiarati

- Finché gli editor sono una persona sola, proponente e decisore possono coincidere, e la revisione
  della pull request da parte di un secondo editor non esiste.
- La protezione del ramo e i segreti sono impostazioni della piattaforma, non file del repository:
  chi clona il progetto deve rifarle.
- Il giudizio di pertinenza del modello è un filtro all'ingresso, non una decisione: può sbagliare
  in entrambe le direzioni, e per questo rimanda ma non chiude mai.
