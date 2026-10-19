#!/usr/bin/env python3
"""Wichtigster Test: Seite gegen das Excel (LibreOffice-Neuberechnung) und gegen eine unabhaengige
Dezimal-Nachrechnung, ueber alle 38 Excel-Zeilen.

Aufruf:  python3 -I tests/pruefe_excel.py
Dauer:   ca. 5 Minuten (LibreOffice rechnet 72 Dateien neu, danach UI-Durchlauf mit 228 Zustaenden)

Teil A  456 Zufallszustaende (12 je Zeile), Seite = Rechenkern im Browser (window.GLUECK.kern.rechne)
Teil B  912 Haelftenfaelle (Summe endet exakt auf x.x5, Rundung auf eine Stelle entscheidet)
Teil C  228 Zustaende (6 je Zeile) ueber die Bedienoberflaeche: Option waehlen, Wurf eintippen,
        angezeigte Zahlen aus der Seite lesen (Resultat, Boost, Balken, Aenderungen, Werte danach)
Alle Teile laufen ueber http:// ; Teil A zusaetzlich einmal ueber file://.

Verglichen werden je Zustand 16 Werte: Q, S-Y, AA-AF, AI, AN. «Abweichung null» heisst hier:
Betrag der Differenz kleiner als 1e-9 (reines Gleitkomma-Rauschen der letzten Stelle).
"""
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import excel_referenz as X
from hilfen import Server, Fehler, PROJEKT
from playwright.sync_api import sync_playwright

TOL = 1e-9
AUSGABEDATEI = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ergebnis_excel.txt")
zeilen_log = []


def log(*a):
    t = " ".join(str(x) for x in a)
    print(t)
    zeilen_log.append(t)


MAP_JS = """
(args) => {
  const K = window.GLUECK.kern, D = window.GLUECK.daten;
  const zmap = {};
  D.episoden.forEach(e => ['A','B'].forEach(k => zmap[e.optionen[k].excelZeile] = [e.id, k]));
  return args.map(c => {
    const [ep, opt] = zmap[c.zeile];
    const z = c.zustand;
    const r = K.rechne(ep, opt, {zeit:z.zeit, energie:z.energie, soz:z.soz, erfuellung:z.erfuellung, lebensstil:z.lebensstil, finanzen:z.finanzen, stimmung:z.stimmung}, z.wurf);
    return {
      resultat: r.resultat,
      nachher_zeit: r.nachher.zeit, nachher_energie: r.nachher.energie, nachher_soz: r.nachher.soz,
      nachher_erfuellung: r.nachher.erfuellung, nachher_lebensstil: r.nachher.lebensstil, nachher_finanzen: r.nachher.finanzen,
      nachher_stimmung: r.nachher.stimmung,
      wirk_zeit: r.beitraege.zeit, wirk_energie: r.beitraege.energie, wirk_soz: r.beitraege.soz,
      wirk_erfuellung: r.beitraege.erfuellung, wirk_lebensstil: r.beitraege.lebensstil, wirk_finanzen: r.beitraege.finanzen,
      energie_aenderung: r.energieAenderung, stimmung_aenderung: r.stimmungsaenderung
    };
  });
}
"""

SCHLUESSEL = list(X.AUSGABE.keys())
Y_ABHAENGIG = {"nachher_stimmung", "energie_aenderung", "nachher_energie"}  # in Zeile 3 und 40 vom fehlenden Y abhaengig


