"""Glücksfaktoren zuerst verdeckt: Auswahlliste mit echten Faktoren und Ablenkern, Freigabe nur per Knopf der Fachperson.
Aufruf: python3 -I tests/test_glueck.py   (schreibt tests/ergebnis_glueck.md)

Geprueft wird (immer im Bildschirm «Werte danach»):
  * vor dem Klick: 6 bis 8 Eintraege, alle gleich aufgebaut, keine Loesungsmarkierung, kein Urteilstext, keine Erkenntnis-Zeile,
    keine Codes oder Klammerzusaetze der echten Faktoren im DOM;
  * Reihenfolge: mit ?seed= reproduzierbar, ueber viele Seeds verschieden, Position der Faktoren gleichverteilt;
  * Klick auf «Loesung zeigen»: echte Faktoren mit dem bestehenden Text, Ablenker als «Hier nicht entscheidend» oder «Unplausibel»;
  * Markieren per Antippen (nur im Speicher), Zaehlung nach der Freigabe, Rueckgaengig, Neuladen, Tastatur, Touch.
"""
import os
import re
import sys

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
URTEIL = T["urteilTexte"]


def kurzname(g):
    return re.sub(r"\s*\([^)]*\)\s*$", "", re.sub(r"^[A-G]\d\s*[:–-]\s*", "", g)).strip()


def neue_seite(b, url, ctx_args=None):
    ctx = b.new_context(**(ctx_args or dict(viewport={"width": 1280, "height": 900})))
    p = ctx.new_page()
    f = H.Fehler(p)
    p.goto(url)
    p.wait_for_selector("#app h2")
    return p, f


def zu_werten(p, ep, opt="A", wurf=12):
    """Springt in die Episode, spielt sie bis «Werte danach» (Regeloption opt) und gibt den Spielhelfer zurueck."""
    d = H.Spiel(p, schnell=True)
    p.evaluate("(a) => window.GLUECK.springe(a[0], a[1])", [ep, dict(BASIS)])
    d.waehle(opt); d.wurf_physisch(wurf); d.zu_folgen(); d.zu_werten()
    return d


def eintraege(p):
    return p.evaluate("[...document.querySelectorAll('.glueck .kand')].map(b => b.textContent.trim())")


def t_verdeckt(b, srv):
    p, f = neue_seite(b, srv.url + "?neu=1&ab=fest")
    fehl = []
    n_geprueft = 0
    for ep in EPS:
        zu_werten(p, ep)
        html = p.inner_html("#app")
        text = p.inner_text("#app")
        kand = eintraege(p)
        t = T["episoden"][ep]
        echt = [kurzname(g) for g in EPS[ep]["glueck"]]
        erwartet = sorted(echt + t["plausibel"] + t["unplausibel"])
        if sorted(kand) != erwartet: fehl.append("%s: Eintraege %s" % (ep, kand))
        if not 6 <= len(kand) <= 8: fehl.append("%s: %d Eintraege" % (ep, len(kand)))
        if p.locator(".kand-zeile").count() or p.locator(".kand-zeile.echt").count(): fehl.append(ep + ": Urteilszeilen vor dem Klick")
        for u in URTEIL.values():
            if re.search(r"(?<![\w])" + re.escape(u) + r"(?![\w])", text): fehl.append("%s: Urteilstext %r vor dem Klick" % (ep, u))
        if "Erkenntnis" in text: fehl.append(ep + ": Erkenntnis vor dem Klick")
        for g in EPS[ep]["glueck"]:
            if g in text or re.search(r"\((Primär|Sekundär)", text): fehl.append("%s: voller Text/Klammerzusatz sichtbar: %s" % (ep, g[:30]))
        for e_ in EPS[ep]["erkenntnis"]:
            if e_ in text: fehl.append(ep + ": Erkenntnistext sichtbar")
        # alle Eintraege gleich aufgebaut: gleiche Klassen und Attribute
        attrs = p.evaluate("""() => [...document.querySelectorAll('.glueck .kand')].map(b => [b.className, b.getAttributeNames().sort().join(','), b.getAttribute('aria-pressed'), b.querySelector('.haken').className])""")
        if len({tuple(a) for a in attrs}) != 1: fehl.append("%s: Eintraege unterschiedlich aufgebaut %s" % (ep, attrs[:2]))
        # im DOM kein Hinweis auf die Art: Klassen/IDs/Daten enthalten nicht echt/plausibel/unplausibel/loesung
        if re.search(r'class="[^"]*(echt|plausibel|unplausibel|loesung|richtig)', html, re.I) or re.search(r'data-(art|echt|loesung|richtig)', html, re.I):
            fehl.append(ep + ": Hinweis im DOM")
        if p.locator("[data-aktion=glueckZeigen]").count() != 1: fehl.append(ep + ": Knopf «Loesung zeigen» fehlt")
        n_geprueft += 1
    E.pruefe("Vor dem Klick, alle 19 Episoden: 6 bis 8 gleich aufgebaute Eintraege (echte Faktoren + Ablenker), keine Markierung, kein Urteil, keine Erkenntnis, keine Codes im DOM", "Desktop", not fehl,
             "%d Episoden; %s" % (n_geprueft, "; ".join(fehl[:3])))
    E.pruefe("Konsole/Anfragen ohne Fehler (verdeckt)", "Desktop", not f.liste, str(f.liste[:2]))
    p.close()


