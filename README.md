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

Il sorteggio è casuale davvero: usa i numeri casuali del browser
(`crypto.getRandomValues`) con un mescolamento Fisher-Yates, quindi ogni
accoppiamento ha la stessa probabilità. L'unica regola in più è che due Bye
non si incontrano, finché i numeri lo permettono: se i Bye sono più dei
presenti, qualche Bye contro Bye diventa inevitabile e la pagina lo dice.

Nomi e stato restano scritti nel browser di chi la usa (`localStorage`):
alla riapertura il tabellone è quello di prima. Non vengono inviati da
nessuna parte, non c'è un server.

## Cosa c'è dentro

Un file solo, `index.html`, con dentro struttura, stile e codice. Niente
librerie da installare, niente passaggio di compilazione. Per provarla in
locale basta aprirlo con un doppio clic, oppure:

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
