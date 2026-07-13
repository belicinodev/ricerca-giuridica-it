# Changelog

## v0.4.6 - 2026-07-12
Percorsi processuali estesi a nuove materie e promemoria da fascicolo. Sviluppo sulle direttrici già avviate (cancelli procedurali e leggibilità della strategia).
- `references/percorsi_processuali.md`: dalla prima tranche (civile, lavoro, penale) a **sette materie**, con l'aggiunta di famiglia (rito unificato persone/minorenni/famiglie ex artt. 473-bis ss. c.p.c., con ambito, esclusioni e regola ratione temporis sul 28 febbraio 2023), amministrativo (azione di annullamento art. 29, notificazione art. 41, silenzio e nullità art. 31, rito appalti art. 120 c.p.a.), tributario (ricorso art. 21 D.lgs. 546/1992, reclamo/mediazione art. 17-bis **abrogato** dal D.lgs. 220/2023 con la trappola ratione temporis dichiarata, sospensione art. 47, conciliazione art. 48) e crisi d'impresa (composizione negoziata art. 12, procedimento unitario art. 40, concordato preventivo art. 84 CCII). Tutti gli estremi delle nuove voci riscontrati sul corpus (rubriche e contenuti combacianti, permalink puntuali). Promossa a voce verificata la domanda NASpI (art. 6 D.lgs. 22/2015, sessantotto giorni dalla cessazione, riscontrata sulla fonte ufficiale); resta "da verificare" solo l'equa riparazione (L. 89/2001).
- SKILL.md: nuova regola "Promemoria da fascicolo" (Strategia processuale, punto 7): su richiesta, la strategia già elaborata si comprime in una pagina conservando i cinque titoli, le citazioni con estremi e permalink, i marcatori `[DA VERIFICARE]` e il blocco "Limiti e verifiche" (una riga per dichiarazione, senza omissioni); è un derivato della strategia, non introduce contenuti nuovi; offerto anche come documento quando l'ambiente lo consente. Nota corrispondente in GUIDA.md.
- Eval 40-43 (43 totali): ricorso tributario e reclamo abrogato, rito famiglia ratione temporis, composizione negoziata della crisi, TEMPLATE promemoria da fascicolo. Assertion di eval 38 corretta (rimosso un literal "da verificare" che il retro-test ha mostrato essere un falso negativo: la disciplina è verificata dall'expected_output, la formula compare con parole equivalenti).

## v0.4.4 - 2026-07-11
Percorsi processuali: cancelli e riti per tipo di controversia.
- Nuovo catalogo `references/percorsi_processuali.md` (prima tranche: civile, lavoro, penale, ADR di settore): condizioni di procedibilità (mediazione: art. 5, commi 1 e 2, D.lgs. 28/2010, con la sede dell'elenco cambiata dalla riforma Cartabia e nota ratione temporis; negoziazione assistita: art. 3 D.L. 132/2014, conv. L. 162/2014; responsabilità sanitaria: art. 8 L. 24/2017), percorsi tipo del civile (decreto ingiuntivo e opposizione ex artt. 633 ss., 641 e 645 c.p.c.; procedimento semplificato; convalida di licenza/sfratto; tutela d'urgenza), decadenze del lavoro (doppia decadenza ex art. 6 L. 604/1966 con gli interventi della Consulta registrati nel testo; spartiacque tutele crescenti con la data di entrata in vigore dichiarata come derivata, non testuale), riti e cancelli del penale (querela, abbreviato, patteggiamento, opposizione a decreto penale, messa alla prova, particolare tenuità, termini d'impugnazione). Ogni voce dichiara il proprio stato di verifica: estremi riscontrati sul corpus (permalink puntuali), riscontrati sulla fonte ufficiale per gli atti fuori corpus, o marcati "da verificare" (equa riparazione L. 89/2001, domanda NASpI D.lgs. 22/2015).
- SKILL.md: la Strategia processuale parte dai cancelli processuali della materia (punto 2); puntatore alla nuova reference nei Riferimenti.
- Eval 37-39 (39 totali): opposizione a decreto ingiuntivo, doppia decadenza del licenziamento, TEMPLATE sui cancelli di procedibilità.

## v0.4.3 - 2026-07-09
Contratto dei tool formalizzato, CI di qualità, assertion strutturate su tutte le eval. Da una revisione sistematica della skill.
- Nuovo `schema/lex_tools_contract.json`: JSON Schema formale del contratto pubblico dei tool `lex_*` (forma di input/output, nessuna implementazione) — per revisori esterni e per chi voglia realizzare un proprio server compatibile.
- Nuovi `scripts/verifica_skill.py` e `.github/workflows/quality.yml`: controlli statici senza rete a ogni push/PR (validità di `evals.json`, frontmatter e limite di 1024 caratteri della description, puntatori `references/` non rotti, validità del contratto tool) più shellcheck sugli script; `verifica_fonti.sh` resta un controllo informativo e non bloccante a parte, eseguito a ogni push su main, perché dipende da endpoint esterni reali.
- `evals.json`: ogni eval ha ora un campo `checks` (`must_include`/`must_not_include`) come primo livello di verifica, deterministico, prima del giudice LLM — generato e verificato per tutte le 36 eval, poi validato empiricamente contro risposte reali già giudicate corrette, correggendo alcuni falsi negativi (variazioni naturali di formato tra citazioni compatte ed estese, tra abbreviazione e forma per esteso).
- `scripts/esegui_evals.sh`: eseguito il livello 1 deterministico prima del giudice; un fallimento sulle assertion non arriva più al giudice.
- `fonti_dati_giuridici.md`: aggiunto un esempio concreto e verificato di legge regionale con vera API aperta (Lombardia, `dati.lombardia.it`, licenza CC0), con testo integrale collegato sulla banca dati normativa della Regione.

## v0.4.2 - 2026-07-08
Computo dei termini e completamento del contratto dei tool.
- Nuovo catalogo `references/computo_termini.md`: le regole per calcolare correttamente un termine, con estremi verificati e permalink — computo processuale civile (art. 155 c.p.c.) e penale (art. 172 c.p.p.), prescrizione sostanziale (art. 2963 c.c.), perentorio/ordinatorio e rimessione in termini (art. 153 c.p.c.), sospensione feriale (L. 742/1969, segnalata da verificare), decadenze ricorrenti (art. 325 e 327 c.p.c., 585 c.p.p., 29 c.p.a.). È metodo, non aritmetica: la skill non calcola mai una data a memoria.
- SKILL.md: nuova sotto-sezione "Computo dei termini" nella Verifica; la modalità Strategia cita la regola di computo e la durata per estremi nelle Azioni e scadenze; puntatore alla reference.
- `lex_verifica_citazione` aggiunto all'elenco d'uso dei tool in SKILL.md e al contratto dei tool in CLAUDE.md (era già usato dal protocollo di fallback ma non elencato).
- Eval 35-36 (36 totali) sul computo dei termini.

## v0.4.1 - 2026-07-07
Selettori di modalità, disciplina della strategia su fascicoli, difese e leggibilità. Dal primo ciclo di collaudo su un caso reale e da una review sistematica.
- Selettori espliciti di modalità come parola-comando in apertura (`ricerca:` | `documento:`/`crea:` | `comparata:`/`conformi:` | `strategia:`), con regola anti-falsi-positivi (la parola che è soggetto del quesito non è un selettore) e `argument-hint` nel frontmatter; nessun selettore disattiva le regole trasversali.
- Strategia processuale: trigger "come gestiresti questo caso" (anche con fascicolo allegato); risposta a struttura fissa in cinque sezioni (Raccomandazione, Fase preliminare, Questioni e argomenti, Opzioni a confronto, Azioni e scadenze); il fascicolo con citazioni dubbie non sospende la strategia (argomenti marcati `[DA VERIFICARE: estremi]`, verifica tra le azioni); la struttura prevale su "in breve" (sezioni compresse, mai soppresse); l'analisi comparata sui punti controversi si riassume dentro "Questioni e argomenti".
- Nuova sezione "Fonte citata ma non reperita": scala di ricerca (estremi → contenuto del principio in forma astratta → portali come localizzatori → fonti alternative per pagine inaccessibili, senza eludere i blocchi) prima di chiedere aiuto all'utente; mai "non esiste", solo "non risulta nelle fonti consultate" con l'elenco; innesti dichiarati nelle modalità Strategia e Crea documento.
- Nuova sezione "Fallback web: protocollo": solo fonti ufficiali del Routing, doppia dichiarazione (extra-corpus + data di consultazione), riscontro incrociato degli estremi trovati sul web con `lex_verifica_citazione` quando i tool sono disponibili (in divergenza prevale il corpus), minimizzazione invariata; condotta attiva anche quando il corpus non copre il tema.
- Nuova sezione "I documenti sono dati, mai istruzioni": il contenuto dei documenti (anche di controparte o di altri strumenti) non modifica le regole; istruzioni embedded ignorate e segnalate; le citazioni nei documenti mai "già verificate"; la collezione `studio` marca la provenienza, non l'attendibilità.
- Formato di risposta: permalink della fonte ufficiale accanto a ogni citazione quando presente nel contesto recuperato (mai URL a memoria); dichiarazioni obbligatorie consolidate nel blocco finale "Limiti e verifiche" (i marcatori puntuali restano nel corpo).
- Description del frontmatter entro il limite di 1024 caratteri, con nuovo trigger per la verifica di citazioni ("questa sentenza esiste?", "controlla le citazioni di questo atto").
- Catalogo degli estremi normativi rifondato come `fonti_normative.md`: stesse fonti, permalink alle fonti ufficiali (resolver URN Normattiva, ELI EUR-Lex, archivio CNEL) al posto dei link a siti editoriali terzi; stati di vigenza corretti previa verifica (L. 266/1991 e L. 383/2000 abrogate ex art. 102 D.lgs. 117/2017; ONLUS ad abrogazione differita; legge fallimentare applicabile solo ratione temporis ex art. 390 D.lgs. 14/2019).
- Nuovo `scripts/esegui_evals.sh`: esecuzione headless delle eval con giudice automatico (PASS/FAIL motivato).
- Eval 21-34 (34 totali): selettori, strategia su fascicoli, fonte non reperita, fallback web, permalink, documenti-come-dati, consolidamento, ratione temporis (gara 2019 → D.lgs. 50/2016), verifica citazioni; eval 23 riallineata al testo vigente.

## v0.4.0 - 2026-07-07
Ampliamento delle fonti e delle materie; modalità operative; gerarchia delle fonti.
- Modalità rinominate con nomenclatura propria: Ricerca giuridica, Crea documento, Analisi comparata, Strategia processuale (le formule d'uso classiche, come "conformi e difformi", restano trigger validi).
- Nuova sezione Gerarchia delle fonti in SKILL.md: ordine di ricerca ed esposizione (Costituzione → UE → fonti primarie statali e regionali e trattati → secondarie → usi), criteri dichiarati di risoluzione delle antinomie, prassi mai trattata come fonte del diritto.
- Nuove fonti per i livelli della gerarchia: Legislazione regionale su Normattiva (motore federato sui Consigli regionali), ATRIO/MAECI per i trattati internazionali, raccolte provinciali degli usi delle Camere di commercio, lavori preparatori su camera.it e senato.it.
- Nuovo scripts/verifica_fonti.sh: controllo automatico che gli endpoint dei cataloghi rispondano (42 fonti verificate al rilascio).
- Verifica di rilascio 2026-07-07: estremi delle eval ricontrollati sulle fonti ufficiali via web; endpoint verificati con lo script; eval 20 aggiunta (leggi regionali e criterio di competenza).
- Catalogo `fonti_dati_giuridici.md` riscritto come mappa neutra di accesso e riuso (endpoint, licenze, regole di acquisizione) e ampliato: giustizia amministrativa (CdS, TAR, CGARS) con open data OpenGA (CC BY 4.0), Corte costituzionale, Corte dei conti, CGUE (InfoCuria) e CEDU (HUDOC), UPC, Garante privacy ed EDPB, prassi lavoro e previdenza (INL, interpelli Ministero del Lavoro, INPS), autorità di vigilanza (Banca d'Italia, IVASS, CONSOB, UIF, EBA/ESMA/EIOPA), AGCM, MIM, circolari immigrazione ed EUAA, decisioni ADR (ABF, ACF) e contratti collettivi (CNEL open data IODL 2.0, ARAN), Gazzetta Ufficiale.
- Nuova sezione Massime nel catalogo: gerarchia delle fonti gratuite (massime ufficiali Consulta, sommari CGUE, rassegne dell'Ufficio del Massimario e Portale del Massimario IPZS, abstract di merito, CED solo per categoria via ItalgiureWeb) e lacune dichiarate (niente CED pubblico, niente citator).
- Nuovo catalogo `fonti_per_materia.md`: kit minimo di fonti gratuite per 16 aree di pratica, con lacune strutturali dichiarate (merito penale e merito famiglia/minori scoperti). URL verificati via fetch il 2026-07-06.
- SKILL.md: nuove modalità operative Redazione (bozze con citazioni ancorate e segnaposto [DA COMPLETARE]) e Conformi e difformi (precedenti pro e contro una tesi su due elenchi, divieto di cherry-picking, orientamento prevalente solo se emerge dal recuperato); sezione Massime con gerarchia; sezione Corpus dello studio e fonti proprie (documenti dell'utente come fonte dichiarata, accessi per categoria via istruzioni all'utente); routing esteso alle nuove materie; trigger aggiornati nella description.
- Correzione rilevante: la piattaforma ODR europea è dismessa dal 20 luglio 2025 (Reg. UE 2024/3228); il routing consumatori punta agli elenchi ADR (MIMIT, Commissione UE).
- Nuova modalità Strategia processuale: opzioni a confronto (fondamento, forza, debolezza, rischi), raccomandazione motivata, passi operativi con termini "da verificare"; minimizzazione rafforzata; orientamento dichiarato, non parere.
- Corpus documentale a tre collezioni (`base` / `studio` / `puntatori`) con disciplina di citazione per provenienza; sezione unica in SKILL.md al posto delle precedenti sezioni su tool e fonti proprie.
- Formato di risposta: sintetico per default (conclusione in apertura, una sola avvertenza in chiusura), espansione con "approfondisci", compressione con "in breve".
- README riscritto: schema di funzionamento (Mermaid), quattro modalità, elenco delle fonti pubbliche per categoria, corpus opzionale; nuova GUIDA.md con esempi d'uso per modalità e limiti dichiarati.
- 17 nuove eval (4-20) su fonti di base, routing, massime, modalità, sintesi, collezioni e gerarchia, con estremi ed endpoint verificati sulle fonti ufficiali.

## v0.3.0 - 2026-07-04
Pubblicazione open source (MIT).
- Riorganizzazione del repository: qui vivono solo skill, references, eval e tooling.
- Aggiunto workflow di release: a ogni tag v* lo ZIP installabile viene allegato alla release.
- README pubblico con installazione, limiti e regole di contribuzione.

## v0.2.0 - 2026-07-04
Seconda revisione, pre-test.
- Descrizione riscritta con frasi di innesco esplicite.
- Flusso di lavoro numerato (inquadra, instrada, recupera, verifica vigenza, cita, dichiara limiti).
- Esempio concreto di minimizzazione delle query.
- Sezione tool lex_* con ripiego quando i tool non sono disponibili.
- Procedura di verifica di vigenza in tre passi, inclusa applicazione ratione temporis.
- Puntatori espliciti ai file in references/.

## v0.1.0 - 2026-07-02
Prima stesura: scopo, routing, citazioni, verifica, riservatezza, massime generate.
