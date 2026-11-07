# -*- coding: utf-8 -*-
"""La prima schermata: nomi, sorteggio, conto alla rovescia, temi, piede."""
from comune import App

IPHONE = ("Mozilla/5.0 (iPhone; CPU iPhone OS 17_5 like Mac OS X) AppleWebKit/605.1.15 "
          "(KHTML, like Gecko) Version/17.5 Mobile/15E148 Safari/604.1")


def elenco_e_sorteggio(ctx, sito, dire):
    a = App(ctx, sito)
    assert a.pg.locator(".testa-lista p").count() == 0, "la descrizione doveva sparire"
    assert a.pg.locator(".testa-lista .marchio").is_visible(), "manca il bersaglio nella testata"
    riga = a.pg.locator(".riga").bounding_box()
    testa = a.pg.locator(".testa-lista").bounding_box()
    assert riga["y"] >= testa["y"] + testa["height"] - 2
    assert a.largo() <= 390, "deborda di lato"
    a.estrai()
    assert a.pg.locator(".partita").count() > 0, "nessuna coppia"
    assert a.largo() <= 390
    dire("elenco e sorteggio: niente descrizione, bersaglio in testata, nessuno sbordo")
    a.chiudi()


def conto_alla_rovescia(ctx, sito, dire):
    a = App(ctx, sito)
    a.pg.click("#avvia")
    a.pg.wait_for_timeout(1500)
    assert a.pg.locator(".freccia").count() == 2, a.pg.locator(".freccia").count()
    a.pg.wait_for_timeout(1000)
    assert a.pg.locator(".freccia").count() == 3
    a.pg.wait_for_timeout(1300)
    assert a.pg.locator("#sipario").is_hidden(), "il sipario non si e' chiuso"
    assert a.pg.locator(".partita").count() > 0
    # rifacendola le freccette ripartono da capo
    a.pg.get_by_role("button", name="Rifai l'estrazione").click()
    a.pg.wait_for_timeout(700)
    assert a.pg.locator(".freccia").count() == 1
    a.pg.wait_for_timeout(3200)
    assert a.pg.locator("#sipario").is_hidden()
    dire("conto alla rovescia: una freccetta al secondo, e si rifa' da capo")
    a.chiudi()


def i_due_temi(ctx, sito, dire):
    for schema, atteso in (("light", "chiaro"), ("dark", "scuro")):
        pg = ctx.new_page()
        pg.add_init_script("localStorage.removeItem('estrazione-torneo:tema')")
        pg.emulate_media(color_scheme=schema)
        pg.goto(sito); pg.wait_for_timeout(500)
        vero = pg.get_attribute("html", "data-tema")
        assert vero == atteso, "telefono %s: mi aspettavo %s, ho %s" % (schema, atteso, vero)
        assert pg.get_attribute("#tema" + atteso.capitalize(), "aria-pressed") == "true"
        pg.close()
    a = App(ctx, sito, tema="scuro")
    a.pg.click("#temaChiaro"); a.pg.wait_for_timeout(300)
    assert a.pg.get_attribute("html", "data-tema") == "chiaro"
    assert a.pg.evaluate("document.querySelector('meta[name=\\'theme-color\\']').content") == "#f5f3ee"
    a.pg.reload(); a.pg.wait_for_timeout(500)
    assert a.pg.get_attribute("html", "data-tema") == "chiaro", "la scelta non e' sopravvissuta"
    dire("temi: segue il telefono, ma la scelta a mano vince e resta")
    a.chiudi()


def contrasti_sui_grigi(ctx, sito, dire):
    """Nel tema scuro, il testo sopra i grigi deve essere scuro: era slavato."""
    a = App(ctx, sito, bye=(2, 7, 12), tema="scuro")
    a.estrai()
    chip = a.pg.locator(".partita.conbye .n").first
    sfondo = chip.evaluate("e=>getComputedStyle(e).backgroundColor")
    testo = a.pg.locator(".partita.conbye .n b").first.evaluate("e=>getComputedStyle(e).color")
    assert sfondo == "rgb(147, 163, 189)" and testo == "rgb(15, 23, 42)", (sfondo, testo)
    dire("tema scuro: sopra i grigi l'inchiostro e' scuro, non bianco")
    a.chiudi()


def piede_e_installazione(ctx, sito, dire):
    a = App(ctx, sito)
    assert a.pg.locator("#installa").is_hidden(), "qui il tasto installa non va mostrato"
    firma = a.pg.locator(".firma a")
    assert firma.inner_text().strip() == "Powered by Rems"
    assert firma.get_attribute("href") == "https://www.instagram.com/rems_2.0_"
    assert firma.get_attribute("rel") == "noopener" and firma.get_attribute("target") == "_blank"
    assert a.pg.locator("#versione").inner_text().startswith("v")
    for f in ("manifest.webmanifest", "icona-192.png", "icona-512.png", "sw.js", "favicon.svg"):
        r = a.pg.request.get(sito + f)
        assert r.status == 200, f + " -> " + str(r.status)
    import json as _json
    man = _json.loads(a.pg.request.get(sito + "manifest.webmanifest").text())
    assert man["start_url"] == "./" and man["display"] == "standalone"
    dire("piede: firma, versione, manifesto e icone al loro posto")
    a.chiudi()


def installa_su_iphone(ctx_iphone, sito, dire):
    pg = ctx_iphone.new_page()
    pg.goto(sito); pg.wait_for_timeout(600)
    assert pg.locator("#installa").is_visible(), "su iPhone il tasto deve esserci"
    assert pg.locator("#istruzioni").is_hidden()
    pg.locator("#installa").scroll_into_view_if_needed()
    pg.click("#installa"); pg.wait_for_timeout(300)
    assert pg.locator("#istruzioni").is_visible()
    assert "Aggiungi a Home" in pg.locator("#istruzioni").inner_text()
    dire("iPhone: il tasto spiega come si aggiunge alla schermata Home")
    pg.close()


PROVE = [elenco_e_sorteggio, conto_alla_rovescia, i_due_temi,
         contrasti_sui_grigi, piede_e_installazione]
PROVE_IPHONE = [installa_su_iphone]
