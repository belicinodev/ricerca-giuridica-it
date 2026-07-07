# Changelog

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