def vergleiche(name, faelle, seite, referenz, ohne_y_zeilen=False):
    """Gibt (n_werte, max_abw, anzahl_abweichungen, beispiele) zurueck."""
    n = 0
    maxabw = 0.0
    bad = []
    for f, s in zip(faelle, seite):
        ref = referenz[(f["durchgang"], f["zeile"])]
        for k in SCHLUESSEL:
            if ohne_y_zeilen and f["zeile"] in (3, 40) and k in Y_ABHAENGIG:
                continue
            r = ref[k]
            if r is None or r == "":
                bad.append((f["zeile"], k, s[k], r, f["zustand"]))
                continue
            d = abs(float(s[k]) - float(r))
            n += 1
            maxabw = max(maxabw, d)
            if d > TOL:
                bad.append((f["zeile"], k, s[k], r, f["zustand"]))
    log("  %-48s %6d Werte  max. Abweichung %.2e  Abweichungen > %.0e: %d" % (name, n, maxabw, TOL, len(bad)))
    return n, maxabw, len(bad), bad


def teil_a_b(seite_http, seite_file):
    ok = True
    log("== Teil A: 456 Zufallszustaende (38 Zeilen x 12), Seite = Rechenkern im Browser")
    t = time.time()
    faelle, lo, dec = X.referenz_erzeugen(12, seed=20261013)
    log("  LibreOffice-Neuberechnung (3 Varianten x 12 Durchgaenge): %.0f s" % (time.time() - t))
    zeilen = sorted({f["zeile"] for f in faelle})
    log("  Zeilen abgedeckt: %d von 38, Zustaende: %d" % (len(zeilen), len(faelle)))
    args = [{"zeile": f["zeile"], "zustand": f["zustand"]} for f in faelle]
    s_http = seite_http.evaluate(MAP_JS, args)
    s_file = seite_file.evaluate(MAP_JS, args)
    r1 = vergleiche("Seite (http)  gegen Excel (LibreOffice, repariert)", faelle, s_http, lo["repariert"])
    r2 = vergleiche("Seite (file)  gegen Excel (LibreOffice, repariert)", faelle, s_file, lo["repariert"])
    r3 = vergleiche("Seite (http)  gegen Excel (LibreOffice, original)*", faelle, s_http, lo["original"], ohne_y_zeilen=True)
    r4 = vergleiche("Seite (http)  gegen Excel (sequenzielle Summe)", faelle, s_http, lo["sequentiell"])
    r5 = vergleiche("Seite (http)  gegen Dezimal-Nachrechnung", faelle, s_http, dec)
    log("  * original = Quell-Excel unveraendert; in Zeile 3 und 40 ohne Y, AI, T (dort fehlt die Formel Y)")
    # Was passiert im unveraenderten Excel in Zeile 3 und 40? Y ist leer (= 0), also AI = AW + ROUND(8*(0-50)/50,0)/2 = AW - 4.
    eb = {3: 0, 40: 0}  # AW3 = 0, AW40 = 0
    leer = 0
    ai_ok = 0
    gesamt = 0
    for f in faelle:
        if f["zeile"] in (3, 40):
            o = lo["original"][(f["durchgang"], f["zeile"])]
            gesamt += 1
            leer += 1 if o["nachher_stimmung"] in (None, "") else 0
            ai_ok += 1 if abs(float(o["energie_aenderung"]) - (eb[f["zeile"]] - 4)) < TOL else 0
    log("  Quell-Excel Zeile 3/40: Y leer in %d von %d Zustaenden, AI dort immer = AW - 4 (%d von %d); die Seite rechnet dort mit M+AN wie in den anderen 36 Zeilen" % (leer, gesamt, ai_ok, gesamt))
    ok = ok and r1[2] == 0 and r2[2] == 0 and r3[2] == 0
    teil_a = {"zustaende": len(faelle), "zeilen": len(zeilen), "werte": r1[0], "abw_repariert": r1[2], "max_abw": r1[1],
              "abw_sequentiell": r4[2], "abw_decimal": r5[2], "bad_decimal": r5[3][:3]}
    if r5[2]:
        log("  Dezimal-Abweichungen (exakte Haelften, Gleitkomma-Rauschen entscheidet):")
        for b in r5[3][:5]:
            log("     Zeile %s %s: Seite %s, Dezimal %s, Zustand %s" % (b[0], b[1], b[2], b[3], b[4]))

    log("")
    log("== Teil B: 912 Haelftenfaelle (2*Summe+Wuerfel endet exakt auf x.x5)")
    t = time.time()
    faelle2, lo2, dec2 = X.referenz_erzeugen(24, seed=777, nur_haelften=True, varianten=("repariert", "sequentiell"))
    log("  LibreOffice-Neuberechnung: %.0f s" % (time.time() - t))
    args2 = [{"zeile": f["zeile"], "zustand": f["zustand"]} for f in faelle2]
    s2 = seite_http.evaluate(MAP_JS, args2)
    b1 = vergleiche("Seite gegen Excel (LibreOffice, SUM wie im Excel)", faelle2, s2, lo2["repariert"])
    b2 = vergleiche("Seite gegen Excel (sequenzielle Summe)", faelle2, s2, lo2["sequentiell"])
    b3 = vergleiche("Seite gegen Dezimal-Nachrechnung", faelle2, s2, dec2)
    if b1[2]:
        log("  Abweichungen gegen LibreOffice-SUM (nur Resultate nahe 0 bis 1, Rauschen kippt die Haelfte):")
        for b in b1[3][:6]:
            log("     Zeile %s %s: Seite %s, LibreOffice %s" % (b[0], b[1], b[2], b[3]))
    ok = ok and b2[2] == 0
    teil_b = {"zustaende": len(faelle2), "abw_lo_sum": b1[2], "abw_sequentiell": b2[2], "abw_decimal": b3[2]}
    return ok, teil_a, teil_b, faelle, lo


