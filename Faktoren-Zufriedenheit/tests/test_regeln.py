"""Regel- und Randfaelle (Wuerfel, Schwellen, Schranken, Undo, Mikroszenen, Spielende, Speicher) gegen die Excel-Referenz.
Aufruf: python3 -I tests/test_regeln.py   (schreibt tests/ergebnis_regeln.md)"""
import os
import sys
from decimal import Decimal

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from playwright.sync_api import sync_playwright

import hilfen as H
import referenz_spiel as R

HIER = os.path.dirname(os.path.abspath(__file__))
E = H.Ergebnisse()
KEYS = ["zeit", "energie", "soz", "erfuellung", "lebensstil", "finanzen"]
BASIS = {"zeit": 0, "energie": 0, "soz": 1, "erfuellung": 1, "lebensstil": 1, "finanzen": 1, "stimmung": 50}
MIKRO_REGEL = {"zeit": ["M1", "M3", "M5", "M10"], "energie": ["M1", "M3", "M5", "M10"], "soz": ["M2", "M5"],
               "erfuellung": ["M4", "M6", "M8"], "lebensstil": ["M7", "M9"]}  # Quelle: Word «Mikroszenen strategisch einsetzen»


def neue_seite(b, url, ctx_args=None, **kw):
    ctx = b.new_context(**(ctx_args or dict(viewport={"width": 1280, "height": 800})), **kw)
    p = ctx.new_page()
    f = H.Fehler(p)
    p.goto(url)
    p.wait_for_selector("#app h2")
    return p, f


def referenz(ep, opt, werte, wurf):
    r = R.Referenz()
    r.w = {k: Decimal(str(v)) for k, v in dict(BASIS, **werte).items()}
    return r.episode(ep, opt, wurf)


def spiele_episode(p, ep, opt, werte, wurf):
    """Springt in die Episode mit den Werten, waehlt, wuerfelt physisch, liest die Zahlen aus den Ansichten."""
    d = H.Spiel(p, schnell=True)
    p.evaluate("(a) => window.GLUECK.springe(a[0], a[1])", [ep, dict(BASIS, **werte)])
    d.waehle(opt)
    d.wurf_physisch(wurf)
    out = {"resultat": H.zahl(p.inner_text("#z-ergebnis")), "text_ergebnis": p.inner_text("#app")}
    d.zu_folgen()
    out["stimmung"] = H.zahl(p.inner_text("#f-stimmung"))
    out["nachher"] = {k: H.zahl(p.inner_text("[data-nachher=%s]" % k)) for k in KEYS}
    out["aenderung"] = {k: H.zahl(p.inner_text("[data-aenderung=%s]" % k)) for k in KEYS}
    out["text_folgen"] = p.inner_text("#app")
    d.zu_werten()
    out["kacheln"] = H.kacheln(p)
    out["z"] = d.z()
    return out


def vergleiche(name, geraet, p, ep, opt, werte, wurf):
    o = spiele_episode(p, ep, opt, werte, wurf)
    r = referenz(ep, opt, werte, wurf)
    ok = abs(o["resultat"] - float(r["resultat"])) < 1e-9 and abs(o["stimmung"] - float(r["nachher_stimmung"])) < 1e-9
    ok = ok and all(abs(o["nachher"][k] - float(r["nachher_" + k])) < 1e-9 for k in KEYS)
    E.pruefe(name, geraet, ok, "Ep %s/%s Wurf %d: Resultat %s, Stimmung %s" % (ep, opt, wurf, o["resultat"], o["stimmung"]))
    return o, r


# ----------------------------------------------------------------------------------------------
def t_wuerfel(b, srv):
    p, f = neue_seite(b, srv.url + "?neu=1")
    n = 20000
    z = p.evaluate("""(n) => { const w = GLUECK_KERN.neuerWuerfel(20); const c = new Array(21).fill(0); for (let i=0;i<n;i++) c[w()]++; return c; }""", n)
    erw = n / 20
    chi = sum((z[i] - erw) ** 2 / erw for i in range(1, 21))
    E.pruefe("Virtueller W20 ohne Seed: nur 1..20, 1 und 20 kommen vor", "Desktop", z[0] == 0 and z[1] > 0 and z[20] > 0 and sum(z) == n, "Haeufigkeit 1: %d, 20: %d" % (z[1], z[20]))
    E.pruefe("Virtueller W20: Gleichverteilung (Chi-Quadrat, 19 FG, Grenze 43.8 bei p=0.001)", "Desktop", chi < 43.8, "chi2 = %.1f aus %d Wuerfen" % (chi, n))
    zs = p.evaluate("""(n) => { const w = GLUECK_KERN.neuerWuerfel(20, 'abc'); const c = new Array(21).fill(0); for (let i=0;i<n;i++) c[w()]++; return c; }""", n)
    chi = sum((zs[i] - erw) ** 2 / erw for i in range(1, 21))
    E.pruefe("W20 mit ?seed=: Gleichverteilung", "Desktop", chi < 43.8 and zs[0] == 0, "chi2 = %.1f" % chi)
    p.close()

    def folge(seed, k=8):
        pp, ff = neue_seite(b, srv.url + "?seed=%s" % seed)
        d = H.Spiel(pp, schnell=True)
        d.start(); out = []
        for i in range(k):
            d.waehle("A"); d.wurf_virtuell(); out.append(int(pp.inner_text("#z-wurf")))
            pp.evaluate("window.GLUECK.entsperren()")
            d.zu_folgen(); d.zu_werten()
            if i < k - 1:
                d.weiter()
        pp.close()
        return out
    a1, a2, c1 = folge("klasse-1"), folge("klasse-1"), folge("klasse-2")
    E.pruefe("?seed= reproduzierbar (zwei Sitzungen, gleiche Wuerfe)", "Desktop", a1 == a2, str(a1))
    E.pruefe("?seed= anderer Wert gibt andere Folge", "Desktop", a1 != c1, "%s gegen %s" % (a1, c1))
    # Taste W
    p, f = neue_seite(b, srv.url + "?neu=1")
    d = H.Spiel(p, schnell=True)
    d.start(); d.waehle("A"); p.evaluate("window.GLUECK.entsperren()"); p.keyboard.press("w")
    E.pruefe("Taste W wuerfelt (virtuell)", "Desktop", d.phase() == "ergebnis" and d.z()["wurfArt"] == "virtuell", d.phase())
    p.close()


