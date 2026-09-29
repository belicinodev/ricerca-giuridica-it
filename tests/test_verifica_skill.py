"""Test unitari dei controlli statici (scripts/verifica_skill.py).

Ogni controllo è esercitato su una fixture di repo minimale costruita in una
cartella temporanea: prima nel caso valido (nessun errore), poi rompendo un solo
elemento alla volta e verificando che l'errore atteso compaia. Solo libreria
standard: `python3 -m unittest discover -s tests -v`.
"""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import verifica_skill as vs  # noqa: E402  (import dopo il sys.path)

SKILL_MD = """---
name: ricerca-giuridica-it
description: >
  Ricerca giuridica di prova: usare quando serve
  un test dei controlli statici.
license: MIT
metadata:
  version: "0.1.0"
  author: test
---

# Skill di prova

Chiama `lex_stato_corpus` sui temi non ovvi e leggi
`references/fonti_per_materia.md`, `references/fonti_normative.md`
e `references/altro.md` quando servono.
"""

FONTI_PER_MATERIA = """# Kit minimo

## 1. Civile [copertura piena]

- Normativa: codice civile.

## 2. Penale [copertura parziale]

- Legittimità: SentenzeWeb.
"""

FONTI_NORMATIVE = """# Catalogo

### Codici
| Fonte | Estremi | Stato | Testo ufficiale |
|---|---|---|---|
| Codice Civile | R.D. 16 marzo 1942, n. 262 | Vigente | https://www.normattiva.it/uri-res/N2Ls?urn:nir:stato:regio.decreto:1942-03-16;262!vig= |
| GDPR | Reg. UE 27 aprile 2016, n. 679 | Vigente | https://eur-lex.europa.eu/eli/reg/2016/679/oj/ita |
"""

ALTRO = """# Altro catalogo

| Cancello | Dove sta |
|---|---|
| Mediazione | art. 5 D.lgs. 28/2010 |

Fonte: https://www.esempio.it/pagina
"""

EVALS = {
    "skill_name": "ricerca-giuridica-it",
    "evals": [
        {
            "id": 1,
            "prompt": "Che estremi ha il codice civile?",
            "expected_output": "R.D. 16 marzo 1942, n. 262.",
            "files": [],
            "checks": {"must_include": ["262"], "must_not_include": ["267"]},
        },
        {
            "id": 2,
            "prompt": "TEMPLATE minimizzazione",
            "expected_output": "Nessun dato del caso nelle query.",
            "files": [],
            "checks": {
                "must_include": [],
                "must_not_include": [],
                "tool_input_must_not_include": ["Mario Rossi"],
            },
        },
    ],
}

CONTRACT = {"tools": {"lex_stato_corpus": {"description": "stato del corpus"}}}

CHANGELOG = """# Changelog

## v0.1.0 - 2026-01-10
- seconda versione

## v0.0.1 - 2026-01-01
- prima versione
"""


def crea_repo(root: Path) -> vs.Percorsi:
    p = vs.Percorsi(root)
    p.refs_dir.mkdir(parents=True)
    (root / "evals").mkdir()
    (root / "schema").mkdir()
    p.skill_md.write_text(SKILL_MD, encoding="utf-8")
    p.fonti_per_materia.write_text(FONTI_PER_MATERIA, encoding="utf-8")
    p.fonti_normative.write_text(FONTI_NORMATIVE, encoding="utf-8")
    (p.refs_dir / "altro.md").write_text(ALTRO, encoding="utf-8")
    p.evals.write_text(json.dumps(EVALS, ensure_ascii=False, indent=2), encoding="utf-8")
    p.contract.write_text(json.dumps(CONTRACT, indent=2), encoding="utf-8")
    p.changelog.write_text(CHANGELOG, encoding="utf-8")
    return p


