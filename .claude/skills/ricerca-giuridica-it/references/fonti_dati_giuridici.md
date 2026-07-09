# Fonti dati giuridici - Mappa di accesso e riuso

Companion tecnico del catalogo degli estremi normativi (`fonti_normative.md`): per ogni fonte ufficiale, come accedervi (anche in modo automatico), con quale licenza e con quali regole di riuso. Serve alla skill per instradare le ricerche e per valutare cosa è lecito acquisire in un corpus documentale.

- Data: 2026-07-04
- Regola generale: il testo degli atti è libero, il valore aggiunto editoriale no. Verificare sempre licenza e termini d'uso prima di qualsiasi acquisizione.

---

## 1. Asimmetria di fondo

La normativa (statale e UE) è risolta: open data, API, licenza riusabile. La giurisprudenza no: gratuita da leggere, ma senza open data ufficiale in blocco. L'Italia non ha un equivalente del Caselaw Access Project statunitense o di OpenCaseLaw svizzero. Il Ministero non ha rilasciato le sentenze come open data.

Conseguenza pratica: un corpus normativo ampio e aggiornato è costruibile legittimamente; un corpus giurisprudenziale ampio no. La giurisprudenza si raccoglie in profondità sui propri temi, per raccolta mirata, non in ampiezza.

---

## 2. Normativa

| Livello | Fonte / endpoint | Accesso macchina | Licenza | Idoneità all'acquisizione |
|---|---|---|---|---|
| Costituzione e leggi costituzionali | Normattiva; giurisprudenza su cortecostituzionale.it | Come normativa statale | CC BY 4.0 (Normattiva) | Alta |
| Normativa statale | dati.normattiva.it | REST API con OpenAPI, config Postman, collezioni bulk | CC BY 4.0 | Alta |
| Leggi regionali | normattiva.it/legislazioneRegionale (motore federato: rinvia alle banche dati dei Consigli regionali e delle Province autonome) | Ricerca web federata; il testo vive sulla banca dati regionale di origine. Esempio di banca dati regionale con vera API aperta: Lombardia, dati.lombardia.it/resource/abjw-hhay.json (Socrata, CC0), con testo integrale in HTML/XML collegato su normelombardia.consiglio.regione.lombardia.it; verificato attivo il 2026-07-09. Le altre regioni restano da verificare caso per caso: non presumere la stessa apertura | Atti pubblici; le singole banche dati regionali hanno condizioni proprie | Media (fonte distribuita, niente API unica salvo eccezioni verificate come la Lombardia) |
| Trattati internazionali | ATRIO — atrio.esteri.it (archivio trattati del MAECI, bilaterali e multilaterali) | Consultazione web per materia e cronologia | Dati istituzionali, citare la fonte | Media |
| Diritto UE | EUR-Lex / CELLAR | SPARQL, REST API, Data Dump, webservice SOAP | Riuso da policy Publications Office | Alta |
| Fonti secondarie (regolamenti) | gazzettaufficiale.it + siti istituzionali degli enti emananti | Consultazione web | Atto pubblico | Media |
| Consuetudini e usi | Raccolte provinciali degli usi delle Camere di commercio (ex R.D. 2011/1934), sui siti delle singole CCIAA | Consultazione web/PDF per provincia | Documenti camerali pubblici, citare la fonte | Bassa (fonte frammentata per provincia) |
| Lavori preparatori | senato.it e camera.it (iter dei disegni di legge, dossier) | Consultazione web | Atti pubblici | Media |
| Pubblicazione ufficiale | gazzettaufficiale.it | Consultazione web | Atto pubblico | Media |

Le fonti di base — Costituzione, codice civile (R.D. 16 marzo 1942, n. 262), codice penale (R.D. 19 ottobre 1930, n. 1398), codici di procedura, testi unici — sono catalogate con estremi e stato di vigenza in `fonti_normative.md`. Il testo autorevole e aggiornato è sempre Normattiva.

---

## 3. Giurisprudenza

