# -*- coding: utf-8 -*-
"""Fa girare tutte le prove.

    python3 prove/esegui.py            tutte
    python3 prove/esegui.py gara       solo quelle della gara

Serve la cartella del progetto su una porta libera, apre Chromium e usa
l'app come la userebbe una persona. Non serve niente di installato oltre
a Playwright.
"""
import sys, time, traceback
from playwright.sync_api import sync_playwright

import comune
import prova_estrazione, prova_gara, prova_tabellone, prova_stabilita, prova_passaggio
import prova_girone

GRUPPI = [
    ("estrazione", prova_estrazione),
    ("gara",       prova_gara),
    ("tabellone",  prova_tabellone),
    ("stabilita",  prova_stabilita),
    ("passaggio",  prova_passaggio),
    ("girone",     prova_girone),
]
IPHONE = prova_estrazione.IPHONE
TELEFONO = {"width": 390, "height": 844}
TABLET = {"width": 1180, "height": 900}


def main():
    volute = [a.lower() for a in sys.argv[1:]]
    gruppi = [g for g in GRUPPI if not volute or g[0] in volute]
    if not gruppi:
        print("gruppi: " + ", ".join(g[0] for g in GRUPPI))
        return 2

    fatte = andate = 0
    inizio = time.time()
    with comune.sito() as indirizzo, sync_playwright() as pw:
        b = comune.browser(pw)
        telefono = b.new_context(viewport=TELEFONO, device_scale_factor=2)
        tablet = b.new_context(viewport=TABLET, device_scale_factor=2)
        iphone = b.new_context(viewport=TELEFONO, user_agent=IPHONE)

        for nome, modulo in gruppi:
            print("\n=== %s" % nome)
            elenco = [(p, telefono) for p in getattr(modulo, "PROVE", [])]
            elenco += [(p, iphone) for p in getattr(modulo, "PROVE_IPHONE", [])]
            elenco += [(p, tablet) for p in getattr(modulo, "PROVE_TABLET", [])]
            for prova, ctx in elenco:
                fatte += 1
                def dire(testo, _p=prova):
                    print("   ok  %s" % testo)
                try:
                    prova(ctx, indirizzo, dire)
                    andate += 1
                except Exception:
                    print("   NO  %s" % prova.__name__)
                    traceback.print_exc()
        b.close()

    print("\n%d prove su %d in %.0f secondi" % (andate, fatte, time.time() - inizio))
    if andate != fatte:
        print("ESITO: qualcosa non va")
        return 1
    print("ESITO: tutto verde")
    return 0


if __name__ == "__main__":
    sys.exit(main())