def t_eingabe(b, srv):
    p, f = neue_seite(b, srv.url + "?neu=1")
    d = H.Spiel(p, schnell=True)
    d.start(); d.waehle("A")
    schlecht = ["", "0", "21", "3.5", "abc", "1e1", "-3", "100", "  ", "7a", "٣"]
    for s in schlecht:
        p.evaluate("window.GLUECK.entsperren()")
        p.evaluate("(v) => { document.getElementById('wurf-eingabe').value = v; }", s)
        p.press("#wurf-eingabe", "Enter")
        ok = d.phase() == "wurf" and "1 bis 20" in p.inner_text("#wurf-fehler")
        E.pruefe("Eingabe %r wird abgelehnt (Hinweis sichtbar, kein Wurf)" % s, "Desktop", ok, d.phase())
    for s, erw in [("1", 1), ("20", 20), ("07", 7), (" 7 ", 7), ("13", 13)]:
        d2 = H.Spiel(p, schnell=True)
        p.evaluate("window.GLUECK.entsperren()")
        p.evaluate("(v) => { document.getElementById('wurf-eingabe').value = v; }", s)
        p.press("#wurf-eingabe", "Enter")
        z = d.z()
        E.pruefe("Eingabe %r wird als %d uebernommen (eigener Wuerfel)" % (s, erw), "Desktop", z["phase"] == "ergebnis" and z["wurf"] == erw and z["wurfArt"] == "physisch", str(z["wurf"]))
        d.undo()
    E.pruefe("Konsole/Anfragen ohne Fehler (Eingabetest)", "Desktop", not f.liste, str(f.liste[:2]))
    p.close()


def t_rechenrand(b, srv):
    p, f = neue_seite(b, srv.url + "?neu=1")
    G = "Desktop"
    # Wurf 1 und 20 in mehreren Zeilen
    for ep, opt in [("1", "A"), ("5B", "B"), ("12A1", "A"), ("12B2", "B")]:
        for w in (1, 20):
            vergleiche("Wurf %d, Ep %s Option %s, Normalwerte" % (w, ep, opt), G, p, ep, opt, {}, w)
    # Resultat < 0 -> 0
    o, r = vergleiche("Alle Attribute -10, Wurf 1: Resultat negativ wird 0", G, p, "3", "A", {k: -10 for k in KEYS}, 1)
    E.pruefe("  Resultat ist 0 und Hinweis «auf 0 gesetzt» sichtbar", G, o["resultat"] == 0 and "auf 0 gesetzt" in o["text_ergebnis"], "")
    o, r = vergleiche("Alle Attribute +10, Wurf 20", G, p, "3", "B", {k: 10 for k in KEYS}, 20)
    E.pruefe("  Saettigung: Resultat 20 + 2*(0.5+0.6+2+5.5+4.5+0.5) = 47.2", G, abs(o["resultat"] - 47.2) < 1e-9, str(o["resultat"]))
    vergleiche("Attribute -10 / +10 gemischt, Wurf 7", G, p, "9", "A", dict(zeit=-10, energie=10, soz=-10, erfuellung=10, lebensstil=-10, finanzen=10), 7)
    # Stimmung genau 0 / -1 nach der Episode
    ep, opt, w = "3", "A", 3
    an = R.Referenz()
    an.w = {k: Decimal(str(v)) for k, v in BASIS.items()}
    r0 = an.episode(ep, opt, w)
    dn = r0["nachher_stimmung"] - 50
    for ziel, spiel_ende in [(0, False), (-1, True), (1, False)]:
        o = spiele_episode(p, ep, opt, {"stimmung": float(Decimal(ziel) - dn)}, w)
        phase_ok = o["z"]["rech"]["spielende"] == spiel_ende and o["stimmung"] == ziel
        sicht = p.locator("[data-aktion=weiter]").count() == (0 if spiel_ende else 1)
        zeigt = p.locator("[data-aktion=abschluss]").count() == 1 and (p.locator("[data-aktion=mikroOeffnen][data-wert=rettung]").count() == (1 if spiel_ende else 0))
        E.pruefe("Stimmung nach Episode genau %d: %s" % (ziel, "Spielende-Angebot" if spiel_ende else "Spiel laeuft weiter"), G, phase_ok and sicht and (zeigt if spiel_ende else True),
                 "spielende=%s, Weiter-Knopf=%d" % (o["z"]["rech"]["spielende"], p.locator("[data-aktion=weiter]").count()))
        if spiel_ende:
            E.pruefe("  Spielende: beide Wege angeboten (Abschluss / Rettungs-Mikroszene)", G,
                     p.locator("[data-aktion=abschluss]").count() == 1 and p.locator("[data-aktion=mikroOeffnen][data-wert=rettung]").count() == 1, "")
    # Finanzen < -2
    o2, _ = vergleiche("Finanzen -2 (kein Zeitabzug)", G, p, "9", "B", {"finanzen": -2}, 12)
    o3, _ = vergleiche("Finanzen -3 (Zeit -1 zusaetzlich)", G, p, "9", "B", {"finanzen": -3}, 12)
    E.pruefe("  Zeitabzug nur bei Finanzen -3 sichtbar und genau 1", G,
             "wegen Finanzen" in o3["text_folgen"] and "wegen Finanzen" not in o2["text_folgen"] and abs(o2["aenderung"]["zeit"] - o3["aenderung"]["zeit"] - 1) < 1e-9, "")
    # Zufallsserie ueber alle 38 Zeilen
    import random
    rng = random.Random(7)
    ok = True; n = 0
    for (ep, opt) in sorted(R.Referenz().zeilen):
        for _ in range(2):
            werte = {k: rng.randint(-20, 20) / 2 for k in KEYS}; werte["stimmung"] = rng.randint(1, 99)
            w = rng.randint(1, 20)
            o = spiele_episode(p, ep, opt, werte, w)
            r = referenz(ep, opt, werte, w)
            n += 1
            dev = abs(o["resultat"] - float(r["resultat"])) > 1e-9 or abs(o["stimmung"] - float(r["nachher_stimmung"])) > 1e-9 or any(abs(o["nachher"][k] - float(r["nachher_" + k])) > 1e-9 for k in KEYS)
            if dev:
                ok = False
                print("  Abweichung", ep, opt, werte, w, o["resultat"], r["resultat"])
    E.pruefe("Zufallsserie ueber die Bedienoberflaeche, %d Zustaende, alle 38 Zeilen (Dezimal-Referenz)" % n, G, ok, "Abweichung bei exakten Haelften moeglich, siehe ergebnis_excel.txt")
    E.pruefe("Konsole/Anfragen ohne Fehler (Rechenrand)", G, not f.liste, str(f.liste[:2]))
    p.close()