| Corte | Fonte / endpoint | Accesso | Riuso | Note |
|---|---|---|---|---|
| Cassazione | SentenzeWeb (italgiure.giustizia.it/sncass) | Ricerca web gratuita senza registrazione: full-text con booleani AND/OR/NOT, estremi, riferimenti normativi, ECLI, filtri sezione/anno; niente API | Atto pubblico, nessuna licenza di riuso massivo | Raccolta mirata, no bulk; certificato *.giustizia.it non verificabile dai fetcher standard |
| Massime CED e altre corti | ItalgiureWeb area riservata (italgiure.giustizia.it) | Login gratuito riservato: magistrati, PA e avvocati iscritti Cassa Forense (convenzione, attivazione da cassaforense.it) | Uso personale, non redistribuibile | Fonte "per categoria": l'avvocato abilitato può verificare i numeri Rv; non riutilizzabile in un corpus |
| Merito civile | Banca Dati di Merito / BDP (bdp.giustizia.it) | Gratuita ma NON anonima: SPID/CIE/CNS; full-text + abstract, ~3,5 mln provvedimenti dal 2016 | Atto pubblico; riuso editoriale massivo regolato da convenzione dedicata | **Esclusi famiglia, minori e stato della persona**; niente API: istruzioni all'utente |
| Giustizia amministrativa (Consiglio di Stato, TAR, CGARS) | giustizia-amministrativa.it, sezione "Decisioni e pareri" | Ricerca web, full-text liberi | Atto pubblico | Contenzioso amministrativo e appalti |
| Giustizia amministrativa, open data | OpenGA (openga.giustizia-amministrativa.it) | Portale CKAN con API standard, dataset su provvedimenti e attività | **CC BY 4.0 dichiarata** (a livello di risorsa via API `package_show`/export RDF-DCAT; la pagina HTML del singolo dataset mostra fuorviantemente "Nessuna licenza indicata" — verificare via API, non dal widget della pagina) | Unico portale di giustizia con licenza open esplicita |
| Brevetti unificati | UPC — unifiedpatentcourt.org/en/decisions-and-orders | Consultazione libera via browser; 403 ai fetch automatici | Decisioni pubbliche, citare la fonte | Fallback: ricerca `site:unifiedpatentcourt.org` |
| Corte costituzionale | cortecostituzionale.it, sezione "Ricerca pronunce" | Ricerca web, full-text con identificatore ECLI | Atto pubblico | Come seme di ricerca vedi anche il dataset LAWSUIT (§5) |
| Corte dei conti | banchedati.corteconti.it | Ricerca web | Atto pubblico | Giurisdizione contabile, responsabilità erariale, enti locali |
| CGUE | curia.europa.eu (InfoCuria); sentenze anche su EUR-Lex | Ricerca web; EUR-Lex con API | Riuso da policy Publications Office | Citare con ECLI/CELEX |
| CEDU | HUDOC (hudoc.echr.coe.int) | Ricerca web | Copyright Consiglio d'Europa, consultazione e citazione libere | Convenzione europea dei diritti dell'uomo |

---

## 3-bis. Massime: cosa esiste gratis e cosa no

Gerarchia delle fonti gratuite di massime e orientamenti, dalla più autorevole:

1. **Massime ufficiali della Corte costituzionale** — cortecostituzionale.it, "Ricerca sulle massime": unico massimario ufficiale italiano integralmente gratuito (dal 1956). La maschera massime ha protezione anti-bot: accesso da browser libero, automatico no.
2. **Sommari/massime CGUE** — Raccolta su InfoCuria (curia.europa.eu, ricerca avanzata con 20+ campi, operatori `*`, `_`, virgolette, spazio=E, virgola=O, `!`=SALVO) e su EUR-Lex (settore CELEX 6, con note di dottrina; API e bulk gratuiti previa registrazione; il sito blocca i fetch non-browser).
3. **Rassegne e relazioni dell'Ufficio del Massimario** — cortedicassazione.it (oltre 440 PDF liberi: rassegne mensili civili e penali, annuali, tematiche, relazioni su contrasti e novità normative; citano i numeri Rv) e **Portale del Massimario IPZS** (portaledelmassimario.ipzs.it: rassegne annuali 2010-2024, full-text online). Orientamenti autorevoli ma non massime ufficiali: citare la rassegna e la sentenza sottostante.
4. **Abstract della Banca Dati di Merito** — quasi-massime automatiche del merito civile (SPID, dal 2016, esclusi famiglia/minori).
5. **Massime CED con numero Rv** — NON pubbliche: solo ItalgiureWeb (per categoria: avvocati Cassa Forense, magistrati, PA) o banche dati commerciali. Citare un numero Rv solo se presente nel contesto recuperato.
6. **Massime generate dal full-text** — bozze di lavoro, mai autorità (v. regole della skill).

Cosa resta impossibile gratis: il massimario CED completo interrogabile; un citator (verifica che un orientamento sia ancora attuale); le massime redazionali di merito; la ricerca unificata trasversale su legittimità + merito + costituzionale + UE (si orchestrano 4-5 motori distinti).

---

