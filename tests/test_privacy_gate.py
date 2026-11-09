"""Test del privacy gate (scripts/privacy_gate.py): rilevatori, decisione dell'hook, redazione, banco di misura."""
import json
import os
import subprocess
import sys
import unittest
from pathlib import Path

RADICE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RADICE / "scripts"))

import privacy_gate as pg  # noqa: E402


def tipi(testo):
    return {r.tipo for r in pg.rileva(testo)}


class TestChecksum(unittest.TestCase):
    def test_codice_fiscale(self):
        self.assertTrue(pg.codice_fiscale_valido("RSSMRA80A01H501U"))
        self.assertFalse(pg.codice_fiscale_valido("RSSMRA80A01H501X"))

    def test_partita_iva(self):
        self.assertTrue(pg.partita_iva_valida("00743110157"))   # checksum valido
        self.assertFalse(pg.partita_iva_valida("01234567890"))

    def test_iban(self):
        self.assertTrue(pg.iban_valido("IT60X0542811101000000123456"))
        self.assertTrue(pg.iban_valido("IT60 X054 2811 1010 0000 0123 456"))
        self.assertFalse(pg.iban_valido("IT60X0542811101000000123457"))


class TestRilevatoriBlocca(unittest.TestCase):
    def test_codice_fiscale_anche_con_checksum_errato(self):
        # i CF di prova/inventati non superano il checksum: la forma basta
        self.assertIn("codice_fiscale", tipi("cliente C.F. VRDPLA75M01F205X"))
        self.assertIn("codice_fiscale", tipi("RSSMRA80A01H501U"))

    def test_partita_iva_con_etichetta_o_checksum(self):
        self.assertIn("partita_iva", tipi("(P.IVA 04455667788, sede a Bergamo)"))
        self.assertIn("partita_iva", tipi("società con partita IVA 00743110157"))
        self.assertNotIn("partita_iva", tipi("codice 12345678901 di un protocollo"))  # checksum errato, senza etichetta

    def test_iban(self):
        self.assertIn("iban", tipi("bonifico su IT60X0542811101000000123456 entro il"))

    def test_telefono_ed_email(self):
        self.assertIn("telefono", tipi("tel. 035-1234567"))
        self.assertIn("telefono", tipi("cell. 347 1234567"))
        self.assertIn("telefono", tipi("+39 06 12345678"))
        self.assertIn("email", tipi("scrivere a studio.legale@pec.it"))

    def test_targa_documento_polizza_file(self):
        self.assertIn("targa", tipi("auto targata AB123CD"))
        self.assertIn("documento_identita", tipi("carta d'identità n. AX1234567"))
        self.assertIn("documento_identita", tipi("CIE CA12345AA"))
        self.assertIn("polizza_sinistro", tipi("polizza RCA n. POL-998877"))
        self.assertIn("file_allegato", tipi("vedi Sinistro_Ferri_Alfa_2026.pdf"))

    def test_ruolo_generale(self):
        self.assertIn("ruolo_generale", tipi("causa RG 4521/2025 presso il Tribunale"))
        self.assertIn("ruolo_generale", tipi("n. R.G. 12/2024"))
        self.assertNotIn("ruolo_generale", tipi("Cass. civ. n. 4521/2025"))

    def test_ragione_sociale(self):
        self.assertIn("ragione_sociale", tipi("contro Edilcasa srl"))
        self.assertIn("ragione_sociale", tipi("Bianchi Costruzioni S.r.l."))
        self.assertIn("ragione_sociale", tipi("Rheinmetall Bauteile GmbH"))
        self.assertNotIn("ragione_sociale", tipi("responsabilità amministratore Srl"))
        self.assertNotIn("ragione_sociale", tipi("Trasformazione S.p.A. in S.r.l."))


