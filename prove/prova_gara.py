# -*- coding: utf-8 -*-
"""Il motore del torneo: tabellone da 16 a doppio K.O.

Qui si gioca il torneo per intero, piu' volte, e si controlla che il
tabellone sia quello del foglio federale FIGeST e che la classifica torni.
"""
from comune import App, NOMI


def finale_secca(ctx, sito, dire):
    a = App(ctx, sito)
    a.estrai_e_parti()
    assert [x["n"] for x in a.pronte()] == [1, 2, 3, 4, 5, 6, 7, 8]
    assert a.conta() == (0, 16), a.conta()
    a.gioca_tutto()
    fatte, _ = a.conta()
    assert fatte == 30, "finale secca: dovevano essere 30 partite, sono %d" % fatte
    assert a.pg.locator("#garaVinta").is_visible(), "manca il vincitore"
    cl = a.classifica()
    posti = [x[0] for x in cl]
    atteso = ['1°', '2°', '3°', '4°', '5°', '5°', '7°', '7°'] + ['9°'] * 4 + ['13°'] * 4
    assert posti == atteso, posti
    assert len(set(x[1] for x in cl)) == 16, "qualcuno compare due volte: %s" % cl
    dire("torneo intero con finale secca: 30 partite, classifica completa")
    a.chiudi()


def bella(ctx, sito, dire):
    a = App(ctx, sito)
    a.estrai_e_parti()
    a.gioca_tutto(lambda n: 'b' if n == 30 else 'a')
    fatte, _ = a.conta()
    assert fatte == 31, "con la bella dovevano essere 31, sono %d" % fatte
    cl = a.classifica()
    assert [x[0] for x in cl][:2] == ['1°', '2°'] and len(cl) == 16
    dire("bella: chi arriva dai perdenti deve vincere due volte")
    a.chiudi()


def bye(ctx, sito, dire):
    a = App(ctx, sito, bye=(2, 7, 12))
    a.estrai_e_parti()
    fatte, _ = a.conta()
    ufficio = [r for r in a.storia() if r["ufficio"]]
    assert len(ufficio) == fatte and fatte >= 3, (fatte, len(ufficio))
    assert a.pg.locator("#garaStoria .esito-riga.ufficio .x").count() == 0, \
        "le partite d'ufficio non si annullano a mano"
    a.gioca_tutto()
    cl = a.classifica()
    # un bye esce 13°; se ne incontra un altro fra i perdenti passa e viene
    # eliminato al giro dopo, quindi 9°. Piu' in su non puo' arrivare.
    for i in (2, 7, 12):
        riga = [x for x in cl if x[1].startswith(NOMI[i])]
        assert len(riga) == 1, (NOMI[i], cl)
        assert riga[0][0] in ('13°', '9°'), (NOMI[i], riga)
    assert len(set(x[1] for x in cl)) == 16
    dire("tre bye: chiusi d'ufficio, eliminati senza toccare il bersaglio")
    a.chiudi()


def annulla_a_cascata(ctx, sito, dire):
    a = App(ctx, sito)
    a.estrai_e_parti()
    a.vince(1); a.vince(2)
    assert sorted(x["n"] for x in a.pronte()) == [3, 4, 5, 6, 7, 8, 9, 13]
    a.vince(9); a.vince(13)
    assert a.conta()[0] == 4

    riga = a.pg.locator("#garaStoria .esito-riga:has(.q:text-is('1'))")
    riga.locator(".x").click(); a.pg.wait_for_timeout(250)
    avviso = a.pg.locator("#garaStoria .esito-riga.chiede p").inner_text()
    assert "9" in avviso and "13" in avviso, avviso
    a.pg.locator("#garaStoria .esito-riga.chiede button").nth(1).click()
    a.pg.wait_for_timeout(250)
    assert a.conta()[0] == 4, "«Lascia stare» non doveva cancellare niente"

    riga = a.pg.locator("#garaStoria .esito-riga:has(.q:text-is('1'))")
    riga.locator(".x").click(); a.pg.wait_for_timeout(250)
    a.pg.locator("#garaStoria .esito-riga.chiede button.si").click()
    a.pg.wait_for_timeout(300)
    assert a.conta()[0] == 1, "doveva restare solo la 2, invece %d" % a.conta()[0]
    dire("annulla: avvisa di cosa cade, e se confermi porta via anche le figlie")
    a.chiudi()


