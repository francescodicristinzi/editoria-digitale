#!/usr/bin/env bash
# Una proposta, dall'istruttoria al ramo: la pull request in locale.
#   ./proposta.sh proposte/007-ce-marking.yaml                          chiede la decisione a tastiera
#   ./proposta.sh proposte/007-ce-marking.yaml approva "motivazione"    decisione gia' data (cosi' fara' Actions)
set -e
cd "$(dirname "$0")"
FILE="$1"; RAMO="proposta/$(basename "$FILE" .yaml)"; BASE=$(git rev-parse --abbrev-ref HEAD)
[ -z "$(git status --porcelain data proposte)" ] || { echo "modifiche non committate: prima commit o scarta"; exit 1; }

git checkout -q -b "$RAMO"
set +e
if [ -n "$2" ]; then python3 scripts/istruttoria.py "$FILE" --decidi "$2" --motivazione "$3"; else python3 scripts/istruttoria.py "$FILE"; fi
ESITO=$?                                                   # 0 approvata, 3 nessuna modifica, altro: errore
set -e
if [ "$ESITO" != 0 ] && [ "$ESITO" != 3 ]; then
    git checkout -q -- data proposte 2>/dev/null || true; git checkout -q "$BASE"; git branch -q -D "$RAMO"
    echo "istruttoria interrotta: niente e' cambiato"; exit 1
fi

if [ "$ESITO" = 0 ] && python3 scripts/validate.py; then
    MOTIVAZIONE=$(python3 -c "import yaml,sys; print(yaml.safe_load(open(sys.argv[1]))['motivazione_decisione'])" "$FILE")
    git add data proposte
    git commit -q -m "feat(voce): $(basename "$FILE" .yaml)

$MOTIVAZIONE

Proposta: $FILE
Deciso-da: editor"
    git checkout -q "$BASE"
    echo "modifica sul ramo $RAMO, validata e committata. Per unirla:  git merge $RAMO"
else
    git checkout -q -- data 2>/dev/null || true             # la voce torna com'era
    git checkout -q "$BASE"; git branch -q -D "$RAMO"
    git add proposte; git diff --cached --quiet || git commit -q -m "chore(proposte): $(basename "$FILE" .yaml), esito dell'istruttoria"
    echo "nessuna modifica alle voci; l'esito e' nel file della proposta"
fi