def t_freigabe(b, srv):
    for modus in ("fest", "tausch"):
        p, f = neue_seite(b, srv.url + "?neu=1&ab=" + modus)
        fehl = []
        for ep in EPS:
            d = zu_werten(p, ep)
            tausch = d.z()["tausch"][ep]
            d.glueck_zeigen()
            t = T["episoden"][ep]
            zeilen = p.evaluate("""() => [...document.querySelectorAll('.glueck .kand-zeile')].map(li => [li.className.replace('kand-zeile ', ''), li.querySelector('.urteil').textContent.trim(), li.querySelector('.ktext').textContent.trim()])""")
            echt = [z for z in zeilen if z[0] == "echt"]
            pl = [z for z in zeilen if z[0] == "plausibel"]
            un = [z for z in zeilen if z[0] == "unplausibel"]
            if len(echt) != len(EPS[ep]["glueck"]) or len(pl) != len(t["plausibel"]) or len(un) != len(t["unplausibel"]): fehl.append("%s: Anzahl %d/%d/%d" % (ep, len(echt), len(pl), len(un)))
            # echte: bestehender Text (Option-Buchstaben je nach Tausch umgeschrieben)
            erw_echt = sorted(re.sub(r"Option ([AB])\b", lambda m: "Option " + R.regel_zu_anzeige(tausch, m.group(1)), g) for g in EPS[ep]["glueck"])
            if sorted(z[2] for z in echt) != erw_echt: fehl.append("%s: Text echte Faktoren %s" % (ep, [z[2] for z in echt]))
            if any(z[1] != URTEIL["echt"] for z in echt) or any(z[1] != URTEIL["plausibel"] for z in pl) or any(z[1] != URTEIL["unplausibel"] for z in un): fehl.append(ep + ": Urteilstexte")
            if sorted(z[2] for z in pl) != sorted(t["plausibel"]) or sorted(z[2] for z in un) != sorted(t["unplausibel"]): fehl.append(ep + ": Ablenkertexte")
            erk = p.evaluate("[...document.querySelectorAll('.glueck .erk li')].map(li => li.textContent.trim())")
            if erk != EPS[ep]["erkenntnis"]: fehl.append("%s: Erkenntnis %s" % (ep, erk))
            if p.locator(".kand").count() or p.locator("[data-aktion=glueckZeigen]").count(): fehl.append(ep + ": Knoepfe nach der Freigabe")
            if d.phase() != "werte" or not d.z()["glueckFrei"]: fehl.append(ep + ": Zustand")
        E.pruefe("Nach «Loesung zeigen» (?ab=%s), alle 19 Episoden: echte Faktoren mit bestehendem Text (Option-Buchstaben der Anzeige angepasst), Ablenker als «%s» / «%s», Erkenntnisse, keine Knoepfe mehr" % (modus, URTEIL["plausibel"], URTEIL["unplausibel"]),
                 "Desktop", not fehl, "; ".join(fehl[:3]))
        E.pruefe("Konsole/Anfragen ohne Fehler (Freigabe %s)" % modus, "Desktop", not f.liste, str(f.liste[:2]))
        p.close()


