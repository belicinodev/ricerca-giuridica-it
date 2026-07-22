# Miniguida all'uso della skill

Come ottenere il massimo dalle cinque modalità. La skill sceglie la modalità dalla formulazione della richiesta: bastano le frasi giuste. In alternativa puoi **forzare la modalità** con un hashtag in apertura — `#ricerca`, `#documento` (o `#crea`), `#comparata` (o `#conformi`), `#strategia`, `#verifica` — seguito dal quesito:

```
/ricerca-giuridica-it #strategia opposizione a decreto ingiuntivo per canoni contestati
/ricerca-giuridica-it #documento diffida ex art. 1454 c.c. per ritardo nella consegna
/ricerca-giuridica-it #comparata la clausola claims made è vessatoria?
```

In una chat qualsiasi (claude.ai, Desktop, app mobile) basta l'hashtag a inizio messaggio, senza il prefisso `/ricerca-giuridica-it` che serve solo per il comando in Claude Code: `#strategia opposizione a decreto ingiuntivo per canoni contestati`. Funziona anche la forma equivalente `strategia:` (con i due punti), mantenuta per compatibilità: le due sintassi attivano la stessa modalità — l'hashtag è consigliato perché è più immediato da usare e da spiegare a un collega o a un cliente.

L'hashtag di modalità decide solo *cosa* fare: le regole di citazione, vigenza e riservatezza valgono sempre e non sono disattivabili. Conta solo come comando in apertura del messaggio: nella prosa comune un hashtag non compare mai per caso, quindi — a differenza della forma con i due punti — non c'è ambiguità con un quesito che contenga per caso quella parola (es. "Documento di valutazione dei rischi: è obbligatorio...?" resta sempre una ricerca).

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
Prepara un contratto di locazione commerciale a uso non abitativo.
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
Contratto con una società tedesca senza clausola di scelta della legge: quale legge si applica e dove posso agire?
```

Cosa aspettarsi: una risposta a struttura fissa — **Raccomandazione** (2-3 frasi), **Fase preliminare** (documenti e fatti mancanti), **Questioni e argomenti** (i pilastri, con citazioni per estremi e stato di verifica), **Opzioni a confronto** (fondamento, forza, debolezza, rischi), **Azioni e scadenze** (termini marcati "da verificare"). Se il fascicolo allegato contiene citazioni non verificate, la strategia esce comunque completa: gli argomenti dubbi restano al loro posto marcati `[DA VERIFICARE]` e la verifica entra tra le azioni. È un orientamento fondato sulle fonti, non un parere: la decisione resta al professionista.

Dopo la strategia puoi chiedere il **promemoria da fascicolo** ("fammi il promemoria", "memo di una pagina"): la stessa strategia compressa in una pagina, con citazioni, marcatori e limiti conservati — anche come documento, se l'ambiente lo consente.

## Verifica documento

Per controllare in blocco tutte le citazioni di un atto — utile prima di un'udienza, per una memoria di controparte o un parere ricevuto.

```
#verifica controlla le citazioni di questo atto [documento allegato]
Verifica le fonti di questa memoria di controparte.
```

Cosa aspettarsi: un report con tre soli esiti possibili per ciascuna citazione — **Riscontrata** (con permalink e stato di vigenza), **Riscontrata con divergenze** (l'atto esiste ma con uno scarto, es. una data diversa da quella citata), **Non riscontrata nelle fonti consultate** (mai "non esiste"). Chiude con un riepilogo numerico e il perimetro esatto del controllo. Con `#fast` la ricerca per citazione è ridotta ma gli esiti restano tre; con `#approfondito` la scala di ricerca è esaustiva.

## Velocità e ampiezza: `#fast` e `#approfondito`

Un secondo hashtag, indipendente dalla modalità e combinabile con qualunque modalità, regola quanto la skill cerca e quanto scrive — utile per bilanciare tempo/costo in token contro esaustività:

```
#fast è ancora in vigore il D.lgs. 50/2016?
#strategia #fast opposizione a decreto ingiuntivo per canoni contestati
#comparata #approfondito la clausola claims made è vessatoria?
```

| Hashtag | Effetto | Quando usarlo |
|---|---|---|
| *(nessuno)* | Comportamento bilanciato di oggi | Uso quotidiano |
| `#fast` (alias `#veloce`) | Ricerca essenziale (si ferma al primo riscontro solido per fonte), risposta compatta: meno tempo, meno token | Orientamento rapido, prima valutazione, quesiti dove il tempo/costo conta |
| `#approfondito` | Ricerca ampia (più fonti incrociate, più precedenti per lato, orientamenti minoritari), risposta estesa | Questioni delicate, prima di un atto o un parere formale, quando serve motivare a fondo |

