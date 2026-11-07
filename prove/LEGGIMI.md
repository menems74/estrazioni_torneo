# Le prove

Controllano che l'app funzioni davvero, usandola in un browser vero come
la userebbe una persona: toccano i nomi, avviano il sorteggio, segnano i
risultati, premono il tasto indietro. Non guardano dentro al codice, così
restano valide anche se il codice viene riscritto.

**Qui dentro non entra nessun dato di una gara vera.** I giocatori si
chiamano Marco, Luca, Andrea: sono inventati, e devono restare inventati.

## Farle girare

```bash
pip install playwright
python3 -m playwright install --with-deps chromium
python3 prove/esegui.py
```

Per farne girare solo un gruppo: `python3 prove/esegui.py gara`. I gruppi
sono `estrazione`, `gara`, `tabellone`, `stabilita`.

Girano anche da sole a ogni modifica spedita su GitHub: vedi
`.github/workflows/prove.yml`.

## Cosa controllano

- **estrazione** — la prima schermata, il conto alla rovescia con le
  freccette, i due temi, i contrasti sui grigi, il piede e l'installazione.
- **gara** — tornei interi giocati fino in fondo: finale secca e bella, i
  bye chiusi d'ufficio, l'annulla a cascata, la gara che riprende dopo il
  ricaricamento, e il controllo casella per casella che il tabellone sia
  quello del foglio federale.
- **tabellone** — le 31 caselle senza sovrapposizioni, nell'ordine giusto,
  e il foglio che entra in una pagina sola di A4 orizzontale.
- **stabilita** — il doppio tocco scartato, il tasto indietro, la gara che
  non si cancella per sbaglio, il formato scritto nei dati, la fascia
  rossa quando l'apparecchio non salva.
