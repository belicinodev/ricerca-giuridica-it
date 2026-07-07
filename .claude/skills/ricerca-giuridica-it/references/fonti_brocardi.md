# Database Fonti Normative - brocardi.it

Catalogo strutturato delle fonti normative indicizzate da brocardi.it, pensato come file di riferimento da inserire in un progetto.

- Fonte della struttura: https://www.brocardi.it/fonti.html
- Data di generazione: 2026-07-01
- Copertura: circa 100 fonti in 7 categorie, più mappa delle tipologie di contenuto del sito

---

## 0. Avvertenze critiche (da leggere prima dell'uso)

### 0.1 Copyright e riutilizzo
- Il **testo degli atti normativi** (codici, leggi, decreti, regolamenti) non è coperto da diritto d'autore ai sensi dell'art. 5 della L. 633/1941: è liberamente riproducibile.
- Il **contenuto editoriale di brocardi.it** non lo è. Spiegazioni, commenti, note, selezione e massimazione della giurisprudenza, voci di dizionario e traduzioni dei brocardi sono opere protette. Il sito riporta "Tutti i diritti riservati - Copyright Brocardi.it 2003-2026".
- La **banca dati in sé** è protetta dal diritto sui generis del costitutore (art. 102-bis L. 633/1941): l'estrazione o il riutilizzo di una parte sostanziale è vietato anche quando i singoli contenuti sono di per sé liberi. Lo scraping massivo è quindi esposto su due fronti: contrattuale (Termini d'uso) e diritto sui generis.

Conclusione operativa: si può riprendere liberamente il testo di legge, non il valore aggiunto editoriale di brocardi, e non si può estrarre in blocco la loro banca dati.