def t_schranken(b, srv):
    G = "Desktop"
    D = None
    for url, schr in [(srv.url + "?neu=1", False), (srv.url + "?neu=1&schranken=1", True)]:
        p, f = neue_seite(b, url)
        D = p.evaluate("window.GLUECK.daten")
        ep = [e for e in D["episoden"] if e["optionen"]["A"]["aenderung"]["soz"] > 0 or e["optionen"]["B"]["aenderung"]["soz"] > 0][0]
        opt = "A" if ep["optionen"]["A"]["aenderung"]["soz"] > 0 else "B"
        plus = ep["optionen"][opt]["aenderung"]["soz"]
        o = spiele_episode(p, ep["id"], opt, {"soz": 10}, 10)
        erw = 10 if schr else 10 + plus
        E.pruefe("Schranken %s: Soziale Verbindungen 10 + %s -> %s" % ("an" if schr else "aus (Standard)", plus, erw), G, abs(o["kacheln"]["soz"] - erw) < 1e-9 and (p.locator(".begrenzt").count() == (1 if schr else 0)),
                 "angezeigt %s, Marker begrenzt=%d" % (o["kacheln"]["soz"], p.locator(".begrenzt").count()))
        ep2 = [e for e in D["episoden"] if e["optionen"]["A"]["aenderung"]["erfuellung"] < 0][0]
        o = spiele_episode(p, ep2["id"], "A", {"erfuellung": -10}, 10)
        erw = -10 if schr else -10 + ep2["optionen"]["A"]["aenderung"]["erfuellung"]
        E.pruefe("Schranken %s: Erfuellung -10 + %s -> %s" % ("an" if schr else "aus", ep2["optionen"]["A"]["aenderung"]["erfuellung"], erw), G, abs(o["kacheln"]["erfuellung"] - erw) < 1e-9, str(o["kacheln"]["erfuellung"]))
        o = spiele_episode(p, "3", "B", {"stimmung": 100}, 20)
        E.pruefe("Schranken %s: Stimmung 100 und starkes Ergebnis -> %s" % ("an (max. 100)" if schr else "aus", "100" if schr else ">100"), G,
                 (o["kacheln"]["stimmung"] == 100) if schr else (o["kacheln"]["stimmung"] > 100), str(o["kacheln"]["stimmung"]))
        E.pruefe("Konsole/Anfragen ohne Fehler (Schranken)", G, not f.liste, str(f.liste[:2]))
        p.close()


