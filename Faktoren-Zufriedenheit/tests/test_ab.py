"""A/B-Randomisierung: pro Episode ist zufaellig, welche Regeloption als «A» und welche als «B» erscheint.
Aufruf: python3 -I tests/test_ab.py   (schreibt tests/ergebnis_ab.md)

Geprueft wird:
  * Statistik: Anteil der vertauschten Episoden ueber viele Seeds und mit crypto.getRandomValues (je Episode ca. 50 %),
    Paare benachbarter Episoden unabhaengig, Muster verschieden; ohne Seed wird crypto benutzt, Math.random nie.
  * Modi: ?ab=fest (alles wie im Excel), ?ab=tausch (alles vertauscht), Standard (zufaellig); Seed reproduzierbar;
    der Plan stimmt mit einer unabhaengigen Python-Fassung (FNV-1a, mulberry32, Fisher-Yates) ueberein;
    die Wuerfelfolge zu einem Seed bleibt wie vorher.
  * Zuordnung ueber die Oberflaeche: alle 19 Episoden x beide Buchstaben x 3 Modi: Karte, Gewaehlt-Zeile, Regeloption,
    Rechnung gegen die Excel-Referenz, Verzweigung folgt der Regeloption, Protokoll mit Ausrichtung.
  * Ausrichtung waehrend des Spiels nirgends sichtbar (alle Phasen), im Abschluss je Episode sichtbar.
  * Rueckgaengig, Neuladen in jeder Phase, Neues Spiel (neuer Plan), Mikroszenen (nicht vertauscht).
"""
import math
import os
import re
import sys
from decimal import Decimal

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from playwright.sync_api import sync_playwright

import hilfen as H
import referenz_spiel as R
from test_dateien import lade_daten, lade_texte

HIER = os.path.dirname(os.path.abspath(__file__))
E = H.Ergebnisse()
BASIS = {"zeit": 0, "energie": 0, "soz": 1, "erfuellung": 1, "lebensstil": 1, "finanzen": 1, "stimmung": 50}
D = lade_daten()
T = lade_texte()
EPS = {e["id"]: e for e in D["episoden"]}
IDS = [e["id"] for e in D["episoden"]]
MIKRO = {m["id"]: m for m in D["mikroszenen"]}
AUSR_NAMEN = T["ausrichtungNamen"]
VERBOTEN = [r"ausrichtung", r"langfristige investition", r"kurzfristige optimierung", r"data-ausr"]
MODI = [("fest", "?ab=fest&neu=1"), ("tausch", "?ab=tausch&neu=1"), ("zufall (Seed 11)", "?seed=11")]


# ------------------------------------------------------------------ unabhaengige Fassung des Plans
def imul(a, b):
    return (a * b) & 0xFFFFFFFF


def hash_seed(s):
    h = 2166136261
    for ch in str(s):
        h ^= ord(ch)
        h = imul(h, 16777619)
    return h & 0xFFFFFFFF


def mulberry32(a):
    st = [a & 0xFFFFFFFF]

    def f():
        st[0] = (st[0] + 0x6D2B79F5) & 0xFFFFFFFF
        a_ = st[0]
        t = imul(a_ ^ (a_ >> 15), 1 | a_)
        t = ((t + imul(t ^ (t >> 7), 61 | t)) & 0xFFFFFFFF) ^ t
        return ((t ^ (t >> 14)) & 0xFFFFFFFF) / 4294967296
    return f


def anzahl_kandidaten(ep):
    return len(EPS[ep]["glueck"]) + len(T["episoden"][ep]["plausibel"]) + len(T["episoden"][ep]["unplausibel"])


def plan_referenz(rnd, modus="zufall"):
    """Gleiche Reihenfolge der Ziehungen wie die Seite: je Episode ein Bit, dann Fisher-Yates ueber die Kandidaten."""
    tausch, ordnung = {}, {}
    for ep in IDS:
        bit = math.floor(rnd() * 2)
        tausch[ep] = 0 if modus == "fest" else (1 if modus == "tausch" else bit)
        idx = list(range(anzahl_kandidaten(ep)))
        for i in range(len(idx) - 1, 0, -1):
            j = math.floor(rnd() * (i + 1))
            idx[i], idx[j] = idx[j], idx[i]
        ordnung[ep] = idx
    return tausch, ordnung


# ------------------------------------------------------------------ Hilfen
def neue_seite(b, url, ctx_args=None, init=None):
    ctx = b.new_context(**(ctx_args or dict(viewport={"width": 1280, "height": 900})))
    p = ctx.new_page()
    f = H.Fehler(p)
    if init:
        p.add_init_script(init)
    p.goto(url)
    p.wait_for_selector("#app h2")
    return p, f


def zustand(p):
    return p.evaluate("window.GLUECK.zustand()")


