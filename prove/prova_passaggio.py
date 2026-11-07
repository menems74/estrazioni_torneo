# -*- coding: utf-8 -*-
"""Portare via una gara: il file di copia e il link per un altro apparecchio."""
import json, os, tempfile
from comune import App


def _gara_a_meta(ctx, sito, bye=()):
    a = App(ctx, sito, bye=bye)
    a.estrai_e_parti()
    for _ in range(6):
        pr = a.pronte()
        if not pr:
            break
        a.vince(pr[0]["n"])
    return a


def link_di_passaggio(ctx, sito, dire):
    a = _gara_a_meta(ctx, sito)
    fatte, _ = a.conta()
    classifica_prima = a.classifica()
    storia_prima = [r["testo"] for r in a.storia()]

    # il link: lo prendiamo dal codice come lo costruisce il tasto
    a.pg.evaluate("""() => {
        Object.defineProperty(navigator, 'clipboard', {value:undefined, configurable:true});
        Object.defineProperty(navigator, 'share', {value:undefined, configurable:true}); }""")
    a.pg.locator("#passaGara").scroll_into_view_if_needed()
    a.pg.click("#passaGara"); a.pg.wait_for_timeout(400)
    campo = a.pg.locator("#notaPassa input")
    assert campo.count() == 1, "doveva mostrare l'indirizzo da copiare"
    via = campo.input_value()
    assert "#g=" in via, via
    assert len(via) < 1800, "link troppo lungo per una chat: %d caratteri" % len(via)
    avviso = a.pg.locator("#notaPassa").inner_text()
    assert "nomi dei giocatori" in avviso, "deve dire cosa contiene il link"
    a.chiudi()

    # un altro apparecchio: contesto nuovo, archivio vuoto
    b = ctx.browser.new_context(viewport={"width": 390, "height": 844})
    pg = b.new_page()
    pg.goto(via); pg.wait_for_timeout(700)
    assert pg.locator("#invito").is_visible(), "doveva chiedere, non aprirsi da sola"
    assert "%d partite segnate" % fatte in pg.locator("#invitoTesto").inner_text(), \
        pg.locator("#invitoTesto").inner_text()
    assert pg.locator("#vistaGara").is_hidden(), "non deve entrare in gara prima del sì"
    assert "#g=" not in pg.url, "l'indirizzo doveva essere ripulito: %s" % pg.url

    pg.click("#invitoSi"); pg.wait_for_timeout(500)
    assert pg.locator("#vistaGara").is_visible()
    dopo = int(pg.locator("#garaConta").inner_text())
    assert dopo == fatte, "di là ci sono %d partite invece di %d" % (dopo, fatte)
    cl = pg.evaluate("() => [...document.querySelectorAll('#garaClassifica .posto')]"
                     ".map(e => [e.querySelector('.pp').textContent, e.querySelector('.nn').textContent])")
    assert cl == classifica_prima, (cl, classifica_prima)
    st = pg.evaluate("() => [...document.querySelectorAll('#garaStoria .esito-riga')]"
                     ".map(e => e.innerText.replace(/\\n/g,' '))")
    assert st == storia_prima, "i risultati non combaciano"
    # e continua a funzionare
    pronte = pg.evaluate("() => document.querySelectorAll('#garaPronte .incontro').length")
    assert pronte > 0
    pg.close(); b.close()
    dire("link: chiede prima di aprire, e di là la gara e' identica (%d caratteri)" % len(via))


