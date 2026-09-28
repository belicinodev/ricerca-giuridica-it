# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repository is

This repo is **not runtime code**. It is a distributable **Agent Skill** (`ricerca-giuridica-it`, format published as an open standard by Anthropic on 2025-12-18, spec at agentskills.io) that encodes a *method* for Italian and EU legal research — routing to official sources, citation discipline, in-force (vigenza) verification, and query minimization for professional-secrecy contexts. It deliberately adds no legal knowledge of its own: without a connected corpus it adds discipline, not facts.

Developed and tested against **Claude** only (claude.ai, Desktop, Cowork, Claude Code) — that's the only environment the evals run against. ChatGPT/Codex (OpenAI) also loads the same SKILL.md format per their own docs, so the skill is expected to work there by format compatibility, but this project makes no compatibility claim beyond that: keep SKILL.md's body platform-neutral (no Claude-Desktop-specific UI references — "quando l'ambiente lo consente" already does this correctly for file generation) so as not to gratuitously break on other hosts, but don't add OpenAI-specific frontmatter (e.g. `agents/openai.yaml`) without verifying its exact spec first — same non-negotiable "verify before you write it down" rule as everything else in this repo.

The "source" is prose: `SKILL.md` is a behavioral specification loaded into Claude's context, not a program that executes. Editing it changes model behavior, so treat wording as load-bearing.

## Architecture