def t_undo(b, srv):
    G = "Desktop"
    p, f = neue_seite(b, srv.url + "?neu=1")
    d = H.Spiel(p, schnell=True)
    E.pruefe("Rueckgaengig am Anfang gesperrt", G, p.locator("#btn-undo").is_disabled(), "")
    zust = [d.z()]
    d.start(); zust.append(d.z())
    d.waehle("B"); zust.append(d.z())
    d.wurf_physisch(11); zust.append(d.z())
    d.zu_folgen(); zust.append(d.z())
    d.zu_werten(); zust.append(d.z())
    d.weiter(); zust.append(d.z())
    d.waehle("A"); zust.append(d.z())
    E.pruefe("Undo-Tiefe nach 7 Schritten = 7", G, p.evaluate("window.GLUECK.undoTiefe()") == 7, str(p.evaluate("window.GLUECK.undoTiefe()")))
    ok = True
    for i in range(len(zust) - 2, -1, -1):
        d.undo()
        if d.z() != zust[i]:
            ok = False
            print("  Undo-Abweichung bei Schritt", i)
    E.pruefe("7x Rueckgaengig: jeder Zwischenzustand identisch zum gespeicherten", G, ok, "")
    E.pruefe("Danach wieder gesperrt, Startansicht", G, p.locator("#btn-undo").is_disabled() and d.phase() == "start", d.phase())
    # Wiederholen nach Undo: anderes Ergebnis moeglich (anderer Wurf)
    d.start(); d.waehle("A"); d.wurf_physisch(5); d.undo(); d.wurf_physisch(18)
    E.pruefe("Nach Undo neu wuerfeln: neuer Wurf zaehlt", G, d.z()["wurf"] == 18, "")
    # Strg+Z
    p.evaluate("window.GLUECK.entsperren()"); p.keyboard.press("Control+z")
    E.pruefe("Strg+Z entspricht Rueckgaengig", G, d.phase() == "wurf", d.phase())
    # Undo ueber Mikroszene und Spielende
    d.wurf_physisch(20); d.zu_folgen(); d.zu_werten()
    vor = d.z()
    d._aktion("[data-aktion=mikroOeffnen][data-wert=normal]"); d._aktion("[data-aktion=mikroStart][data-wert=M2]"); d._aktion("[data-aktion=mikroWahl][data-wert=B]")
    d.undo(); d.undo(); d.undo()
    z = d.z()
    E.pruefe("3x Rueckgaengig nach Mikroszene: wieder bei «Werte danach» mit Rechnung", G, z["phase"] == "werte" and z["mikroGespielt"] == [] and z["rech"]["resultat"] == vor["rech"]["resultat"], z["phase"])
    p.close()
    # Spielende -> Abschluss -> Undo
    p, f = neue_seite(b, srv.url + "?neu=1")
    d = H.Spiel(p, schnell=True)
    p.evaluate("(a) => window.GLUECK.springe(a[0], a[1])", ["3", dict(BASIS, stimmung=0, erfuellung=-10, zeit=-10, energie=-10)])
    d.waehle("A"); d.wurf_physisch(1); d.zu_folgen(); d.zu_werten()
    E.pruefe("Stimmung unter 0 nach Wurf 1: Spielende-Ansicht", G, d.z()["rech"]["spielende"] and p.locator("[data-aktion=weiter]").count() == 0, "")
    d._aktion("[data-aktion=abschluss]")
    z = d.z()
    E.pruefe("  Abschluss mit Hinweis «Stimmung unter 0», Diagramm da", G, z["phase"] == "abschluss" and z["ende"] == "stimmung" and "unter 0" in p.inner_text("#app") and p.locator("#diagramm svg").count() == 1, "")
    d.undo()
    E.pruefe("  Rueckgaengig aus dem Abschluss zurueck zu «Werte danach»", G, d.phase() == "werte", d.phase())
    p.close()