class Base(unittest.TestCase):
    def setUp(self) -> None:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.p = crea_repo(Path(tmp.name))

    # -- utilità -------------------------------------------------------------

    def sostituisci(self, path: Path, vecchio: str, nuovo: str) -> None:
        testo = path.read_text(encoding="utf-8")
        self.assertIn(vecchio, testo, f"fixture inattesa: '{vecchio}' non trovato in {path.name}")
        path.write_text(testo.replace(vecchio, nuovo), encoding="utf-8")

    def scrivi_evals(self, evals: list[dict]) -> None:
        self.p.evals.write_text(json.dumps({"evals": evals}, ensure_ascii=False), encoding="utf-8")

    def eval_base(self, ident: object) -> dict:
        return {"id": ident, "prompt": f"p{ident}", "expected_output": "e", "files": []}

    def assertErrore(self, esito: vs.Esito, frammento: str) -> None:
        self.assertFalse(esito.ok, "atteso almeno un errore")
        self.assertTrue(
            any(frammento in err for err in esito.errori),
            f"nessun errore contiene '{frammento}': {esito.errori}",
        )

    def assertNota(self, esito: vs.Esito, frammento: str) -> None:
        self.assertTrue(
            any(frammento in n for n in esito.note),
            f"nessuna nota contiene '{frammento}': {esito.note}",
        )


class TestRepoValido(Base):
    def test_ogni_controllo_passa_sulla_fixture(self) -> None:
        for controllo in vs.CONTROLLI:
            with self.subTest(controllo=controllo.__name__):
                self.assertTrue(controllo(self.p).ok, controllo(self.p).errori)

    def test_main_restituisce_zero(self) -> None:
        with mock.patch("sys.stdout"):
            self.assertEqual(vs.main([str(self.p.root)]), 0)

    def test_note_riportano_i_conteggi_attesi(self) -> None:
        esito = vs.esegui_tutti(self.p)
        self.assertNota(esito, "evals.json: 2 eval, 2 con assertion strutturate")
        self.assertNota(esito, "1/2 eval con tool_input_must_not_include")
        self.assertNota(esito, "1/2 TEMPLATE")
        self.assertNota(esito, "references/: 3 file, 3 puntatori in SKILL.md, 0 rotti, 0 orfani")
        self.assertNota(esito, "fonti_normative.md: 2 voci di catalogo verificate, 0 problemi")
        self.assertNota(esito, "copertura piena: 1, copertura parziale: 1, solo instradamento: 0")
        self.assertNota(esito, "CHANGELOG.md: 2 versioni, in testa v0.1.0 (2026-01-10)")
        self.assertNota(esito, "SKILL.md: versione dichiarata 0.1.0")


