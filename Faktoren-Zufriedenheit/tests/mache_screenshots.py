"""Erzeugt die Bilder in screenshots/ fuer die Kernansichten (Desktop 1280 und Handy 390x844 mit Touch):
Entscheidung, Ergebnis mit Kurztext, Auswahlliste verdeckt (mit zwei Markierungen), Loesung freigegeben, Abschluss mit Ausrichtung.
Aufruf: python3 -I tests/mache_screenshots.py   (Bilder wurf und mikro-wahl liefert test_durchlauf.py)"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from playwright.sync_api import sync_playwright

import hilfen as H
import referenz_spiel as R
from test_dateien import lade_daten

HIER = os.path.dirname(os.path.abspath(__file__))
SHOTS = os.path.join(os.path.dirname(HIER), "screenshots")
D = lade_daten()
EPS = {e["id"]: e for e in D["episoden"]}
BASIS = {"zeit": 0, "energie": 0, "soz": 1, "erfuellung": 1, "lebensstil": 1, "finanzen": 1, "stimmung": 50}
GERAETE = {
    "desktop": (dict(viewport={"width": 1280, "height": 900}), False),
    "phone": (dict(viewport={"width": 390, "height": 844}, has_touch=True, is_mobile=True, device_scale_factor=2), True),
}


def bild(p, name, voll=False):
    """voll=True: Fenster auf die Seitenhoehe vergroessern (statt full_page), damit die untere Aktionsleiste unten sitzt wie im Spiel."""
    p.wait_for_timeout(500)
    if voll:
        vp = p.viewport_size
        h = p.evaluate("document.documentElement.scrollHeight")
        p.set_viewport_size({"width": vp["width"], "height": max(vp["height"], h)})
        p.wait_for_timeout(300)
        p.screenshot(path=os.path.join(SHOTS, name + ".jpg"), type="jpeg", quality=65)
        p.set_viewport_size(vp)
    else:
        p.screenshot(path=os.path.join(SHOTS, name + ".jpg"), type="jpeg", quality=65)


def main():
    os.makedirs(SHOTS, exist_ok=True)
    srv = H.Server()
    with sync_playwright() as pw:
        b = pw.chromium.launch()
        for gname, (args, touch) in GERAETE.items():
            ctx = b.new_context(**args)
            p = ctx.new_page()
            fe = H.Fehler(p)
            p.goto(srv.url + "?seed=21")
            p.wait_for_selector("[data-aktion=start]")
            d = H.Spiel(p, touch=touch, schnell=True)
            d.start()
            # zwei Episoden spielen, damit die Werte nicht mehr die Startwerte sind
            ep = "1"
            for letter in ("A", "B"):
                z = p.evaluate("window.GLUECK.zustand()")
                regel = R.anzeige_zu_regel(z["tausch"][ep], letter)
                d.waehle_anzeige(letter)
                d.wurf_physisch(max(1, min(20, EPS[ep]["optionen"][regel]["soll"] + 2)))
                d.zu_folgen(); d.zu_werten()
                ep = R.WEITER[(ep, regel)]
                d.weiter()
            bild(p, gname + "-entscheidung", voll=True)
            z = p.evaluate("window.GLUECK.zustand()")
            regel = R.anzeige_zu_regel(z["tausch"][z["ep"]], "A")
            d.waehle_anzeige("A")
            d.wurf_physisch(max(1, min(20, EPS[z["ep"]]["optionen"][regel]["soll"] + 3)))
            bild(p, gname + "-ergebnis", voll=True)
            d.zu_folgen(); d.zu_werten()
            for nr in (1, 4):
                p.evaluate("window.GLUECK.entsperren()")
                (p.locator(".glueck .kand").nth(nr).tap() if touch else p.locator(".glueck .kand").nth(nr).click())
            p.mouse.move(0, 0)
            bild(p, gname + "-werte-verdeckt", voll=True)
            d.glueck_zeigen()
            bild(p, gname + "-werte-frei", voll=True)
            # Rest des Weges bis zum Abschluss (Wahl abwechselnd), dann Abschluss
            ep = z["ep"]
            letters = ["B", "A", "B", "A", "B", "B", "A", "A", "B", "A"]
            d.weiter()
            for letter in letters:
                z = p.evaluate("window.GLUECK.zustand()")
                ep = z["ep"]
                regel = R.anzeige_zu_regel(z["tausch"][ep], letter)
                d.waehle_anzeige(letter)
                d.wurf_physisch(max(1, min(20, EPS[ep]["optionen"][regel]["soll"] + 1)))
                d.zu_folgen(); d.zu_werten()
                nxt = R.WEITER.get((ep, regel))
                if nxt is None:
                    d._aktion("[data-aktion=abschluss]")
                    break
                d.weiter()
            bild(p, gname + "-abschluss", voll=True)
            print(gname, "Konsole/Anfragen:", fe.liste[:2])
            ctx.close()
        b.close()
    srv.stop()


if __name__ == "__main__":
    main()
