# Contribuire

Una sola regola non negoziabile: **ogni nuova regola di comportamento in `SKILL.md` entra solo con almeno una eval che la verifica**, e la risposta attesa si scrive solo dopo averla controllata a mano sulla fonte ufficiale (Normattiva per le leggi italiane, EUR-Lex per il diritto UE) — mai a memoria o per plausibilità. Estendere un catalogo in `references/` (una nuova fonte, una nuova materia) non richiede una nuova eval, ma richiede la stessa disciplina di verifica sulla fonte prima di scrivere la voce.

## Aggiungere o modificare una eval

Ogni voce di `evals/evals.json` ha questa forma:

```json
{
  "id": 44,
  "prompt": "il quesito posto alla skill",
  "expected_output": "descrizione narrativa del comportamento atteso, verificata sulla fonte",
  "checks": {
    "must_include": ["stringhe che devono comparire nella risposta"],
    "must_not_include": ["stringhe che NON devono comparire"],
    "tool_input_must_not_include": ["opzionale: stringhe vietate negli input ai tool, non solo nella risposta"]
  }
}
```

I prompt che iniziano con `TEMPLATE` descrivono un comportamento senza un caso concreto: non girano nel runner headless, si collaudano in sessione interattiva confrontando la risposta con `expected_output`.

## Prima di aprire una PR

Esegui in locale, da un terminale normale (non da dentro una sessione Claude Code):

```bash
python3 scripts/verifica_skill.py   # controlli statici: evals.json, frontmatter, puntatori, catalogo normativo
shellcheck scripts/*.sh             # stile degli script di shell
scripts/esegui_evals.sh <id>        # ripassa le eval toccate dalla modifica
```

La CI (`quality.yml`) ripete i primi due in modo bloccante a ogni push/PR; `scripts/verifica_fonti.sh` (raggiungibilità degli endpoint) è solo informativo, perché dipende da rete e anti-bot esterni.

## Cosa NON entra nel repo

Solo capacità presenti: niente roadmap, niente "sviluppi futuri", niente riferimenti a sistemi in costruzione attorno alla skill. Solo fonti gratuite o ufficiali: mai banche dati commerciali (DeJure, Pluris, OneLegale) né massime redazionali di terzi.