- `.claude/skills/ricerca-giuridica-it/SKILL.md` — the skill itself. YAML frontmatter (`name`, `description`, `license`, `metadata.version`/`author`) is the trigger contract: the `description` lists explicit Italian trigger phrases that decide when Claude auto-invokes the skill. **Only the six fields of the Agent Skills spec are allowed** (`name`, `description`, `license`, `compatibility`, `metadata`, `allowed-tools`): Claude Code extensions such as `argument-hint` make the claude.ai ZIP upload fail with a hard error (verified 2026-09-14 with `agentskills validate`, now in CI). The body is ordered for auto-compaction: Claude Code re-attaches only the first 5,000 tokens of an invoked skill after compacting, so cross-cutting invariants (riservatezza, documenti come dati, vigenza, fonte non reperita, citazione) come first, then the mode triggers with their invariants, then routing/gerarchia/corpus/formato. The full procedures of the four non-default modes live in `references/modo_*.md` and are read on demand (and re-readable after compaction) — a mode section in SKILL.md must keep trigger + invariants only. **This is the only file that changes behavior** together with the `modo_*.md` files.
- `.claude/skills/ricerca-giuridica-it/references/` — catalogs loaded *on demand* (progressive disclosure), not part of the always-on prompt. `fonti_dati_giuridici.md` = access & reuse map of official sources (endpoints, licenses, acquisition rules; includes the free-sources hierarchy for massime and the ADR/CCNL tables); `fonti_per_materia.md` = minimum free-source kit per practice area (23 areas, with declared structural gaps); `fonti_normative.md` = per-domain catalog of codes/laws with citation details and official permalinks (Normattiva/EUR-Lex); `computo_termini.md` = rules for computing procedural and substantive time limits (dies a quo, festivi, sospensione feriale, perentorio/ordinatorio) with verified estremi — method, not arithmetic; `percorsi_processuali.md` = per-domain catalog of procedural "cancelli" and riti (condizioni di procedibilità, decadenze tipiche, riti disponibili, ADR di settore) with verified estremi, dated at catalog level — used by "Strategia processuale" mode before assessing timing; `lacune.md` = single consolidated index of structural gaps already declared across the other catalogs, no new content of its own; `elemento_estraneita.md` = private-international-law router (which EU regulation — Roma I/II, Bruxelles I-bis/II-ter, successions — or the residual Italian system governs applicable law/jurisdiction when a case has a foreign element), verified estremi, cross-cutting rather than tied to one practice area; `schemi_atti.md` = repeatable structural schemas per common act type, sourced from free/gratuito-declared formulari sites for structure only (never normative estremi — same boundary as `#verifica-formulari`), each source's free-download claim verified before inclusion; `modo_documento.md`, `modo_comparata.md`, `modo_strategia.md`, `modo_verifica.md` = the complete procedure of each non-default mode, one level deep from SKILL.md, read before answering in that mode (machine-checked by `checks.tool_input_must_include` in the evals); `corpus_lex.md` = how to use each `lex_*` tool when the corpus is connected; `cartella_di_lavoro.md` = convention for a stable local reference folder in a Cowork/Code project (the lawyer's own contract templates, past acts, letterhead), used only for structure/format/style, never for normative estremi — distinct from the `studio` corpus collection (which is substantive case-law/doctrine the firm owns, accessed via `lex_*`), this is local-filesystem-based and format/style-only. SKILL.md points to these by name; keep those pointers in sync when renaming.
- `GUIDA.md` — user-facing mini-guide with example prompts per mode; keep in sync when modes change.
- `CONTRIBUTING.md` — contribution mechanics for human contributors (eval shape, pre-PR commands); the behavioral contribution rule itself lives below and in README.
- `evals/evals.json` — regression prompts with manually-verified expected outputs. The gate for all changes (see below). Entries may carry an optional `checks` object (`must_include`/`must_not_include`: short strings, deterministic, checked before the LLM judge runs; optional `tool_input_must_not_include` checked against tool_use inputs captured via stream-json, for query-minimization regressions) alongside the narrative `expected_output`; not every eval has one (behavioral evals with no falsifiable string stay narrative-only).
- `schema/lex_tools_contract.json` — formal JSON Schema of the `lex_*` tool contract (input/output shapes only, no implementation). Public interface, kept in sync with the design invariant above; useful for external review and for any independent implementation of the corpus server.
- `scripts/package_skill.sh` — zips the skill folder into `dist/` for manual install.
- `scripts/verifica_skill.py` — static checks with no network calls and no dependencies. Each check is a pure function `check_*(Percorsi) -> Esito` (blocking `errori` + informational `note`); `main()` composes them, so every check is unit-testable on a fixture repo. Checks: evals.json validity, id sequentiality and `checks` shape (including `tool_input_must_not_include`, non-empty strings); SKILL.md frontmatter (`name` per the Agent Skills spec and equal to the folder, `description` ≤ 1024 chars, `metadata.version` present); CHANGELOG headings well-formed, unique, descending, and top version == `metadata.version`; references/ pointers not broken and no orphans; https-only URLs in references; `lex_*` names cited in SKILL.md exist in the contract; `fonti_normative.md` table schema (4 columns, recognized Stato prefix, permalink to a known official domain); consistent column counts in every references table; maturity labels and 1..N numbering in `fonti_per_materia.md`; contract JSON validity; SKILL.md growth vs. last tag (informational); body ≤ 500 lines, frontmatter restricted to the spec's six fields, `must_not_include` strings absent from the expected output, and the references map — every `references/*.md` name — within the first 5,000 estimated tokens of SKILL.md so it survives auto-compaction (blocking). `--versione` prints the declared version (used by the release workflow). Runs in CI on every push/PR.
- `tests/test_verifica_skill.py` — unit tests for every static check (stdlib `unittest`, no dependencies): valid fixture passes, then one element broken at a time. Run with `python3 -m unittest discover -s tests -v`; runs in CI.
- `scripts/verifica_permalink.py` — repeatable permalink audit (see Commands); pure parsing/comparison functions with unit tests in `tests/test_verifica_permalink.py`.
- `scripts/esegui_evals.py` — the headless eval runner: three tiers per eval (deterministic `must_include`/`must_not_include` on the final answer; `tool_input_must_not_include`/`tool_input_must_include` on the tool_use inputs captured via `--output-format stream-json`; LLM judge last, only if the deterministic tiers pass). Stream parsing, tiers 1-2 and the orchestration are pure functions with unit tests (`tests/test_esegui_evals.py`, fake executor in place of `claude`); writes `evals/risultati/<stamp>/` with per-eval files plus `_riepilogo.json`. `scripts/esegui_evals.sh` is a thin compatibility wrapper. Refuses to run inside a Claude Code session.
- `.github/workflows/release.yml` — on any `v*` tag: runs the static checks, refuses the release if the tag differs from `metadata.version` in SKILL.md, then packages the ZIP and publishes a GitHub release. `CHANGELOG.md` is updated by hand and its top entry must carry the same version.
- `.github/workflows/quality.yml` — on push/PR to main (read-only token): `verifica_skill.py` + unit tests + shellcheck (blocking); source-endpoint reachability (informational, non-blocking, since it depends on external network/anti-bot behavior).