class TestEvals(Base):
    def test_id_duplicati(self) -> None:
        self.scrivi_evals([self.eval_base(1), self.eval_base(1)])
        self.assertErrore(vs.check_evals(self.p), "id duplicati")

    def test_id_non_sequenziali(self) -> None:
        self.scrivi_evals([self.eval_base(1), self.eval_base(3)])
        self.assertErrore(vs.check_evals(self.p), "mancanti: [2]")

    def test_id_non_interi_segnalati_senza_crash(self) -> None:
        # guardia introdotta in v0.6.2: sorted() su [1, None] solleverebbe TypeError
        self.scrivi_evals([self.eval_base(1), self.eval_base(None), self.eval_base(3)])
        self.assertErrore(vs.check_evals(self.p), "non sono interi")

    def test_campo_obbligatorio_mancante(self) -> None:
        senza_prompt = self.eval_base(1)
        del senza_prompt["prompt"]
        self.scrivi_evals([senza_prompt])
        self.assertErrore(vs.check_evals(self.p), "priva del campo 'prompt'")

    def test_checks_con_lista_mancante(self) -> None:
        e1 = self.eval_base(1)
        e1["checks"] = {"must_include": ["x"]}
        self.scrivi_evals([e1])
        self.assertErrore(vs.check_evals(self.p), "checks.must_not_include mancante")

    def test_checks_con_voce_vuota(self) -> None:
        e1 = self.eval_base(1)
        e1["checks"] = {"must_include": ["ok", ""], "must_not_include": []}
        self.scrivi_evals([e1])
        self.assertErrore(vs.check_evals(self.p), "checks.must_include contiene voci vuote")

    def test_tool_input_non_lista(self) -> None:
        e1 = self.eval_base(1)
        e1["checks"] = {"must_include": [], "must_not_include": [], "tool_input_must_not_include": "Mario"}
        self.scrivi_evals([e1])
        self.assertErrore(vs.check_evals(self.p), "tool_input_must_not_include non è una lista")

    def test_must_include_non_ancorato_ne_all_atteso_ne_al_prompt(self) -> None:
        e = self.eval_base(1)
        e["prompt"] = "Quale decreto disciplina gli interpelli?"
        e["expected_output"] = "Interpelli ex art. 9 D.lgs. 124/2004."
        e["checks"] = {"must_include": ["n. 124"], "must_not_include": []}
        self.scrivi_evals([e])
        self.assertErrore(vs.check_evals(self.p), "must_include assenti sia dall'expected_output sia dal prompt ['n. 124']")

    def test_must_include_ancorato_al_prompt_basta(self) -> None:
        e = self.eval_base(1)
        e["prompt"] = "Redigi una diffida per il mio cliente Mario Rossi."
        e["expected_output"] = "La bozza riporta per esteso i dati forniti."
        e["checks"] = {"must_include": ["Mario Rossi"], "must_not_include": []}
        self.scrivi_evals([e])
        self.assertTrue(vs.check_evals(self.p).ok)

    def test_must_include_non_ancorato_in_template_non_blocca(self) -> None:
        e = self.eval_base(1)
        e["prompt"] = "TEMPLATE collaudo manuale"
        e["checks"] = {"must_include": ["Conformi"], "must_not_include": []}
        self.scrivi_evals([e])
        self.assertTrue(vs.check_evals(self.p).ok)

    def test_must_not_include_presente_nell_atteso(self) -> None:
        e = self.eval_base(1)
        e["expected_output"] = "Si applica la procedura negoziata, non l'affidamento diretto."
        e["checks"] = {"must_include": [], "must_not_include": ["affidamento diretto"]}
        self.scrivi_evals([e])
        self.assertErrore(vs.check_evals(self.p), "già presenti nell'expected_output")

    def test_must_not_include_presente_nell_atteso_template_solo_nota(self) -> None:
        e = self.eval_base(1)
        e["prompt"] = "TEMPLATE fonte non reperita"
        e["expected_output"] = "Mai concludere che non esiste."
        e["checks"] = {"must_include": [], "must_not_include": ["non esiste"]}
        self.scrivi_evals([e])
        esito = vs.check_evals(self.p)
        self.assertTrue(esito.ok, esito.errori)
        self.assertNota(esito, "AVVISO")

    def test_tool_input_must_include_non_lista(self) -> None:
        e = self.eval_base(1)
        e["checks"] = {"must_include": [], "must_not_include": [], "tool_input_must_include": "modo_strategia.md"}
        self.scrivi_evals([e])
        self.assertErrore(vs.check_evals(self.p), "tool_input_must_include non è una lista")

    def test_files_non_lista(self) -> None:
        e1 = self.eval_base(1)
        e1["files"] = "allegato.pdf"
        self.scrivi_evals([e1])
        self.assertErrore(vs.check_evals(self.p), "'files' non è una lista")

    def test_json_invalido(self) -> None:
        self.p.evals.write_text("{non json", encoding="utf-8")
        self.assertErrore(vs.check_evals(self.p), "non è JSON valido")

    def test_campo_evals_vuoto(self) -> None:
        self.scrivi_evals([])
        self.assertErrore(vs.check_evals(self.p), "assente o vuoto")

    def test_file_mancante(self) -> None:
        self.p.evals.unlink()
        self.assertErrore(vs.check_evals(self.p), "non trovato")