def sichtbar_sauber(p):
    """Kein Hinweis auf die Ausrichtung im sichtbaren Dokument (Text, Attribute, Ansage, Titel); Skripte ausgenommen."""
    html = p.evaluate("""() => { const c = document.body.cloneNode(true); c.querySelectorAll('script,style').forEach(e => e.remove());
        return (c.innerHTML + ' ' + document.title).toLowerCase(); }""")
    return [v for v in VERBOTEN if re.search(v, html)]


def referenz_episode(ep, opt, wurf_wunsch=None):
    """Referenz-Ergebnis der Episode mit den Basiswerten; waehlt einen Wurf nahe dem Soll, der kein Haelftenfall ist."""
    r = R.Referenz()
    r.w = {k: Decimal(str(v)) for k, v in BASIS.items()}
    soll = EPS[ep]["optionen"][opt]["soll"]
    w0 = wurf_wunsch or soll
    for dv in (0, 1, -1, 2, -2, 3, -3, 4, -4):
        w = w0 + dv
        if 1 <= w <= 20 and not r.tie(ep, opt, w):
            return w, r.episode(ep, opt, w), soll
    raise AssertionError("kein geeigneter Wurf")


def spiele_bis_werte(p, d, ep, letter, fehl, mit_ref=True):
    """Springt in die Episode (Basiswerte), waehlt den ANGEZEIGTEN Buchstaben und spielt bis «Werte danach»."""
    p.evaluate("(a) => window.GLUECK.springe(a[0], a[1])", [ep, dict(BASIS)])
    z = zustand(p)
    tausch = z["tausch"][ep]
    regel = R.anzeige_zu_regel(tausch, letter)
    # die Karte mit diesem Buchstaben zeigt die Regeloption
    label = p.inner_text('section[aria-label="Option %s"] .name' % letter).strip()
    if label != EPS[ep]["optionen"][regel]["label"]:
        fehl.append("%s: Karte %s zeigt %r statt Regeloption %s" % (ep, letter, label, regel))
    d.waehle_anzeige(letter)
    z = zustand(p)
    if not (z["wahl"] == regel and z["wahlAnz"] == letter and z["phase"] == "wurf"):
        fehl.append("%s: Zustand nach Klick auf %s: wahl=%s wahlAnz=%s phase=%s, erwartet Regel %s" % (ep, letter, z["wahl"], z["wahlAnz"], z["phase"], regel))
    gew = p.inner_text(".gewaehlt strong").strip()
    if gew != "%s · %s" % (letter, EPS[ep]["optionen"][regel]["label"]):
        fehl.append("%s: Gewaehlt-Zeile %r" % (ep, gew))
    wurf, r, soll = referenz_episode(ep, regel)
    d.wurf_physisch(wurf)
    # Rechnung gegen die Referenz (gewaehlte Regeloption!)
    res = H.zahl(p.inner_text("#z-ergebnis"))
    if abs(res - float(r["resultat"])) > 1e-9:
        fehl.append("%s/%s: Resultat %s statt %s" % (ep, letter, res, r["resultat"]))
    if int(p.inner_text("#z-soll")) != soll:
        fehl.append("%s/%s: Soll %s statt %s" % (ep, letter, p.inner_text("#z-soll"), soll))
    art = "Erfolg" if float(r["resultat"]) >= soll else "Misserfolg"
    if p.text_content("#kt-titel").strip() != art:
        fehl.append("%s/%s: Kurztext-Titel" % (ep, letter))
    d.zu_folgen()
    for k in ("zeit", "energie", "soz", "erfuellung", "lebensstil", "finanzen"):
        if abs(H.zahl(p.inner_text("[data-nachher=%s]" % k)) - float(r["nachher_" + k])) > 1e-9:
            fehl.append("%s/%s: nachher %s" % (ep, letter, k))
    d.zu_werten()
    return regel, tausch


