# Miniguida all'uso della skill

Come ottenere il massimo dalle quattro modalità. La skill sceglie la modalità dalla formulazione della richiesta: bastano le frasi giuste. In alternativa puoi **forzare la modalità** con una parola chiave in apertura — `ricerca`, `documento` (o `crea`), `comparata` (o `conformi`), `strategia` — seguita dal quesito:

```
/ricerca-giuridica-it strategia opposizione a decreto ingiuntivo per canoni contestati
/ricerca-giuridica-it documento diffida ex art. 1454 c.c. per ritardo nella consegna
/ricerca-giuridica-it comparata la clausola claims made è vessatoria?
```

La parola chiave decide solo la modalità: le regole di citazione, vigenza e riservatezza valgono sempre e non sono disattivabili. E conta solo come comando in apertura: se è parte della domanda ("Documento di valutazione dei rischi: è obbligatorio...?") la skill sceglie da sola la modalità giusta.

## Ricerca giuridica (default)

Per trovare, inquadrare o verificare norme, prassi e giurisprudenza.

```
Cosa dice l'art. 473-bis c.p.c. e a quali procedimenti si applica?
È ancora in vigore il D.lgs. 50/2016? Quale codice si applica a una gara del 2021?
Che estremi ha la disciplina delle locazioni brevi? Dove verifico il testo vigente?
```

Cosa aspettarsi: risposta che apre con la conclusione, estremi completi e verificabili, indicazione della fonte dove controllare. Se un estremo non è recuperabile, la skill lo dice invece di inventarlo.

## Crea documento

Per bozze di atti, pareri, clausole, memorie, diffide.

```
Redigi una diffida per inadempimento contrattuale ex art. 1454 c.c.
Prepara una bozza di clausola compromissoria per un appalto privato.
Imposta un parere sul recesso del socio in una s.r.l.
```

Cosa aspettarsi: bozza strutturata (fatto/diritto/conclusioni, o clausola con nota di contesto), citazioni ancorate alle fonti recuperate, segnaposto espliciti `[DA COMPLETARE: ...]` per i dati mancanti. La bozza va sempre rivista prima dell'uso.

## Analisi comparata

Per mappare la giurisprudenza a favore e contro una tesi (funzionano anche le formule classiche: "conformi e difformi", "pro e contro").

```
Conformi e difformi: la clausola claims made nei contratti assicurativi è vessatoria?
Cerca precedenti pro e contro la compensatio lucri cum damno in caso di indennizzo assicurativo.
C'è contrasto giurisprudenziale sulla notifica via PEC oltre le ore 21?
```

Cosa aspettarsi: due elenchi distinti (Conformi / Difformi) con estremi completi, l'indicazione dell'orientamento prevalente **solo** se emerge dal materiale trovato (con il criterio dichiarato), e sempre l'avvertenza che non esiste un citator gratuito: l'assenza di difformi non prova che non esistano.

## Strategia processuale

Per valutare come impostare un'azione o una difesa — anche partendo da un fascicolo o dossier allegato.

```
Valuta le opzioni processuali: [descrizione del caso]. Conviene agire o transigere?
Come imposto la difesa contro un decreto ingiuntivo fondato su fatture contestate?
Come gestiresti questo caso? [con documenti allegati]
```

Cosa aspettarsi: una risposta a struttura fissa — **Raccomandazione** (2-3 frasi), **Fase preliminare** (documenti e fatti mancanti), **Questioni e argomenti** (i pilastri, con citazioni per estremi e stato di verifica), **Opzioni a confronto** (fondamento, forza, debolezza, rischi), **Azioni e scadenze** (termini marcati "da verificare"). Se il fascicolo allegato contiene citazioni non verificate, la strategia esce comunque completa: gli argomenti dubbi restano al loro posto marcati `[DA VERIFICARE]` e la verifica entra tra le azioni. È un orientamento fondato sulle fonti, non un parere: la decisione resta al professionista.

## Controllare la lunghezza

- La risposta è **sintetica di default**: conclusione prima, dettaglio minimo.
- `in breve` / `in sintesi` → solo conclusione e fonti.
- `approfondisci` / `in dettaglio` / `versione estesa` → orientamenti a confronto, argomentazione completa, testo delle disposizioni chiave.

## Il corpus documentale (se collegato)

Se la conversazione espone i tool `lex_*`, la skill interroga un corpus locale in tre collezioni: `base` (fonti aperte indicizzate), `studio` (i tuoi documenti: citati come "fonte dello studio"), `puntatori` (indici di fonti a riuso ristretto: la skill ti rimanda all'originale). Chiedi "che copertura ha il corpus?" per farti dichiarare collezioni e data di aggiornamento. Senza corpus, la skill lavora sulle fonti ufficiali via web dichiarandolo.

## La gerarchia delle fonti

Le risposte costruiscono il quadro dall'alto verso il basso: Costituzione e leggi costituzionali → diritto UE → fonti primarie (leggi statali e regionali, trattati) → fonti secondarie (regolamenti) → usi e consuetudini. In caso di norme in conflitto, la skill dichiara il criterio che applica (gerarchico, di competenza, cronologico, di specialità) — e se una circolare contrasta con la legge, segnala il contrasto invece di seguire la circolare.

## Riservatezza

Puoi descrivere il caso liberamente nella conversazione: la skill è progettata per **non** far uscire i dettagli — le ricerche verso corpus e web usano solo concetti giuridici astratti (istituti, norme, fattispecie), mai nomi di parti o dati riconducibili a persone o cause.

## Limiti da conoscere

| Limite | Conseguenza | Cosa fa la skill |
|---|---|---|
| Massime CED (numeri Rv) non pubbliche | Nessuna ricerca per Rv | Rassegne del Massimario come surrogato; ItalgiureWeb per gli avvocati Cassa Forense (ti prepara la query) |
| Nessun citator gratuito | Non si può provare che un precedente sia superato | Lo dichiara sempre; usa le relazioni su contrasti del Massimario |
| Merito penale e merito famiglia/minori senza fonte gratuita | Copertura scoperta | Lo dichiara e lavora su legittimità e fonti disponibili |
| Vigenza non sempre verificabile dal contesto | Rischio versione sbagliata | Rimanda a Normattiva e indica la versione ratione temporis |

Per gli estremi degli atti e il catalogo completo delle fonti: `references/` nella cartella della skill.