class TestFrontmatter(Base):
    def test_name_con_maiuscole(self) -> None:
        self.sostituisci(self.p.skill_md, "name: ricerca-giuridica-it", "name: Ricerca-Giuridica-IT")
        self.assertErrore(vs.check_frontmatter(self.p), "non conforme alla specifica")

    def test_name_con_trattini_consecutivi(self) -> None:
        self.sostituisci(self.p.skill_md, "name: ricerca-giuridica-it", "name: ricerca--giuridica")
        self.assertErrore(vs.check_frontmatter(self.p), "non conforme alla specifica")

    def test_name_diverso_dalla_cartella(self) -> None:
        self.sostituisci(self.p.skill_md, "name: ricerca-giuridica-it", "name: altra-skill")
        self.assertErrore(vs.check_frontmatter(self.p), "diverso dal nome della cartella")

    def test_name_troppo_lungo(self) -> None:
        lungo = "a" * (vs.LIMITE_NAME + 1)
        self.sostituisci(self.p.skill_md, "name: ricerca-giuridica-it", f"name: {lungo}")
        self.assertErrore(vs.check_frontmatter(self.p), "oltre il limite di 64")

    def test_campo_fuori_specifica(self) -> None:
        self.sostituisci(self.p.skill_md, "license: MIT\n", 'license: MIT\nargument-hint: "[#ricerca] quesito"\n')
        self.assertErrore(vs.check_frontmatter(self.p), "fuori dalla specifica")

    def test_name_mancante(self) -> None:
        self.sostituisci(self.p.skill_md, "name: ricerca-giuridica-it\n", "")
        self.assertErrore(vs.check_frontmatter(self.p), "privo del campo 'name:'")

    def test_description_troppo_lunga(self) -> None:
        self.sostituisci(self.p.skill_md, "  un test dei controlli statici.", "  " + "x" * vs.LIMITE_DESCRIPTION)
        self.assertErrore(vs.check_frontmatter(self.p), "oltre il limite di 1024")

    def test_description_ripiegata_conteggiata_come_una_riga(self) -> None:
        esito = vs.check_frontmatter(self.p)
        atteso = len("Ricerca giuridica di prova: usare quando serve un test dei controlli statici.")
        self.assertNota(esito, f"description {atteso} caratteri")

    def test_description_mancante(self) -> None:
        testo = self.p.skill_md.read_text(encoding="utf-8")
        inizio = testo.index("description: >")
        fine = testo.index("license: MIT")
        self.p.skill_md.write_text(testo[:inizio] + testo[fine:], encoding="utf-8")
        self.assertErrore(vs.check_frontmatter(self.p), "privo del campo 'description:'")

    def test_metadata_version_mancante(self) -> None:
        self.sostituisci(self.p.skill_md, '  version: "0.1.0"\n', "")
        self.assertErrore(vs.check_frontmatter(self.p), "privo di metadata.version")

    def test_metadata_version_formato_errato(self) -> None:
        self.sostituisci(self.p.skill_md, 'version: "0.1.0"', 'version: "0.1"')
        self.assertErrore(vs.check_frontmatter(self.p), "non nel formato X.Y.Z")

    def test_frontmatter_assente(self) -> None:
        self.p.skill_md.write_text("# Senza frontmatter\n", encoding="utf-8")
        self.assertErrore(vs.check_frontmatter(self.p), "frontmatter YAML non trovato")

    def test_versione_dichiarata(self) -> None:
        self.assertEqual(vs.versione_dichiarata(self.p), "0.1.0")

    def test_leggi_frontmatter_valori_semplici_e_annidati(self) -> None:
        fm = vs.leggi_frontmatter(SKILL_MD)
        assert fm is not None
        self.assertEqual(fm["name"], "ricerca-giuridica-it")
        self.assertEqual(fm["license"], "MIT")
        self.assertEqual(fm["license"], "MIT")
        self.assertEqual(fm["metadata"], {"version": "0.1.0", "author": "test"})