# ------------------------------------------------------------------ Tests
def t_statistik(b, srv):
    p, f = neue_seite(b, srv.url + "?neu=1")
    res = p.evaluate("""() => {
      const K = window.GLUECK_KERN, kern = window.GLUECK.kern, ids = window.GLUECK.daten.episoden.map(e => e.id);
      function lauf(n, seedFn) {
        const z = {}; ids.forEach(i => z[i] = 0); let gleich = 0, paare = 0, swap = 0; const muster = new Set();
        for (let s = 0; s < n; s++) {
          const pl = kern.neuerPlan(K.neuerZufall(seedFn(s), "plan"), "zufall");
          let m = "";
          ids.forEach((i, k) => { z[i] += pl.tausch[i]; m += pl.tausch[i]; swap += pl.tausch[i];
            if (k > 0) { paare++; if (pl.tausch[i] === pl.tausch[ids[k - 1]]) gleich++; } });
          muster.add(m);
        }
        return { n: n, z: z, gleich: gleich, paare: paare, muster: muster.size, swap: swap };
      }
      return { seed: lauf(2000, s => String(s)), crypto: lauf(4000, s => null), ids: ids };
    }""")
    for name, label in (("seed", "2000 Seeds"), ("crypto", "4000 Spiele mit crypto.getRandomValues")):
        r = res[name]
        n = r["n"]
        grenze = 4 * math.sqrt(n) / 2  # 4 Standardabweichungen
        abw = {ep: r["z"][ep] - n / 2 for ep in res["ids"]}
        schlecht = [ep for ep, a in abw.items() if abs(a) > grenze]
        E.pruefe("A/B: Anteil vertauscht je Episode (%s), alle 19 Episoden innerhalb 4 Sigma" % label, "Desktop", not schlecht,
                 "kleinster Anteil %.3f, groesster %.3f (n=%d)" % (min(r["z"].values()) / n, max(r["z"].values()) / n, n))
        gesamt = r["swap"] / (n * len(res["ids"]))
        E.pruefe("A/B: Gesamtanteil vertauscht ca. 50 %% (%s)" % label, "Desktop", abs(gesamt - 0.5) < 4 * 0.5 / math.sqrt(n * 19) + 1e-9, "%.4f" % gesamt)
        pg = r["gleich"] / r["paare"]
        E.pruefe("A/B: benachbarte Episoden unabhaengig (%s): Anteil gleicher Paare ca. 50 %%" % label, "Desktop",
                 abs(pg - 0.5) < 4 * 0.5 / math.sqrt(r["paare"]), "%.4f" % pg)
        E.pruefe("A/B: Muster der 19 Bits verschieden (Doppelte nur im Rahmen des Geburtstagsparadoxons) (%s)" % label, "Desktop", n - r["muster"] <= 2 * (n * (n - 1) / 2 / 2 ** 19) + 10, "%d von %d (zufaellige Doppelte erwartet: %.0f)" % (r["muster"], n, n * (n - 1) / 2 / 2 ** 19))
    p.close()

    # echte Seiten ohne Seed: crypto wird benutzt, Math.random nie
    zaehler = """(() => { window.__crypto = 0; window.__mathrandom = 0;
        const g = crypto.getRandomValues.bind(crypto); crypto.getRandomValues = function (a) { window.__crypto++; return g(a); };
        const m = Math.random; Math.random = function () { window.__mathrandom++; return m(); }; })();"""
    muster, bits = [], 0
    ok_crypto = True
    for i in range(40):
        p, f = neue_seite(b, srv.url + "?neu=1", init=zaehler)
        z = zustand(p)
        c = p.evaluate("[window.__crypto, window.__mathrandom]")
        if not (c[0] > 0 and c[1] == 0):
            ok_crypto = False
        m = "".join(str(z["tausch"][ep]) for ep in IDS)
        muster.append(m)
        bits += m.count("1")
        p.close()
    E.pruefe("A/B: Seite ohne Seed benutzt crypto.getRandomValues und nie Math.random (40 Ladevorgaenge)", "Desktop", ok_crypto, "")
    E.pruefe("A/B: 40 Spiele ohne Seed haben 40 verschiedene Muster, Anteil vertauscht ca. 50 %", "Desktop",
             len(set(muster)) == 40 and abs(bits - 40 * 19 / 2) < 4 * math.sqrt(40 * 19) / 2, "%d Muster, %d von %d vertauscht" % (len(set(muster)), bits, 40 * 19))
    p, f = neue_seite(b, srv.url + "?seed=5", init=zaehler)
    c = p.evaluate("[window.__crypto, window.__mathrandom]")
    E.pruefe("A/B: Seite mit ?seed= benutzt weder crypto noch Math.random", "Desktop", c == [0, 0], str(c))
    p.close()