## 4. Prassi amministrativa

| Materia | Fonte / endpoint | Accesso | Riuso |
|---|---|---|---|
| Fiscale | Agenzia delle Entrate "Normativa e prassi" + def.finanze.it | Documenti PDF/HTML pubblicati | Atto pubblico, citare fonte |
| Appalti, atti interpretativi | ANAC anticorruzione.it (delibere, pareri, linee guida, bandi-tipo) | Documenti pubblicati | Atto pubblico |
| Appalti, dati gare | dati.anticorruzione.it/opendata (BDNCP) | CSV/JSON/OCDS bulk, API via PDND | Open data (dato transazionale, non testo giuridico) |
| Lavoro, vigilanza | INL ispettorato.gov.it (circolari, note, pareri) | Documenti pubblicati | Atto pubblico |
| Lavoro, interpelli | lavoro.gov.it, sezione "Interpelli" (art. 9 D.lgs. 124/2004) | Documenti pubblicati | Atto pubblico |
| Previdenza | INPS, sezione "Circolari, Messaggi e Normativa" | Documenti pubblicati | Atto pubblico |
| Privacy | Garante gpdp.it (provvedimenti, banca dati DocWeb) | Ricerca web | Atto pubblico, citare il numero doc web |
| Privacy, livello UE | EDPB edpb.europa.eu (linee guida, opinioni) | Documenti pubblicati | Riuso con attribuzione |
| Vigilanza bancaria | Banca d'Italia (normativa e orientamenti di vigilanza, sanzioni) | Archivi web + PDF, ricerca per keyword/anno | Testo degli atti citabile; nota copyright del sito restrittiva: no ripubblicazione massiva |
| Assicurativo | IVASS (regolamenti, lettere al mercato) | Archivio per anno + ricerca keyword | Come Banca d'Italia: testo degli atti con citazione, no dump |
| Finanziario | CONSOB (bollettino, regolamentazione) | Ricerca full-text nel bollettino | Atti ufficiali citabili; "tutti i diritti riservati" su sito e banca dati |
| Antiriciclaggio | UIF uif.bancaditalia.it (indicatori di anomalia, schemi, Quaderni) | Documenti pubblicati | Atti citabili con fonte |
| Autorità UE finanza | EBA (Interactive Single Rulebook, Q&A), ESMA (Document Library), EIOPA (Solvency II Rulebook) | Ricerca web + PDF, nessun login | Riproduzione autorizzata con citazione (legal notice verificate); per derivati dichiarare le modifiche |
| Concorrenza e consumo | AGCM (ricerca avanzata provvedimenti) | Libera via browser; **tutto il dominio risponde 403 ai fetch**: fallback `site:agcm.it` o Bollettino PDF | Provvedimenti citabili con fonte |
| Istruzione | MIM mim.gov.it/web/guest/normativa (circolari, decreti, ordinanze) | Filtri tipologia/tematica/data, niente full-text: fallback `site:` | Atti citabili con fonte |
| Immigrazione | Ministero dell'Interno, Dipartimento Libertà Civili (circolari); Commissione nazionale asilo | Consultazione libera, solo filtro data: fallback `site:` | Atti citabili con fonte |
| Protezione internazionale UE | EUAA euaa.europa.eu + portale COI coi.euaa.europa.eu | Pubblico, ricerca avanzata per paese | Riproduzione autorizzata con citazione (legal notice) |

**Banche dati commerciali** (DeJure, Pluris, OneLegale): accesso su abbonamento; la licenza vieta estrazione e travaso dei contenuti. Non sono una fonte di acquisizione ammessa, in nessun caso.

---

## 4-bis. Decisioni ADR e contratti collettivi