def t_mikro(b, srv):
    G = "Desktop"
    p, f = neue_seite(b, srv.url + "?neu=1")
    d = H.Spiel(p, schnell=True)
    D = p.evaluate("window.GLUECK.daten")
    mdat = {m["id"]: m for m in D["mikroszenen"]}
    E.pruefe("10 Mikroszenen mit je zwei Optionen in den Daten", G, len(mdat) == 10 and all(set(m["optionen"]) == {"A", "B"} for m in mdat.values()), "")
    faelle = [({"zeit": -8}, "Zeit -8"), ({"zeit": -5.5}, "Zeit -5.5 (nach Episode)"), ({"energie": -9}, "Energie -9"), ({"soz": -3}, "Soz -3"),
              ({"erfuellung": -3}, "Erfuellung -3"), ({"lebensstil": -4}, "Lebensstil -4"), ({}, "Normalwerte"), ({"zeit": 6, "energie": 6}, "Zeit/Energie hoch")]
    for werte, name in faelle:
        o = spiele_episode(p, "3", "B", werte, 12)
        nach = o["kacheln"]
        erw = set()
        for k, ids in MIKRO_REGEL.items():
            if nach[k] < (-5 if k in ("zeit", "energie") else 0):
                erw |= set(ids)
        chips = set(p.evaluate("[...document.querySelectorAll('.vorschlag-box [data-aktion=mikroStart]')].map(b => b.dataset.wert)"))
        E.pruefe("Mikroszenen-Vorschlag bei %s" % name, G, chips == erw and d.phase() == "werte", "erwartet %s, angezeigt %s, Phase %s (nie automatisch)" % (sorted(erw), sorted(chips), d.phase()))
    # Schwellen exakt: Zeit/Energie genau -5 (kein Vorschlag) und -5.5 (Vorschlag); andere Attribute genau 0 / -0.5
    ep3 = [e for e in D["episoden"] if e["id"] == "3"][0]["optionen"]["B"]["aenderung"]
    for attr_, schwelle, ids in [("zeit", -5, MIKRO_REGEL["zeit"]), ("soz", 0, MIKRO_REGEL["soz"]), ("erfuellung", 0, MIKRO_REGEL["erfuellung"]), ("lebensstil", 0, MIKRO_REGEL["lebensstil"])]:
        for nach_ziel, erw in [(schwelle, set()), (schwelle - 0.5, set(ids))]:
            o = spiele_episode(p, "3", "B", {attr_: nach_ziel - ep3[attr_]}, 12)
            nach = o["kacheln"][attr_]
            chips = set(p.evaluate("[...document.querySelectorAll('.vorschlag-box [data-aktion=mikroStart]')].map(b => b.dataset.wert)"))
            ok = (chips & set(ids)) == erw  # Szenen dieses Attributs sind genau dann vorgeschlagen, wenn der Wert unter der Schwelle liegt
            E.pruefe("Schwelle %s: Wert nach Episode %s -> %s Vorschlag" % (attr_, nach, "mit" if erw else "kein"), G, ok and abs(nach - nach_ziel) < 1e-9, "Chips %s" % sorted(chips))
    # Einfuegen und regulaer weiter
    o = spiele_episode(p, "3", "B", {"zeit": -8}, 12)
    kz = o["kacheln"]
    d._aktion("[data-aktion=mikroStart][data-wert=M1]")
    E.pruefe("Vorschlagsknopf startet Mikroszene M1 (Entscheidung A/B, kein Wuerfel)", G, d.phase() == "mikro-entscheidung" and p.locator("#wurf-eingabe").count() == 0, "")
    d._aktion("[data-aktion=mikroWahl][data-wert=A]")
    dl = mdat["M1"]["optionen"]["A"]["deltas"]
    kz2 = H.kacheln(p)
    ok = all(abs(kz2[k] - (kz[k] + dl.get(k, 0))) < 1e-9 for k in kz) and kz2["stimmung"] == kz["stimmung"]
    E.pruefe("Mikroszene M1 A: Deltas %s exakt angewendet, Stimmung unveraendert" % {k: v for k, v in dl.items() if v}, G, ok, str(kz2))
    E.pruefe("  Glücksfaktoren erst nach der Entscheidung sichtbar", G, "Glücksfaktoren" in p.inner_text("#app") or not mdat["M1"]["glueck"], "")
    d._aktion("[data-aktion=mikroWeiter]")
    z = d.z()
    erst = z["ep"] == "4" and z["phase"] == "entscheidung"
    kz3 = H.kacheln(p)
    E.pruefe("Danach regulaer Episode 4 mit Beginn-Aenderungen (+3 Zeit, +3 Energie)", G, erst and abs(kz3["zeit"] - (kz2["zeit"] + 3)) < 1e-9 and abs(kz3["energie"] - (kz2["energie"] + 3)) < 1e-9, "Ep %s, Zeit %s -> %s" % (z["ep"], kz2["zeit"], kz3["zeit"]))
    # Liste: alle 10, gespielte gesperrt
    d.waehle("A"); d.wurf_physisch(12); d.zu_folgen(); d.zu_werten()
    d._aktion("[data-aktion=mikroOeffnen][data-wert=normal]")
    n_btn = p.locator(".mikro-karte").count()
    gesperrt = p.locator(".mikro-karte[disabled]").count()
    E.pruefe("Liste zeigt alle 10 Mikroszenen, bereits gespielte (M1) gesperrt", G, n_btn == 10 and gesperrt == 1, "%d Knoepfe, %d gesperrt" % (n_btn, gesperrt))
    # Szenen alle spielen: Optionen A und B der Daten pruefen (Deltas)
    alle_ok = True
    for mid in sorted(mdat, key=lambda s: int(s[1:])):
        for opt in "AB":
            p.evaluate("(a) => window.GLUECK.springe(a[0], a[1])", ["3", dict(BASIS, zeit=-8)])
            p.evaluate("window.GLUECK.setze({mikroGespielt: []})")
            d.waehle("B"); d.wurf_physisch(12); d.zu_folgen(); d.zu_werten()
            vor = H.kacheln(p)
            d._aktion("[data-aktion=mikroOeffnen][data-wert=normal]")
            d._aktion("[data-aktion=mikroStart][data-wert=%s]" % mid)
            d._aktion("[data-aktion=mikroWahl][data-wert=%s]" % opt)
            nach = H.kacheln(p)
            dl = mdat[mid]["optionen"][opt]["deltas"]
            ok = all(abs(nach[k] - (vor[k] + dl.get(k, 0))) < 1e-9 for k in vor)
            if not ok:
                alle_ok = False
                E.pruefe("Mikroszene %s %s Deltas" % (mid, opt), G, False, "vor %s nach %s Deltas %s" % (vor, nach, dl))
    E.pruefe("Alle 10 Mikroszenen x Option A/B: Wertaenderung = Deltas aus den Daten", G, alle_ok, "20 Kombinationen")
    E.pruefe("Konsole/Anfragen ohne Fehler (Mikroszenen)", G, not f.liste, str(f.liste[:2]))
    p.close()