def t_modi(b, srv):
    def lade(query):
        p, f = neue_seite(b, srv.url + query)
        z = zustand(p)
        modus = p.evaluate("window.GLUECK.abModus")
        p.close()
        return z, modus
    zf, mf = lade("?seed=7&ab=fest")
    zt, mt = lade("?seed=7&ab=tausch")
    zz, mz = lade("?seed=7")
    zz2, _ = lade("?seed=7")
    z8, _ = lade("?seed=8")
    zx, mx = lade("?seed=7&ab=unsinn")
    E.pruefe("?ab=fest: alle 19 Episoden unvertauscht, Modus «fest»", "Desktop", mf == "fest" and all(zf["tausch"][ep] == 0 for ep in IDS), mf)
    E.pruefe("?ab=tausch: alle 19 Episoden vertauscht, Modus «tausch»", "Desktop", mt == "tausch" and all(zt["tausch"][ep] == 1 for ep in IDS), mt)
    E.pruefe("Standard: Modus «zufall», gemischt", "Desktop", mz == "zufall" and 0 < sum(zz["tausch"].values()) < 19, "%d von 19 vertauscht" % sum(zz["tausch"].values()))
    E.pruefe("Unbekannter Wert bei ?ab= wirkt wie der Standard", "Desktop", mx == "zufall" and zx["tausch"] == zz["tausch"], mx)
    E.pruefe("?seed= reproduzierbar: gleicher Seed, gleicher Plan (A/B und Reihenfolge)", "Desktop", zz["tausch"] == zz2["tausch"] and zz["ordnung"] == zz2["ordnung"], "")
    E.pruefe("Anderer Seed gibt anderen Plan", "Desktop", zz["tausch"] != z8["tausch"] and zz["ordnung"] != z8["ordnung"], "")
    E.pruefe("Reihenfolge der Kandidaten haengt nicht vom ab-Modus ab (gleicher Seed in allen drei Modi)", "Desktop",
             zf["ordnung"] == zt["ordnung"] == zz["ordnung"], "")
    for seed in ("7", "8", "abc"):
        z, _ = lade("?seed=%s" % seed)
        tr, orr = plan_referenz(mulberry32(hash_seed(seed + "|plan")))
        E.pruefe("Plan zum Seed %r stimmt mit unabhaengiger Python-Fassung ueberein (A/B und Reihenfolge, 19 Episoden)" % seed, "Desktop",
                 z["tausch"] == tr and {k: v for k, v in z["ordnung"].items()} == orr, "")
    # Wuerfelfolge zu einem Seed bleibt unveraendert (Plan zieht aus einem eigenen Strom)
    def wuerfe(query, n=6):
        p, f = neue_seite(b, srv.url + query)
        d = H.Spiel(p, schnell=True)
        d.start()
        out = []
        for _ in range(n):
            d.waehle_anzeige("A")
            d.wurf_virtuell()
            out.append(zustand(p)["wurf"])
            d.zu_folgen(); d.zu_werten(); d.weiter()
        p.close()
        return out
    rnd = mulberry32(hash_seed("5"))
    erwartet = [math.floor(rnd() * 20) + 1 for _ in range(6)]
    w1, w2, w3 = wuerfe("?seed=5&ab=fest"), wuerfe("?seed=5&ab=tausch"), wuerfe("?seed=5")
    E.pruefe("Wuerfelfolge zu ?seed=5 ist in allen Modi gleich und entspricht FNV-1a/mulberry32 (unveraendert)", "Desktop",
             w1 == w2 == w3 == erwartet, "%s gegen %s" % (w1, erwartet))


def t_zuordnung(b, srv):
    for modus, query in MODI:
        p, f = neue_seite(b, srv.url + query)
        d = H.Spiel(p, schnell=True)
        d.start()
        fehl, n, n_tausch = [], 0, 0
        for ep in IDS:
            for letter in "AB":
                regel, tausch = spiele_bis_werte(p, d, ep, letter, fehl)
                n += 1
                n_tausch += tausch
                nxt = R.WEITER.get((ep, regel))
                if modus == "fest" and tausch != 0: fehl.append("%s: fest, aber vertauscht" % ep)
                if modus == "tausch" and tausch != 1: fehl.append("%s: tausch, aber nicht vertauscht" % ep)
                if nxt is None:
                    d._aktion("[data-aktion=abschluss]")
                    if d.phase() != "abschluss": fehl.append("%s/%s: kein Abschluss" % (ep, letter))
                    pr = [x for x in zustand(p)["protokoll"] if x["typ"] == "ep"][-1]
                else:
                    d.weiter()
                    pr = [x for x in zustand(p)["protokoll"] if x["typ"] == "ep"][-1]  # der Eintrag entsteht beim Weitergehen
                    z = zustand(p)
                    if z["ep"] != nxt:
                        fehl.append("%s/%s (Regeloption %s): naechste Episode %s statt %s" % (ep, letter, regel, z["ep"], nxt))
                if not (pr["option"] == regel and pr["optionAnzeige"] == letter and pr["ausrichtung"] == R.AUSRICHTUNG[ep][regel]
                        and bool(pr["unscharf"]) == (ep in R.UNSCHARF)):
                    fehl.append("%s/%s: Protokoll %s" % (ep, letter, {k: pr.get(k) for k in ("option", "optionAnzeige", "ausrichtung", "unscharf")}))
        E.pruefe("Zuordnung ueber die Oberflaeche, Modus %s: 38 Faelle (19 Episoden x A/B), Karte, Regeloption, Rechnung, Verzweigung, Protokoll" % modus,
                 "Desktop", not fehl and n == 38, "%d Faelle, %d mit vertauschten Buchstaben; %s" % (n, n_tausch, "; ".join(fehl[:3])))
        E.pruefe("Konsole/Anfragen ohne Fehler (Zuordnung %s)" % modus, "Desktop", not f.liste, str(f.liste[:2]))
        p.close()


