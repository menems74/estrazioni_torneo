# -*- coding: utf-8 -*-
"""Quello che tiene in piedi una gara: tocchi, tasto indietro, archivio."""
import json
from comune import App


def doppio_tocco(ctx, sito, dire):
    a = App(ctx, sito)
    a.estrai_e_parti()
    prima = a.conta()[0]
    box = a.pg.locator("#garaPronte .sfidante").first.bounding_box()
    x, y = box["x"] + box["width"] / 2, box["y"] + box["height"] / 2
    a.pg.mouse.click(x, y)
    a.pg.wait_for_timeout(120)
    a.pg.mouse.click(x, y)          # il rimbalzo del dito
    a.pg.wait_for_timeout(400)
    assert a.conta()[0] - prima == 1, \
        "due tocchi rapidi hanno segnato %d partite" % (a.conta()[0] - prima)
    assert a.pg.locator("#garaScarto").is_visible(), "doveva dire che ha scartato il tocco"
    a.pg.wait_for_timeout(400)
    a.pg.locator("#garaPronte .sfidante").first.click()
    a.pg.wait_for_timeout(300)
    assert a.conta()[0] - prima == 2, "passato il momento, il tasto deve rispondere"
    dire("doppio tocco: una partita sola, e l'app dice che ha scartato il secondo")
    a.chiudi()


def tasto_indietro(ctx, sito, dire):
    a = App(ctx, sito)
    a.estrai_e_parti()
    a.vince(1); a.vince(2)
    segnate = a.conta()[0]

    a.pg.click("#vediTabellone"); a.pg.wait_for_timeout(350)
    assert a.vista() == "tabellone"
    a.pg.go_back(); a.pg.wait_for_timeout(350)
    assert a.vista() == "gara", "indietro dal tabellone: sono in %s" % a.vista()
    a.pg.go_back(); a.pg.wait_for_timeout(350)
    assert a.vista() == "coppie", "indietro dalla gara: sono in %s" % a.vista()
    assert a.pg.locator("#etichettaAvvia").inner_text().strip() == "Torna alla gara"
    a.pg.go_back(); a.pg.wait_for_timeout(350)
    assert a.vista() == "elenco", a.vista()
    assert a.pg.locator("#ripresa").is_visible(), "manca il richiamo alla gara aperta"
    a.pg.go_forward(); a.pg.go_forward(); a.pg.wait_for_timeout(450)
    assert a.vista() == "gara", a.vista()

    # riaprendo l'app con una gara salvata, indietro resta dentro
    a.pg.reload(); a.pg.wait_for_timeout(700)
    assert a.vista() == "gara"
    a.pg.go_back(); a.pg.wait_for_timeout(350)
    # riaperta l'app la strada e' scelta -> gara, quindi indietro porta alla scelta
    assert a.vista() == "scelta", "riaperta l'app, indietro deve restare dentro: %s" % a.vista()
    assert "in corso" in a.pg.locator("#scegliTabellone .eti").inner_text().lower(), \
        "la scelta deve dire che c'e' una gara aperta"
    a.pg.click("#scegliTabellone"); a.pg.wait_for_timeout(350)
    assert a.vista() == "gara" and a.conta()[0] == segnate
    dire("indietro ripercorre la strada e non butta mai fuori dall'app")
    a.chiudi()


def sorteggio_non_cancella_di_nascosto(ctx, sito, dire):
    a = App(ctx, sito)
    a.estrai_e_parti()
    a.vince(1)
    a.pg.go_back(); a.pg.go_back(); a.pg.wait_for_timeout(500)   # elenco
    assert a.vista() == "elenco"
    a.pg.click("#avvia"); a.pg.wait_for_timeout(400)
    assert a.vista() == "elenco", "non doveva partire il sorteggio"
    assert "gara in corso" in a.pg.locator("#avviso").inner_text()
    assert a.gara_salvata(), "la gara non doveva sparire al primo tocco"
    a.pg.wait_for_timeout(300)
    a.pg.click("#avvia"); a.pg.wait_for_timeout(4400)
    assert a.vista() == "coppie"
    assert a.gara_salvata() is None, "al secondo tocco la vecchia gara doveva sparire"
    dire("rifare il sorteggio con una gara aperta chiede conferma")
    a.chiudi()


def archivio(ctx, sito, dire):
    a = App(ctx, sito)
    a.estrai_e_parti()
    salvata = a.gara_salvata()
    assert salvata["formato"] == "tab16-dko" and salvata["v"] == 1 and salvata["nata"], salvata.keys()

    # una gara scritta da una versione futura non si apre e non si rovina
    a.pg.evaluate("() => { const g = JSON.parse(localStorage.getItem('estrazione-torneo:gara'));"
                  "g.v = 99; localStorage.setItem('estrazione-torneo:gara', JSON.stringify(g)); }")
    a.pg.reload(); a.pg.wait_for_timeout(700)
    assert a.vista() == "scelta", a.vista()
    assert a.pg.locator("#allarme").is_visible()
    assert "versione più nuova" in a.pg.locator("#allarme").inner_text()
    assert a.pg.evaluate("localStorage.getItem('estrazione-torneo:gara')"), "non doveva cancellarla"
    dire("la gara salvata dice formato e versione, e una dal futuro non viene toccata")
    a.chiudi()


def archivio_che_non_scrive(ctx, sito, dire):
    a = App(ctx, sito)
    a.pg.evaluate("() => { Storage.prototype.setItem = function(){ throw new Error('pieno'); }; }")
    a.pg.locator(".nome").first.fill("Prova")
    a.pg.locator(".nome").first.dispatch_event("input")
    a.pg.wait_for_timeout(300)
    assert a.pg.locator("#allarme").is_visible(), "doveva comparire la fascia rossa"
    assert "non sta salvando" in a.pg.locator("#allarme").inner_text()
    dire("se l'apparecchio non salva, l'app lo dice invece di tacere")
    a.chiudi()


PROVE = [doppio_tocco, tasto_indietro, sorteggio_non_cancella_di_nascosto,
         archivio, archivio_che_non_scrive]
