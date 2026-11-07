# Estrazione Torneo

Pagina per sorteggiare le coppie del primo turno di un torneo, pensata per
essere usata al bancone: scritte grandi, poche cose da toccare, niente
registrazione e niente connessione obbligatoria.

**Si usa qui:** <https://menems74.github.io/estrazioni_torneo/>

## Come funziona

1. Il tabellone è sempre da sedici caselle: per ognuna si scrive il nome e
   si segna **Presente** o **Bye**. Chi non c'è resta un bye.
2. Si preme **Avvia estrazione**: parte il conto alla rovescia sul
   bersaglio — una freccetta si pianta a ogni secondo — e al terzo
   compaiono le partite.
3. L'organizzatore chiama le coppie una alla volta e tocca la partita
   quando l'ha chiamata, così non perde il segno.
4. Poi **Inizia la gara**, che porta i giocatori nel tabellone a doppio
   K.O.

## La gara

Il tabellone è quello federale da 16 a doppio K.O. — si esce alla seconda
sconfitta — con una differenza voluta: la finale è doppia, cioè chi arriva
dal girone perdenti deve battere due volte chi arriva dai vincenti. In
tutto 30 partite, 31 se serve la bella.

La schermata è una fila sola: le partite con le coppie già formate, in
ordine di chiamata. Si tocca il nome di chi ha vinto e la partita scende
fra le fatte; appena un risultato completa una coppia nuova, quella
compare in cima alla fila. L'app non sa quanti tabelloni ha il locale:
chi ne ha uno chiama la prima partita, chi ne ha quattro chiama le prime
quattro.

I **bye** sono giocatori a tutti gli effetti, ma perdono d'ufficio: la
loro partita non scende mai al bersaglio, l'app la chiude da sola e lo
scrive. Se due bye si incontrano passa quello sopra, che perderà
d'ufficio anche la partita seguente.

Da **Guarda il tabellone** si vede tutto lo schema, con il filetto che
distingue i due gironi e in nero chi ha vinto; si scorre di lato e si
allarga con due dita. **Stampa il foglio** manda lo stesso tabellone,
bianco e nero, su un A4 orizzontale: buono da appendere al muro, così i
giocatori guardano da soli invece di chiedere.

Il tasto **indietro** del telefono ripercorre la strada — tabellone,
gara, coppie, elenco — invece di uscire dall'app, e durante la gara lo
schermo non si spegne da solo. Se all'elenco c'è una gara aperta, in cima
compare il richiamo per riprenderla, e rifare il sorteggio chiede conferma
prima di cancellarla.

Un tocco che arriva meno di tre decimi di secondo dopo il precedente viene
scartato e l'app lo dice: senza questa guardia il rimbalzo di un dito
chiuderebbe anche la partita salita al posto di quella appena segnata.

Un risultato sbagliato si annulla. Se ha già prodotto altre partite l'app
lo dice prima — «annullando la 1 si cancella anche la 9 e la 13» — e
aspetta conferma. La gara si salva a ogni tocco: se il telefono si spegne
o si chiude il browser, alla riapertura riprende da dov'era.

In alto a sinistra ci sono due tasti, **Chiaro** e **Scuro**: il primo è il
vestito da giorno (carta e rosso), il secondo quello da sera (blu notte e
arancio), più riposante con le luci basse. Chi non tocca niente riceve
quello del telefono; chi sceglie, se lo ritrova alla riapertura.

Il sorteggio è casuale davvero: usa i numeri casuali del browser
(`crypto.getRandomValues`) con un mescolamento Fisher-Yates, quindi ogni
accoppiamento ha la stessa probabilità. L'unica regola in più è che due Bye
non si incontrano, finché i numeri lo permettono: se i Bye sono più dei
presenti, qualche Bye contro Bye diventa inevitabile e la pagina lo dice.

## Dove finiscono i dati

Da nessuna parte. Nomi, bye, risultati e tema restano nel browser
dell'apparecchio che li ha scritti (`localStorage`): niente server,
niente account, niente che esca di lì. Due bar che usano l'app la stessa
sera non si vedono fra loro, e il repository contiene solo il codice e le
prove automatiche, mai i dati di una gara.

L'app chiede al browser di tenere l'archivio al riparo dalle pulizie
automatiche, e se una scrittura fallisce — spazio esaurito, navigazione
privata — compare una fascia rossa in cima invece di tacere. Ogni gara
salvata porta scritto il formato e la versione con cui è nata, così una
gara di domani non viene letta con le regole di ieri.

## Installarla sul telefono

In fondo alla pagina c'è **Installa App**. Su Android apre la finestra del
telefono e l'icona finisce nel cassetto delle applicazioni; su iPhone il
tasto spiega la strada, che lì è a mano: *Condividi* → *Aggiungi a Home*.
Installata, si apre a tutto schermo senza il browser intorno e funziona
anche senza linea.

## Cosa c'è dentro

`index.html` è l'app intera: struttura, stile e codice in un file solo,
senza librerie da installare e senza passaggio di compilazione. Intorno ci
sono soltanto i pezzi che servono per l'installazione sul telefono —
`manifest.webmanifest`, `sw.js` (che tiene la pagina in cache per l'uso
senza linea) e le due icone `icona-192.png` e `icona-512.png`.

Per provarla in locale basta aprire `index.html` con un doppio clic; il
tasto *Installa App* però compare solo servendo i file in https, quindi
dal sito pubblicato. In locale:

```bash
python3 -m http.server 8000   # poi http://localhost:8000
```

Dall'esterno arrivano soltanto i caratteri di Google Fonts; senza rete la
pagina funziona lo stesso, cambia solo il disegno delle lettere.

## Pubblicazione

Il sito è servito da GitHub Pages direttamente dal ramo `main`, cartella
radice (Settings → Pages → Source: *Deploy from a branch*, `main` / `/root`).
Ogni push su `main` aggiorna la pagina pubblicata nel giro di un minuto.

## Per le altre squadre

Chi vuole la propria copia può fare un fork e accendere Pages allo stesso
modo: ognuno avrà il suo indirizzo e la sua lista di giocatori, senza
disturbare gli altri.
