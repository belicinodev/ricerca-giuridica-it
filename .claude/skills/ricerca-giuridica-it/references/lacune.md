# Registro delle lacune dichiarate

Elenco unico delle lacune strutturali già dichiarate nei singoli cataloghi (`fonti_per_materia.md`, `fonti_dati_giuridici.md`, `percorsi_processuali.md`) — punto d'ingresso per vederle tutte insieme prima di prioritizzare un aggiornamento — più osservazioni operative emerse da audit successivi sulla skill stessa (es. qualità della ricerca full-text, copertura delle eval), datate singolarmente nella rispettiva sezione. In caso di conflitto tra questo file e il catalogo di origine per una lacuna di fonti, prevale il catalogo di origine.

- Data di consolidamento delle lacune di fonti (sezioni seguenti fino a "Limiti strutturali trasversali" incluso): 2026-07-21. Le sezioni datate singolarmente sono osservazioni operative successive, non consolidamento.

## Maturità per area (`fonti_per_materia.md`)

Ogni sezione porta l'etichetta nel titolo; qui solo l'indice, verificato staticamente da `scripts/verifica_skill.py`.

| Copertura piena (15) | Copertura parziale (6) | Solo instradamento (2) |
|---|---|---|
| Civile, Amministrativo, Tributario, Lavoro e previdenza, Bancario/assicurativo/finanziario, Societario, Crisi d'impresa, Proprietà intellettuale, Consumatori e concorrenza, Real estate ed edilizia, Privacy e data protection, Compliance e 231, Diritto scolastico, Immigrazione, Appalti | Penale (merito scoperto), Famiglia e minori (merito scoperto), Deontologia forense (giurisprudenza disciplinare non verificata), Successioni (cancelli non verificati), Ambiente ed energia (portale MASE instabile, licenza GSE non verificata), Terzo settore (giurisprudenza specifica non verificata) | Diritto sportivo (estremi normativi da verificare), Diritto dei trasporti (estremi normativi da verificare) |

## Copertura giurisprudenziale

- **Merito penale**: privo di fonte gratuita strutturata (`fonti_per_materia.md` § 2, § Lacune trasversali).
- **Merito famiglia e minori**: escluso dalla Banca Dati di Merito, privo di fonte gratuita (`fonti_per_materia.md` § 9, § Lacune trasversali).
- **Giurisprudenza disciplinare forense**: nessuna banca dati pubblica gratuita e ricercabile verificata (`fonti_per_materia.md` § 17).
- **Giurisprudenza federale sportiva** (es. FIGC): non verificata, non presumerne la reperibilità gratuita (`fonti_per_materia.md` § 21).
- **Giurisprudenza specifica del terzo settore**: non verificata; il contenzioso ricade nel civile o amministrativo generale (`fonti_per_materia.md` § 22).
- **Citator gratuito**: nessuna fonte dice se un precedente è superato; si ricostruisce con ricerche incrociate e le relazioni su contrasti del Massimario (`fonti_per_materia.md` § Lacune trasversali; `fonti_dati_giuridici.md` § 3-bis).
- **Massime CED con numero Rv**: non liberamente accessibili (per categoria: ItalgiureWeb, avvocati Cassa Forense) — surrogati in `fonti_dati_giuridici.md` § 3-bis.

## Copertura normativa e di cancelli procedurali

- **Successioni**: nessun cancello procedurale specifico (termini per accettazione con beneficio d'inventario, rinuncia, azione di riduzione) ancora verificato in `percorsi_processuali.md` (`fonti_per_materia.md` § 19).
- **Percorsi processuali**: il catalogo copre solo civile (incluse esecuzione forzata e azione di classe), condominio, lavoro e previdenza, famiglia (rito), amministrativo, tributario, crisi d'impresa, proprietà intellettuale, immigrazione, penale — le altre 14 aree di `fonti_per_materia.md` non hanno ancora un cancello procedurale dedicato (`percorsi_processuali.md`, Regole d'uso, punto 4).

## Copertura di fonti per materia

- **Diritto della navigazione e marittimo**: esplorato ma non catalogato — le fonti delle 16 Autorità di Sistema Portuale sono frammentate su portali distinti senza indice unico (`fonti_per_materia.md` § 23).
- **Registro OCC (sovraindebitamento)**: fonte reale ma il sotto-dominio blocca ogni fetch automatico testato — verificabile solo da browser umano dell'utente finale (`fonti_per_materia.md` § 8).

## Copertura degli schemi ripetibili (Crea documento)