class TestDimensione(Base):
    def test_fixture_entro_i_limiti(self) -> None:
        esito = vs.check_dimensione_skill(self.p)
        self.assertTrue(esito.ok, esito.errori)
        self.assertNota(esito, "token stimati")

    def test_troppe_righe(self) -> None:
        corpo = "\n".join(f"- riga {i}" for i in range(vs.LIMITE_RIGHE_SKILL + 5))
        self.p.skill_md.write_text(SKILL_MD + corpo + "\n", encoding="utf-8")
        self.assertErrore(vs.check_dimensione_skill(self.p), "oltre le 500")

    def test_oltre_il_budget_di_token_e_solo_avviso(self) -> None:
        corpo = ("parola " * 12) + "\n"
        self.p.skill_md.write_text(SKILL_MD + corpo * 300, encoding="utf-8")  # ~25 KB su 300 righe
        esito = vs.check_dimensione_skill(self.p)
        self.assertTrue(esito.ok, esito.errori)
        self.assertNota(esito, "AVVISO")


class TestMappaRiferimenti(Base):
    def test_fixture_entro_il_budget(self) -> None:
        esito = vs.check_mappa_riferimenti(self.p)
        self.assertTrue(esito.ok, esito.errori)
        self.assertNota(esito, "mappa dei riferimenti completa entro")

    def test_puntatore_in_coda_oltre_il_budget(self) -> None:
        # sposta il puntatore a altro.md dopo ~25 KB di corpo: oltre i 5.000 token stimati
        self.sostituisci(self.p.skill_md, "e `references/altro.md` quando servono.", "quando servono.")
        riempitivo = (("parola " * 12) + "\n") * 300
        self.p.skill_md.write_text(
            self.p.skill_md.read_text(encoding="utf-8") + riempitivo + "\nLeggi `references/altro.md`.\n", encoding="utf-8"
        )
        esito = vs.check_mappa_riferimenti(self.p)
        self.assertErrore(esito, "altro.md")
        self.assertErrore(esito, "oltre il budget di ri-attacco")

    def test_senza_puntatori_non_solleva(self) -> None:
        self.p.skill_md.write_text(SKILL_MD.split("# Skill di prova")[0] + "# Skill di prova\n", encoding="utf-8")
        self.assertTrue(vs.check_mappa_riferimenti(self.p).ok)


class TestChangelog(Base):
    def test_versione_in_testa_diversa_dal_frontmatter(self) -> None:
        self.sostituisci(self.p.skill_md, 'version: "0.1.0"', 'version: "0.2.0"')
        self.assertErrore(vs.check_changelog(self.p), "diversa dalla voce in testa a CHANGELOG.md (v0.1.0)")

    def test_versione_duplicata(self) -> None:
        self.sostituisci(self.p.changelog, "## v0.0.1 - 2026-01-01", "## v0.1.0 - 2026-01-01")
        self.assertErrore(vs.check_changelog(self.p), "versioni duplicate: ['v0.1.0']")

    def test_ordine_non_decrescente(self) -> None:
        self.sostituisci(self.p.changelog, "## v0.0.1 - 2026-01-01", "## v0.3.0 - 2026-01-01")
        self.assertErrore(vs.check_changelog(self.p), "v0.3.0 compare dopo v0.1.0")

    def test_intestazione_malformata(self) -> None:
        self.sostituisci(self.p.changelog, "## v0.0.1 - 2026-01-01", "## v0.0.1 (1 gennaio 2026)")
        self.assertErrore(vs.check_changelog(self.p), "non nel formato '## vX.Y.Z - AAAA-MM-GG'")

    def test_buchi_di_versione_ammessi(self) -> None:
        # una versione mai rilasciata (es. v0.4.5 nella storia reale) non è un errore
        self.sostituisci(self.p.changelog, "## v0.0.1 - 2026-01-01", "## v0.0.3 - 2026-01-01")
        self.assertTrue(vs.check_changelog(self.p).ok)

    def test_file_mancante(self) -> None:
        self.p.changelog.unlink()
        self.assertErrore(vs.check_changelog(self.p), "CHANGELOG.md non trovato")


