"""Test unitari del runner delle eval (scripts/esegui_evals.py): parsing dello
stream NDJSON, livelli 1-2, esito del giudice e orchestrazione con un esecutore
finto al posto di `claude`. Solo libreria standard."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import esegui_evals as ee  # noqa: E402


def evento(tipo: str, **campi) -> str:
    return json.dumps({"type": tipo, **campi}, ensure_ascii=False)


def evento_tool_use(nome: str, input_tool: dict) -> str:
    return evento("assistant", message={"content": [
        {"type": "text", "text": "leggo"},
        {"type": "tool_use", "name": nome, "input": input_tool},
    ]})


STREAM_OK = "\n".join([
    evento("system", subtype="init"),
    evento_tool_use("Read", {"file_path": "/repo/.claude/skills/ricerca-giuridica-it/references/modo_documento.md"}),
    evento_tool_use("mcp__lex-corpus__lex_cerca_norma", {"query": "diffida ad adempiere termine congruo"}),
    "questa riga non è JSON",
    evento("result", result="Bozza di diffida ex art. 1454 c.c. [DA COMPLETARE: parti]. È una bozza."),
])


class TestAnalizzaStream(unittest.TestCase):
    def test_risposta_e_tool_input(self) -> None:
        st = ee.analizza_stream(STREAM_OK)
        self.assertTrue(st.result_trovato)
        self.assertIn("art. 1454", st.risposta)
        self.assertEqual(len(st.tool_inputs), 2)
        self.assertIn("modo_documento.md", st.tool_input_testo)
        self.assertIn("diffida ad adempiere", st.tool_input_testo)

    def test_senza_result_usa_il_grezzo(self) -> None:
        testo = "\n".join([evento("system", subtype="init"), "riga grezza"])
        st = ee.analizza_stream(testo)
        self.assertFalse(st.result_trovato)
        self.assertIn("riga grezza", st.risposta)
        self.assertEqual(st.tool_inputs, [])

    def test_stream_vuoto(self) -> None:
        st = ee.analizza_stream("")
        self.assertFalse(st.result_trovato)
        self.assertEqual(st.risposta, "")

    def test_eventi_non_oggetto_ignorati(self) -> None:
        st = ee.analizza_stream("[1, 2]\n" + evento("result", result="ok"))
        self.assertEqual(st.risposta, "ok")


class TestLivelli(unittest.TestCase):
    def test_assertion_senza_checks(self) -> None:
        self.assertEqual(ee.livello_assertion({}, "qualsiasi"), ("OK", "nessuna assertion definita"))

    def test_assertion_soddisfatte_senza_maiuscole(self) -> None:
        stato, dett = ee.livello_assertion({"must_include": ["normattiva"], "must_not_include": ["dejure"]}, "Testo su Normattiva")
        self.assertEqual((stato, dett), ("OK", "assertion soddisfatte"))

    def test_assertion_mancante_e_vietata(self) -> None:
        stato, dett = ee.livello_assertion({"must_include": ["art. 1454"], "must_not_include": ["non esiste"]}, "La sentenza non esiste.")
        self.assertEqual(stato, "FAIL")
        self.assertIn("mancanti: art. 1454", dett)
        self.assertIn("presenti e vietati: non esiste", dett)

    def test_tool_input_senza_controlli(self) -> None:
        self.assertEqual(ee.livello_tool_input({}, "")[0], "OK")

    def test_tool_input_assente_solo_avviso_per_minimizzazione(self) -> None:
        stato, _ = ee.livello_tool_input({"tool_input_must_not_include": ["Mario Rossi"]}, "")
        self.assertEqual(stato, "AVVISO")

    def test_tool_input_assente_e_fail_se_lettura_richiesta(self) -> None:
        stato, dett = ee.livello_tool_input({"tool_input_must_include": ["modo_strategia.md"]}, "")
        self.assertEqual(stato, "FAIL")
        self.assertIn("modo_strategia.md", dett)

    def test_dato_identificativo_negli_input(self) -> None:
        stato, dett = ee.livello_tool_input({"tool_input_must_not_include": ["Mario Rossi"]}, '{"query": "causa Mario Rossi"}')
        self.assertEqual(stato, "FAIL")
        self.assertIn("dati identificativi presenti", dett)

    def test_lettura_richiesta_non_avvenuta(self) -> None:
        stato, dett = ee.livello_tool_input({"tool_input_must_include": ["modo_verifica.md"]}, '{"query": "art. 1454"}')
        self.assertEqual(stato, "FAIL")
        self.assertIn("letture o chiamate richieste non avvenute: modo_verifica.md", dett)

    def test_input_conformi(self) -> None:
        checks = {"tool_input_must_not_include": ["Mario Rossi"], "tool_input_must_include": ["modo_documento.md"]}
        stato, _ = ee.livello_tool_input(checks, ee.analizza_stream(STREAM_OK).tool_input_testo)
        self.assertEqual(stato, "OK")

    def test_esito_giudice(self) -> None:
        self.assertTrue(ee.esito_giudice("PASS: tutto bene\n"))
        self.assertFalse(ee.esito_giudice("FAIL: estremo diverso"))
        self.assertFalse(ee.esito_giudice(""))

    def test_strumenti_con_e_senza_web(self) -> None:
        self.assertNotIn("WebSearch", ee.strumenti(False))
        self.assertTrue(ee.strumenti(True).endswith("WebSearch,WebFetch"))
        self.assertTrue(ee.strumenti(False).startswith("Skill,"))

    def test_seleziona_eval(self) -> None:
        evals = [{"id": 1}, {"id": 2}, {"id": 3}]
        self.assertEqual(ee.seleziona_eval(evals, {1, 3}), [{"id": 1}, {"id": 3}])
        self.assertEqual(ee.seleziona_eval(evals, None), evals)


def esecutore_finto(stream_per_prompt: dict[str, str], giudizio: str = "PASS: coerente con l'atteso", giudice_rc: int = 0):
    """Sostituto di subprocess.run: scrive lo stream canned sullo stdout della
    prima chiamata (stream-json) e risponde come giudice alla seconda."""
    chiamate: list[list[str]] = []

    def run(cmd, **kwargs):
        chiamate.append(list(cmd))
        if "stream-json" in cmd:
            kwargs["stdout"].write(stream_per_prompt.get(cmd[2], ""))
            return subprocess.CompletedProcess(cmd, 0, "", "")
        return subprocess.CompletedProcess(cmd, giudice_rc, giudizio + "\n", "")

    run.chiamate = chiamate  # type: ignore[attr-defined]
    return run


EVALS = [
    {"id": 1, "prompt": "TEMPLATE comportamento", "expected_output": "x", "files": [], "checks": {"must_include": [], "must_not_include": []}},
    {"id": 2, "prompt": "documento: diffida", "expected_output": "Bozza con [DA COMPLETARE].", "files": [],
     "checks": {"must_include": ["1454", "[DA COMPLETARE"], "must_not_include": ["non esiste"], "tool_input_must_include": ["modo_documento.md"]}},
    {"id": 3, "prompt": "che estremi ha il codice civile?", "expected_output": "R.D. 262/1942", "files": [],
     "checks": {"must_include": ["262"], "must_not_include": []}},
    {"id": 4, "prompt": "strategia: caso", "expected_output": "struttura fissa", "files": [],
     "checks": {"must_include": [], "must_not_include": [], "tool_input_must_include": ["modo_strategia.md"]}},
]


class TestEsegui(unittest.TestCase):
    def setUp(self) -> None:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.out = Path(tmp.name) / "run"
        self.log: list[str] = []

    def test_orchestrazione_completa(self) -> None:
        run = esecutore_finto({
            "documento: diffida": STREAM_OK,
            "che estremi ha il codice civile?": evento("result", result="Il codice civile è il R.D. 16 marzo 1942, n. 267."),
            "strategia: caso": evento("result", result="Raccomandazione..."),
        })
        r = ee.esegui(EVALS, self.out, run=run, log=self.log.append)
        self.assertEqual((r.superate, r.fallite, r.template), (1, 2, 1))
        self.assertEqual(r.per_eval["1"]["stato"], "TEMPLATE")
        self.assertEqual(r.per_eval["2"]["stato"], "PASS")
        self.assertEqual(r.per_eval["3"], {"stato": "FAIL", "livello": 1, "dettaglio": "mancanti: 262"})
        self.assertEqual(r.per_eval["4"]["livello"], 2)
        # file di risultato con gli stessi nomi del runner storico
        for nome in ("2.stream.jsonl", "2.err", "2.risposta.md", "2.tool_input.txt", "2.giudizio.txt", "_riepilogo.json"):
            self.assertTrue((self.out / nome).exists(), nome)
        self.assertEqual((self.out / "2.giudizio.txt").read_text(encoding="utf-8").strip(), "PASS: coerente con l'atteso")
        self.assertTrue((self.out / "3.giudizio.txt").read_text(encoding="utf-8").startswith("FAIL: assertion deterministica"))
        self.assertTrue((self.out / "4.giudizio.txt").read_text(encoding="utf-8").startswith("FAIL: input dei tool"))
        riepilogo = json.loads((self.out / "_riepilogo.json").read_text(encoding="utf-8"))
        self.assertEqual(riepilogo["pass"], 1)
        self.assertEqual(riepilogo["template_saltate"], 1)
        # il giudice gira solo per l'eval che ha superato i livelli deterministici
        giudici = [c for c in run.chiamate if "--output-format" in c and "text" in c]
        self.assertEqual(len(giudici), 1)
        self.assertIn("COMPORTAMENTO ATTESO: <<<Bozza con [DA COMPLETARE].>>>", giudici[0][2])
        # le chiamate di esecuzione usano stream-json e l'elenco dei tool
        esecuzioni = [c for c in run.chiamate if "stream-json" in c]
        self.assertEqual(len(esecuzioni), 3)
        self.assertEqual(esecuzioni[0][esecuzioni[0].index("--allowedTools") + 1], ee.strumenti(False))
        self.assertTrue(any("Esito: PASS=1 FAIL=2 TEMPLATE_SALTATE=1" in riga for riga in self.log))

    def test_giudice_non_eseguito_conta_come_fail(self) -> None:
        run = esecutore_finto({"documento: diffida": STREAM_OK}, giudizio="", giudice_rc=1)
        r = ee.esegui([EVALS[1]], self.out, run=run, log=self.log.append)
        self.assertEqual((r.superate, r.fallite), (0, 1))
        self.assertEqual((self.out / "2.giudizio.txt").read_text(encoding="utf-8").strip(), ee.GIUDICE_NON_ESEGUITO)

    def test_eval_web_aggiunge_i_tool_web(self) -> None:
        run = esecutore_finto({"documento: diffida": STREAM_OK})
        ee.esegui([EVALS[1]], self.out, eval_web=True, run=run, log=self.log.append)
        cmd = run.chiamate[0]
        self.assertIn("WebFetch", cmd[cmd.index("--allowedTools") + 1])

    def test_senza_tool_use_e_solo_minimizzazione_va_al_giudice_con_nota(self) -> None:
        ev = {"id": 5, "prompt": "p", "expected_output": "e", "files": [],
              "checks": {"must_include": [], "must_not_include": [], "tool_input_must_not_include": ["Mario"]}}
        run = esecutore_finto({"p": evento("result", result="risposta")})
        r = ee.esegui([ev], self.out, run=run, log=self.log.append)
        self.assertEqual(r.superate, 1)
        self.assertTrue(any("(nota:" in riga for riga in self.log))


class TestMain(unittest.TestCase):
    def test_rifiuta_sessione_annidata(self) -> None:
        with mock.patch.dict(os.environ, {"CLAUDECODE": "1"}), mock.patch("sys.stderr"):
            self.assertEqual(ee.main([]), 1)

    def test_richiede_claude_nel_path(self) -> None:
        with mock.patch.dict(os.environ, {"CLAUDECODE": ""}), mock.patch.object(ee.shutil, "which", return_value=None), mock.patch("sys.stderr"):
            os.environ.pop("CLAUDECODE", None)
            self.assertEqual(ee.main([]), 1)

    def test_id_non_interi(self) -> None:
        with mock.patch.dict(os.environ, {"CLAUDECODE": ""}), mock.patch.object(ee.shutil, "which", return_value="/usr/bin/claude"), mock.patch("sys.stderr"):
            os.environ.pop("CLAUDECODE", None)
            self.assertEqual(ee.main(["1", "x"]), 2)


if __name__ == "__main__":
    unittest.main()