- **`schemi_atti.md`**: copre tutte le 10 aree pianificate (25 tipi di atto).
- **Fonti strutturali confermate**: 10 dei 25 tipi di atto hanno una fonte gratuita verificata con doppio riscontro indipendente (ricorso ex art. 414 c.p.c.; i 3 atti stragiudiziali; i 4 contratti; le 2 dichiarazioni successorie — queste ultime da una fonte commerciale, moduli.it, non istituzionale). Gli altri 15 hanno solo lo schema di convenzione processuale generale: nessun sito specifico ha superato la doppia verifica (in diversi casi perché la dichiarazione di gratuità, pur presente nei risultati di ricerca, non reggeva a un secondo riscontro diretto sulla pagina — v. anche la nota sulla qualità della ricerca full-text più sotto).

## Qualità della ricerca full-text (audit del 2026-07-25)

- **`lex_cerca_norma` è per parole chiave, non semantica**: un audit su ~10 query di concetto in aree diverse ha trovato due casi concreti in cui una disposizione pertinente e presente nel corpus (art. 2119 c.c. "Recesso per giusta causa"; art. 52 c.p. "Difesa legittima") non compariva tra i primi risultati di una query formulata con terminologia comune ("licenziamento" invece di "recesso"; "legittima difesa domiciliare" invece di "difesa legittima"), verificato con lookup diretto che confermava la presenza dell'articolo nel corpus. Non è un difetto di copertura del corpus, ma un limite strutturale della ricerca a parole chiave (BM25) senza sinonimi — mitigato in SKILL.md (sezione Corpus documentale) con l'istruzione di riprovare con formulazioni alternative prima di dichiarare un tema non coperto.
- **Aree a copertura normativa buona nonostante l'etichetta "parziale"**: l'audit ha confermato buona precisione normativa per Famiglia (artt. 337-ter e ss. c.c.), Successioni (artt. 552-561 c.c.), Ambiente (D.lgs. 152/2006), Terzo settore (D.lgs. 117/2017) — la maturità "copertura parziale" di queste aree riguarda la giurisprudenza di merito o i cancelli procedurali non ancora verificati, non il testo normativo di base, che è solido.
- **Deontologia forense confermata scoperta anche a livello di query**: `lex_cerca_norma` su "responsabilità disciplinare dell'avvocato" restituisce solo rumore scollegato (nessun risultato sulla L. 247/2012, assente dal corpus) — coerente con l'etichetta dichiarata, ma va notato che il tool non segnala esplicitamente "fuori copertura" come fa `lex_verifica_citazione`: la skill deve riconoscere il rumore come tale, non presentarlo come se fosse pertinente.

## Copertura eval (audit del 2026-08-21)

- **Quattro aree di routing senza eval — colmato in v0.6.4**: Proprietà intellettuale, Societario, Immigrazione e Diritto scolastico (tutte `[copertura piena]` in `fonti_per_materia.md`) erano citate nel Routing senza nessuna eval che le verificasse. Le eval 94-97 le coprono ora come eval di routing (dove cercare e con quale valore delle fonti), scritte solo dopo aver ri-verificato raggiungibili le fonti del catalogo il 2026-09-14 — incluso il dominio della banca dati UIBM, che è `uibm.gov.it/bancadati` (chiuso il dubbio sollevato qui in v0.6.2) — e dopo aver integrato in `fonti_per_materia.md` i domini delle massime notarili di Milano e del Triveneto. Le altre lacune di copertura eval trovate dallo stesso audit (selettori di profondità in conflitto, alias hashtag, categorie particolari, elenco dati meno ovvi, soglia citazioni in Verifica documento, cancello stragiudiziale in Crea documento, strutture parere/contratto, accessi riservati, massime redazionali, criteri cronologico/specialità) sono state colmate con nuove eval (72-86).
- **Altre 21 scoperte dello stesso audit** (compattazione token, coerenza tra file, controlli statici, contaminazione normativa in `schemi_atti.md`, riservatezza in `cartella_di_lavoro.md`) sono state tutte implementate nella stessa release: v. CHANGELOG.md per il dettaglio.

## Limiti strutturali trasversali

- **Ricerca unificata trasversale**: non esiste gratis; si instrada su più motori distinti secondo il Routing (`fonti_per_materia.md` § Lacune trasversali).
- **Accesso programmatico**: API disponibili solo per Normattiva, EUR-Lex, OpenGA (CKAN), EPO OPS, dataset CNEL; molti siti istituzionali bloccano i fetch automatici, con fallback `site:` o istruzioni all'utente (`fonti_per_materia.md` § Lacune trasversali).
- **Copertura eval di minimizzazione**: solo una minoranza delle eval verifica `tool_input_must_not_include` (conteggio esatto riportato da `scripts/verifica_skill.py` a ogni esecuzione) — la maggior parte della disciplina di minimizzazione resta verificata solo narrativamente o a mano.