class TestReferences(Base):
    def test_puntatore_rotto(self) -> None:
        self.sostituisci(self.p.skill_md, "references/altro.md", "references/inesistente.md")
        self.assertErrore(vs.check_reference_pointers(self.p), "inesistenti: ['inesistente.md']")

    def test_orfano_bloccante(self) -> None:
        (self.p.refs_dir / "bozza.md").write_text("# bozza\n", encoding="utf-8")
        self.assertErrore(vs.check_reference_pointers(self.p), "non citate in SKILL.md (mai caricate): ['bozza.md']")

    def test_orfano_in_allowlist(self) -> None:
        (self.p.refs_dir / "bozza.md").write_text("# bozza\n", encoding="utf-8")
        with mock.patch.object(vs, "ORFANI_AMMESSI", frozenset({"bozza.md"})):
            self.assertTrue(vs.check_reference_pointers(self.p).ok)

    def test_url_http_segnalato(self) -> None:
        self.sostituisci(self.p.refs_dir / "altro.md", "https://www.esempio.it/pagina", "http://www.esempio.it/pagina")
        self.assertErrore(vs.check_url_references(self.p), "altro.md riga 7: URL non-https")

    def test_tabella_con_colonne_incoerenti(self) -> None:
        self.sostituisci(self.p.refs_dir / "altro.md", "| Mediazione | art. 5 D.lgs. 28/2010 |", "| Mediazione | art. 5 | in più |")
        self.assertErrore(vs.check_tabelle_generiche(self.p), "altro.md riga 5: 3 colonne, ne attendevo 2")


class TestMaturita(Base):
    def test_etichetta_mancante(self) -> None:
        self.sostituisci(self.p.fonti_per_materia, "## 2. Penale [copertura parziale]", "## 2. Penale")
        self.assertErrore(vs.check_maturita_aree(self.p), "priva di un'etichetta di maturità")

    def test_numerazione_con_buco(self) -> None:
        self.sostituisci(self.p.fonti_per_materia, "## 2. Penale", "## 3. Penale")
        self.assertErrore(vs.check_maturita_aree(self.p), "mancanti [2], duplicati []")

    def test_numerazione_duplicata(self) -> None:
        self.sostituisci(self.p.fonti_per_materia, "## 2. Penale", "## 1. Penale")
        self.assertErrore(vs.check_maturita_aree(self.p), "mancanti [2], duplicati [1]")


class TestToolLex(Base):
    def test_tool_citato_assente_dal_contratto(self) -> None:
        self.sostituisci(self.p.skill_md, "`lex_stato_corpus`", "`lex_stato_corpus` e `lex_inventato`")
        self.assertErrore(vs.check_coerenza_tool_lex(self.p), "assenti dal contratto: ['lex_inventato']")

    def test_tool_nel_contratto_non_citato_e_solo_avviso(self) -> None:
        self.p.contract.write_text(json.dumps({"tools": {"lex_stato_corpus": {}, "lex_cerca_prassi": {}}}), encoding="utf-8")
        esito = vs.check_coerenza_tool_lex(self.p)
        self.assertTrue(esito.ok)
        self.assertNota(esito, "AVVISO (non bloccante): tool nel contratto mai citati per nome esplicito in SKILL.md o references/: ['lex_cerca_prassi']")


