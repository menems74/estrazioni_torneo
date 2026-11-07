# -*- coding: utf-8 -*-
"""Il girone all'italiana, per ora in prova dietro un indirizzo apposta."""
from comune import App, NOMI


def _apri(ctx, sito, quanti=None):
    a = App(ctx, sito, formato="girone")
    assert a.vista() == "gelenco", a.vista()
    if quanti:
        ora = int(a.pg.locator("#girNumero").inner_text())
        tasto = "#girPiu" if quanti > ora else "#girMeno"
        for _ in range(abs(quanti - ora)):
            a.pg.click(tasto); a.pg.wait_for_timeout(120)
    n = int(a.pg.locator("#girNumero").inner_text())
    for i in range(n):
        a.pg.locator("#girElenco .nome").nth(i).fill(NOMI[i])
        a.pg.locator("#girElenco .nome").nth(i).dispatch_event("input")
    a.pg.wait_for_timeout(200)
    a.pg.click("#girInizia"); a.pg.wait_for_timeout(400)
    assert a.vista() == "ggara", a.vista()
    return a


def _partite(a):
    return a.pg.evaluate(
        "() => [...document.querySelectorAll('#girDaFare .incontro')].map(e => ({"
        "n:+e.querySelector('.numP').textContent,"
        "turno:e.closest('.fila').previousElementSibling.textContent,"
        "nomi:[...e.querySelectorAll('.sfidante .gg')].map(x=>x.textContent.trim())}))")


def _classifica(a):
    return a.pg.evaluate(
        "() => [...document.querySelectorAll('#girClassifica .voce')].map(e => ({"
        "posto:e.querySelector('.pst').textContent,"
        "chi:e.querySelector('.chi>span').textContent,"
        "perche:e.querySelector('.chi small') ? e.querySelector('.chi small').textContent : '',"
        "g:+e.querySelectorAll('.num')[0].textContent,"
        "v:+e.querySelectorAll('.num')[1].textContent,"
        "pt:+e.querySelector('.pti').textContent}))")


def _vince_prima(a):
    a.pg.locator("#girDaFare .incontro .sfidante").first.click()
    a.pg.wait_for_timeout(340)


def dalla_scelta(ctx, sito, dire):
    a = App(ctx, sito, formato=None)
    assert a.vista() == "scelta", a.vista()
    assert a.pg.locator("#scegliGirone").is_enabled(), "il girone deve essere cliccabile"
    # inner_text torna in maiuscolo: e' il CSS che le scrive cosi'
    assert a.pg.locator("#scegliTabellone .eti").inner_text().strip().lower() == "16 giocatori"
    assert "16 giocatori" in a.pg.locator("#etiGirone").inner_text().lower()

    a.pg.click("#scegliTabellone"); a.pg.wait_for_timeout(300)
    assert a.vista() == "elenco"
    a.pg.go_back(); a.pg.wait_for_timeout(300)
    assert a.vista() == "scelta"
    a.pg.click("#scegliGirone"); a.pg.wait_for_timeout(300)
    assert a.vista() == "gelenco", "dalla scelta si deve entrare nel girone: %s" % a.vista()
    a.pg.go_back(); a.pg.wait_for_timeout(300)
    assert a.vista() == "scelta", "e indietro si deve tornare alla scelta"
    a.chiudi()

    # l'indirizzo con #girone resta una scorciatoia
    b = App(ctx, sito, formato="girone")
    assert b.vista() == "gelenco"
    b.chiudi()
    dire("i due tornei si scelgono dalla prima schermata, e #girone resta una scorciatoia")


