"""Vollstaendige Spielablaeufe als Nutzer (Maus, Touch, nur Tastatur) gegen die unabhaengige Excel-Referenz.
Aufruf: python3 -I tests/test_durchlauf.py   (schreibt tests/ergebnis_durchlauf.md; Bilder Wurf und Mikroszene in screenshots/, die uebrigen macht mache_screenshots.py)"""
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from playwright.sync_api import sync_playwright

import hilfen as H
import referenz_spiel as R

HIER = os.path.dirname(os.path.abspath(__file__))
SHOTS = os.path.join(os.path.dirname(HIER), "screenshots")
E = H.Ergebnisse()
ZUSCHLAG = [2, -3, 4, 0, 5, -1, 3, 1, 4, 2, 5, 3]  # Wurf = Soll + Zuschlag (begrenzt auf 1..20), je Episode

# Wege: (Optionen je Episode). Ep1 A=BWL, B=Psychologie; Ep7 A=Berater, B=Jugend.
WEGE = {
    "R1 BWL/Berater/12A1": ["A", "B", "A", "A", "B", "A", "A", "A", "B", "A", "A", "A"],
    "R2 Psychologie/Jugend/12A2": ["B", "A", "B", "B", "A", "B", "B", "A", "A", "A", "B", "B"],
    "R3 Psychologie/Berater/12B1": ["B", "B", "A", "A", "A", "B", "A", "B", "B", "B", "A", "A"],
    "R4 BWL/Jugend/12B2": ["A", "A", "B", "B", "B", "A", "B", "B", "A", "B", "B", "B"],
    "R5 Tastatur Psychologie/Berater/12B2": ["B", "A", "A", "A", "A", "A", "A", "B", "A", "B", "B", "A"],
}


def letzte_ep(i, wege_opts):
    return i == len(wege_opts) - 1