def t_spielende(b, srv):
    G = "Desktop"
    p, f = neue_seite(b, srv.url + "?neu=1")
    d = H.Spiel(p, schnell=True)
    # Spielende nach Episode, Rettungs-Mikroszene, danach regulaer weiter
    p.evaluate("(a) => window.GLUECK.springe(a[0], a[1])", ["3", dict(BASIS, stimmung=-2)])
    d.waehle("A"); d.wurf_physisch(1); d.zu_folgen(); d.zu_werten()
    st = H.kacheln(p)["stimmung"]
    E.pruefe("Spielende nach Episode (Stimmung %s)" % st, G, st < 0 and p.locator("[data-aktion=mikroOeffnen][data-wert=rettung]").count() == 1, "")
    d._aktion("[data-aktion=mikroOeffnen][data-wert=rettung]")
    karten = p.evaluate("[...document.querySelectorAll('.mikro-karte')].map(b => b.dataset.wert + (b.classList.contains('vorschlag') ? '*' : ''))")
    E.pruefe("Rettungsauswahl: M1, M3, M5, M10 zuerst hervorgehoben", G, karten[:4] == ["M1*", "M3*", "M5*", "M10*"] and len(karten) == 10, str(karten))
    d._aktion("[data-aktion=mikroStart][data-wert=M10]"); d._aktion("[data-aktion=mikroWahl][data-wert=A]"); d._aktion("[data-aktion=mikroWeiter]")
    z = d.z()
    E.pruefe("Nach Rettungs-Mikroszene geht es mit Episode 4 weiter (Beginn +3/+3, Stimmung bleibt unter 0, Entscheidung moeglich)", G, z["ep"] == "4" and z["phase"] == "entscheidung" and z["werte"]["stimmung"] < 0 and p.locator(".hinweis-beginn").count() == 1, "%s / %s, Stimmung %s" % (z["ep"], z["phase"], z["werte"]["stimmung"]))
    # letzte Episode: kein Rettungsangebot
    p.evaluate("(a) => window.GLUECK.springe(a[0], a[1])", ["12A1", dict(BASIS, stimmung=1)])
    d.waehle("B"); d.wurf_physisch(1); d.zu_folgen(); d.zu_werten()
    E.pruefe("Letzte Episode mit Stimmung unter 0: nur Abschlussansicht (keine Rettung moeglich, keine naechste Episode)", G,
             H.kacheln(p)["stimmung"] < 0 and p.locator("[data-aktion=mikroOeffnen]").count() == 0 and p.locator("[data-aktion=abschluss]").count() == 1, "")
    # Spielende zu Beginn der Episode 12 (Beginn -10)
    ref = R.Referenz(); ref.w = {k: Decimal(str(v)) for k, v in BASIS.items()}
    r = ref.episode("11A", "A", 12)
    an = float(r["nachher_stimmung"]) - 50
    for ziel, erw in [(10, "entscheidung"), (9, "spielende")]:  # nach Ep 11 Stimmung ziel; Beginn Ep12: ziel-10
        p.evaluate("(a) => window.GLUECK.springe(a[0], a[1])", ["11A", dict(BASIS, stimmung=ziel - an)])
        d.waehle("A"); d.wurf_physisch(12); d.zu_folgen(); d.zu_werten()
        d.weiter()
        z = d.z()
        E.pruefe("Stimmung nach Ep 11 = %d, Beginn Ep 12 (-10) ergibt %d -> %s" % (ziel, ziel - 10, erw), G, z["ep"] == "12A1" and z["phase"] == erw and abs(z["werte"]["stimmung"] - (ziel - 10)) < 1e-9, "Phase %s, Stimmung %s" % (z["phase"], z["werte"]["stimmung"]))
    both = p.locator("[data-aktion=abschluss]").count() == 1 and p.locator("[data-aktion=mikroOeffnen][data-wert=rettung]").count() == 1
    E.pruefe("  Spielende zu Beginn: beide Wege angeboten", G, both, "")
    d._aktion("[data-aktion=mikroOeffnen][data-wert=rettung]"); d._aktion("[data-aktion=mikroStart][data-wert=M5]"); d._aktion("[data-aktion=mikroWahl][data-wert=B]"); d._aktion("[data-aktion=mikroWeiter]")
    E.pruefe("  Nach Rettung zurueck zur Entscheidung derselben Episode 12A1", G, d.z()["ep"] == "12A1" and d.phase() == "entscheidung", d.phase())
    p.close()


def t_speicher(b, srv):
    G = "Desktop"
    p, f = neue_seite(b, srv.url + "?neu=1")
    d = H.Spiel(p, schnell=True)
    d.start(); d.waehle("B"); d.wurf_physisch(9); d.zu_folgen(); d.zu_werten(); d.weiter()
    z0 = d.z(); u0 = p.evaluate("window.GLUECK.undoTiefe()")
    p.goto(srv.url); p.wait_for_selector("#app h2")
    E.pruefe("Neu laden: Spielstand (sessionStorage) wiederhergestellt inkl. Rueckgaengig-Tiefe", G, d.z() == z0 and p.evaluate("window.GLUECK.undoTiefe()") == u0, d.phase())
    p.goto(srv.url + "?neu=1"); p.wait_for_selector("#app h2")
    E.pruefe("?neu=1 beginnt ohne gespeicherten Stand", G, d.phase() == "start", d.phase())
    p.close()
    # Speicher blockiert
    ctx = b.new_context(viewport={"width": 390, "height": 800})
    ctx.add_init_script("""Object.defineProperty(window, 'sessionStorage', {get(){ throw new Error('blockiert'); }}); Object.defineProperty(window, 'localStorage', {get(){ throw new Error('blockiert'); }});""")
    p = ctx.new_page(); f = H.Fehler(p); p.goto(srv.url); p.wait_for_selector("#app h2")
    d = H.Spiel(p, schnell=True)
    d.start(); d.waehle("A"); d.wurf_physisch(14); d.zu_folgen(); d.zu_werten(); d.weiter()
    E.pruefe("Speicher blockiert: Spiel laeuft trotzdem, keine Fehler in der Konsole", "Phone", d.z()["ep"] == "2A" and not f.liste, str(f.liste[:2]))
    ctx.close()
    # Neues Spiel mit Rueckfrage
    p, f = neue_seite(b, srv.url + "?neu=1")
    d = H.Spiel(p, schnell=True)
    d.start(); d.waehle("A")
    p.click("#btn-neu"); p.click("#btn-neu-nein")
    E.pruefe("Neues Spiel: «Abbrechen» behaelt den Stand", G, d.phase() == "wurf", "")
    p.click("#btn-neu"); p.click("#btn-neu-ja")
    E.pruefe("Neues Spiel: «Ja» setzt zurueck", G, d.phase() == "start" and p.evaluate("window.GLUECK.undoTiefe()") == 0, "")
    p.close()