def calendario_pari(ctx, sito, dire):
    a = _apri(ctx, sito, quanti=6)
    P = _partite(a)
    assert len(P) == 15, "sei giocatori fanno quindici partite, non %d" % len(P)
    turni = {}
    for p in P:
        turni.setdefault(p["turno"], []).append(p["nomi"])
    assert len(turni) == 5, "dovevano essere cinque turni, sono %d" % len(turni)
    for turno, partite in turni.items():
        assert len(partite) == 3, (turno, partite)
        dentro = [n for coppia in partite for n in coppia]
        assert len(set(dentro)) == 6, "%s: qualcuno gioca due volte" % turno
    coppie = set(tuple(sorted(p["nomi"])) for p in P)
    assert len(coppie) == 15, "due giocatori si incontrano piu' di una volta"
    dire("sei giocatori: 15 partite in 5 turni, nessuno gioca due volte nello stesso turno")
    a.chiudi()


def calendario_dispari(ctx, sito, dire):
    a = _apri(ctx, sito, quanti=5)
    P = _partite(a)
    assert len(P) == 10, len(P)
    turni = {}
    for p in P:
        turni.setdefault(p["turno"], []).append(p["nomi"])
    assert len(turni) == 5
    for turno, partite in turni.items():
        assert len(partite) == 2, (turno, partite)
        dentro = [n for coppia in partite for n in coppia]
        assert len(set(dentro)) == 4, "%s: qualcuno gioca due volte" % turno
    dire("cinque giocatori: 10 partite, e a ogni turno uno riposa")
    a.chiudi()


def girone_intero(ctx, sito, dire):
    a = _apri(ctx, sito, quanti=5)
    totali = int(a.pg.locator("#girTotali").inner_text())
    for _ in range(totali):
        _vince_prima(a)
    assert int(a.pg.locator("#girConta").inner_text()) == totali
    assert len(_partite(a)) == 0, "non dovevano restare partite da chiamare"
    cl = _classifica(a)
    assert len(cl) == 5
    assert sum(r["v"] for r in cl) == totali, "le vittorie non tornano"
    assert sum(r["g"] for r in cl) == totali * 2, "le partite giocate non tornano"
    assert all(r["pt"] == r["v"] * 2 for r in cl), "due punti a vittoria"
    punti = [r["pt"] for r in cl]
    assert punti == sorted(punti, reverse=True), punti
    assert a.pg.locator("#girVinta").is_visible(), "manca il vincitore"
    dire("girone intero: la classifica torna e il primo e' in cima")
    a.chiudi()


def scontro_diretto(ctx, sito, dire):
    """Tre giocatori che si battono in cerchio: pari punti e pari scontri."""
    a = _apri(ctx, sito, quanti=3)
    for _ in range(3):
        _vince_prima(a)
    cl = _classifica(a)
    assert len(cl) == 3 and all(r["pt"] == 2 for r in cl), cl
    assert all(r["posto"] == "1°" for r in cl), "a pari merito stanno tutti primi: %s" % cl
    nota = a.pg.locator("#girClassifica .pari")
    assert nota.count() == 1 and "spareggio" in nota.inner_text()
    assert all(r["perche"] == "" for r in cl), \
        "qui nessuno e' stato separato dallo scontro diretto: %s" % cl
    assert "pari merito" in a.pg.locator("#girVinta").inner_text().lower()
    dire("tre vittorie in cerchio: pari merito dichiarato, niente vincitore inventato")
    a.chiudi()


