"""Test delle parti pure di scripts/verifica_permalink.py (parsing di URN ed
estremi, confronto con il titolo Normattiva, estrazione dei CELEX) e dei due
livelli con un fetch finto. Nessuna rete."""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import verifica_permalink as vp  # noqa: E402

URL_CC = "https://www.normattiva.it/uri-res/N2Ls?urn:nir:stato:regio.decreto:1942-03-16;262!vig="
URL_ART = "https://www.normattiva.it/uri-res/N2Ls?urn:nir:stato:regio.decreto:1940-10-28;1443~art696bis!vig="
URL_COST = "https://www.normattiva.it/uri-res/N2Ls?urn:nir:stato:costituzione!vig="

FONTI = """# Catalogo
| Fonte | Estremi | Stato | Testo ufficiale |
|---|---|---|---|
| Codice Civile | R.D. 16 marzo 1942, n. 262 | Vigente | https://www.normattiva.it/uri-res/N2Ls?urn:nir:stato:regio.decreto:1942-03-16;262!vig= |
| Codice Appalti | D.lgs. 31 marzo 2023, n. 36 | Vigente | https://www.normattiva.it/uri-res/N2Ls?urn:nir:stato:decreto.legislativo:2016-04-18;50!vig= |
| Costituzione | Costituzione della Repubblica Italiana (G.U. 27 dicembre 1947, n. 298) | Vigente | https://www.normattiva.it/uri-res/N2Ls?urn:nir:stato:costituzione!vig= |
| Cura Italia | L. 24 aprile 2020, n. 27 (conversione) | Vigente | https://www.normattiva.it/uri-res/N2Ls?urn:nir:stato:legge:2020-04-24;27!vig= |
| GDPR | Reg. UE 27 aprile 2016, n. 679 | Vigente | https://eur-lex.europa.eu/eli/reg/2016/679/oj/ita |
| CCNL | Contratto collettivo | Vigente | https://www.cnel.it/Archivio-Contratti |
"""

ALTRO = "Roma I: https://eur-lex.europa.eu/legal-content/IT/TXT/?uri=CELEX:32008R0593 e " + URL_ART + " .\n"


class TestParsing(unittest.TestCase):
    def test_urn_atto_intero(self) -> None:
        self.assertEqual(vp.urn_atteso(URL_CC), ("regio.decreto", "16 marzo 1942", "262"))

    def test_urn_ad_articolo(self) -> None:
        self.assertEqual(vp.urn_atteso(URL_ART), ("regio.decreto", "28 ottobre 1940", "1443"))

    def test_urn_costituzione_e_non_normattiva(self) -> None:
        self.assertEqual(vp.urn_atteso(URL_COST), ("costituzione", None, None))
        self.assertIsNone(vp.urn_atteso("https://eur-lex.europa.eu/eli/reg/2016/679/oj/ita"))

    def test_estremi(self) -> None:
        self.assertEqual(vp.estremi_parsati("D.lgs. 31 marzo 2023, n. 36"), ("decreto.legislativo", "31 marzo 2023", "36"))
        self.assertEqual(vp.estremi_parsati("L. 24 aprile 2020, n. 27 (conversione)"), ("legge", "24 aprile 2020", "27"))
        self.assertEqual(vp.estremi_parsati("D.P.R. 22 settembre 1988, n. 447"), ("decreto.del.presidente.della.repubblica", "22 settembre 1988", "447"))
        self.assertIsNone(vp.estremi_parsati("Reg. UE 27 aprile 2016, n. 679"))

    def test_titolo_coerente(self) -> None:
        self.assertTrue(vp.titolo_coerente("REGIO DECRETO 16 marzo 1942, n. 262 - Normattiva", vp.urn_atteso(URL_CC)))
        self.assertFalse(vp.titolo_coerente("REGIO DECRETO 16 marzo 1942, n. 267 - Normattiva", vp.urn_atteso(URL_CC)))
        self.assertTrue(vp.titolo_coerente("COSTITUZIONE - Normattiva", vp.urn_atteso(URL_COST)))
        self.assertIsNone(vp.titolo_coerente("qualsiasi", None))

    def test_celex_da_entrambe_le_forme(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            d = Path(tmp)
            (d / "fonti_normative.md").write_text(FONTI, encoding="utf-8")
            (d / "altro.md").write_text(ALTRO, encoding="utf-8")
            self.assertEqual(vp.celex_nei_cataloghi(d), {"32016R0679", "32008R0593"})
            urls = vp.url_normattiva(d)
            self.assertIn(URL_ART, urls)
            self.assertEqual(urls[URL_CC], {"fonti_normative.md"})


class TestLivelli(unittest.TestCase):
    def setUp(self) -> None:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.refs = Path(tmp.name)
        (self.refs / "fonti_normative.md").write_text(FONTI, encoding="utf-8")
        (self.refs / "altro.md").write_text(ALTRO, encoding="utf-8")

    def test_offline_trova_il_permalink_sbagliato(self) -> None:
        esiti = vp.verifica_offline(self.refs)
        per_fonte = {e["fonte"]: e["ok"] for e in esiti}
        self.assertTrue(per_fonte["Codice Civile"])
        self.assertFalse(per_fonte["Codice Appalti"])  # estremi del 36/2023, link al 50/2016
        self.assertTrue(per_fonte["Costituzione"])
        self.assertTrue(per_fonte["Cura Italia"])
        self.assertNotIn("GDPR", per_fonte)  # non Normattiva: fuori dal livello offline

    def test_online_con_fetch_finto(self) -> None:
        def fetch(url, headers=None):
            if "1443" in url:
                return 200, "<title>REGIO DECRETO 28 ottobre 1940, n. 1443 - Normattiva</title>"
            if "costituzione" in url:
                return 200, "<title>COSTITUZIONE - Normattiva</title>"
            if "2016-04-18;50" in url:
                raise OSError("timeout")
            return 200, "<title>ALTRO ATTO</title>"
        esiti = vp.verifica_online(vp.url_normattiva(self.refs), fetch=fetch, pausa=0, log=lambda s: None)
        per_url = {e["url"]: e for e in esiti}
        self.assertTrue(per_url[URL_ART]["ok"])
        self.assertTrue(per_url[URL_COST]["ok"])
        self.assertFalse(per_url[URL_CC]["ok"])  # titolo di un altro atto
        ko = per_url["https://www.normattiva.it/uri-res/N2Ls?urn:nir:stato:decreto.legislativo:2016-04-18;50!vig="]
        self.assertEqual(ko["status"], "ERR")
        self.assertIn("timeout", ko["errore"])

    def test_eurlex_con_fetch_finto(self) -> None:
        chiamate = []
        def fetch(url, headers=None):
            chiamate.append((url, headers))
            return 200, "Regolamento (UE) 2016/679 del Parlamento europeo" if "32016R0679" in url else "altro"
        esiti = vp.verifica_eurlex({"32016R0679", "32008R0593"}, fetch=fetch, pausa=0, log=lambda s: None)
        per = {e["celex"]: e["ok"] for e in esiti}
        self.assertTrue(per["32016R0679"])
        self.assertFalse(per["32008R0593"])
        self.assertTrue(all(h and h.get("Accept-Language") == "ita" for _, h in chiamate))


if __name__ == "__main__":
    unittest.main()