def link_rifiutato_e_rotto(ctx, sito, dire):
    a = _gara_a_meta(ctx, sito)
    a.pg.evaluate("""() => {
        Object.defineProperty(navigator, 'clipboard', {value:undefined, configurable:true});
        Object.defineProperty(navigator, 'share', {value:undefined, configurable:true}); }""")
    a.pg.locator("#passaGara").scroll_into_view_if_needed()
    a.pg.click("#passaGara"); a.pg.wait_for_timeout(400)
    via = a.pg.locator("#notaPassa input").input_value()
    a.chiudi()

    b = ctx.browser.new_context(viewport={"width": 390, "height": 844})
    pg = b.new_page()
    # si può dire di no
    pg.goto(via); pg.wait_for_timeout(700)
    pg.click("#invitoNo"); pg.wait_for_timeout(300)
    assert pg.locator("#invito").is_hidden() and pg.locator("#vistaElenco").is_visible()
    assert pg.evaluate("localStorage.getItem('estrazione-torneo:gara')") is None, \
        "aver detto no non deve lasciare niente"
    # un link storpiato non apre niente e lo dice
    pg.goto(via[:-12] + "zzzzzzzzzzzz"); pg.wait_for_timeout(700)
    assert pg.locator("#vistaElenco").is_visible()
    assert pg.locator("#invito").is_hidden(), "un link rotto non deve proporre niente"
    assert pg.locator("#allarme").is_visible()
    pg.close(); b.close()
    dire("link: si può rifiutare, e uno spezzato non apre niente")


def nomi_con_dentro_del_codice(ctx, sito, dire):
    """Una gara che arriva da fuori puo' avere nomi scritti apposta per
    fare danni: devono restare testo."""
    a = App(ctx, sito)
    a.pg.evaluate("""() => {
        const brutto = '<img src=x onerror=\\"window.__bucato=1\\">';
        const lista = [...Array(16)].map((_,i) => ({nome: i===0 ? brutto : 'G'+(i+1), bye:false}));
        localStorage.setItem('estrazione-torneo:giocatori', JSON.stringify(lista)); }""")
    a.pg.reload(); a.pg.wait_for_timeout(500)
    a.estrai_e_parti()
    a.vince(a.pronte()[0]["n"])
    a.vince(a.pronte()[0]["n"])
    # nel tabellone ci sono tutti e sedici i nomi, qualunque sia il sorteggio
    a.pg.click("#vediTabellone"); a.pg.wait_for_timeout(400)
    assert a.pg.evaluate("window.__bucato") is None, "il nome ha eseguito del codice"
    assert a.pg.locator("#tabellone img").count() == 0, "il nome e' diventato un pezzo di pagina"
    testo = a.pg.locator("#tabellone").inner_text()
    assert "<img" in testo, "il nome doveva comparire come testo"
    a.chiudi()
    dire("un nome che contiene del codice resta testo e non combina niente")


def copia_su_file(ctx, sito, dire):
    a = _gara_a_meta(ctx, sito, bye=(3,))
    fatte, _ = a.conta()
    with a.pg.expect_download() as atteso:
        a.pg.locator("#salvaCopia").scroll_into_view_if_needed()
        a.pg.click("#salvaCopia")
    scarico = atteso.value
    dove = os.path.join(tempfile.mkdtemp(), scarico.suggested_filename)
    scarico.save_as(dove)
    assert scarico.suggested_filename.startswith("torneo-") and \
        scarico.suggested_filename.endswith(".json"), scarico.suggested_filename
    with open(dove, encoding="utf-8") as f:
        copia = json.load(f)
    assert copia["f"] == "tab16-dko" and len(copia["n"]) == 16, copia.keys()
    a.chiudi()

    # si riapre su un apparecchio pulito
    b = ctx.browser.new_context(viewport={"width": 390, "height": 844}, accept_downloads=True)
    pg = b.new_page()
    pg.goto(sito); pg.wait_for_timeout(500)
    pg.set_input_files("#fileCopia", dove)
    pg.wait_for_timeout(600)
    assert pg.locator("#invito").is_visible(), "anche il file deve chiedere prima di aprire"
    pg.click("#invitoSi"); pg.wait_for_timeout(500)
    assert int(pg.locator("#garaConta").inner_text()) == fatte
    pg.close(); b.close()
    dire("copia su file: si salva, si riapre altrove e chiede sempre prima")


PROVE = [link_di_passaggio, link_rifiutato_e_rotto, nomi_con_dentro_del_codice, copia_su_file]
