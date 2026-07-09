#!/bin/bash
# Esegue le eval del repo contro Claude Code in modalità headless e produce un
# rapporto con doppio livello di verifica per ciascuna: (1) assertion
# deterministiche must_include/must_not_include quando l'eval le ha (grep
# sulla risposta, nessun giudizio linguistico coinvolto); (2) giudice LLM
# come secondo livello, per la qualità comportamentale che una stringa non
# cattura. Un FAIL sulle assertion deterministiche non arriva nemmeno al
# giudice: è già un fatto, non un'opinione.
#
# Va lanciato da un terminale normale (NON dentro una sessione Claude Code:
# la sessione annidata non ha credenziali). Le eval TEMPLATE, che descrivono
# un comportamento senza un prompt concreto, vengono saltate e vanno
# collaudate in sessione interattiva (v. Workflow "ripasso end-to-end").
#
# Uso:  scripts/esegui_evals.sh [id ...]     # senza argomenti: tutte
set -euo pipefail
cd "$(dirname "$0")/.."

command -v claude >/dev/null || { echo "claude CLI non trovato"; exit 1; }
command -v python3 >/dev/null || { echo "python3 non trovato"; exit 1; }
[ -z "${CLAUDECODE:-}" ] || { echo "Non lanciare da dentro Claude Code: apri un terminale normale."; exit 1; }

STAMP=$(date +%Y%m%d_%H%M)
OUT="evals/risultati/$STAMP"
mkdir -p "$OUT"
TOOLS="Skill,mcp__lex-corpus,mcp__lex-corpus__lex_stato_corpus,mcp__lex-corpus__lex_cerca_norma,mcp__lex-corpus__lex_leggi_articolo,mcp__lex-corpus__lex_cerca_giurisprudenza,mcp__lex-corpus__lex_cerca_prassi,mcp__lex-corpus__lex_verifica_citazione"

python3 - "$@" <<'PYEOF' > "$OUT/_lista.tsv"
import json, sys
evals = json.load(open('evals/evals.json'))['evals']
ids = {int(x) for x in sys.argv[1:]} if len(sys.argv) > 1 else None
for e in evals:
    if ids and e['id'] not in ids:
        continue
    if e['prompt'].startswith('TEMPLATE'):
        print(f"{e['id']}\tSKIP_TEMPLATE\t")
        continue
    dati = {'p': e['prompt'], 'a': e['expected_output'], 'checks': e.get('checks', {})}
    print(f"{e['id']}\tRUN\t{json.dumps(dati, ensure_ascii=False)}")
PYEOF

PASS=0; FAIL=0; SKIP=0
while IFS=$'\t' read -r ID AZIONE DATI; do
  if [ "$AZIONE" = "SKIP_TEMPLATE" ]; then
    SKIP=$((SKIP+1)); echo "eval $ID: TEMPLATE (collaudo interattivo, v. Workflow ripasso end-to-end)"; continue
  fi
  PROMPT=$(printf '%s' "$DATI" | python3 -c "import json,sys; print(json.load(sys.stdin)['p'])")
  ATTESO=$(printf '%s' "$DATI" | python3 -c "import json,sys; print(json.load(sys.stdin)['a'])")
  echo "eval $ID: esecuzione..."
  claude -p "$PROMPT" --allowedTools "$TOOLS" --output-format text > "$OUT/$ID.risposta.md" 2>"$OUT/$ID.err" || true

  # Livello 1: assertion deterministiche (fatto, non opinione)
  ESITO_CHECK=$(printf '%s' "$DATI" | python3 -c "
import json, sys
d = json.load(sys.stdin)
checks = d.get('checks') or {}
risposta = open('$OUT/$ID.risposta.md', encoding='utf-8').read()
mancanti = [s for s in checks.get('must_include', []) if s.lower() not in risposta.lower()]
vietati = [s for s in checks.get('must_not_include', []) if s.lower() in risposta.lower()]
if mancanti or vietati:
    dett = []
    if mancanti: dett.append('mancanti: ' + '; '.join(mancanti))
    if vietati: dett.append('presenti e vietati: ' + '; '.join(vietati))
    print('FAIL_ASSERTION\t' + ' | '.join(dett))
else:
    print('OK\t' + ('nessuna assertion definita' if not checks.get('must_include') and not checks.get('must_not_include') else 'assertion soddisfatte'))
")
  IFS=$'\t' read -r STATO_CHECK DETT_CHECK <<< "$ESITO_CHECK"

  if [ "$STATO_CHECK" = "FAIL_ASSERTION" ]; then
    echo "FAIL: assertion deterministica — $DETT_CHECK" > "$OUT/$ID.giudizio.txt"
    FAIL=$((FAIL+1))
    echo "  -> FAIL (assertion deterministica: $DETT_CHECK)"
    continue
  fi

  # Livello 2: giudice LLM, per la qualità comportamentale
  GIUDIZIO=$(claude -p "Sei il giudice di una eval. RISPOSTA DA VALUTARE: <<<$(cat "$OUT/$ID.risposta.md")>>> COMPORTAMENTO ATTESO: <<<$ATTESO>>> Rispondi con una sola riga: PASS oppure FAIL, due punti, motivo in una frase. Sii severo sugli estremi normativi: un estremo diverso dall'atteso è FAIL." --output-format text 2>/dev/null || echo "FAIL: giudice non eseguito")
  echo "$GIUDIZIO" > "$OUT/$ID.giudizio.txt"
  case "$GIUDIZIO" in PASS*) PASS=$((PASS+1));; *) FAIL=$((FAIL+1));; esac
  echo "  -> $GIUDIZIO ($DETT_CHECK)"
done < "$OUT/_lista.tsv"

echo ""
echo "Esito: PASS=$PASS FAIL=$FAIL TEMPLATE_SALTATE=$SKIP — dettagli in $OUT/"
[ "$FAIL" -eq 0 ]