def t_sichtbarkeit_abschluss(b, srv):
    """Ganzer Weg (12 Episoden) mit zufaelliger Zuordnung: Ausrichtung nirgends sichtbar, im Abschluss je Episode sichtbar."""
    for modus, query in (("zufall (Seed 21)", "?seed=21"), ("fest", "?ab=fest&neu=1")):
        p, f = neue_seite(b, srv.url + query)
        d = H.Spiel(p, schnell=True)
        z0 = zustand(p)
        plan0 = (z0["tausch"], z0["ordnung"])
        d.start()
        ep = "1"
        wahl = ["A", "B", "A", "B", "A", "B", "B", "A", "A", "B", "A", "B"]  # ANGEZEIGTE Buchstaben
        gespielt, leaks, plan_aendert = [], [], []
        for i, letter in enumerate(wahl):
            z = zustand(p)
            assert z["ep"] == ep, (z["ep"], ep)
            leaks += ["Ep %s entscheidung: %s" % (ep, x) for x in sichtbar_sauber(p)]
            regel = R.anzeige_zu_regel(z["tausch"][ep], letter)
            d.waehle_anzeige(letter)
            leaks += ["Ep %s wurf: %s" % (ep, x) for x in sichtbar_sauber(p)]
            soll = EPS[ep]["optionen"][regel]["soll"]
            d.wurf_physisch(max(1, min(20, soll + 1)))
            leaks += ["Ep %s ergebnis: %s" % (ep, x) for x in sichtbar_sauber(p)]
            d.zu_folgen()
            leaks += ["Ep %s folgen: %s" % (ep, x) for x in sichtbar_sauber(p)]
            d.zu_werten()
            leaks += ["Ep %s werte verdeckt: %s" % (ep, x) for x in sichtbar_sauber(p)]
            if i % 3 == 0:
                d.glueck_zeigen()
                leaks += ["Ep %s werte frei: %s" % (ep, x) for x in sichtbar_sauber(p)]
            gespielt.append((ep, regel, letter))
            zz = zustand(p)
            if (zz["tausch"], zz["ordnung"]) != plan0: plan_aendert.append(ep)
            nxt = R.WEITER.get((ep, regel))
            if nxt is None:
                d._aktion("[data-aktion=abschluss]")
            else:
                d.weiter(); ep = nxt
        E.pruefe("Ausrichtung waehrend des Spiels nirgends sichtbar (%s): Text, Attribute, Ansage, alle Phasen von 12 Episoden" % modus, "Desktop", not leaks, "; ".join(leaks[:3]))
        E.pruefe("Plan (A/B und Reihenfolge) bleibt waehrend des ganzen Spiels unveraendert (%s)" % modus, "Desktop", not plan_aendert, str(plan_aendert[:3]))
        # Abschluss
        zz = zustand(p)
        E.pruefe("Abschluss erreicht, 12 Episoden im Protokoll (%s)" % modus, "Desktop", zz["phase"] == "abschluss" and len([x for x in zz["protokoll"] if x["typ"] == "ep"]) == 12, zz["phase"])
        erw_a = [R.AUSRICHTUNG[e][o] for e, o, _ in gespielt]
        ist_a = p.evaluate("[...document.querySelectorAll('[data-ausrichtung]')].map(e => e.dataset.ausrichtung)")
        ist_txt = p.evaluate("[...document.querySelectorAll('[data-ausrichtung]')].map(e => e.textContent.replace(' *','').trim())")
        E.pruefe("Abschluss (%s): je Episode die richtige Ausrichtung (Wert und Anzeigetext)" % modus, "Desktop",
                 ist_a == erw_a and ist_txt == [AUSR_NAMEN[a] for a in erw_a], "%s" % ist_a[:4])
        zeilen = p.evaluate("[...document.querySelectorAll('ol.verlauf li:not(.mikro) .l2')].map(e => e.textContent)")
        E.pruefe("Abschluss (%s): je Episode der angezeigte Buchstabe und der Name der Option" % modus, "Desktop",
                 len(zeilen) == 12 and all(t.startswith("Option %s · %s" % (g[2], EPS[g[0]]["optionen"][g[1]]["label"])) for t, g in zip(zeilen, gespielt)), zeilen[0] if zeilen else "")
        nl, nk = erw_a.count("langfristig"), erw_a.count("kurzfristig")
        zahl = p.inner_text("#ausr-zahlen").strip()
        E.pruefe("Abschluss (%s): Zaehlzeile stimmt (%d x langfristig, %d x kurzfristig, Summe 12)" % (modus, nl, nk), "Desktop",
                 zahl == "Gewählte Ausrichtung: %d × %s, %d × %s." % (nl, AUSR_NAMEN["langfristig"], nk, AUSR_NAMEN["kurzfristig"]) and nl + nk == 12, zahl)
        hint = p.inner_text("#app .hint")
        E.pruefe("Abschluss (%s): Hinweis zur Verteilung der Buchstaben passt zum Modus" % modus, "Desktop",
                 ("zufällig verteilt" in hint) == (modus != "fest") and "nicht sichtbar" in hint, hint[:90])
        if modus == "fest":
            E.pruefe("?ab=fest: angezeigter Buchstabe = Regeloption in allen 12 Episoden (alte Zuordnung)", "Desktop",
                     all(g[1] == g[2] for g in gespielt), "")
        E.pruefe("Abschluss (%s): Stern nur bei unscharfer Zuordnung" % modus, "Desktop",
                 ("*" in p.inner_text("#app")) == any(e in R.UNSCHARF for e, _, _ in gespielt), "")
        E.pruefe("Konsole/Anfragen ohne Fehler (Sichtbarkeit %s)" % modus, "Desktop", not f.liste, str(f.liste[:2]))
        p.close()