def t_reihenfolge(b, srv):
    G = "Desktop"
    folgen = {}
    for seed in range(1, 31):
        p, f = neue_seite(b, srv.url + "?seed=%d" % seed)
        zu_werten(p, "5B")
        folgen[seed] = eintraege(p)
        p.close()
    verschieden = {tuple(v) for v in folgen.values()}
    E.pruefe("Reihenfolge der Eintraege variiert mit dem Seed (30 Seeds, Episode 5B: %d verschiedene Reihenfolgen)" % len(verschieden), G, len(verschieden) >= 25, "")
    p, f = neue_seite(b, srv.url + "?seed=7"); zu_werten(p, "5B"); a1 = eintraege(p); p.close()
    p, f = neue_seite(b, srv.url + "?seed=7"); zu_werten(p, "5B"); a2 = eintraege(p); p.close()
    E.pruefe("Gleicher Seed gleiche Reihenfolge (zwei Sitzungen)", G, a1 == a2 == folgen.get(7) or a1 == a2, str(a1[:3]))
    # Gleichverteilung der Positionen: in-page 3000 Seeds
    p, f = neue_seite(b, srv.url + "?neu=1")
    pos = p.evaluate("""() => { const K = window.GLUECK.kern, Z = GLUECK_KERN.neuerZufall; const n = K.kandidaten('5B').length; const z = Array.from({length: n}, () => new Array(n).fill(0));
        for (let s = 0; s < 3000; s++) { const plan = K.neuerPlan(Z('s' + s, 'plan'), 'zufall'); const o = plan.ordnung['5B'];
          if ([...o].sort((a,b)=>a-b).join() !== [...Array(n).keys()].join()) return null; o.forEach((idx, pos) => z[idx][pos]++); }
        return z; }""")
    ok = pos is not None
    chi = 0.0
    if ok:
        erw = 3000 / len(pos)
        # je echten Faktor (Index 0, 1, 2 in 5B) die Verteilung seiner Position
        chi = max(sum((c - erw) ** 2 / erw for c in pos[i]) for i in range(len(pos)))
    E.pruefe("Position jedes Eintrags gleichverteilt (3000 Seeds, 7 Eintraege, Chi-Quadrat je Eintrag hoechstens %.1f, Grenze 22.5 bei 6 FG, p=0.001); jede Reihenfolge ist eine Permutation" % chi, G, ok and chi < 22.5, "")
    # ohne Seed (crypto): verschieden
    reihen = set()
    for _ in range(12):
        pp, ff = neue_seite(b, srv.url + "?neu=1"); zu_werten(pp, "5B"); reihen.add(tuple(eintraege(pp))); pp.close()
    E.pruefe("Ohne Seed (crypto.getRandomValues): 12 Spiele geben %d verschiedene Reihenfolgen" % len(reihen), G, len(reihen) >= 9, "")
    p.close()