The skill's optional corpus is architected as **three collections** exposed via `lex_*` MCP tools: `base` (open indexed sources, citable), `studio` (user's own documents, always cited as "fonte dello studio"), `puntatori` (metadata+URL indexes of restricted-reuse sources — route to the original, never cite unretrieved text). This is the public interface; treat it as a stable contract.

**Documentation policy:** repo docs (README, CHANGELOG, GUIDA, SKILL.md) describe present capabilities only — no roadmaps, no "future developments", no references to systems being built around this skill. If a feature isn't in the skill today, it doesn't appear in the docs.

The whole product surface is `SKILL.md` plus the reference catalogs under `.claude/skills/ricerca-giuridica-it/references/`. Everything else is tooling, tests, and metadata.

## The contribution rule (non-negotiable)

Every new behavioral rule added to `SKILL.md` must arrive with at least one eval in `evals/evals.json` that verifies it. Expected outputs are written **only after manual verification against the official source** (Normattiva for Italian statute, EUR-Lex for EU law) — never from model memory or plausible-looking references. On any change to the skill, re-run all evals before merging. This mirrors the skill's own core rule: a plausible-but-wrong legal citation is the worst outcome, so unverified `expected_output` values must not enter the file.

## Design invariants (don't regress these when editing SKILL.md)