def t_tastatur_fokus(b, srv):
    p, f = neue_seite(b, srv.url + "?neu=1")
    p.keyboard.press("Tab"); p.keyboard.press("Tab"); p.keyboard.press("Tab")
    info = p.evaluate("""() => { const e = document.activeElement; const s = getComputedStyle(e); return [e.tagName, e.textContent.trim().slice(0,20), s.outlineStyle, parseFloat(s.outlineWidth), s.boxShadow]; }""")
    E.pruefe("Sichtbarer Fokus bei Tab (Outline oder Schatten)", "Desktop", (info[2] != "none" and info[3] >= 2) or info[4] != "none", str(info))
    d = H.Spiel(p, schnell=True)
    d.start()
    p.evaluate("window.GLUECK.entsperren()"); p.keyboard.press("b")
    z = d.z()
    E.pruefe("Tastenkuerzel B waehlt die Option, die als B angezeigt wird (Regeloption je nach Tausch)", "Desktop",
             d.phase() == "wurf" and z["wahlAnz"] == "B" and z["wahl"] == R.anzeige_zu_regel(z["tausch"]["1"], "B"), "Tausch Ep 1: %s, Regeloption %s" % (z["tausch"]["1"], z["wahl"]))
    d.undo()
    p.evaluate("window.GLUECK.entsperren()"); p.keyboard.press("a")
    z = d.z()
    E.pruefe("Tastenkuerzel A waehlt die Option, die als A angezeigt wird", "Desktop",
             d.phase() == "wurf" and z["wahlAnz"] == "A" and z["wahl"] == R.anzeige_zu_regel(z["tausch"]["1"], "A"), "Regeloption %s" % z["wahl"])
    p.close()


def kontrast_js():
    return """() => {
      function parse(c){ const m = c.match(/rgba?\\(([^)]+)\\)/); if(!m) return [0,0,0,0]; const a = m[1].split(',').map(parseFloat); if (m[1].includes('/')) { const q = m[1].split(/[ /]+/).map(parseFloat); return [q[0],q[1],q[2],q[3]===undefined?1:q[3]]; } return [a[0],a[1],a[2],a.length>3?a[3]:1]; }
      function lum(c){ const f = v => { v/=255; return v<=0.03928? v/12.92 : Math.pow((v+0.055)/1.055,2.4); }; return 0.2126*f(c[0])+0.7152*f(c[1])+0.0722*f(c[2]); }
      function hintergrund(el){ let layers=[]; for(let e=el;e;e=e.parentElement){ const c = parse(getComputedStyle(e).backgroundColor); if(c[3]>0) layers.push(c); if(c[3]>=1) break; } let base=[255,255,255,1]; if(!layers.length || layers[layers.length-1][3]<1){ layers.push(parse(getComputedStyle(document.body).backgroundColor)); }
        let r = layers[layers.length-1].slice(0,3); for(let i=layers.length-2;i>=0;i--){ const a=layers[i][3]; r = r.map((v,k)=> layers[i][k]*a+v*(1-a)); } return r; }
      const out=[]; const w = document.createTreeWalker(document.getElementById('app').parentElement, NodeFilter.SHOW_TEXT);
      const seen=new Set(); let n;
      while(n = w.nextNode()){ if(!n.textContent.trim()) continue; const el=n.parentElement; if(seen.has(el)) continue; seen.add(el); const st=getComputedStyle(el); if(st.visibility==='hidden'||st.display==='none') continue; const r=el.getBoundingClientRect(); if(r.width===0||r.height===0) continue;
        if (el.closest('svg')) continue;
        const fg=parse(st.color); const bg=hintergrund(el); const a=fg[3]; const f=[0,1,2].map(k=>fg[k]*a+bg[k]*(1-a));
        const L1=lum(f), L2=lum(bg); const ratio=(Math.max(L1,L2)+0.05)/(Math.min(L1,L2)+0.05);
        const gross = parseFloat(st.fontSize)>=24 || (parseFloat(st.fontSize)>=18.66 && parseInt(st.fontWeight)>=700);
        const dis = el.closest('button[disabled]');
        if (ratio < (gross?3:4.5) && !dis) out.push([el.textContent.trim().slice(0,30), ratio.toFixed(2), st.color]); }
      return out; }"""