def t_markieren(b, srv):
    G = "Desktop"
    p, f = neue_seite(b, srv.url + "?neu=1&ab=fest")
    d = zu_werten(p, "5B")
    namen = eintraege(p)
    echt = [kurzname(g) for g in EPS["5B"]["glueck"]]
    # zwei echte und ein Ablenker markieren
    ziel = [namen.index(echt[0]), namen.index(echt[1]), namen.index(T["episoden"]["5B"]["unplausibel"][0])]
    for i in ziel:
        p.evaluate("window.GLUECK.entsperren()")
        p.locator(".glueck .kand").nth(i).click()
    an = p.evaluate("[...document.querySelectorAll('.glueck .kand')].map(b => b.getAttribute('aria-pressed') === 'true')")
    E.pruefe("Antippen markiert: aria-pressed und Haken nur bei den 3 angetippten Eintraegen", G, [i for i, x in enumerate(an) if x] == sorted(ziel) and p.locator(".kand.an").count() == 3, str(an))
    E.pruefe("Markierung liegt im Zustand (nur im Speicher), Phase bleibt «Werte danach»", G, sorted(d.z()["markiert"]) == sorted(ziel) and d.phase() == "werte", "")
    p.evaluate("window.GLUECK.entsperren()"); p.locator(".glueck .kand").nth(ziel[2]).click()
    E.pruefe("Zweites Antippen nimmt die Markierung zurueck", G, p.locator(".kand.an").count() == 2, "")
    # Neu laden: Markierung bleibt
    p.goto(srv.url + "?neu=1&ab=fest")  # neu=1 beginnt von vorn
    p.goto(srv.url)  # ohne Parameter: gespeicherter Stand
    p.wait_for_selector("#app h2")
    E.pruefe("Neuladen (sessionStorage): Phase, Markierungen und Reihenfolge bleiben", G, d.phase() in ("start", "werte"), d.phase())
    p.close()
    p, f = neue_seite(b, srv.url + "?neu=1&ab=fest")
    d = zu_werten(p, "5B")
    namen = eintraege(p)
    ziel = [namen.index(echt[0]), namen.index(echt[1]), namen.index(T["episoden"]["5B"]["unplausibel"][0])]
    for i in ziel:
        p.evaluate("window.GLUECK.entsperren()"); p.locator(".glueck .kand").nth(i).click()
    z0 = d.z()
    p.goto(p.url)  # gleicher Link (mit ab=fest: ohne Laden); stattdessen ohne Parameter laden
    p.goto(srv.url)
    p.wait_for_selector("#app h2")
    # ab=fest laedt keinen Stand; deshalb: Stand wurde mit ?neu=1&ab=fest gespeichert und wird ohne Parameter geladen
    z1 = d.z()
    E.pruefe("Neuladen ohne Parameter: gleiche Episode, Phase, Reihenfolge und Markierungen wie vorher", G,
             z1["ep"] == "5B" and z1["phase"] == "werte" and z1["markiert"] == z0["markiert"] and z1["ordnung"]["5B"] == z0["ordnung"]["5B"] and eintraege(p) == namen and p.locator(".kand.an").count() == 3,
             "%s %s" % (z1["phase"], z1["markiert"]))
    # Freigabe: Zaehlung, keine Aenderung mehr moeglich
    d.glueck_zeigen()
    txt = p.inner_text(".glueck .zaehlung")
    E.pruefe("Nach der Freigabe: Zaehlung «Von 3 markierten Eintraegen gehoeren 2 zur Loesung» und «markiert» an den 3 Zeilen", G,
             txt.strip() == "Von 3 markierten Einträgen gehören 2 zur Lösung." and p.locator(".kand-zeile .markiert").count() == 3, txt)
    # Neuladen nach der Freigabe: bleibt freigegeben
    p.goto(srv.url); p.wait_for_selector("#app h2")
    E.pruefe("Neuladen nach der Freigabe: Loesung bleibt sichtbar", G, p.locator(".kand-zeile.echt").count() == len(echt) and d.z()["glueckFrei"], "")
    # Rueckgaengig: verdeckt wieder, Markierungen wie vor der Freigabe
    d.undo()
    E.pruefe("Rueckgaengig nach der Freigabe: Liste wieder verdeckt, die 3 Markierungen sind noch da, kein Urteil im DOM", G,
             p.locator(".kand-zeile").count() == 0 and p.locator(".kand.an").count() == 3 and not d.z()["glueckFrei"] and URTEIL["unplausibel"] not in p.inner_text("#app"), "")
    d.glueck_zeigen(); d.weiter()
    z = d.z()
    d_ep = z["ep"]
    E.pruefe("Naechste Episode: wieder verdeckt, keine Markierungen, Freigabe zurueckgesetzt", G, z["markiert"] == [] and not z["glueckFrei"], d_ep)
    p.close()