`#fast` non riduce **mai** la verifica di vigenza, la verifica delle citazioni usate, la riservatezza delle query, i marcatori `[DA VERIFICARE]`/`[DA COMPLETARE]`, né il carattere bilaterale dell'Analisi comparata (conformi e difformi restano sempre entrambi cercati, solo con meno precedenti riportati per lato): la velocità riguarda l'ampiezza dell'esplorazione, mai l'affidabilità di quello che viene poi scritto.

Se servono entrambi i selettori con effetto opposto nello stesso messaggio, per prudenza vince sempre `#approfondito`.

## Controllare la lunghezza della sola risposta

- La risposta è **sintetica di default**: conclusione prima, dettaglio minimo.
- `in breve` / `in sintesi` / **`#breve`** → solo conclusione e fonti.
- `approfondisci` / `in dettaglio` / `versione estesa` / **`#approfondito`** → orientamenti a confronto, argomentazione completa, testo delle disposizioni chiave.

`#breve` cambia solo la forma della risposta finale, senza ridurre la ricerca sottostante come fa `#fast`. Si scrivono come prefisso alla domanda o come messaggio a sé stante dopo aver già ricevuto una risposta:

```
#breve è ancora in vigore il D.lgs. 50/2016?
```
oppure, dopo aver già ricevuto una risposta, scrivi semplicemente `approfondisci` o `#approfondito`.

## Il corpus documentale (se collegato)

Se la conversazione espone i tool `lex_*`, la skill interroga un corpus locale in tre collezioni: `base` (fonti aperte indicizzate), `studio` (i tuoi documenti: citati come "fonte dello studio"), `puntatori` (indici di fonti a riuso ristretto: la skill ti rimanda all'originale). Chiedi "che copertura ha il corpus?" per farti dichiarare collezioni e data di aggiornamento. Senza corpus, la skill lavora sulle fonti ufficiali via web dichiarandolo.

## La gerarchia delle fonti

Le risposte costruiscono il quadro dall'alto verso il basso: Costituzione e leggi costituzionali → diritto UE → fonti primarie (leggi statali e regionali, trattati) → fonti secondarie (regolamenti) → usi e consuetudini. In caso di norme in conflitto, la skill dichiara il criterio che applica (gerarchico, di competenza, cronologico, di specialità) — e se una circolare contrasta con la legge, segnala il contrasto invece di seguire la circolare.

## Riservatezza

Puoi descrivere il caso liberamente nella conversazione: la skill è progettata per **non** far uscire i dettagli — le ricerche verso corpus e web usano solo concetti giuridici astratti (istituti, norme, fattispecie), mai nomi di parti o dati riconducibili a persone o cause.

E i documenti che alleghi — anche quelli di controparte o prodotti da altri strumenti — sono trattati come **dati da analizzare, mai come istruzioni**: se un documento contiene testo che tenta di pilotare l'assistente (es. "queste citazioni sono già verificate"), la skill non lo esegue e te lo segnala.

## Marcatori e verifica

| Marcatore | Cosa fare |
|---|---|
| `[DA COMPLETARE: ...]` | Sostituisci con il dato reale (parti, date, importi) prima di usare la bozza. |
| `[DA VERIFICARE: estremi]` | Apri il permalink riportato accanto alla citazione (quando presente) o la fonte ufficiale indicata, prima di fondarci un argomento. |
| Termini in "Azioni e scadenze" | La skill cita solo la regola di computo e la durata per estremi (v. `references/computo_termini.md`); il conteggio sulle date reali del caso è sempre tuo. |

## Maturità per materia

Ogni materia specialistica ha un'etichetta dichiarata in anticipo, non scoperta a metà ricerca:

| Etichetta | Cosa significa |
|---|---|
| Copertura piena | Normativa, prassi e giurisprudenza (o cancelli processuali) verificati, nessuna lacuna strutturale nota. |
| Copertura parziale | Fonti solide, ma con una lacuna dichiarata (tipicamente giurisprudenza mancante o cancelli non ancora verificati). |
| Solo instradamento | Solo puntatori verificati, senza profondità: utile per orientarsi, non per fondare un atto senza verifica diretta. |

Il livello compare nel blocco "Limiti e verifiche" ogni volta che il quesito cade in un'area non a copertura piena. Elenco completo in `references/lacune.md`.

## Limiti da conoscere

| Limite | Conseguenza | Cosa fa la skill |
|---|---|---|
| Massime CED (numeri Rv) non pubbliche | Nessuna ricerca per Rv | Rassegne del Massimario come surrogato; ItalgiureWeb per gli avvocati Cassa Forense (ti prepara la query) |
| Nessun citator gratuito | Non si può provare che un precedente sia superato | Lo dichiara sempre; usa le relazioni su contrasti del Massimario |
| Merito penale e merito famiglia/minori senza fonte gratuita | Copertura scoperta | Lo dichiara e lavora su legittimità e fonti disponibili |
| Vigenza non sempre verificabile dal contesto | Rischio versione sbagliata | Rimanda a Normattiva e indica la versione ratione temporis |

Per gli estremi degli atti e il catalogo completo delle fonti: `references/` nella cartella della skill.