class TestToolLexNelleReference(Base):
    def test_tool_citato_solo_in_una_reference_conta_come_citato(self) -> None:
        self.p.contract.write_text(json.dumps({"tools": {"lex_stato_corpus": {}, "lex_cerca_norma": {}}}), encoding="utf-8")
        (self.p.refs_dir / "altro.md").write_text(ALTRO + "\nUsa `lex_cerca_norma` per il normativo.\n", encoding="utf-8")
        esito = vs.check_coerenza_tool_lex(self.p)
        self.assertTrue(esito.ok, esito.errori)
        self.assertFalse(any("mai citati" in n for n in esito.note), esito.note)

    def test_tool_assente_dal_contratto_citato_in_reference(self) -> None:
        (self.p.refs_dir / "altro.md").write_text(ALTRO + "\nUsa `lex_inesistente`.\n", encoding="utf-8")
        self.assertErrore(vs.check_coerenza_tool_lex(self.p), "lex_inesistente")


class TestCatalogoNormativo(Base):
    def test_stato_non_riconosciuto(self) -> None:
        self.sostituisci(self.p.fonti_normative, "| Vigente | https://eur-lex", "| In vigore | https://eur-lex")
        self.assertErrore(vs.check_catalogo_normativo(self.p), "non inizia con un valore riconosciuto")

    def test_url_non_ufficiale(self) -> None:
        self.sostituisci(self.p.fonti_normative, "https://eur-lex.europa.eu/eli/reg/2016/679/oj/ita", "https://www.brocardi.it/gdpr")
        self.assertErrore(vs.check_catalogo_normativo(self.p), "URL non punta a una fonte ufficiale riconosciuta")

    def test_normattiva_senza_permalink(self) -> None:
        self.sostituisci(self.p.fonti_normative, "https://www.normattiva.it/uri-res/N2Ls?urn:nir:stato:regio.decreto:1942-03-16;262!vig=", "https://www.normattiva.it/codici/codice-civile")
        self.assertErrore(vs.check_catalogo_normativo(self.p), "senza il formato permalink atteso")

    def test_numero_colonne_sbagliato(self) -> None:
        self.sostituisci(self.p.fonti_normative, "| GDPR | Reg. UE 27 aprile 2016, n. 679 | Vigente |", "| GDPR | Vigente |")
        self.assertErrore(vs.check_catalogo_normativo(self.p), "colonne invece di 4")


class TestContratto(Base):
    def test_json_invalido(self) -> None:
        self.p.contract.write_text("{", encoding="utf-8")
        self.assertErrore(vs.check_contract_schema(self.p), "non è JSON valido")

    def test_senza_campo_tools(self) -> None:
        self.p.contract.write_text(json.dumps({"title": "x"}), encoding="utf-8")
        self.assertErrore(vs.check_contract_schema(self.p), "campo 'tools' assente")


class TestCrescita(Base):
    def test_senza_repository_git_non_solleva(self) -> None:
        esito = vs.check_crescita_skill(self.p)
        self.assertTrue(esito.ok)
        self.assertNota(esito, "controllo saltato")


class TestMain(Base):
    def test_exit_code_uno_con_errori(self) -> None:
        self.scrivi_evals([self.eval_base(1), self.eval_base(1)])
        with mock.patch("sys.stdout"):
            self.assertEqual(vs.main([str(self.p.root)]), 1)

    def test_opzione_versione_stampa_la_versione(self) -> None:
        with mock.patch("sys.stdout") as out:
            self.assertEqual(vs.main(["--versione", str(self.p.root)]), 0)
        scritto = "".join(str(c.args[0]) for c in out.write.call_args_list)
        self.assertIn("0.1.0", scritto)

    def test_opzione_versione_fallisce_se_assente(self) -> None:
        self.sostituisci(self.p.skill_md, '  version: "0.1.0"\n', "")
        with mock.patch("sys.stderr"):
            self.assertEqual(vs.main(["--versione", str(self.p.root)]), 1)


if __name__ == "__main__":
    unittest.main()