| Fonte | Endpoint | Accesso | Riuso |
|---|---|---|---|
| ABF — Arbitro Bancario Finanziario | arbitrobancariofinanziario.it/decisioni/ricerca-avanzata | Ricerca libera senza login: decisioni dal 2010, per oggetto/anno/testo | Decisioni citabili con fonte; sito © Banca d'Italia restrittivo, no dump |
| ACF — Arbitro Controversie Finanziarie | acf.consob.it/decisioni-del-collegio | Consultazione libera: decisioni dal 2017 | Decisioni citabili con fonte |
| ADR consumatori | Elenco MIMIT (organismi ADR nazionali); elenco UE su consumer-redress.ec.europa.eu; ConciliaWeb AGCOM (tlc, SPID); Servizio Conciliazione ARERA (energia/acqua/rifiuti) | Consultazione libera; procedure via identità digitale | Dati istituzionali, citare la fonte |
| Piattaforma ODR europea | **DISMESSA dal 20 luglio 2025** (Reg. UE 2024/3228) | — | Non instradare più verso ec.europa.eu/consumers/odr |
| CCNL, archivio nazionale | CNEL cnel.it/Archivio-Contratti | Ricerca libera per settore; testi autentici depositati ex art. 17 L. 936/1986 | Riproduzione consentita citando la fonte (dichiarazione in pagina) |
| CCNL, open data | cnel.it/Archivio-Contratti-Collettivi/Contratti-Open-Data | Download diretto, formati aperti, URL stabili | **IODL 2.0**: riuso anche commerciale con attribuzione |
| CCNL pubblico impiego | ARAN aranagenzia.it (contratti per comparto, orientamenti applicativi) | Libera via browser; 403 ai fetch: fallback `site:aranagenzia.it` | Documenti istituzionali citabili con fonte |

---

## 5. Dataset aperti e di ricerca (da valutare, non ufficiali)

Da usare come seme di ricerca, con audit obbligatorio di copertura, aggiornamento e provenienza. Non sono fonti autorevoli.

| Dataset | Contenuto | Licenza dichiarata | Uso |
|---|---|---|---|
| italian-legal-corpus (Hugging Face) | Legge IT, diritto UE, decisioni giudiziarie; testi di pubblico dominio | CC BY 4.0 sulla compilazione | Seme ampio; verificare quali decisioni e quanto recenti |
| LAWSUIT | 14.000 sentenze Corte Costituzionale 1956-2022 con massime scritte da esperti | Rilascio aperto per ricerca | Ottimo per la Consulta e come esempio di massimazione; non è Cassazione |
| Italia Corpus | Legislazione italiana in Markdown, aggiornata | Aperto | Alternativa pronta all'ingestione da Normattiva; verificare completezza |
| Italian Civil Code (A. Simeri, HF) | Codice civile strutturato con riferimenti incrociati | Aperto | Utile per la struttura articolo e rinvii |

Nota: questi coprono normativa e Corte Costituzionale. Per la Cassazione restano parziali o assenti: la Cassazione ampia e aggiornata si costruisce solo per raccolta mirata da SentenzeWeb.

---

## 6. Vincoli legali sintetici

- Testo degli atti (leggi, sentenze): libero (art. 5 L. 633/1941).
- Contenuto editoriale (massime redazionali, commenti, note, dizionari): protetto.
- Banca dati in sé: diritto sui generis del costitutore (art. 102-bis L. 633/1941), vietata l'estrazione di parte sostanziale, a prescindere da chi la esegue e dal fatto che non si rivenda.
- Normattiva: CC BY 4.0, riuso con attribuzione.
- EUR-Lex: riuso secondo la policy della Publications Office.
- Sentenze: atti pubblici, ma nessuna licenza di riuso in blocco. La raccolta mirata sui propri temi è accettabile; la redistribuzione di un corpus ampio di sentenze no.
- Italgiure area riservata: uso personale dell'avvocato iscritto, non redistribuibile.
- Banche dati commerciali: la licenza vieta il travaso, qualunque sia la destinazione.

---

## 7. Regole operative di acquisizione (cosa non fare)

- Non costruire né eseguire estrattori massivi puntati su banche dati commerciali o su Italgiure.
- Non riprodurre massime redazionali altrui (Giuffrè, Wolters Kluwer, Ufficio del Massimario): il full-text della sentenza è libero, la massima redazionale è opera protetta. Se serve una massima, generarla dal testo integrale e trattarla come bozza.
- Non trattare una massima generata come citabile: citare sempre la sentenza sottostante.
- Non forzare i siti istituzionali (SentenzeWeb, def.finanze, Banca Dati di Merito) con richieste aggressive o automatizzate oltre i termini d'uso.

---

## 8. Manutenzione

- Multivigenza: gestire la versione della norma applicabile a una certa data è il rischio tecnico più serio. Normattiva la espone via API, ma l'open data multivigente pieno copre per ora gli ultimi 5 anni.
- Citazioni: citare solo ciò che è nel contesto recuperato, con estremi verificabili.
- Citator assente: nessuna fonte gratuita dice se una sentenza è ancora buon diritto. Limite non colmabile senza banca dati a pagamento.
- Encoding: molti PDF e pagine di siti terzi non sono UTF-8 (frequente il Windows-1252). Prevedere normalizzazione.
- Verifica finale: per uso con conseguenze (PA, gare, atti) l'output va sempre confrontato con la fonte ufficiale.