def fahre(pw, name, wege_opts, geraet, kontext_args, klasse, url, mikro_plan=None, shots=None):
    mikro_plan = mikro_plan or {}
    browser = pw.chromium.launch()
    ctx = browser.new_context(**kontext_args)
    seite = ctx.new_page()
    fe = H.Fehler(seite)
    seite.goto(url)
    seite.wait_for_selector("[data-aktion=start]")
    d = klasse(seite, touch=kontext_args.get("has_touch", False), schnell=False)
    ref = R.Referenz()
    daten = seite.evaluate("window.GLUECK.daten")
    daten_texte = seite.evaluate("window.GLUECK.texte")
    titel = {e["id"]: e["titel"] for e in daten["episoden"]}
    mikro_daten = {m["id"]: m for m in daten["mikroszenen"]}
    fehler = []
    gespielt = []  # (Episode, Regeloption, angezeigter Buchstabe)
    n_vertauscht = 0

    def pruef(bedingung, text):
        if not bedingung:
            fehler.append(text)

    pruef(H.kacheln(seite) == {"stimmung": 50, "zeit": 0, "energie": 0, "soz": 1, "erfuellung": 1, "lebensstil": 1, "finanzen": 1}, "Startwerte")
    d.start()
    ep = "1"
    t0 = time.time()
    for i, opt in enumerate(wege_opts):
        z = d.z()
        pruef(z["ep"] == ep, "Episode %d: Seite %s, erwartet %s" % (i + 1, z["ep"], ep))
        pruef(seite.inner_text("#titel").strip() == titel[ep], "Titel Ep %s" % ep)
        pruef("Episode %d von 12" % (i + 1) in seite.inner_text("#app"), "Fortschritt Ep %s" % ep)
        # A/B: die Karte mit dem Buchstaben X zeigt die Regeloption, die dahinter liegt (Tausch pro Episode zufaellig)
        tausch = d.z()["tausch"][ep]
        ep_daten = [e for e in daten["episoden"] if e["id"] == ep][0]
        for anz in "AB":
            regel_k = R.anzeige_zu_regel(tausch, anz)
            pruef(seite.inner_text('section[aria-label="Option %s"] .name' % anz).strip() == ep_daten["optionen"][regel_k]["label"], "Karte Option %s zeigt Regeloption %s (Ep %s)" % (anz, regel_k, ep))
        # (Die Woerter «langfristig» und «kurzfristig» stehen in den Wort-Texten von 11A A und 11B B in anderer Bedeutung; geprueft wird die Einordnung selbst.)
        sicht = seite.inner_text("#app").lower()
        pruef("ausrichtung" not in sicht and "langfristige investition" not in sicht and "kurzfristige optimierung" not in sicht and seite.locator("[data-ausrichtung]").count() == 0, "Ausrichtung auf der Entscheidungsseite sichtbar (Ep %s)" % ep)
        vor = ref.beginn(ep)
        pruef(abs(H.kacheln(seite)["stimmung"] - float(vor["stimmung"])) < 1e-9 and abs(H.kacheln(seite)["zeit"] - float(vor["zeit"])) < 1e-9, "Werte nach Beginn Ep %s" % ep)
        soll = [e for e in daten["episoden"] if e["id"] == ep][0]["optionen"][opt]["soll"]
        wurf = max(1, min(20, soll + ZUSCHLAG[i]))
        for versuch in (0, 1, -1, 2, -2, 3, -3):  # exakte Haelftenfaelle meiden (siehe README, Rundung)
            w = wurf + versuch
            if 1 <= w <= 20 and not ref.tie(ep, opt, w):
                wurf = w
                break
        anz_gewaehlt = d.anzeige_fuer(opt)
        n_vertauscht += 1 if anz_gewaehlt != opt else 0
        gespielt.append((ep, opt, anz_gewaehlt))
        d.waehle(opt)
        z_w = d.z()
        pruef(z_w["wahl"] == opt and z_w["wahlAnz"] == anz_gewaehlt, "Zustand: Regeloption %s, angezeigt %s (Ep %s)" % (opt, anz_gewaehlt, ep))
        pruef(seite.inner_text(".gewaehlt strong").strip() == "%s · %s" % (anz_gewaehlt, ep_daten["optionen"][opt]["label"]), "Gewaehlt-Zeile (Ep %s)" % ep)
        if shots and i == 1:
            seite.screenshot(path=os.path.join(SHOTS, shots + "-wurf.jpg"), type="jpeg", quality=60)
        if name.startswith("R2") and i % 2 == 0:  # Phone: virtueller Wurf, Wert aus der Seite in die Referenz uebernehmen
            d.wurf_virtuell()
            wurf = int(seite.inner_text("#z-wurf"))
            if ref.tie(ep, opt, wurf):
                fehler.append("(Hinweis) virtueller Wurf %d ist Haelftenfall, Ep %s" % (wurf, ep))
        else:
            d.wurf_physisch(wurf)
        r = ref.episode(ep, opt, wurf)
        pruef(seite.inner_text("#z-ergebnis").replace("−", "-") == ("%g" % float(r["resultat"])) or abs(H.zahl(seite.inner_text("#z-ergebnis")) - float(r["resultat"])) < 1e-9, "Resultat Ep %s" % ep)
        pruef(int(seite.inner_text("#z-wurf")) == wurf, "Wurf angezeigt Ep %s" % ep)
        # Kurztext: Erfolg/Misserfolg passend zum Resultat (Resultat >= Soll), 1 bis 2 Saetze, keine Platzhalter
        art = "Erfolg" if float(r["resultat"]) >= soll else "Misserfolg"
        kt = seite.text_content("#kt-text").strip()
        pruef(seite.text_content("#kt-titel").strip() == art, "Kurztext-Titel %s erwartet (Ep %s)" % (art, ep))
        pruef(1 <= len([x for x in __import__("re").split(r"(?<=[.!?])\s+", kt) if x]) <= 2 and "{" not in kt and len(kt) > 40, "Kurztext (Ep %s): %r" % (ep, kt[:60]))
        pruef(int(seite.inner_text("#z-soll")) == soll, "Soll Ep %s" % ep)
        for k in ("zeit", "energie", "soz", "erfuellung", "lebensstil", "finanzen"):
            pruef(abs(H.zahl(seite.inner_text('.bwert[data-attr=%s]' % k)) - 2 * float(r["wirk_" + k])) < 0.0051, "Wirkung %s Ep %s" % (k, ep))
        d.zu_folgen()
        pruef(abs(H.zahl(seite.inner_text("#f-stimmung")) - float(r["nachher_stimmung"])) < 1e-9, "Stimmung Folgen Ep %s" % ep)
        for k in ("zeit", "energie", "soz", "erfuellung", "lebensstil", "finanzen"):
            pruef(abs(H.zahl(seite.inner_text("[data-nachher=%s]" % k)) - float(r["nachher_" + k])) < 1e-9, "Nachher %s Ep %s" % (k, ep))
        d.zu_werten()
        kz = H.kacheln(seite)
        for k, v in ref.zahlen().items():
            pruef(abs(kz[k] - v) < 1e-9, "Kachel %s nach Ep %s: Seite %s, Referenz %s" % (k, ep, kz[k], v))
        pruef(not d.z()["rech"]["spielende"], "unerwartetes Spielende nach Ep %s" % ep)
        # Glücksfaktoren: zuerst verdeckte Auswahlliste, Loesung nur nach Klick der Fachperson
        n_kand = len(ep_daten["glueck"]) + len(daten_texte["episoden"][ep]["plausibel"]) + len(daten_texte["episoden"][ep]["unplausibel"])
        pruef(seite.locator(".kand").count() == n_kand and seite.locator(".kand-zeile").count() == 0, "Auswahlliste verdeckt, %d Eintraege (Ep %s)" % (n_kand, ep))
        pruef("Unplausibel" not in seite.inner_text("#app") and "Hier nicht entscheidend" not in seite.inner_text("#app") and "Wichtige Erkenntnis" not in seite.inner_text("#app"), "Loesung vor dem Klick sichtbar (Ep %s)" % ep)
        if i % 2 == 0 or letzte_ep(i, wege_opts):
            d.glueck_zeigen()
            pruef(seite.locator(".kand-zeile.echt").count() == len(ep_daten["glueck"]) and seite.locator(".kand-zeile").count() == n_kand and seite.locator(".kand").count() == 0, "Loesung nach Klick (Ep %s)" % ep)
            pruef(d.phase() == "werte" and seite.locator("[data-aktion=glueckZeigen]").count() == 0, "Freigabe nur einmal, Phase bleibt (Ep %s)" % ep)
        letzte = i == len(wege_opts) - 1
        nxt = R.WEITER.get((ep, opt))
        pruef((nxt is None) == letzte, "Ende der Verzweigung Ep %s" % ep)
        # Mikroszene (nur ueber Knopf der Fachperson)
        if i in mikro_plan and not letzte:
            via, mid, mopt = mikro_plan[i]
            if via == "liste":
                d._aktion("[data-aktion=mikroOeffnen][data-wert=normal]")
                pruef(d.phase() == "mikro-wahl", "Mikro-Auswahl oeffnet")
                if shots:
                    seite.wait_for_timeout(500)
                    seite.screenshot(path=os.path.join(SHOTS, shots + "-mikro-wahl.jpg"), type="jpeg", quality=60)
            d._aktion("[data-aktion=mikroStart][data-wert=%s]" % mid)
            pruef(d.phase() == "mikro-entscheidung", "Mikroszene startet")
            d._aktion("[data-aktion=mikroWahl][data-wert=%s]" % mopt)
            ref.mikro(mikro_daten[mid]["optionen"][mopt]["deltas"])
            kz = H.kacheln(seite)
            for k, v in ref.zahlen().items():
                pruef(abs(kz[k] - v) < 1e-9, "Kachel %s nach Mikroszene %s" % (k, mid))
            d._aktion("[data-aktion=mikroWeiter]")
        elif not letzte:
            d.weiter()
        if not letzte:
            ep = nxt
    # Abschluss
    d._aktion("[data-aktion=abschluss]")
    z = d.z()
    pruef(z["phase"] == "abschluss" and z["ende"] == "regulaer", "Abschluss erreicht")
    pruef(len([p for p in z["protokoll"] if p["typ"] == "ep"]) == 12, "Protokoll 12 Episoden")
    pruef(seite.locator("#diagramm svg polyline").count() == 1, "Diagramm vorhanden")
    pruef(seite.locator("#diagramm svg circle").count() >= 13, "Diagramm-Punkte")
    pruef(seite.locator("ol.verlauf li").count() == 12 + len(mikro_plan), "Liste gewaehlte Optionen")
    erw = [R.AUSRICHTUNG[e][o] for e, o, _ in gespielt]
    ist = seite.evaluate("[...document.querySelectorAll('[data-ausrichtung]')].map(e => e.dataset.ausrichtung)")
    pruef(ist == erw, "Abschluss: Ausrichtung je Episode %s, erwartet %s" % (ist, erw))
    zeilen = seite.evaluate("[...document.querySelectorAll('ol.verlauf li:not(.mikro) .l2')].map(e => e.textContent)")
    pruef(all(z_.startswith("Option %s" % g[2]) for z_, g in zip(zeilen, gespielt)), "Abschluss: angezeigter Buchstabe je Episode")
    pruef(("*" in seite.inner_text("#app")) == any(e in R.UNSCHARF for e, _, _ in gespielt), "Abschluss: Stern bei unscharfer Zuordnung")
    kz = H.kacheln(seite)
    for k, v in ref.zahlen().items():
        pruef(abs(kz[k] - v) < 1e-9, "Endwert %s" % k)
    pruef(seite.evaluate("document.documentElement.scrollWidth <= window.innerWidth + 1"), "kein horizontaler Scroll im Abschluss")
    pruef(not fe.liste, "Konsole/Anfragen: %s" % fe.liste[:3])
    hinweise = [f for f in fehler if f.startswith("(Hinweis)")]
    echte = [f for f in fehler if not f.startswith("(Hinweis)") and f]
    E.pruefe("Vollstaendiger Durchlauf " + name, geraet, not echte,
             "%d Episoden, %d mit vertauschten Buchstaben, %.0f s, Endstimmung %.1f%s" % (len(wege_opts), n_vertauscht, time.time() - t0, ref.zahlen()["stimmung"], ("; FEHLER: " + "; ".join(echte[:4])) if echte else ""))
    browser.close()


