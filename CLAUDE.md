# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repository is

This repo is **not runtime code**. It is a distributable **Claude Agent Skill** (`ricerca-giuridica-it`) that encodes a *method* for Italian and EU legal research — routing to official sources, citation discipline, in-force (vigenza) verification, and query minimization for professional-secrecy contexts. It deliberately adds no legal knowledge of its own: without a connected corpus it adds discipline, not facts.

The "source" is prose: `SKILL.md` is a behavioral specification loaded into Claude's context, not a program that executes. Editing it changes model behavior, so treat wording as load-bearing.

## Architecture

- `.claude/skills/ricerca-giuridica-it/SKILL.md` — the skill itself. YAML frontmatter (`name`, `description`) is the trigger contract: the `description` lists explicit Italian trigger phrases that decide when Claude auto-invokes the skill. The body defines the workflow, source routing by legal domain, citation rules, and confidentiality constraints. **This is the only file that changes behavior.**
- `.claude/skills/ricerca-giuridica-it/references/` — catalogs loaded *on demand* (progressive disclosure), not part of the always-on prompt. `fonti_dati_giuridici.md` = access & reuse map of official sources (endpoints, licenses, acquisition rules; includes the free-sources hierarchy for massime and the ADR/CCNL tables); `fonti_per_materia.md` = minimum free-source kit per practice area (16 areas, with declared structural gaps); `fonti_brocardi.md` = per-domain catalog of codes/laws with citation details. SKILL.md points to these by name; keep those pointers in sync when renaming.
- `GUIDA.md` — user-facing mini-guide with example prompts per mode; keep in sync when modes change.
- `evals/evals.json` — regression prompts with manually-verified expected outputs. The gate for all changes (see below).
- `scripts/package_skill.sh` — zips the skill folder into `dist/` for manual install.
- `.github/workflows/release.yml` — on any `v*` tag, packages the ZIP and publishes a GitHub release. `CHANGELOG.md` is updated by hand.

The skill's optional corpus is architected as **three collections** exposed via `lex_*` MCP tools: `base` (open indexed sources, citable), `studio` (user's own documents, always cited as "fonte dello studio"), `puntatori` (metadata+URL indexes of restricted-reuse sources — route to the original, never cite unretrieved text). This is the public interface; treat it as a stable contract.

**Documentation policy:** repo docs (README, CHANGELOG, GUIDA, SKILL.md) describe present capabilities only — no roadmaps, no "future developments", no references to systems being built around this skill. If a feature isn't in the skill today, it doesn't appear in the docs.

The whole product surface is the three files under `.claude/skills/ricerca-giuridica-it/`. Everything else is tooling, tests, and metadata.

## The contribution rule (non-negotiable)

Every new behavioral rule added to `SKILL.md` must arrive with at least one eval in `evals/evals.json` that verifies it. Expected outputs are written **only after manual verification against the official source** (Normattiva for Italian statute, EUR-Lex for EU law) — never from model memory or plausible-looking references. On any change to the skill, re-run all evals before merging. This mirrors the skill's own core rule: a plausible-but-wrong legal citation is the worst outcome, so unverified `expected_output` values must not enter the file.

## Design invariants (don't regress these when editing SKILL.md)

- **No invented citations.** Never emit article numbers, sentence numbers, or dates absent from retrieved context. If an extremo isn't there, say it isn't.
- **Query minimization.** Queries to `lex_*` tools carry only abstract legal concepts — never party names, identifying data, or case-specific details (professional secrecy). The SKILL.md example contrast (avoid vs. correct) illustrates this; preserve it.
- **`lex_*` tool contract.** The skill integrates with MCP tools `lex_stato_corpus` (call first on non-obvious topics to learn corpus coverage), `lex_cerca_norma`, `lex_leggi_articolo`, `lex_cerca_giurisprudenza`. When these tools are absent, it must fall back to web search over official sources *and declare* that the answer is not from the verified corpus.
- **Ratione temporis.** In-force checks must find the version applicable to the facts, not merely today's version (e.g. appalti: D.lgs. 36/2023 is current; 50/2016 and 163/2006 are abrogated but relevant to past facts).
- **Hierarchy of sources.** Search and presentation follow the gerarchia delle fonti (Costituzione -> EU law -> primary state/regional law and treaties -> secondary sources -> usi); antinomy criteria are declared; administrative practice (circolari) is never treated as a source of law against a statute.
- **Ingestion boundaries.** Only the corpus or open official sources; never suggest extracting from commercial DBs (DeJure, Pluris, OneLegale) or reproducing third-party editorial massime.
- **Two-sided precedent search.** The "Analisi comparata" mode (triggered also by the classic phrase "conformi e difformi") must search both sides of a thesis with equal effort, present two distinct lists, declare the prevailing orientation only when it emerges from retrieved material, and always state that no free citator exists. No cherry-picking.
- **Drafting discipline.** The "Crea documento" mode anchors every citation to retrieved context and renders missing facts as explicit `[DA COMPLETARE: ...]` placeholders — never invented facts, dates, or amounts.
- **User-provided sources stay separate.** Documents supplied by the user (including purchased dottrina) belong to the `studio` collection, are cited as "fonte dello studio", distinct from official sources, and never reproduced beyond short quotation.
- **Strategy mode is orientation, not advice.** The "Strategia processuale" mode opens with the recommendation, compares options with explicit risks, marks deadlines as "da verificare" (never computed from memory), applies reinforced query minimization (strategy cases are always concrete), and always declares itself orientation — the decision stays with the professional.
- **Synthetic by default.** Answers open with the conclusion, no restating the question, no method preambles, one closing caveat at most; expand only on explicit request ("approfondisci"), compress on "in breve".

## Commands

Build the installable ZIP locally:
```bash
scripts/package_skill.sh            # version defaults to date (YYYYMMDD)
scripts/package_skill.sh v0.3.1     # explicit version → dist/ricerca-giuridica-it_v0.3.1.zip
```

Cut a release (triggers the workflow that packages + publishes the ZIP):
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

There is no build/lint/test toolchain beyond this — "tests" are the evals, run by having Claude answer each `prompt` and comparing against `expected_output`.

## Language

The skill, references, evals, README, and changelog are written in Italian (the skill's users are Italian legal professionals). Match that language when editing skill content; this CLAUDE.md is in English for the working agent.
