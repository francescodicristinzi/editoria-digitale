#!/usr/bin/env bash
# La catena di produzione, dal sorgente al sito. Si ferma al primo passo che fallisce.
#
#   ./pipeline.sh          valida, costruisce pagine ed export, il PDF, il sito in site/
#   ./pipeline.sh serve    come sopra, poi apre il sito in locale su http://127.0.0.1:8000
set -e                                   # un errore ferma tutto: come && fra i comandi
cd "$(dirname "$0")"                     # funziona da qualunque cartella lo si lanci

echo "1/4  validazione del sorgente"
python3 scripts/validate.py

echo "2/4  pagine Markdown ed export in docs/"
python3 scripts/build.py

echo "3/4  documento stampabile: docs/dati/tesauro.pdf"
(cd docs/dati && pandoc tesauro.md --from markdown --standalone --toc --toc-depth=2 \
    --css stampa.css --pdf-engine=weasyprint --pdf-engine-opt=--full-fonts --metadata lang=it -o tesauro.pdf)
# --full-fonts: WeasyPrint incorpora i font interi invece di un sottoinsieme. Senza, il PDF
# si apre con pagine bianche in alcuni lettori (poppler, e quindi molte anteprime): il testo
# c'e' ma il font ridotto non si disegna. Verificato: con il sottoinsieme il lettore segnala
# "Couldn't create a font", con i font interi nessun errore e le pagine sono leggibili.

echo "4/4  sito in site/"
mkdocs build --quiet

if [ "$1" = "serve" ]; then
    echo "sito in locale: http://127.0.0.1:8000  (Ctrl+C per fermare)"
    mkdocs serve --quiet
fi