def annulla_e_riprende(ctx, sito, dire):
    a = _apri(ctx, sito, quanti=4)
    _vince_prima(a); _vince_prima(a)
    assert int(a.pg.locator("#girConta").inner_text()) == 2
    prima = _classifica(a)

    a.pg.reload(); a.pg.wait_for_timeout(700)
    assert a.vista() == "ggara", "il girone non si e' riaperto: %s" % a.vista()
    assert int(a.pg.locator("#girConta").inner_text()) == 2
    assert _classifica(a) == prima

    a.pg.locator("#girStoria .esito-riga .x").first.click()
    a.pg.wait_for_timeout(350)
    assert int(a.pg.locator("#girConta").inner_text()) == 1, "l'annulla non ha tolto niente"

    # e il doppio tocco e' scartato anche qui
    a.pg.locator("#girDaFare .sfidante").first.scroll_into_view_if_needed()
    a.pg.wait_for_timeout(200)
    box = a.pg.locator("#girDaFare .sfidante").first.bounding_box()
    x, y = box["x"] + box["width"] / 2, box["y"] + box["height"] / 2
    a.pg.mouse.click(x, y); a.pg.wait_for_timeout(120); a.pg.mouse.click(x, y)
    a.pg.wait_for_timeout(400)
    assert int(a.pg.locator("#girConta").inner_text()) == 2, "due tocchi rapidi hanno segnato troppo"
    assert a.pg.locator("#girScarto").is_visible()

    a.pg.click("#girChiudi"); a.pg.wait_for_timeout(200)
    a.pg.click("#girChiudi"); a.pg.wait_for_timeout(350)
    assert a.vista() == "scelta", "chiudendo si torna alla scelta del torneo: %s" % a.vista()
    assert a.pg.evaluate("localStorage.getItem('estrazione-torneo:girone')") is None
    dire("annulla, ricaricamento, doppio tocco e chiusura: come nel tabellone")
    a.chiudi()


def fino_a_sedici(ctx, sito, dire):
    a = _apri(ctx, sito, quanti=16)
    assert a.pg.locator("#girTotali").inner_text() == "120", \
        "sedici giocatori fanno 120 partite, non %s" % a.pg.locator("#girTotali").inner_text()
    P = _partite(a)
    assert len(P) == 120
    turni = {}
    for p in P:
        turni.setdefault(p["turno"], []).append(p["nomi"])
    assert len(turni) == 15, len(turni)
    for turno, partite in turni.items():
        assert len(partite) == 8, (turno, len(partite))
        dentro = [n for coppia in partite for n in coppia]
        assert len(set(dentro)) == 16, "%s: qualcuno gioca due volte" % turno
    a.chiudi()
    dire("sedici giocatori: 120 partite in 15 turni da otto")


def etichetta_scontro_diretto(ctx, sito, dire):
    """Quattro giocatori a coppie di pari punti: a ogni coppia l'ordine lo
    decide lo scontro diretto, e la classifica deve dirlo."""
    a = _apri(ctx, sito, quanti=4)
    chi = NOMI[:4]                       # Marco, Luca, Andrea, Giulia
    vince = {
        (chi[0], chi[1]): chi[0], (chi[0], chi[2]): chi[0], (chi[0], chi[3]): chi[3],
        (chi[1], chi[2]): chi[1], (chi[1], chi[3]): chi[1], (chi[2], chi[3]): chi[2],
    }
    while True:
        P = _partite(a)
        if not P:
            break
        m = P[0]
        uno, due = m["nomi"]
        w = vince.get((uno, due)) or vince.get((due, uno))
        lato = 0 if uno == w else 1
        c = a.pg.locator("#girDaFare .incontro:has(.numP:text-is('%d')) .sfidante" % m["n"])
        c.nth(lato).scroll_into_view_if_needed()
        c.nth(lato).click()
        a.pg.wait_for_timeout(340)

    cl = _classifica(a)
    assert [r["chi"] for r in cl] == [chi[0], chi[1], chi[2], chi[3]], cl
    assert [r["pt"] for r in cl] == [4, 4, 2, 2], cl
    assert [r["posto"] for r in cl] == ["1°", "2°", "3°", "4°"], cl
    assert all(r["perche"].lower() == "scontro diretto" for r in cl), \
        "tutti e quattro sono stati separati dallo scontro diretto: %s" % cl
    assert a.pg.locator("#girClassifica .pari").count() == 0, "qui non c'e' nessun pari merito"
    a.chiudi()
    dire("a pari punti la classifica scrive che a decidere e' stato lo scontro diretto")


PROVE = [dalla_scelta, calendario_pari, calendario_dispari, fino_a_sedici,
         girone_intero, scontro_diretto, etichetta_scontro_diretto, annulla_e_riprende]