def t_layout_kontrast(b, srv):
    viewports = [("Phone 360x740", dict(viewport={"width": 360, "height": 740}, has_touch=True, is_mobile=True)),
                 ("Phone 390x844", dict(viewport={"width": 390, "height": 844}, has_touch=True, is_mobile=True)),
                 ("Tablet 768x1024", dict(viewport={"width": 768, "height": 1024}, has_touch=True)),
                 ("Desktop 1280x800", dict(viewport={"width": 1280, "height": 800}))]
    schemata = ["light", "dark"]
    shots = os.path.join(os.environ.get("P2_SHOTS", "/tmp"), "")
    for name, args in viewports:
        for schema in schemata:
            ctx = b.new_context(color_scheme=schema, reduced_motion="reduce" if schema == "dark" else "no-preference", **args)
            p = ctx.new_page(); f = H.Fehler(p)
            p.goto(srv.url + "?neu=1"); p.wait_for_selector("#app h2")
            d = H.Spiel(p, touch=args.get("has_touch", False), schnell=True)
            ansichten = []

            def pruefe_ansicht(titel):
                p.wait_for_timeout(450)
                breit = p.evaluate("document.documentElement.scrollWidth - window.innerWidth")
                klein = p.evaluate("""() => [...document.querySelectorAll('#app button, #app input, .kopf button')].filter(e => { const r = e.getBoundingClientRect(); return r.width>0 && (r.height < 43.5 || r.width < 43.5); }).map(e => e.textContent.trim().slice(0,25) + ' ' + Math.round(e.getBoundingClientRect().width) + 'x' + Math.round(e.getBoundingClientRect().height))""")
                raus = p.evaluate("""() => [...document.querySelectorAll('#app *')].filter(e => { const r = e.getBoundingClientRect(); return r.width>0 && (r.right > window.innerWidth + 1 || r.left < -1) && !e.closest('svg'); }).map(e => e.tagName + '.' + e.className).slice(0,3)""")
                kon = p.evaluate(kontrast_js())
                ansichten.append((titel, breit, klein, raus, kon))
                if os.environ.get("P2_SHOTS") and schema == "light" or (os.environ.get("P2_SHOTS") and schema == "dark" and name == "Phone 390x844"):
                    p.screenshot(path=os.path.join(os.environ["P2_SHOTS"], "%s-%s-%s.png" % (name.split()[0].lower() + name.split()[1].split("x")[0], schema, titel)))

            pruefe_ansicht("start")
            d.start(); pruefe_ansicht("entscheidung")
            d.waehle("A"); pruefe_ansicht("wurf")
            d.wurf_physisch(12); pruefe_ansicht("ergebnis")
            d.zu_folgen(); pruefe_ansicht("folgen")
            d.zu_werten(); pruefe_ansicht("werte")
            d.glueck_zeigen(); pruefe_ansicht("glueck-frei")
            d._aktion("[data-aktion=mikroOeffnen][data-wert=normal]"); pruefe_ansicht("mikro-wahl")
            d._aktion("[data-aktion=mikroStart][data-wert=M3]"); pruefe_ansicht("mikro-entscheidung")
            d._aktion("[data-aktion=mikroWahl][data-wert=A]"); pruefe_ansicht("mikro-folgen")
            p.evaluate("(a) => window.GLUECK.springe(a[0], a[1])", ["3", dict(BASIS, stimmung=-3)])
            d.waehle("A"); d.wurf_physisch(1); d.zu_folgen(); d.zu_werten(); pruefe_ansicht("werte-spielende")
            d._aktion("[data-aktion=abschluss]"); pruefe_ansicht("abschluss")
            p.evaluate("(a) => window.GLUECK.springe(a[0], a[1])", ["3", dict(BASIS, stimmung=-3)])
            p.evaluate("window.GLUECK.setze({werte: Object.assign(window.GLUECK.zustand().werte, {stimmung: -4}), phase: 'entscheidung'})")
            geraet = "%s %s" % (name, schema)
            E.pruefe("Kein horizontaler Seitenscroll in allen %d Ansichten" % len(ansichten), geraet, all(a[1] <= 0 for a in ansichten), str([(a[0], a[1]) for a in ansichten if a[1] > 0]))
            E.pruefe("Alle Bedienelemente >= 44x44 px", geraet, all(not a[2] for a in ansichten), str([(a[0], a[2]) for a in ansichten if a[2]][:3]))
            E.pruefe("Kein Element ragt ueber den Bildschirmrand", geraet, all(not a[3] for a in ansichten), str([(a[0], a[3]) for a in ansichten if a[3]][:3]))
            E.pruefe("Kontrast Text AA (>= 4.5, gross >= 3) in allen Ansichten", geraet, all(not a[4] for a in ansichten), str([(a[0], a[4][:3]) for a in ansichten if a[4]][:3]))
            if schema == "dark":
                lang = p.evaluate("""() => [...document.querySelectorAll('*')].filter(e => { const s = getComputedStyle(e); return (s.animationName !== 'none' && parseFloat(s.animationDuration) > 0.011) || parseFloat(s.transitionDuration) > 0.011; }).length""")
                E.pruefe("prefers-reduced-motion: keine laufenden Animationen/Uebergaenge", geraet, lang == 0, "%d Elemente" % lang)
            E.pruefe("Konsole/Anfragen ohne Fehler (Layout)", geraet, not f.liste, str(f.liste[:2]))
            ctx.close()


def main():
    srv = H.Server()
    with sync_playwright() as pw:
        b = pw.chromium.launch()
        for fn in (t_wuerfel, t_eingabe, t_rechenrand, t_schranken, t_undo, t_mikro, t_spielende, t_speicher, t_tastatur_fokus, t_layout_kontrast):
            try:
                fn(b, srv)
            except Exception as ex:  # Testfehler sichtbar machen
                import traceback; traceback.print_exc()
                E.pruefe("Test %s abgebrochen" % fn.__name__, "-", False, repr(ex)[:200])
        b.close()
    srv.stop()
    E.speichern(os.path.join(HIER, "ergebnis_regeln.md"))
    print("Pruefungen:", len(E.zeilen), "Fehler:", len(E.fehler))
    return 1 if E.fehler else 0


if __name__ == "__main__":
    sys.exit(main())