def t_undo(b, srv):
    p, f = neue_seite(b, srv.url + "?ab=tausch&neu=1")
    d = H.Spiel(p, schnell=True)
    d.start()
    z0 = zustand(p)
    plan0 = (z0["tausch"], z0["ordnung"])
    fehl = []
    # Schritt fuer Schritt: waehlen, zurueck, anderen Buchstaben waehlen
    d.waehle_anzeige("A")
    z = zustand(p)
    ok1 = z["wahl"] == "B" and z["wahlAnz"] == "A"
    d.undo()
    z = zustand(p)
    ok2 = z["phase"] == "entscheidung" and z["wahl"] is None and z["wahlAnz"] is None and (z["tausch"], z["ordnung"]) == plan0
    lab = [p.inner_text('section[aria-label="Option %s"] .name' % L).strip() for L in "AB"]
    ok3 = lab == [EPS["1"]["optionen"]["B"]["label"], EPS["1"]["optionen"]["A"]["label"]]
    d.waehle_anzeige("B")
    z = zustand(p)
    ok4 = z["wahl"] == "A" and z["wahlAnz"] == "B"
    E.pruefe("Rueckgaengig nach Wahl (Tausch): Phase, Wahl, Anzeigebuchstabe leer, Plan gleich, Karten unveraendert, danach andere Wahl richtig", "Desktop",
             ok1 and ok2 and ok3 and ok4, "%s %s %s %s" % (ok1, ok2, ok3, ok4))
    d.wurf_physisch(10)
    d.undo()
    z = zustand(p)
    E.pruefe("Rueckgaengig nach Wurf: wieder in «Wuerfeln», gleiche Wahl (Regeloption A, angezeigt B), Gewaehlt-Zeile stimmt", "Desktop",
             z["phase"] == "wurf" and z["wahl"] == "A" and z["wahlAnz"] == "B" and p.inner_text(".gewaehlt strong").startswith("B · "), p.inner_text(".gewaehlt strong")[:40])
    d.undo()
    z = zustand(p)
    E.pruefe("Zweites Rueckgaengig: wieder Entscheidung, Plan gleich", "Desktop", z["phase"] == "entscheidung" and z["wahl"] is None and (z["tausch"], z["ordnung"]) == plan0, "")

    # Zwei Wege: gerade durch und mit Umwegen (Rueckgaengig ueber Episodengrenzen), Endzustand muss gleich sein
    def weg(mit_umwegen):
        pp, ff = neue_seite(b, srv.url + "?seed=31")
        dd = H.Spiel(pp, schnell=True)
        dd.start()
        ep = "1"
        letters = ["A", "B", "B", "A", "A"]
        for i, letter in enumerate(letters):
            zz = zustand(pp)
            regel = R.anzeige_zu_regel(zz["tausch"][ep], letter)
            if mit_umwegen:
                other = "B" if letter == "A" else "A"
                dd.waehle_anzeige(other)
                dd.wurf_physisch(7)
                dd.zu_folgen()
                dd.undo(); dd.undo(); dd.undo()
                if zustand(pp)["phase"] != "entscheidung": fehl.append("Umweg %s: nicht in Entscheidung" % ep)
            dd.waehle_anzeige(letter)
            dd.wurf_physisch(max(1, min(20, EPS[ep]["optionen"][regel]["soll"] + 2)))
            dd.zu_folgen(); dd.zu_werten()
            nxt = R.WEITER.get((ep, regel))
            if nxt is None: break
            dd.weiter()
            if mit_umwegen:
                dd.undo()  # zurueck zu «Werte danach»
                if zustand(pp)["phase"] != "werte" or zustand(pp)["ep"] != ep: fehl.append("Undo ueber Episodengrenze %s" % ep)
                dd.weiter()
            ep = nxt
        zend = zustand(pp)
        pp.close()
        return zend
    z_gerade, z_umweg = weg(False), weg(True)
    felder = ("tausch", "ordnung", "werte", "ep", "phase", "wahl", "wahlAnz", "protokoll", "schritt")
    gleich = all(z_gerade[k] == z_umweg[k] for k in felder)
    E.pruefe("Spiel mit Umwegen (Wahl, Wurf, Folgen, Rueckgaengig, ueber Episodengrenzen) endet im gleichen Zustand wie das gerade Spiel", "Desktop",
             gleich and not fehl, "; ".join(fehl[:2]) or ("abweichend: %s" % [k for k in felder if z_gerade[k] != z_umweg[k]]))
    E.pruefe("Konsole/Anfragen ohne Fehler (Rueckgaengig)", "Desktop", not f.liste, str(f.liste[:2]))
    p.close()