class TestRilevatoriChiedi(unittest.TestCase):
    def test_nome_cognome(self):
        self.assertIn("nome_cognome", tipi("il mio cliente Mario Rossi ha ricevuto"))
        self.assertIn("nome_cognome", tipi("Tizio Bianchi"))
        self.assertNotIn("nome_cognome", tipi("Tizio ha venduto a Caio"))  # placeholder astratti
        self.assertNotIn("nome_cognome", tipi("parrocchia di San Giovanni Battista"))
        self.assertNotIn("nome_cognome", tipi("riforma Cartabia"))

    def test_indirizzo(self):
        self.assertIn("indirizzo", tipi("sede in Via Garibaldi 12, Bergamo"))
        self.assertNotIn("indirizzo", tipi("notifica via PEC oltre le ore 21"))
        self.assertNotIn("indirizzo", tipi("in via di principio"))

    def test_data_nascita_e_importo(self):
        self.assertIn("data_nascita", tipi("nato a Lecce il 3 aprile 1979"))
        self.assertIn("importo", tipi("fornitura da 42.000 euro"))
        self.assertIn("importo", tipi("€ 1.500,00"))
        self.assertNotIn("importo", tipi("art. 2043 c.c."))

    def test_citazione_lunga(self):
        frase = ("'la clausola claims made di secondo livello, che subordina la copertura alla richiesta di "
                 "risarcimento formulata nel medesimo periodo di efficacia del contratto anche per fatti "
                 "denunciati tardivamente dal terzo danneggiato'")
        self.assertIn("citazione_lunga", tipi("cerca " + frase))
        self.assertNotIn("citazione_lunga", tipi('"clausola claims made" nullità'))
        self.assertNotIn("citazione_lunga", tipi("l'art. 1454 c.c. e l'art. 645 c.p.c. del codice"))

    def test_identificativo_dentro_citazione_resta_blocca(self):
        testo = ('"il sig. Rossi, codice fiscale RSSMRA80A01H501U, ha ricevuto in data odierna la diffida '
                 'ad adempiere entro quindici giorni dalla ricezione della presente"')
        ril = pg.rileva(testo)
        self.assertEqual(pg.livello_complessivo(ril), pg.BLOCCA)
        self.assertIn("codice_fiscale", {r.tipo for r in ril})


class TestQueryLegittime(unittest.TestCase):
    def test_citazioni_giuridiche_passano(self):
        for q in (
            "opposizione a decreto ingiuntivo canoni di locazione termini art. 645 c.p.c.",
            "Cass. civ., sez. III, sent. n. 14575 del 30 maggio 2025 responsabilità del vettore",
            "D.lgs. 31 marzo 2023, n. 36 soglie di rilevanza comunitaria",
            "regio decreto 16 marzo 1942, n. 262 codice civile art. 1454",
            "regolamento (UE) 2016/679 art. 17 diritto alla cancellazione",
            "L. 24 novembre 1981, n. 689 sanzioni amministrative notifica 90 giorni",
            "CELEX 32016R0679 versione consolidata",
            "sospensione feriale 1 agosto 31 agosto 2025 termini processuali",
            "TAR Lombardia Milano sez. IV 2024 silenzio assenso",
            "clausola claims made nullità vessatorietà Sezioni Unite 2018",
        ):
            self.assertEqual(pg.rileva(q), [], q)

    def test_url_fonti_ufficiali_ignorati(self):
        dec = pg.valuta({"url": "https://www.normattiva.it/uri-res/N2Ls?urn:nir:stato:regio.decreto:1940-10-28;1443~art645!vig=",
                         "prompt": "estrai il testo dell'art. 645 c.p.c."})
        self.assertIsNone(dec.livello)
        dec = pg.valuta({"url": "https://www.gazzettaufficiale.it/do/atto/serie_generale/caricaPdf?x=Decreto_2024.pdf"})
        self.assertIsNone(dec.livello)


