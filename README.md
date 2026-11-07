# Estrazione Torneo

Pagina per sorteggiare le coppie del primo turno di un torneo, pensata per
essere usata al bancone: scritte grandi, poche cose da toccare, niente
registrazione e niente connessione obbligatoria.

**Si usa qui:** <https://menems74.github.io/estrazioni_torneo/>

## Come funziona

1. Si sceglie quanti giocatori sono in tabellone (parte da 16, da 2 a 64).
2. Per ognuno si scrive il nome e si segna **Presente** o **Bye**.
3. Si preme **Avvia estrazione**: tre secondi di conto alla rovescia e
   compaiono le partite.
4. L'organizzatore chiama le coppie una alla volta e tocca la partita
   quando l'ha chiamata, così non perde il segno.

In alto a sinistra ci sono due tasti, **Chiaro** e **Scuro**: il primo è il
vestito da giorno (carta e rosso), il secondo quello da sera (blu notte e
arancio), più riposante con le luci basse. Chi non tocca niente riceve
quello del telefono; chi sceglie, se lo ritrova alla riapertura.

Il sorteggio è casuale davvero: usa i numeri casuali del browser
(`crypto.getRandomValues`) con un mescolamento Fisher-Yates, quindi ogni
accoppiamento ha la stessa probabilità. L'unica regola in più è che due Bye
non si incontrano, finché i numeri lo permettono: se i Bye sono più dei
presenti, qualche Bye contro Bye diventa inevitabile e la pagina lo dice.

Nomi e stato restano scritti nel browser di chi la usa (`localStorage`):
alla riapertura il tabellone è quello di prima. Non vengono inviati da
nessuna parte, non c'è un server.

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