def t_neuladen(b, srv):
    p, f = neue_seite(b, srv.url + "?ab=tausch&seed=3")
    d = H.Spiel(p, schnell=True)
    d.start()
    z_start = zustand(p)
    fehl = []

    def neu_laden(phase):
        vor = zustand(p)
        text_vor = p.inner_text("#app")
        p.goto(srv.url)  # ohne Parameter: gespeicherten Stand laden
        p.wait_for_selector("#app h2")
        nach = zustand(p)
        text_nach = p.inner_text("#app")
        if vor != nach: fehl.append("%s: Zustand nach Neuladen anders (%s)" % (phase, [k for k in vor if vor[k] != nach.get(k)][:3]))
        if text_vor != text_nach: fehl.append("%s: Anzeige nach Neuladen anders" % phase)
        if phase != "start" and nach["tausch"] != z_start["tausch"]: fehl.append("%s: Plan anders" % phase)

    neu_laden("entscheidung")
    d.waehle_anzeige("A"); neu_laden("wurf")
    d.wurf_physisch(9); neu_laden("ergebnis")
    d.zu_folgen(); neu_laden("folgen")
    d.zu_werten(); neu_laden("werte verdeckt")
    p.locator(".glueck .kand").nth(1).click(); neu_laden("werte markiert")
    d.glueck_zeigen(); neu_laden("werte frei")
    d._aktion("[data-aktion=mikroOeffnen][data-wert=normal]"); neu_laden("mikro-wahl")
    d._aktion("[data-aktion=mikroStart][data-wert=M2]"); neu_laden("mikro-entscheidung")
    d._aktion("[data-aktion=mikroWahl][data-wert=B]"); neu_laden("mikro-folgen")
    d._aktion("[data-aktion=mikroWeiter]"); neu_laden("naechste Episode")
    E.pruefe("Neuladen (ohne Parameter) in 10 Phasen: Zustand, Anzeige und Plan unveraendert (Tausch)", "Desktop", not fehl, "; ".join(fehl[:3]))
    # weiterspielen nach dem Neuladen und Rueckgaengig ueber das Neuladen hinweg
    z = zustand(p)
    d.waehle_anzeige("B")
    z2 = zustand(p)
    E.pruefe("Nach dem Neuladen: Wahl folgt weiter dem gespeicherten Plan", "Desktop", z2["wahl"] == R.anzeige_zu_regel(z["tausch"][z["ep"]], "B") and z2["wahlAnz"] == "B", "")
    d.undo(); d.undo()
    E.pruefe("Rueckgaengig reicht ueber das Neuladen hinweg zurueck", "Desktop", zustand(p)["phase"] in ("mikro-folgen", "werte", "mikro-entscheidung", "entscheidung"), zustand(p)["phase"])

    # Neues Spiel: neuer Plan; mit Seed ist der zweite Plan die Fortsetzung des Stroms
    p2, f2 = neue_seite(b, srv.url + "?seed=3")
    plan1 = zustand(p2)["tausch"]
    p2.click("#btn-neu"); p2.wait_for_timeout(300); p2.click("#btn-neu-ja"); p2.wait_for_timeout(400)
    z_neu = zustand(p2)
    rnd = mulberry32(hash_seed("3|plan"))
    plan_referenz(rnd)
    t2, o2 = plan_referenz(rnd)
    E.pruefe("Neues Spiel (mit Seed): zweiter Plan ist die Fortsetzung des Zufallsstroms (unabhaengige Python-Fassung) und anders als der erste", "Desktop",
             z_neu["phase"] == "start" and z_neu["tausch"] == t2 and z_neu["ordnung"] == o2 and z_neu["tausch"] != plan1, "")
    p2.close()
    p3, f3 = neue_seite(b, srv.url + "?neu=1")
    a = zustand(p3)
    p3.click("#btn-neu"); p3.wait_for_timeout(300); p3.click("#btn-neu-ja"); p3.wait_for_timeout(400)
    bz = zustand(p3)
    E.pruefe("Neues Spiel (ohne Seed): neuer zufaelliger Plan (A/B und Reihenfolge)", "Desktop", (a["tausch"], a["ordnung"]) != (bz["tausch"], bz["ordnung"]) and bz["phase"] == "start", "")
    p3.close()
    E.pruefe("Konsole/Anfragen ohne Fehler (Neuladen)", "Desktop", not f.liste, str(f.liste[:2]))
    p.close()