def riprende_e_si_chiude(ctx, sito, dire):
    a = App(ctx, sito)
    a.estrai_e_parti()
    a.vince(1); a.vince(2)
    prima = a.conta()
    a.pg.reload(); a.pg.wait_for_timeout(700)
    assert a.vista() == "gara", "la gara non si e' riaperta"
    assert a.conta() == prima, (a.conta(), prima)
    a.pg.click("#chiudiGara"); a.pg.wait_for_timeout(200)
    a.pg.click("#chiudiGara"); a.pg.wait_for_timeout(350)
    assert a.vista() == "elenco"
    a.pg.reload(); a.pg.wait_for_timeout(700)
    assert a.vista() == "elenco", "la gara chiusa non doveva tornare"
    dire("la gara sopravvive al ricaricamento e, chiusa, non torna")
    a.chiudi()


def sedici_caselle(ctx, sito, dire):
    a = App(ctx, sito)
    assert a.pg.locator("#meno").count() == 0 and a.pg.locator(".quanti").count() == 0, \
        "c'e' ancora il selettore del numero"
    assert a.pg.locator(".giocatore").count() == 16
    a.pg.evaluate("localStorage.setItem('estrazione-torneo:giocatori', JSON.stringify("
                  "[{nome:'Tizio',bye:false},{nome:'Caio',bye:true}]))")
    a.pg.reload(); a.pg.wait_for_timeout(500)
    assert a.pg.locator(".giocatore").count() == 16
    assert a.pg.locator(".nome").first.input_value() == "Tizio"
    dire("sedici caselle fisse, e le liste corte di prima si allungano")
    a.chiudi()


def colori_dei_gironi(ctx, sito, dire):
    a = App(ctx, sito)
    a.estrai_e_parti()
    for n in range(1, 9):
        a.vince(n)
    for x in a.pronte():
        atteso = 'perdenti' if 9 <= x["n"] <= 12 else 'vincenti'
        assert atteso in x["classe"], (x["n"], x["classe"])
    sfondi = a.pg.evaluate(
        "() => { const g = n => getComputedStyle([...document.querySelectorAll('#garaPronte .incontro')]"
        ".find(e => +e.querySelector('.numP').textContent === n));"
        "return [g(9).backgroundColor, g(13).backgroundColor,"
        "        g(9).borderLeftColor, g(13).borderLeftColor]; }")
    assert sfondi[0] != sfondi[1] and sfondi[2] != sfondi[3], sfondi
    dire("perdenti e vincenti si distinguono a colpo d'occhio")
    a.chiudi()


def tabellone_del_foglio(ctx, sito, dire):
    """Casella per casella, come il foglio FIGeST: si leggono i numeri di
    posizione (1..16) che l'app stampa accanto a ogni nome."""
    a = App(ctx, sito)
    a.estrai_e_parti()
    for n in range(1, 9):
        assert a.posizioni(n) == [2 * n - 1, 2 * n], (n, a.posizioni(n))
    for n in range(1, 9):
        a.vince(n)
    assert a.posizioni(9) == [2, 4] and a.posizioni(12) == [14, 16]
    assert a.posizioni(13) == [1, 3] and a.posizioni(16) == [13, 15]
    for n in (9, 10, 11, 12, 13, 14, 15, 16):
        a.vince(n)
    # l'incrocio: il perdente della 16 sale in cima, quello della 13 va in fondo
    assert a.posizioni(17) == [2, 15], a.posizioni(17)
    assert a.posizioni(18) == [6, 11], a.posizioni(18)
    assert a.posizioni(19) == [10, 7], a.posizioni(19)
    assert a.posizioni(20) == [14, 3], a.posizioni(20)
    for n in (17, 18, 19, 20):
        a.vince(n)
    assert a.posizioni(21) == [2, 6] and a.posizioni(22) == [10, 14]
    a.vince(23); a.vince(24); a.vince(21); a.vince(22)
    assert a.posizioni(25) == [2, 5] and a.posizioni(26) == [10, 13]
    a.vince(25); a.vince(26)
    assert a.posizioni(27) == [2, 10]
    a.vince(28); a.vince(27)
    assert a.posizioni(29) == [2, 9], a.posizioni(29)
    a.vince(29)
    assert a.posizioni(30) == [1, 2]
    a.vince(30, 'b')
    assert a.posizioni(31) == [1, 2], "la bella doveva aprirsi con gli stessi due"
    dire("il tabellone e' quello del foglio, incrocio dei perdenti compreso")
    a.chiudi()


PROVE = [finale_secca, bella, bye, annulla_a_cascata, riprende_e_si_chiude,
         sedici_caselle, colori_dei_gironi, tabellone_del_foglio]