def main():
    srv = H.Server()
    desktop = dict(viewport={"width": 1280, "height": 800})
    phone = dict(viewport={"width": 390, "height": 844}, has_touch=True, is_mobile=True, device_scale_factor=2)
    ns = list(WEGE.items())
    with sync_playwright() as pw:
        fahre(pw, ns[0][0], ns[0][1], "Desktop Maus (http)", desktop, H.Spiel, srv.url + "?neu=1",
              mikro_plan={5: ("liste", "M2", "A"), 8: ("liste", "M7", "B")}, shots="desktop")
        fahre(pw, ns[1][0], ns[1][1], "Phone 390x844 Touch", phone, H.Spiel, srv.url + "?neu=1", mikro_plan={3: ("liste", "M4", "B")}, shots="phone")
        fahre(pw, ns[2][0], ns[2][1], "Desktop Maus (file)", desktop, H.Spiel, srv.file_url + "?neu=1")
        fahre(pw, ns[3][0], ns[3][1], "Phone 390x844 Touch (file)", phone, H.Spiel, srv.file_url + "?neu=1")
        fahre(pw, ns[4][0], ns[4][1], "Desktop nur Tastatur", desktop, H.Tastatur, srv.url + "?neu=1")
    srv.stop()
    E.speichern(os.path.join(HIER, "ergebnis_durchlauf.md"))
    print("Fehler:", len(E.fehler))
    return 1 if E.fehler else 0


if __name__ == "__main__":
    sys.exit(main())