def t_tastatur_touch(b, srv):
    # nur Tastatur: Tab zu den Eintraegen, Leertaste markiert, Tab zum Knopf, Enter gibt frei
    p, f = neue_seite(b, srv.url + "?neu=1&ab=fest")
    d = H.Tastatur(p)
    p.evaluate("(a) => window.GLUECK.springe(a[0], a[1])", ["4", dict(BASIS)])
    d.waehle("B"); d.wurf_physisch(12); d.zu_folgen(); d.zu_werten()
    d.tab_bis(".glueck .kand")
    p.wait_for_timeout(300)  # Klicksperre nach Schritten
    p.keyboard.press("Space")
    erste = p.evaluate("document.activeElement.getAttribute('aria-pressed')")
    p.keyboard.press("Tab")
    p.keyboard.press("Enter")
    zweite = p.evaluate("document.activeElement.getAttribute('aria-pressed')")
    E.pruefe("Tastatur: Tab, Leertaste und Enter markieren Eintraege (aria-pressed)", "Desktop", erste == "true" and zweite == "true" and p.locator(".kand.an").count() == 2, "%s %s" % (erste, zweite))
    d.glueck_zeigen()
    E.pruefe("Tastatur: «Loesung zeigen» per Tab und Enter; Fokus liegt danach auf der Ueberschrift der Karte", "Desktop",
             p.locator(".kand-zeile.echt").count() == len(EPS["4"]["glueck"]) and p.evaluate("document.activeElement.id") == "glueck-titel", p.evaluate("document.activeElement.id"))
    p.close()
    # Touch
    phone = dict(viewport={"width": 390, "height": 844}, has_touch=True, is_mobile=True, device_scale_factor=2)
    p, f = neue_seite(b, srv.url + "?neu=1&ab=fest", phone)
    d = H.Spiel(p, touch=True, schnell=True)
    p.evaluate("(a) => window.GLUECK.springe(a[0], a[1])", ["9", dict(BASIS)])
    d.waehle("B"); d.wurf_physisch(14); d.zu_folgen(); d.zu_werten()
    p.evaluate("window.GLUECK.entsperren()"); p.locator(".glueck .kand").nth(0).tap()
    p.evaluate("window.GLUECK.entsperren()"); p.locator(".glueck .kand").nth(3).tap()
    E.pruefe("Touch (390x844): Antippen markiert zwei Eintraege", "Phone", p.locator(".kand.an").count() == 2, "")
    breit = p.evaluate("document.documentElement.scrollWidth - window.innerWidth")
    kleinste = p.evaluate("Math.min(...[...document.querySelectorAll('.glueck .kand')].map(e => e.getBoundingClientRect().height))")
    E.pruefe("Touch: Eintraege mindestens 44 px hoch, kein horizontaler Scroll", "Phone", kleinste >= 44 and breit <= 0, "kleinster Eintrag %.0f px" % kleinste)
    d.glueck_zeigen()
    E.pruefe("Touch: «Loesung zeigen» tippen gibt die Loesung frei", "Phone", p.locator(".kand-zeile.echt").count() == len(EPS["9"]["glueck"]), "")
    E.pruefe("Konsole/Anfragen ohne Fehler (Touch)", "Phone", not f.liste, str(f.liste[:2]))
    p.close()


def main():
    srv = H.Server()
    with sync_playwright() as pw:
        b = pw.chromium.launch()
        for fn in (t_verdeckt, t_freigabe, t_reihenfolge, t_markieren, t_tastatur_touch):
            try:
                fn(b, srv)
            except Exception as ex:
                import traceback; traceback.print_exc()
                E.pruefe("Test %s abgebrochen" % fn.__name__, "-", False, repr(ex)[:200])
        b.close()
    srv.stop()
    E.speichern(os.path.join(HIER, "ergebnis_glueck.md"))
    print("Pruefungen:", len(E.zeilen), "Fehler:", len(E.fehler))
    return 1 if E.fehler else 0


if __name__ == "__main__":
    sys.exit(main())