### 0.2 Fonte autorevole contro fonte di orientamento
brocardi è una fonte secondaria/editoriale, non ufficiale. Per estremi, testo vigente e citazioni con valore formale (rapporti con la PA, gare d'appalto, atti) vanno usate le fonti ufficiali:
- **Normattiva** (https://www.normattiva.it): testo consolidato e multivigente della legislazione statale. È la fonte di riferimento per il testo aggiornato.
- **Gazzetta Ufficiale** (https://www.gazzettaufficiale.it): pubblicazione ufficiale.
- **EUR-Lex** (https://eur-lex.europa.eu): diritto UE (es. GDPR).

Impiego consigliato: brocardi come layer di mappatura e orientamento, e per i brocardi latini; Normattiva o EUR-Lex come autorità citabile.

### 0.3 Obsolescenza
- Gli estremi e lo stato (vigente/abrogato) riflettono l'indice brocardi e la verifica alla data di generazione. Le fonti cambiano: sul tema appalti, il codice vigente è il **D.lgs. 36/2023**; i **D.lgs. 50/2016** e **D.lgs. 163/2006** sono abrogati e presenti solo come archivio storico.
- Uno snapshot statico invecchia. Prevedere una verifica periodica su Normattiva prima di ogni uso formale.
- Gli URL sono più stabili del contenuto; la ripartizione interna in libri/titoli/sezioni può cambiare.

### 0.4 Note tecniche (se si automatizza l'accesso)
- Encoding delle pagine: **Windows-1252**, non UTF-8. Senza conversione si ottengono caratteri corrotti.
- Verificare `robots.txt` e i Termini prima di qualsiasi accesso automatizzato.
- Gli estremi in questo file sono stati normalizzati e verificati dove possibile. L'indice brocardi contiene almeno un'etichetta imprecisa (le locazioni abitative sono indicizzate come "D.lgs." ma la fonte è una legge, L. 431/1998). Validare comunque su Normattiva.

---

## 1. Architettura dei contenuti del sito

### 1.1 Tipologie di contenuto (macro)
| Tipologia | Contenuto | Natura ai fini copyright |
|---|---|---|
| Fonti normative | Codici, leggi, testi unici, regolamenti (questo catalogo) | Testo libero; struttura/banca dati protetta |
| Massime | Estratti giurisprudenziali collegati agli articoli e ricercabili | Testo sentenza libero; selezione e massimazione protette |
| Brocardi | Massime latine con traduzione e spiegazione (elemento eponimo del sito) | Protetti come contenuto editoriale |
| Dizionario giuridico | Voci e definizioni | Protetto |
| Consulenze legali | Archivio Q&A su quesiti reali (servizio a pagamento) | Protetto |
| Notizie giuridiche | Articoli e aggiornamenti | Protetto |
| Tesi di laurea | Repository di tesi | Protetto (dei rispettivi autori) |

### 1.2 Anatomia di una pagina-articolo
Per ogni articolo di una fonte, la pagina espone in genere:
- Testo dell'articolo (fonte libera)
- Spiegazione o commento (editoriale, protetto)
- Massime collegate (selezione editoriale, protetta)
- Brocardi collegati (protetti)
- Navigazione articolo precedente/successivo e breadcrumb del tipo "Fonti > Fonte > Libro > Titolo > Articolo"

### 1.3 Pattern degli URL
| Livello | Pattern | Esempio |
|---|---|---|
| Indice fonti | `/fonti.html` | https://www.brocardi.it/fonti.html |
| Vista per area tematica | `/fonti.html?layout=area-tematica` | https://www.brocardi.it/fonti.html?layout=area-tematica |
| Home fonte | base + slug | https://www.brocardi.it/codice-civile/ |
| Sezione | base + slug + `/libro-.../titolo-.../` | https://www.brocardi.it/codice-civile/libro-quinto/titolo-v/ |
| Articolo | base + slug + `/libro-.../titolo-.../artN.html` | https://www.brocardi.it/codice-di-procedura-penale/libro-primo/titolo-iii/art56.html |

---

## 2. Catalogo fonti normative

Legenda Stato: Vigente = mantenuta come testo in vigore secondo l'indice brocardi; Abrogato = esplicitamente segnalata come abrogata (archivio storico). Validare su Normattiva.

### 2.1 Costituzione e leggi costituzionali
| Fonte | Estremi | Stato | URL |
|---|---|---|---|
| Costituzione della Repubblica Italiana | 1948 | Vigente | https://www.brocardi.it/costituzione/ |

### 2.2 Normative comunitarie (UE)
| Fonte | Estremi | Stato | URL |
|---|---|---|---|
| GDPR - Regolamento generale sulla protezione dei dati | Reg. UE 27 aprile 2016, n. 679 | Vigente | https://www.brocardi.it/regolamento-privacy-ue/ |

### 2.3 Codici
| Fonte | Estremi | Stato | URL |
|---|---|---|---|
| Nuovo Codice Appalti | D.lgs. 31 marzo 2023, n. 36 | Vigente | https://www.brocardi.it/nuovo-codice-appalti/ |
| Codice Civile | R.D. 16 marzo 1942, n. 262 | Vigente | https://www.brocardi.it/codice-civile/ |
| Preleggi (Disposizioni sulla legge in generale) | R.D. 16 marzo 1942, n. 262 | Vigente | https://www.brocardi.it/preleggi/ |
| Disposizioni per l'attuazione del codice civile e disposizioni transitorie | R.D. 30 marzo 1942, n. 318 | Vigente | https://www.brocardi.it/disposizioni-per-attuazione-del-codice-civile/ |
| Codice di procedura civile | R.D. 28 ottobre 1940, n. 1443 | Vigente | https://www.brocardi.it/codice-di-procedura-civile/ |
| Disposizioni di attuazione del codice di procedura civile | R.D. 18 dicembre 1941, n. 1368 | Vigente | https://www.brocardi.it/disposizioni-per-attuazione-codice-procedura-civile/ |
| Codice Penale | R.D. 19 ottobre 1930, n. 1398 | Vigente | https://www.brocardi.it/codice-penale/ |
| Disposizioni di coordinamento e transitorie per il codice penale | R.D. 28 maggio 1931, n. 601 | Vigente | https://www.brocardi.it/disposizioni-transitorie-codice-penale/ |
| Codice di procedura penale | D.P.R. 22 settembre 1988, n. 447 | Vigente | https://www.brocardi.it/codice-di-procedura-penale/ |
| Disposizioni di attuazione del codice di procedura penale | D.lgs. 28 luglio 1989, n. 271 | Vigente | https://www.brocardi.it/disposizioni-per-attuazione-codice-procedura-penale/ |
| Codice del Processo Penale Minorile | D.P.R. 22 settembre 1988, n. 448 | Vigente | https://www.brocardi.it/processo-penale-minorile/ |
| Codice della Strada | D.lgs. 30 aprile 1992, n. 285 | Vigente | https://www.brocardi.it/codice-della-strada/ |
| Codice del processo tributario | D.lgs. 31 dicembre 1992, n. 546 | Vigente | https://www.brocardi.it/codice-del-processo-tributario/ |
| Codice della privacy | D.lgs. 30 giugno 2003, n. 196 | Vigente | https://www.brocardi.it/codice-della-privacy/ |
| Codice del consumo | D.lgs. 6 settembre 2005, n. 206 | Vigente | https://www.brocardi.it/codice-del-consumo/ |
| Codice delle assicurazioni private | D.lgs. 7 settembre 2005, n. 209 | Vigente | https://www.brocardi.it/codice-delle-assicurazioni-private/ |
| Codice dei beni culturali e del paesaggio | D.lgs. 22 gennaio 2004, n. 42 | Vigente | https://www.brocardi.it/codice-dei-beni-culturali-e-del-paesaggio/ |
| Codice dei contratti pubblici | D.lgs. 18 aprile 2016, n. 50 | Abrogato | https://www.brocardi.it/codice-dei-contratti-pubblici/ |
| Codice del processo amministrativo | D.lgs. 2 luglio 2010, n. 104 | Vigente | https://www.brocardi.it/codice-del-processo-amministrativo/ |
| Codice del turismo | D.lgs. 23 maggio 2011, n. 79 | Vigente | https://www.brocardi.it/codice-del-turismo/ |
| Codice dell'ambiente | D.lgs. 3 aprile 2006, n. 152 | Vigente | https://www.brocardi.it/codice-dell-ambiente/ |
| Codice delle comunicazioni elettroniche | D.lgs. 1 agosto 2003, n. 259 | Vigente | https://www.brocardi.it/codice-delle-comunicazioni-elettroniche/ |
| Codice delle pari opportunità | D.lgs. 11 aprile 2006, n. 198 | Vigente | https://www.brocardi.it/codice-delle-pari-opportunita/ |
| Codice di giustizia contabile | D.lgs. 26 agosto 2016, n. 174 | Vigente | https://www.brocardi.it/codice-di-giustizia-contabile/ |
| Codice della nautica da diporto | D.lgs. 18 luglio 2005, n. 171 | Vigente | https://www.brocardi.it/codice-della-nautica-da-diporto/ |
| Codice della proprietà industriale | D.lgs. 10 febbraio 2005, n. 30 | Vigente | https://www.brocardi.it/codice-della-proprieta-industriale/ |
| Codice dell'amministrazione digitale (CAD) | D.lgs. 7 marzo 2005, n. 82 | Vigente | https://www.brocardi.it/codice-dell-amministrazione-digitale/ |
| Codice antimafia | D.lgs. 6 settembre 2011, n. 159 | Vigente | https://www.brocardi.it/codice-antimafia/ |
| Codice del terzo settore | D.lgs. 3 luglio 2017, n. 117 | Vigente | https://www.brocardi.it/codice-terzo-settore/ |
| Codice della protezione civile | D.lgs. 2 gennaio 2018, n. 1 | Vigente | https://www.brocardi.it/codice-protezione-civile/ |
| Codice della crisi d'impresa e dell'insolvenza | D.lgs. 12 gennaio 2019, n. 14 | Vigente | https://www.brocardi.it/codice-crisi-impresa/ |
| Codice degli appalti | D.lgs. 12 aprile 2006, n. 163 | Abrogato | https://www.brocardi.it/codice-degli-appalti/ |

### 2.4 Leggi e decreti
| Fonte | Estremi | Stato | URL |
|---|---|---|---|
| Separazione dei genitori e affidamento condiviso dei figli | L. 8 febbraio 2006, n. 54 | Vigente | https://www.brocardi.it/affido-condiviso/ |
| Legge sull'aborto | L. 22 maggio 1978, n. 194 | Vigente | https://www.brocardi.it/legge-aborto/ |
| Decreto lavoro 2023 | D.L. 4 maggio 2023, n. 48 | Vigente | https://www.brocardi.it/decreto-lavoro-2023/ |
| Decreto "Semplificazioni bis" | D.L. 31 maggio 2021, n. 77 | Vigente | https://www.brocardi.it/decreto-semplificazioni-bis/ |
| Decreto "Sostegni" | D.L. 22 marzo 2021, n. 41 | Vigente | https://www.brocardi.it/decreto-sostegni/ |
| Decreto "Rilancio" | D.L. 19 maggio 2020, n. 34 | Vigente | https://www.brocardi.it/decreto-rilancio/ |
| Decreto "Cura Italia" | L. 24 aprile 2020, n. 27 (conversione) | Vigente | https://www.brocardi.it/decreto-cura-italia/ |
| Legge sul divorzio | L. 1 dicembre 1970, n. 898 | Vigente | https://www.brocardi.it/legge-sul-divorzio/ |
| Legge Cirinnà (unioni civili e convivenze) | L. 20 maggio 2016, n. 76 | Vigente | https://www.brocardi.it/legge-cirinna/ |
| Legge sull'adozione | L. 4 maggio 1983, n. 184 | Vigente | https://www.brocardi.it/legge-sull-adozione/ |
| Procreazione medicalmente assistita | L. 19 febbraio 2004, n. 40 | Vigente | https://www.brocardi.it/procreazione-medicalmente-assistita/ |
| Legge sul biotestamento | L. 22 dicembre 2017, n. 219 | Vigente | https://www.brocardi.it/legge-biotestamento/ |
| Legge 104 | L. 5 febbraio 1992, n. 104 | Vigente | https://www.brocardi.it/legge-104/ |
| Statuto dei lavoratori | L. 20 maggio 1970, n. 300 | Vigente | https://www.brocardi.it/statuto-lavoratori/ |
| Disciplina organica dei contratti di lavoro (Jobs Act) | D.lgs. 15 giugno 2015, n. 81 | Vigente | https://www.brocardi.it/disciplina-organica-contratti-lavoro/ |
| Contratto di lavoro a tutele crescenti | D.lgs. 4 marzo 2015, n. 23 | Vigente | https://www.brocardi.it/contratto-lavoro-tutele-crescenti/ |
| Tutela del lavoro autonomo e lavoro agile | L. 22 maggio 2017, n. 81 | Vigente | https://www.brocardi.it/lavoro-agile/ |
| Riordino degli ammortizzatori sociali (NASpI) | D.lgs. 4 marzo 2015, n. 22 | Vigente | https://www.brocardi.it/ammortizzatori-sociali/ |
| Norme sui licenziamenti individuali | L. 15 luglio 1966, n. 604 | Vigente | https://www.brocardi.it/norme-sui-licenziamenti-individuali/ |
| Norme in materia di orario di lavoro | D.lgs. 8 aprile 2003, n. 66 | Vigente | https://www.brocardi.it/organizzazione-orario-lavoro/ |
| Legge professionale forense | L. 31 dicembre 2012, n. 247 | Vigente | https://www.brocardi.it/legge-professione-forense/ |
| Legge fallimentare | R.D. 16 marzo 1942, n. 267 | Vigente | https://www.brocardi.it/legge-fallimentare/ |
| Legge sulla protezione del diritto d'autore | L. 22 aprile 1941, n. 633 | Vigente | https://www.brocardi.it/legge-diritto-autore/ |
| Sviluppo della proprietà coltivatrice | L. 26 maggio 1965, n. 590 | Vigente | https://www.brocardi.it/disposizioni-sviluppo-proprieta-coltivatrice/ |
| Norme sui contratti agrari | L. 3 maggio 1982, n. 203 | Vigente | https://www.brocardi.it/norme-contratti-agrari/ |
| Responsabilità professionale del personale sanitario (Gelli-Bianco) | L. 8 marzo 2017, n. 24 | Vigente | https://www.brocardi.it/resposabilita-professionale-personale-sanitario/ |
| Legge sulle locazioni abitative | L. 9 dicembre 1998, n. 431 | Vigente | https://www.brocardi.it/legge-locazioni-abitative/ |
| Legge equo canone | L. 27 luglio 1978, n. 392 | Vigente | https://www.brocardi.it/legge-equo-canone/ |
| Legge sul procedimento amministrativo | L. 7 agosto 1990, n. 241 | Vigente | https://www.brocardi.it/legge-sul-procedimento-amministrativo/ |
| Ricorsi amministrativi | D.P.R. 24 novembre 1971, n. 1199 | Vigente | https://www.brocardi.it/ricorsi-amministrativi/ |
| Responsabilità amministrativa delle persone giuridiche | D.lgs. 8 giugno 2001, n. 231 | Vigente | https://www.brocardi.it/responsabilita-amministrativa-persone-giuridiche/ |
| Legge quadro sul volontariato | L. 11 agosto 1991, n. 266 | Vigente | https://www.brocardi.it/legge-quadro-sul-volontariato/ |
| Legge sulle ONLUS | D.lgs. 4 dicembre 1997, n. 460 | Vigente | https://www.brocardi.it/legge-onlus/ |
| Associazioni di promozione sociale (APS) | L. 7 dicembre 2000, n. 383 | Vigente | https://www.brocardi.it/disciplina-delle-associazioni-di-promozione-sociale/ |
| Mediazione controversie civili e commerciali | D.lgs. 4 marzo 2010, n. 28 | Vigente | https://www.brocardi.it/mediazione-controversie-civili-commerciali/ |
| Ordinamento penitenziario | L. 26 luglio 1975, n. 354 | Vigente | https://www.brocardi.it/legge-ordinamento-penitenziario/ |
| Diritto internazionale privato | L. 31 maggio 1995, n. 218 | Vigente | https://www.brocardi.it/legge-diritto-internazionale-privato/ |
| Reati tributari | D.lgs. 10 marzo 2000, n. 74 | Vigente | https://www.brocardi.it/legge-sui-reati-tributari/ |

### 2.5 Testi unici
| Fonte | Estremi | Stato | URL |
|---|---|---|---|
| T.U. sostegno maternità e paternità | D.lgs. 26 marzo 2001, n. 151 | Vigente | https://www.brocardi.it/testo-unico-sostegno-maternita-paternita/ |
| T.U.P.I. (pubblico impiego) | D.lgs. 30 marzo 2001, n. 165 | Vigente | https://www.brocardi.it/testo-unico-sul-pubblico-impiego/ |
| T.U.E.L. (enti locali) | D.lgs. 18 agosto 2000, n. 267 | Vigente | https://www.brocardi.it/testo-unico-enti-locali/ |
| T.U.B. (bancario) | D.lgs. 1 settembre 1993, n. 385 | Vigente | https://www.brocardi.it/testo-unico-bancario/ |
| T.U. edilizia | D.P.R. 6 giugno 2001, n. 380 | Vigente | https://www.brocardi.it/testo-unico-edilizia/ |
| T.U. immigrazione | D.lgs. 25 luglio 1998, n. 286 | Vigente | https://www.brocardi.it/testo-unico-immigrazione/ |
| T.U. stupefacenti | D.P.R. 9 ottobre 1990, n. 309 | Vigente | https://www.brocardi.it/testo-unico-stupefacenti/ |
| T.U.L.P.S. (pubblica sicurezza) | R.D. 18 giugno 1931, n. 773 | Vigente | https://www.brocardi.it/testo-unico-pubblica-sicurezza/ |
| T.U. assicurazione infortuni sul lavoro | D.P.R. 30 giugno 1965, n. 1124 | Vigente | https://www.brocardi.it/testo-unico-assicurazione-degli-infortuni-sul-lavoro/ |
| T.U. espropri (pubblica utilità) | D.P.R. 8 giugno 2001, n. 327 | Vigente | https://www.brocardi.it/testo-unico-espropriazioni-pubblica-utilita/ |
| T.U.F. (intermediazione finanziaria) | D.lgs. 24 febbraio 1998, n. 58 | Vigente | https://www.brocardi.it/testo-unico-intermediazione-finanziaria/ |
| T.U.S.L. (sicurezza sul lavoro) | D.lgs. 9 aprile 2008, n. 81 | Vigente | https://www.brocardi.it/testo-unico-sicurezza-sul-lavoro/ |
| T.U. agricoltura | D.lgs. 18 maggio 2001, n. 228 | Vigente | https://www.brocardi.it/testo-unico-agricoltura/ |
| T.U. piante officinali | D.lgs. 21 maggio 2018, n. 75 | Vigente | https://www.brocardi.it/testo-unico-piante-officinali/ |
| T.U.S.P. (società a partecipazione pubblica) | D.lgs. 19 agosto 2016, n. 175 | Vigente | https://www.brocardi.it/testo-unico-societa-partecipazione-pubblica/ |
| T.U. successioni e donazioni | D.lgs. 31 ottobre 1990, n. 346 | Vigente | https://www.brocardi.it/testo-unico-successioni-donazioni/ |
| T.U.I.R. (imposte sui redditi) | D.P.R. 22 dicembre 1986, n. 917 | Vigente | https://www.brocardi.it/testo-unico-imposte-redditi/ |
| T.U.R. (imposta di registro) | D.P.R. 26 aprile 1986, n. 131 | Vigente | https://www.brocardi.it/testo-unico-imposta-registro/ |
| T.U. IVA | D.P.R. 26 ottobre 1972, n. 633 | Vigente | https://www.brocardi.it/testo-unico-iva/ |
| Accertamento delle imposte sui redditi | D.P.R. 29 settembre 1973, n. 600 | Vigente | https://www.brocardi.it/disposizioni-accertamento-imposte-redditi/ |
| Riscossione delle imposte sul reddito | D.P.R. 29 settembre 1973, n. 602 | Vigente | https://www.brocardi.it/disposizioni-riscossione-imposte-redditi/ |
| Disposizioni urgenti in materia fiscale | D.L. 30 settembre 1994, n. 564 | Vigente | https://www.brocardi.it/disposizioni-urgenti-materia-fiscale/ |
| Accertamento con adesione e conciliazione giudiziale | D.lgs. 19 giugno 1997, n. 218 | Vigente | https://www.brocardi.it/disposizioni-accertamento-adesione-conciliazione-giudiziale/ |
| Sanzioni amministrative per violazioni tributarie | D.lgs. 18 dicembre 1997, n. 472 | Vigente | https://www.brocardi.it/disposizioni-sanzioni-amministrative-violazioni-norme-tributarie/ |
| Ordinamento organi speciali di giurisdizione tributaria | D.lgs. 31 dicembre 1992, n. 545 | Vigente | https://www.brocardi.it/ordinamento-organi-speciali-giurisdizione-tributaria/ |
| Statuto del contribuente | L. 27 luglio 2000, n. 212 | Vigente | https://www.brocardi.it/statuto-contribuente/ |
| Riordino della finanza degli enti territoriali | D.lgs. 30 dicembre 1992, n. 504 | Vigente | https://www.brocardi.it/finanza-enti-territoriali/ |

### 2.6 Regolamenti
| Fonte | Estremi | Stato | URL |
|---|---|---|---|
| Regolamento posta elettronica certificata (PEC) | D.P.R. 11 febbraio 2005, n. 68 | Vigente | https://www.brocardi.it/regolamento-posta-elettronica-certificata/ |

### 2.7 Altre
| Fonte | Estremi | Stato | URL |
|---|---|---|---|
| CCNL del Lavoro Domestico (Colf e Badanti) | Contratto collettivo | Vigente | https://www.brocardi.it/contratto-collettivo-colf-badanti/ |

---

## 3. Manutenzione e versioning

- Verificare gli estremi e lo stato su Normattiva prima di ogni uso con valore formale.
- Rigenerare il catalogo confrontandolo con `/fonti.html`: le voci nuove o rimosse si individuano per diff sugli slug degli URL.
- Punti di attenzione noti nel dominio di lavoro (consulenza, PA, europrogettazione, appalti):
  - Appalti: fonte viva D.lgs. 36/2023. Le due voci storiche restano solo come archivio.
  - Terzo settore: il regime ONLUS (D.lgs. 460/1997) è in fase di superamento a favore del Codice del Terzo Settore (D.lgs. 117/2017), con disciplina transitoria. Verificare la vigenza caso per caso.
- Rischio di deriva del contenuto: brocardi aggiorna i testi con propria tempistica (nelle pagine compare la dicitura "Aggiornato al ..."). Non assumere allineamento in tempo reale con la Gazzetta Ufficiale.