class TestHook(unittest.TestCase):
    def payload(self, **tool_input):
        return {"tool_name": "WebSearch", "tool_input": tool_input}

    def test_nega_su_identificativo(self):
        out = pg.esito_hook(self.payload(query="opposizione Rossi Costruzioni srl RG 4521/2025"))
        self.assertEqual(out["hookSpecificOutput"]["permissionDecision"], "deny")
        self.assertIn("ragione sociale", out["hookSpecificOutput"]["permissionDecisionReason"])
        self.assertIn("campo query", out["hookSpecificOutput"]["permissionDecisionReason"])

    def test_chiede_su_ambiguo(self):
        out = pg.esito_hook(self.payload(query="competenza giudice di pace 5.000 euro"))
        self.assertEqual(out["hookSpecificOutput"]["permissionDecision"], "ask")

    def test_passa_senza_output(self):
        self.assertIsNone(pg.esito_hook(self.payload(query="opposizione a decreto ingiuntivo termini")))

    def test_input_annidati_mcp(self):
        out = pg.esito_hook({"tool_name": "mcp__lex-corpus__lex_cerca_giurisprudenza",
                             "tool_input": {"query": "sinistro stradale", "filtri": {"note": ["targa AB123CD"]}}})
        self.assertEqual(out["hookSpecificOutput"]["permissionDecision"], "deny")
        self.assertIn("filtri.note[0]", out["hookSpecificOutput"]["permissionDecisionReason"])

    def test_modo_redigi(self):
        out = pg.esito_hook(self.payload(query="sinistro targa AB123CD risarcimento diretto"), modo="redigi")
        self.assertEqual(out["hookSpecificOutput"]["permissionDecision"], "allow")
        self.assertEqual(out["hookSpecificOutput"]["updatedInput"]["query"],
                         "sinistro targa [OMISSIS:targa] risarcimento diretto")
        self.assertNotIn("AB123CD", json.dumps(out))

    def test_modo_redigi_non_tocca_il_livello_chiedi(self):
        out = pg.esito_hook(self.payload(query="soglia 40.000 euro affidamento diretto"), modo="redigi")
        self.assertEqual(out["hookSpecificOutput"]["permissionDecision"], "ask")

    def test_processo_reale_via_stdin(self):
        proc = subprocess.run([sys.executable, str(RADICE / "scripts" / "privacy_gate.py")],
                              input=json.dumps(self.payload(query="C.F. RSSMRA80A01H501U")),
                              capture_output=True, text=True, timeout=30)
        self.assertEqual(proc.returncode, 0)
        self.assertEqual(json.loads(proc.stdout)["hookSpecificOutput"]["permissionDecision"], "deny")
        proc = subprocess.run([sys.executable, str(RADICE / "scripts" / "privacy_gate.py")],
                              input="non è json", capture_output=True, text=True, timeout=30)
        self.assertEqual((proc.returncode, proc.stdout), (0, ""))  # un difetto del gate non blocca mai


class TestBancoDiMisura(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.esito = pg.misura(RADICE / "evals" / "evals.json", pg.SKILL_DIR / "references",
                              [RADICE / "GUIDA.md", pg.SKILL_DIR / "SKILL.md"])

    def test_identificativi_strutturati_delle_eval_sono_bloccati(self):
        attesi_blocca = {"RSSMRA80A01H501U", "VRDPLA75M01F205X", "IT60X0542811101000000123456", "035-1234567",
                         "4521/2025", "01234567890", "04455667788", "AB123CD", "POL-998877",
                         "Sinistro_Ferri_Alfa_2026.pdf", "AX1234567", "Bianchi Costruzioni", "Edilcasa",
                         "Alfa Costruzioni", "Rheinmetall"}
        per_stringa = {x["stringa"]: x for x in self.esito["richiamo"]["dettaglio"]}
        for s in attesi_blocca:
            self.assertIn(s, per_stringa)
            self.assertEqual(per_stringa[s]["livello"], pg.BLOCCA, s)

    def test_nomi_e_date_delle_eval_sono_almeno_chiedi(self):
        per_stringa = {x["stringa"]: x for x in self.esito["richiamo"]["dettaglio"]}
        for s in ("Mario Bianchi", "Mario Rossi", "Tizio Bianchi", "Paolo Verdi", "Marta Colombi",
                  "Giulia Ferri", "Andrea Conti", "3 aprile 1979", "Via Garibaldi 12"):
            self.assertIsNotNone(per_stringa[s]["livello"], s)

    def test_nessun_blocco_su_testo_legittimo(self):
        # le uniche righe bloccate devono essere gli esempi deliberati di query da evitare (SKILL.md,
        # cartella_di_lavoro.md) e l'eval 68, il cui atteso elenca per nome i dati del cliente precedente
        # che NON devono comparire in alcuna query
        bloccati = [x for x in self.esito["falsi_positivi"]["dettaglio"] if x["livello"] == pg.BLOCCA]
        for x in bloccati:
            self.assertTrue(x["origine"].startswith(("SKILL.md:", "cartella_di_lavoro.md:", "eval 68 expected_output")), x)
        self.assertGreaterEqual(len(bloccati), 4)  # gli esempi di SKILL.md devono essere riconosciuti


if __name__ == "__main__":
    unittest.main()