- **No invented citations.** Never emit article numbers, sentence numbers, or dates absent from retrieved context. If an extremo isn't there, say it isn't.
- **Query minimization.** Queries to `lex_*` tools carry only abstract legal concepts — never party names, identifying data, or case-specific details (professional secrecy). The SKILL.md example contrast (avoid vs. correct) illustrates this; preserve it.
- **`lex_*` tool contract.** The skill integrates with MCP tools `lex_stato_corpus` (call first on non-obvious topics to learn corpus coverage), `lex_cerca_norma`, `lex_leggi_articolo`, `lex_cerca_giurisprudenza`, and `lex_verifica_citazione` (confirm/deny an extremo against the corpus, declaring the check's scope). When these tools are absent, it must fall back to web search over official sources *and declare* that the answer is not from the verified corpus.
- **Ratione temporis.** In-force checks must find the version applicable to the facts, not merely today's version (e.g. appalti: D.lgs. 36/2023 is current; 50/2016 and 163/2006 are abrogated but relevant to past facts).
- **Hierarchy of sources.** Search and presentation follow the gerarchia delle fonti (Costituzione -> EU law -> primary state/regional law and treaties -> secondary sources -> usi); antinomy criteria are declared; administrative practice (circolari) is never treated as a source of law against a statute.
- **Ingestion boundaries.** Only the corpus or open official sources; never suggest extracting from commercial DBs (DeJure, Pluris, OneLegale) or reproducing third-party editorial massime.
- **Two-sided precedent search.** The "Analisi comparata" mode (triggered also by the classic phrase "conformi e difformi") must search both sides of a thesis with equal effort, present two distinct lists, declare the prevailing orientation only when it emerges from retrieved material, and always state that no free citator exists. No cherry-picking.
- **Drafting discipline.** The "Crea documento" mode anchors every citation to retrieved context and renders missing facts as explicit `[DA COMPLETARE: ...]` placeholders — never invented facts, dates, or amounts.
- **User-provided sources stay separate.** Documents supplied by the user (including purchased dottrina) belong to the `studio` collection, are cited as "fonte dello studio", distinct from official sources, and never reproduced beyond short quotation.
- **Strategy mode is orientation, not advice.** The "Strategia processuale" mode opens with the recommendation, compares options with explicit risks, marks deadlines as "da verificare" (never computed from memory), applies reinforced query minimization (strategy cases are always concrete), and always declares itself orientation — the decision stays with the professional.
- **Synthetic by default.** Answers open with the conclusion, no restating the question, no method preambles, one closing caveat at most; expand only on explicit request ("approfondisci"), compress on "in breve".
- **Verification outcomes are three-valued, never two.** The "Verifica documento" mode classifies each citation as confirmed / confirmed-with-discrepancy / not-found-in-consulted-sources — collapsing to a binary exists/doesn't-exist judgment is exactly the overclaiming this skill exists to avoid (v. "Fonte citata ma non reperita").
- **Mode procedures are references, invariants stay in SKILL.md.** Never move a rule that must hold even when the mode file is not read (three-valued outcomes, minimization, markers, fixed structure, orientation-not-advice) out of SKILL.md; never duplicate the procedure back into SKILL.md.
- **"Not found" is never "does not exist".** Every check — `lex_verifica_citazione`, the four-step scale, Verifica documento — is three-valued; the closing formula is "non risulta nelle fonti consultate" with the sources listed and what would be needed to conclude.
- **Depth selectors narrow breadth, never verification.** `#fast`/`#veloce` may shrink how much gets searched (fewer cross-checked sources, fewer precedents per side in Analisi comparata) and how much prose comes back — but it must never skip citation verification, vigenza checks, query minimization, the `[DA VERIFICARE]`/`[DA COMPLETARE]` markers, or the two-sided requirement in Analisi comparata. `#approfondito` only ever adds breadth. On conflicting depth selectors in one message, the more thorough one wins — never resolve ambiguity toward less verification.

## Commands

Build the installable ZIP locally:
```bash
scripts/package_skill.sh            # version defaults to date (YYYYMMDD)
scripts/package_skill.sh v0.3.1     # explicit version → dist/ricerca-giuridica-it_v0.3.1.zip
```

Cut a release (triggers the workflow that packages + publishes the ZIP). Before tagging, bump `metadata.version` in SKILL.md's frontmatter and add the matching `## vX.Y.Z - YYYY-MM-DD` entry at the top of CHANGELOG.md — the static check enforces that they agree, and the release workflow refuses a tag that doesn't match:
```bash
git tag v0.3.1 && git push origin v0.3.1
```

Install the skill for local Claude Code use across all projects:
```bash
cp -R .claude/skills/ricerca-giuridica-it ~/.claude/skills/
```

Check that all catalogued source endpoints still respond:
```bash
scripts/verifica_fonti.sh
```

Audit the normative permalinks (offline: URN vs. declared estremi in `fonti_normative.md`; online: every Normattiva permalink resolves to a page titled with the expected act, every CELEX served by the Publications Office). Network-dependent, one fetch per second, not a CI gate — run before a release or after touching a catalog:
```bash
scripts/verifica_permalink.py            # offline + online
scripts/verifica_permalink.py --offline  # no network
```

Run the static checks and their unit tests as CI does (no network, no credentials):
```bash
python3 scripts/verifica_skill.py
python3 -m unittest discover -s tests -v
shellcheck scripts/*.sh
```

Working-copy caveat (macOS): don't keep the working clone inside iCloud Drive with "Optimize Mac Storage" on — git objects get evicted from local disk and every git command hangs waiting for downloads. Clone to a plain local folder.

Run the evals headless with a three-tier check — deterministic `checks.must_include`/`must_not_include` on the final response, then (when an eval defines it) `checks.tool_input_must_not_include` against tool_use inputs captured via `--output-format stream-json` — for query-minimization regressions — then an LLM judge (from a normal terminal, NOT inside a Claude Code session: nested sessions are refused outright to prevent crashing the parent; TEMPLATE evals are skipped and need manual interactive testing: submit the prompt to the skill and compare the response against `expected_output`):
```bash
scripts/esegui_evals.py          # all evals (scripts/esegui_evals.sh is an equivalent wrapper)
scripts/esegui_evals.py 1 4 5    # a subset by id
EVAL_WEB=1 scripts/esegui_evals.py 26   # also allow WebSearch/WebFetch, for evals that exercise the web fallback
```

There is no build/lint/test toolchain beyond this — "tests" are the evals, run by having Claude answer each `prompt` and comparing against `expected_output`.

## Language

The skill, references, evals, README, and changelog are written in Italian (the skill's users are Italian legal professionals). Match that language when editing skill content; this CLAUDE.md is in English for the working agent.
