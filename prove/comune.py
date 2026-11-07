# -*- coding: utf-8 -*-
"""Attrezzi comuni a tutte le prove.

Le prove aprono l'app in un browser vero e la usano come la userebbe una
persona: toccano i nomi, avviano il sorteggio, segnano i risultati. Non
guardano dentro al codice, guardano cosa succede a schermo — così
continuano a valere anche se il codice viene riscritto.

I nomi dei giocatori sono inventati: qui dentro non entra mai un dato di
una gara vera.
"""

import json, os, socket, subprocess, sys, time, contextlib

RADICE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

NOMI = ["Marco", "Luca", "Andrea", "Giulia", "Paolo", "Sara", "Davide", "Fabio",
        "Elena", "Simone", "Chiara", "Matteo", "Alessio", "Nicola", "Ilaria", "Stefano"]

# Fra un tocco e l'altro l'app ne scarta uno che arrivi entro tre decimi di
# secondo: qui si aspetta un filo di piu', come farebbe un dito.
PAUSA = 340


def giocatori(bye=()):
    return [{"nome": n, "bye": i in bye} for i, n in enumerate(NOMI)]


def porta_libera():
    s = socket.socket()
    s.bind(("127.0.0.1", 0))
    p = s.getsockname()[1]
    s.close()
    return p


@contextlib.contextmanager
def sito():
    """Serve la cartella del progetto su una porta libera."""
    porta = porta_libera()
    p = subprocess.Popen([sys.executable, "-m", "http.server", str(porta), "--bind", "127.0.0.1"],
                         cwd=RADICE, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    indirizzo = "http://127.0.0.1:%d/" % porta
    for _ in range(100):
        try:
            socket.create_connection(("127.0.0.1", porta), 0.2).close()
            break
        except OSError:
            time.sleep(0.1)
    try:
        yield indirizzo
    finally:
        p.terminate()
        p.wait(timeout=10)


def browser(pw):
    """Chromium: quello di sistema se c'e', se no quello di Playwright."""
    suo = os.environ.get("CHROMIUM")
    if not suo:
        for p in ("/opt/pw-browsers/chromium-1194/chrome-linux/chrome",
                  "/opt/pw-browsers/chromium/chrome-linux/chrome"):
            if os.path.exists(p):
                suo = p
                break
    opzioni = {"args": ["--no-sandbox"]}
    if suo:
        opzioni["executable_path"] = suo
    return pw.chromium.launch(**opzioni)


class App:
    """L'app aperta in una pagina, con i gesti che servono alle prove."""

    def __init__(self, contesto, indirizzo, bye=(), tema="scuro"):
        self.errori = []
        self.pg = contesto.new_page()
        self.pg.on("console", self._console)
        self.pg.on("pageerror", lambda e: self.errori.append("pageerror: " + str(e)))
        self.pg.add_init_script(
            "if(!sessionStorage.getItem('pronto')){"
            "localStorage.clear();"
            "localStorage.setItem('estrazione-torneo:giocatori', %s);"
            "localStorage.setItem('estrazione-torneo:tema', '%s');"
            "sessionStorage.setItem('pronto','1');}"
            % (json.dumps(json.dumps(giocatori(bye))), tema))
        self.pg.goto(indirizzo)
        self.pg.wait_for_timeout(400)

    def _console(self, m):
        # il 404 della favicon non e' un errore della pagina
        if m.type == "error" and "favicon" not in m.text:
            self.errori.append(m.type + ": " + m.text)

    # ---------------------------------------------------------- navigare --
    def vista(self):
        for n in ("Elenco", "Coppie", "Gara", "Tabellone"):
            if self.pg.locator("#vista" + n).is_visible():
                return n.lower()
        return "?"

    def estrai(self):
        self.pg.click("#avvia")
        self.pg.wait_for_timeout(4300)

    def inizia(self):
        assert self.pg.locator("#etichettaAvvia").inner_text().strip() == "Inizia la gara", \
            self.pg.locator("#etichettaAvvia").inner_text()
        self.pg.click("#avvia")
        self.pg.wait_for_timeout(400)

    def estrai_e_parti(self):
        self.estrai()
        self.inizia()

    # ------------------------------------------------------------- gara ---
    def pronte(self):
        return self.pg.evaluate(
            "() => [...document.querySelectorAll('#garaPronte .incontro')]"
            ".map(e => ({n:+e.querySelector('.numP').textContent,"
            "            classe:e.className,"
            "            pos:[...e.querySelectorAll('.sfidante .pos')].map(x=>+x.textContent),"
            "            nomi:[...e.querySelectorAll('.sfidante .gg')].map(x=>x.textContent.trim())}))")

    def posizioni(self, n):
        for x in self.pronte():
            if x["n"] == n:
                return x["pos"]
        return None

    def vince(self, n, lato="a"):
        self.pg.locator("#garaPronte .incontro:has(.numP:text-is('%d')) .sfidante" % n) \
            .nth(0 if lato == "a" else 1).click()
        self.pg.wait_for_timeout(PAUSA)

    def gioca_tutto(self, scelta=lambda n: "a", massimo=60):
        giri = 0
        while True:
            pr = self.pronte()
            if not pr:
                return giri
            self.vince(pr[0]["n"], scelta(pr[0]["n"]))
            giri += 1
            assert giri < massimo, "troppe partite: qualcosa gira a vuoto"

    def conta(self):
        return (int(self.pg.locator("#garaConta").inner_text()),
                int(self.pg.locator("#garaVivi").inner_text()))

    def classifica(self):
        return self.pg.evaluate(
            "() => [...document.querySelectorAll('#garaClassifica .posto')]"
            ".map(e => [e.querySelector('.pp').textContent, e.querySelector('.nn').textContent])")

    def storia(self):
        return self.pg.evaluate(
            "() => [...document.querySelectorAll('#garaStoria .esito-riga')]"
            ".map(e => ({n:e.querySelector('.q') ? +e.querySelector('.q').textContent : 0,"
            "            testo:e.innerText.replace(/\\n/g,' '),"
            "            ufficio:e.classList.contains('ufficio')}))")

    def gara_salvata(self):
        g = self.pg.evaluate("localStorage.getItem('estrazione-torneo:gara')")
        return json.loads(g) if g else None

    # ------------------------------------------------------------ varie ---
    def largo(self):
        return self.pg.evaluate("document.body.scrollWidth")

    def chiudi(self):
        assert not self.errori, "errori in console: %s" % self.errori
        self.pg.close()
