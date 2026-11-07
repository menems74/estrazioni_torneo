# -*- coding: utf-8 -*-
"""Il tabellone intero e il foglio da stampare."""
from comune import App

# A4 orizzontale con 8 mm di margine: 281 mm di larghezza e 194 di altezza.
# In pixel di stampa (96 per pollice) fanno 1062 e 733.
LARGO_A4 = 1062


def tabellone_intero(ctx, sito, dire):
    a = App(ctx, sito, bye=(2, 7, 12), tema="chiaro")
    a.estrai_e_parti()
    for _ in range(14):
        pr = a.pronte()
        if not pr:
            break
        a.vince(pr[0]["n"])
    a.pg.click("#vediTabellone"); a.pg.wait_for_timeout(400)
    assert a.vista() == "tabellone"
    caselle = a.pg.locator("#tabellone .casella").count()
    assert caselle == 31, caselle

    pos = a.pg.evaluate(
        "() => [...document.querySelectorAll('#tabellone .casella')].map(e => {"
        "const r = e.getBoundingClientRect();"
        "return {n:e.querySelector('.cn').textContent.split(' ')[0],"
        "        x:r.x, y:r.y, w:r.width, h:r.height}; })")
    for i in range(len(pos)):
        for j in range(i + 1, len(pos)):
            u, d = pos[i], pos[j]
            sovra = (u["x"] < d["x"] + d["w"] - 1 and d["x"] < u["x"] + u["w"] - 1 and
                     u["y"] < d["y"] + d["h"] - 1 and d["y"] < u["y"] + u["h"] - 1)
            assert not sovra, "le caselle %s e %s si sovrappongono" % (u["n"], d["n"])

    def x(n):
        return [q for q in pos if q["n"] == str(n)][0]["x"]
    ordine = [29, 27, 25, 21, 17, 9, 1, 13, 23, 28, 30]
    assert all(x(ordine[i]) < x(ordine[i + 1]) for i in range(len(ordine) - 1)), \
        "le colonne non sono nell'ordine del foglio"
    assert a.pg.locator("#tabellone .slot.vinto").count() >= 14
    dire("tabellone: 31 caselle, nessuna sovrapposta, colonne nell'ordine del foglio")

    # torna alla gara e il tasto in alto ricompare
    a.pg.click("#tornaGara"); a.pg.wait_for_timeout(300)
    assert a.vista() == "gara" and a.pg.locator("#vediTabellone").is_visible()
    a.chiudi()


def foglio_a4(ctx, sito, dire):
    a = App(ctx, sito, tema="scuro")
    a.estrai_e_parti()
    for _ in range(10):
        pr = a.pronte()
        if not pr:
            break
        a.vince(pr[0]["n"])
    a.pg.click("#vediTabellone"); a.pg.wait_for_timeout(400)
    a.pg.emulate_media(media="print"); a.pg.wait_for_timeout(300)

    stato = a.pg.evaluate(
        "() => ({capo:getComputedStyle(document.querySelector('.capoTab')).display,"
        "        piede:getComputedStyle(document.querySelector('.piede')).display,"
        "        testata:getComputedStyle(document.querySelector('.intestazione-stampa')).display,"
        "        largo:document.getElementById('tabellone').getBoundingClientRect().width,"
        "        alto:document.getElementById('vistaTabellone').getBoundingClientRect().bottom})")
    assert stato["capo"] == "none" and stato["piede"] == "none", stato
    assert stato["testata"] == "block", "manca l'intestazione del foglio"
    assert stato["largo"] <= LARGO_A4 - 20, "non entra in larghezza: %d" % stato["largo"]
    assert stato["alto"] <= 733, "non entra in altezza: %d, verrebbero due pagine" % stato["alto"]
    a.pg.emulate_media(media="screen")
    dire("foglio: una pagina sola di A4 orizzontale, %d px su %d disponibili"
         % (round(stato["largo"]), LARGO_A4))
    a.chiudi()


PROVE = [tabellone_intero]
PROVE_TABLET = [foglio_a4]      # il foglio si stampa, non si guarda sul telefono