def t_mikro(b, srv):
    p, f = neue_seite(b, srv.url + "?ab=tausch&neu=1")
    d = H.Spiel(p, schnell=True)
    d.start()
    d.waehle_anzeige("A"); d.wurf_physisch(11); d.zu_folgen(); d.zu_werten()
    plan = zustand(p)["tausch"]
    fehl = []
    for mid, wahl in (("M2", "A"), ("M5", "B"), ("M7", "A")):
        d._aktion("[data-aktion=mikroOeffnen][data-wert=normal]")
        d._aktion("[data-aktion=mikroStart][data-wert=%s]" % mid)
        lab = [p.inner_text('section[aria-label="Option %s"] .name' % L).strip() for L in "AB"]
        if lab != [MIKRO[mid]["optionen"]["A"]["label"], MIKRO[mid]["optionen"]["B"]["label"]]:
            fehl.append("%s: Reihenfolge der Mikro-Optionen %s" % (mid, lab))
        d._aktion("[data-aktion=mikroWahl][data-wert=%s]" % wahl)
        z = zustand(p)
        if z["mikro"]["wahl"] != wahl or p.inner_text(".gewaehlt strong").strip() != "%s · %s" % (wahl, MIKRO[mid]["optionen"][wahl]["label"]):
            fehl.append("%s: Wahl %s" % (mid, wahl))
        if z["protokoll"][-1].get("option") != wahl or "optionAnzeige" in z["protokoll"][-1]:
            fehl.append("%s: Protokoll %s" % (mid, z["protokoll"][-1]))
        leaks = sichtbar_sauber(p)
        if leaks: fehl.append("%s: sichtbar %s" % (mid, leaks))
        # zurueck in die Episode-Ansicht (Rueckgaengig, bis «Werte danach» erreicht ist), damit wieder die Liste erreichbar ist
        for _ in range(6):
            if zustand(p)["phase"] == "werte": break
            d.undo()
        if zustand(p)["phase"] != "werte": fehl.append("%s: Undo nicht in «Werte danach»" % mid)
    E.pruefe("Mikroszenen bleiben unvertauscht (A/B wie im Word) auch bei ?ab=tausch; Protokoll ohne Anzeigebuchstabe; Plan der Episoden unveraendert", "Desktop",
             not fehl and zustand(p)["tausch"] == plan, "; ".join(fehl[:3]))
    E.pruefe("Konsole/Anfragen ohne Fehler (Mikroszenen)", "Desktop", not f.liste, str(f.liste[:2]))
    p.close()


def t_phone(b, srv):
    """Kurzer Durchlauf auf dem Handy mit zufaelliger Zuordnung: Antippen waehlt die richtige Regeloption."""
    ctx = dict(viewport={"width": 390, "height": 844}, has_touch=True, is_mobile=True, device_scale_factor=2)
    p, f = neue_seite(b, srv.url + "?seed=21", ctx_args=ctx)
    d = H.Spiel(p, touch=True, schnell=True)
    d.start()
    ep, fehl, n_tausch = "1", [], 0
    for i, letter in enumerate(["B", "A", "B", "B", "A", "A"]):
        z = zustand(p)
        regel = R.anzeige_zu_regel(z["tausch"][ep], letter)
        n_tausch += z["tausch"][ep]
        label_k = p.inner_text('section[aria-label="Option %s"] .name' % letter).strip()
        if label_k != EPS[ep]["optionen"][regel]["label"]: fehl.append("Karte %s Ep %s" % (letter, ep))
        d.waehle_anzeige(letter)
        z = zustand(p)
        if not (z["wahl"] == regel and z["wahlAnz"] == letter): fehl.append("Wahl Ep %s" % ep)
        d.wurf_physisch(max(1, min(20, EPS[ep]["optionen"][regel]["soll"] + 1)))
        d.zu_folgen(); d.zu_werten()
        if p.evaluate("document.documentElement.scrollWidth - window.innerWidth") > 0: fehl.append("horizontaler Scroll Ep %s" % ep)
        nxt = R.WEITER.get((ep, regel))
        if nxt is None: break
        d.weiter(); ep = nxt
    E.pruefe("Phone 390x844 Touch: 6 Episoden mit zufaelliger Zuordnung (%d vertauscht), Karte, Wahl, kein horizontaler Scroll" % n_tausch, "Phone", not fehl, "; ".join(fehl[:3]))
    E.pruefe("Konsole/Anfragen ohne Fehler (Phone A/B)", "Phone", not f.liste, str(f.liste[:2]))
    p.close()


def main():
    srv = H.Server()
    with sync_playwright() as pw:
        b = pw.chromium.launch()
        for fn in (t_statistik, t_modi, t_zuordnung, t_sichtbarkeit_abschluss, t_undo, t_neuladen, t_mikro, t_phone):
            try:
                fn(b, srv)
            except Exception as ex:
                import traceback
                traceback.print_exc()
                E.pruefe("Test %s abgebrochen" % fn.__name__, "-", False, repr(ex)[:200])
        b.close()
    srv.stop()
    E.speichern(os.path.join(HIER, "ergebnis_ab.md"))
    print("Pruefungen:", len(E.zeilen), "Fehler:", len(E.fehler))
    return 1 if E.fehler else 0


if __name__ == "__main__":
    sys.exit(main())