def lies_zahl(t):
    t = t.strip().replace("−", "-").replace("±", "")
    if t.startswith("+"):
        t = t[1:]
    return float(t) if t not in ("", "-") else 0.0


def teil_c(browser, srv, faelle, lo, pro_zeile=6):
    log("")
    log("== Teil C: %d Zustaende ueber die Bedienoberflaeche (Desktop), Zahlen aus dem DOM gelesen" % (38 * pro_zeile))
    ctx = browser.new_context(viewport={"width": 1280, "height": 900})
    seite = ctx.new_page()
    fehler = Fehler(seite)
    seite.goto(srv.url + "?seed=1")
    daten = seite.evaluate("window.GLUECK.daten")
    zmap = {}
    for e in daten["episoden"]:
        for k in ("A", "B"):
            zmap[e["optionen"][k]["excelZeile"]] = (e["id"], k)
    gewaehlt = []
    zaehler = {}
    for f in faelle:
        zaehler[f["zeile"]] = zaehler.get(f["zeile"], 0)
        if zaehler[f["zeile"]] < pro_zeile:
            gewaehlt.append(f)
            zaehler[f["zeile"]] += 1
    maxabw = 0.0
    n = 0
    n_tausch = 0
    bad = []
    attr_keys = ["zeit", "energie", "soz", "erfuellung", "lebensstil", "finanzen"]
    for f in gewaehlt:
        ep, opt = zmap[f["zeile"]]
        z = f["zustand"]
        ref = lo["repariert"][(f["durchgang"], f["zeile"])]
        seite.evaluate("([ep, w]) => { window.GLUECK.springe(ep, w); }", [ep, {k: z[k] for k in attr_keys + ["stimmung"]}])
        seite.evaluate("window.GLUECK.entsperren()")
        # Die Seite vertauscht A und B pro Episode zufaellig: den Knopf mit dem zur Regeloption gehoerenden Buchstaben klicken.
        anz = seite.evaluate("([ep, opt]) => { const t = !!window.GLUECK.zustand().tausch[ep]; return t ? (opt === 'A' ? 'B' : 'A') : opt; }", [ep, opt])
        n_tausch += 1 if anz != opt else 0
        seite.locator('[data-aktion=waehle][data-wert=%s]' % anz).click()
        seite.evaluate("window.GLUECK.entsperren()")
        seite.fill("#wurf-eingabe", str(z["wurf"]))
        seite.press("#wurf-eingabe", "Enter")
        gelesen = {"resultat": lies_zahl(seite.inner_text("#z-ergebnis"))}
        for k in attr_keys:
            gelesen["wirk_" + k] = lies_zahl(seite.inner_text('.bwert[data-attr=%s]' % k))
        boost = lies_zahl(seite.inner_text("#z-boost"))
        seite.evaluate("window.GLUECK.entsperren()")
        seite.locator("[data-aktion=zuFolgen]").click()
        gelesen["nachher_stimmung"] = lies_zahl(seite.inner_text("#f-stimmung"))
        gelesen["stimmung_aenderung"] = lies_zahl(seite.inner_text("#f-dstimmung").strip("()"))
        for k in attr_keys:
            gelesen["nachher_" + k] = lies_zahl(seite.inner_text('[data-nachher=%s]' % k))
        # Aenderung Energie = AI (Seite zeigt Gesamtaenderung)
        gelesen["energie_aenderung"] = lies_zahl(seite.inner_text('[data-aenderung=energie]'))
        for k, v in gelesen.items():
            r = float(ref[k])
            if k.startswith("wirk_"):
                r = 2.0 * r  # die Seite zeigt 2 x Beitrag (Anteil am Boost); Excel AA..AF = Beitrag
            d = abs(v - r)
            n += 1
            maxabw = max(maxabw, d)
            if d > TOL:
                bad.append((f["zeile"], k, v, r, z))
        # Boost = 2 * SUM(AA:AF)
        ref_boost = 2 * sum(float(ref["wirk_" + k]) for k in attr_keys)
        n += 1
        if abs(boost - ref_boost) > TOL:
            bad.append((f["zeile"], "boost", boost, ref_boost, z))
    log("  %d Zustaende, %d gelesene Zahlen, max. Abweichung (Resultat, Stimmung, Werte danach) %.2e, Abweichungen: %d" % (len(gewaehlt), n, maxabw, len(bad)))
    for b in bad[:6]:
        log("     " + repr(b))
    log("  Davon mit vertauschten Buchstaben A/B (Anzeige gegen Regeloption umgerechnet): %d von %d Zustaenden" % (n_tausch, len(gewaehlt)))
    log("  Konsole/Anfragen: %s" % (fehler.liste or "keine Fehler"))
    ctx.close()
    return len(bad) == 0 and not fehler.liste, {"zustaende": len(gewaehlt), "zahlen": n, "abweichungen": len(bad), "vertauscht": n_tausch}


def main():
    srv = Server()
    t0 = time.time()
    with sync_playwright() as p:
        b = p.chromium.launch()
        ctx1 = b.new_context(viewport={"width": 1280, "height": 800})
        s_http = ctx1.new_page()
        e1 = Fehler(s_http)
        s_http.goto(srv.url + "?seed=1")
        ctx2 = b.new_context(viewport={"width": 1280, "height": 800})
        s_file = ctx2.new_page()
        e2 = Fehler(s_file)
        s_file.goto(srv.file_url + "?seed=1")
        ok_ab, ta, tb, faelle, lo = teil_a_b(s_http, s_file)
        log("  Konsole/Anfragen http: %s | file: %s" % (e1.liste or "keine Fehler", e2.liste or "keine Fehler"))
        ok_c, tc = teil_c(b, srv, faelle, lo)
        b.close()
    srv.stop()
    ok = ok_ab and ok_c and not e1.liste and not e2.liste
    log("")
    log("Gesamt: %s  (%.0f s)" % ("BESTANDEN" if ok else "NICHT BESTANDEN", time.time() - t0))
    with open(AUSGABEDATEI, "w", encoding="utf-8") as f:
        f.write("\n".join(zeilen_log) + "\n")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
