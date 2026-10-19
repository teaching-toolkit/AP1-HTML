"""Prüft die rechnende Logik der Seite gegen unabhängige Referenzen in Python:
- Zuteilung (2 oder 3 von 5 Befunden in Fassung A): 1000 Simulationen mit crypto.getRandomValues, 1000 mit Seed,
  dazu 100000 Läufe für die Gleichverteilung über alle 20 möglichen Muster
- Ergebnis-Code (Format v2): Erzeugen/Lesen gegen Python-Implementierung, Fehlererkennung, v1-Code abgelehnt
- Gruppenauswertung gegen Python-Nachrechnung

Aufruf:  python3 -I tests/test_logik.py
"""
import sys
sys.dont_write_bytecode = True
import importlib.util
import itertools
import math
import random
from pathlib import Path

spec = importlib.util.spec_from_file_location("common", Path(__file__).with_name("common.py"))
C = importlib.util.module_from_spec(spec)
spec.loader.exec_module(C)

from playwright.sync_api import sync_playwright
from scipy import stats

ergebnisse = []
N = C.N


def check(name, ok, detail=""):
    ergebnisse.append((name, ok, detail))
    print(("OK    " if ok else "FEHLER"), name, ("- " + detail) if detail else "")


httpd, url = C.start_server()
random.seed(20261015)

with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page()
    wacht = C.Fehlerwaechter(pg)
    pg.goto(url)

    # ------------------------------------------------------------ Zuteilung
    SIM = 1000
    crypto = pg.evaluate("(n) => { const r = P3.cryptoRng(); const o = []; for (let i = 0; i < n; i++) o.push(P3.zuteilung(r).join('')); return o; }", SIM)
    seeded = pg.evaluate("(n) => { const o = []; for (let i = 0; i < n; i++) o.push(P3.zuteilung(P3.seededRng('sim' + i)).join('')); return o; }", SIM)

    # exakte Erwartung für die Paare: P(A_i und A_j) = 0.5 * (2*1)/(5*4) + 0.5 * (3*2)/(5*4) = 0.2
    pe = 0.5 * (2 * 1) / (5 * 4) + 0.5 * (3 * 2) / (5 * 4)
    check("Erwartungswert für Paare: P(A_i und A_j) = %.3f (= 4/20)" % pe, abs(pe - 0.2) < 1e-12)

    for name, sims in (("crypto.getRandomValues", crypto), ("Seed sim0..sim999", seeded)):
        ks = [s.count("A") for s in sims]
        check("[%s] jede Zuteilung hat 2 oder 3 Mal A bei 5 Befunden (%d von %d)" % (name, sum(1 for k in ks if k in (2, 3)), SIM),
              all(k in (2, 3) and len(s) == N and set(s) <= {"A", "B"} for k, s in zip(ks, sims)))
        k2 = ks.count(2)
        pk = stats.binomtest(k2, SIM, 0.5).pvalue
        check("[%s] Anzahl A: 2 mal %d, 3 mal %d (erwartet je 50 %%, p=%.3f)" % (name, k2, SIM - k2, pk), pk > 1e-4)
        freq = [sum(1 for s in sims if s[i] == "A") for i in range(N)]
        pm = [stats.binomtest(f, SIM, 0.5).pvalue for f in freq]
        check("[%s] Häufigkeit A pro Befund 1..5: %s (erwartet 500, kleinstes p=%.3f)" % (name, freq, min(pm)),
              min(pm) > 1e-4 / N)
        pp = []
        for i, j in itertools.combinations(range(N), 2):
            c = sum(1 for s in sims if s[i] == "A" and s[j] == "A")
            pp.append(stats.binomtest(c, SIM, pe).pvalue)
        check("[%s] Paarhäufigkeiten (10 Paare, erwartet %.2f) unauffällig, kleinstes p=%.4f" % (name, pe, min(pp)),
              min(pp) > 1e-4 / 10)

    # Negativkontrolle: ein absichtlich verzerrter Zuteiler (A immer in einem zusammenhängenden Block, nur
    # zyklisch verschoben) muss vom Paar-Test durchfallen, sonst hätte der Test keine Aussagekraft.
    schlecht = pg.evaluate("""(n) => { const r = P3.cryptoRng(); const o = [];
      for (let i = 0; i < n; i++) { const k = r() < 0.5 ? 2 : 3; const s = Math.floor(r() * 5);
        const z = Array(5).fill('B'); for (let j = 0; j < k; j++) z[(s + j) % 5] = 'A'; o.push(z.join('')); } return o; }""", SIM)
    pp_s = min(stats.binomtest(sum(1 for s_ in schlecht if s_[i] == "A" and s_[j] == "A"), SIM, pe).pvalue
               for i, j in itertools.combinations(range(N), 2))
    check("Negativkontrolle: verzerrter Zuteiler fällt beim Paar-Test durch (kleinstes p=%.2g)" % pp_s, pp_s < 1e-4 / 10)

    # Reproduzierbarkeit
    a1 = pg.evaluate("P3.zuteilung(P3.seededRng('x')).join('')")
    a2 = pg.evaluate("P3.zuteilung(P3.seededRng('x')).join('')")
    a3 = pg.evaluate("P3.zuteilung(P3.seededRng('y')).join('')")
    check("Gleicher Seed gibt gleiche Zuteilung, anderer Seed (hier) eine andere", a1 == a2 and a1 != a3, "%s %s %s" % (a1, a2, a3))
    check("Zuteilungen der 1000 crypto-Läufe sind nicht alle gleich (%d verschiedene Muster, möglich 20)" % len(set(crypto)), len(set(crypto)) == 20)

    # Grosse Läufe: alle 20 Muster gleich wahrscheinlich
    gross = pg.evaluate("""(n) => { const r = P3.cryptoRng(); const d = {}; for (let i = 0; i < n; i++) { const s = P3.zuteilung(r).join(''); d[s] = (d[s] || 0) + 1; } return d; }""", 100000)
    muster = ["".join(m) for k in (2, 3) for m in set(itertools.permutations("A" * k + "B" * (N - k)))]
    check("Es gibt genau 20 mögliche Muster (10 mit 2 A, 10 mit 3 A)", len(muster) == 20)
    beob = [gross.get(m, 0) for m in muster]
    fremd = set(gross) - set(muster)
    chi = stats.chisquare(beob)
    check("100000 Läufe: nur gültige Muster (fremde: %d), Gleichverteilung über 20 Muster (chi2=%.1f, p=%.3f, min=%d, max=%d, erwartet %.0f)"
          % (len(fremd), chi.statistic, chi.pvalue, min(beob), max(beob), 100000 / 20),
          not fremd and chi.pvalue > 1e-4)
    # Anteil A pro Befund im grossen Lauf
    fa = [sum(c for m, c in gross.items() if m[i] == "A") / 100000 for i in range(N)]
    check("100000 Läufe: Anteil Version A pro Befund 1..5: %s (erwartet 0.500)" % ", ".join("%.3f" % x for x in fa),
          all(abs(x - 0.5) < 0.01 for x in fa))

    # ------------------------------------------------------------ Ergebnis-Code
    abw_enc = abw_dec = 0
    for _ in range(500):
        zu = [random.choice("AB") for _ in range(N)]
        werte = [random.choice([None, 1, 2, 3, 4, 5]) if random.random() < 0.3 else random.randint(1, 5) for _ in range(N)]
        nonce = "".join(random.choice(C.ALPHA) for _ in range(3))
        py = C.py_encode(zu, werte, nonce)
        js = pg.evaluate("([z, w, k]) => P3.codeErzeugen(z, w, k)", [zu, werte, nonce])
        if py != js:
            abw_enc += 1
        r = pg.evaluate("(c) => P3.codeLesen(c)", py)
        exp = C.py_decode(py)
        got = [None if e is None else (e["v"], e["w"]) for e in r["eintraege"]] if r["ok"] else None
        if got != exp:
            abw_dec += 1
    check("500 zufällige Codes (v2, 5 Befunde): Erzeugen in JS == Python (Abweichungen: %d)" % abw_enc, abw_enc == 0)
    check("500 zufällige Codes (v2, 5 Befunde): Lesen in JS == Python (Abweichungen: %d)" % abw_dec, abw_dec == 0)

    # Rundreise: alle 2 * 5 * 5^... Einzelwerte: jede Kombination Version/Bewertung eines Befunds kommt unverändert zurück
    alle_ok = True
    for pos in range(N):
        for v in "AB":
            for w in range(1, 6):
                zu = ["A"] * N; werte = [3] * N
                zu[pos] = v; werte[pos] = w
                code = pg.evaluate("([z, wt, k]) => P3.codeErzeugen(z, wt, k)", [zu, werte, "k7q"])
                r = pg.evaluate("(c) => P3.codeLesen(c)", code)
                if not r["ok"] or r["eintraege"][pos] != {"v": v, "w": w}:
                    alle_ok = False
    check("Code-Rundreise: alle 50 Kombinationen Befund x Version x Bewertung kommen unverändert zurück", alle_ok)

    # Fehlererkennung: jede Einzelzeichen-Ersetzung muss erkannt werden
    nicht_erkannt = 0
    gesamt = 0
    for _ in range(60):
        zu = [random.choice("AB") for _ in range(N)]
        werte = [random.randint(1, 5) for _ in range(N)]
        code = C.py_encode(zu, werte, "".join(random.choice(C.ALPHA) for _ in range(3)))
        kopf, payload = code.split(".")
        for pos in range(9):
            for alt in C.ALPHA:
                if alt == payload[pos]:
                    continue
                mut = kopf + "." + payload[:pos] + alt + payload[pos + 1:]
                gesamt += 1
                if pg.evaluate("(c) => P3.codeLesen(c).ok", mut):
                    nicht_erkannt += 1
    check("Einzelzeichen-Tippfehler werden erkannt: %d von %d Ersetzungen nicht erkannt" % (nicht_erkannt, gesamt), nicht_erkannt == 0)

    # Vertauschen benachbarter Zeichen (nur informativ, Prüfzeichen ist keine volle Garantie)
    tauschen_gesamt = tauschen_nicht = 0
    for _ in range(200):
        zu = [random.choice("AB") for _ in range(N)]
        werte = [random.randint(1, 5) for _ in range(N)]
        code = C.py_encode(zu, werte, "".join(random.choice(C.ALPHA) for _ in range(3)))
        kopf, payload = code.split(".")
        for pos in range(8):
            if payload[pos] == payload[pos + 1]:
                continue
            mut = kopf + "." + payload[:pos] + payload[pos + 1] + payload[pos] + payload[pos + 2:]
            tauschen_gesamt += 1
            if pg.evaluate("(c) => P3.codeLesen(c).ok", mut):
                tauschen_nicht += 1
    print("INFO  Vertauschte Nachbarzeichen: %d von %d nicht erkannt (%.1f %%)" % (tauschen_nicht, tauschen_gesamt, 100 * tauschen_nicht / tauschen_gesamt))

    # Grenzfälle der Syntax
    gut = C.py_encode(list("ABABA"), [1, 2, 3, 4, 5], "abc")
    alt_v1 = "HSLU-hindsight-v1.139572570kg07"          # Beispielcode der früheren Seitenversion (9 Befunde)
    faelle = {
        "gültig": (gut, True),
        "Grossbuchstaben im Code": (gut.upper(), True),
        "mit Leerzeichen und Tab ringsum": ("  " + gut + "\t", True),
        "unsichtbares Leerzeichen (U+200B) am Ende, wie beim Kopieren aus Chats": (gut + chr(0x200B), True),
        "Byte-Order-Mark (U+FEFF) am Anfang": (chr(0xFEFF) + gut, True),
        "Kennung falsch": (gut.replace("HSLU", "XXXX"), False),
        "Version v3": (gut.replace("v2", "v3"), False),
        "alter v1-Code (9 Befunde)": (alt_v1, False),
        "neuer Code mit Kennung v1": (gut.replace("v2", "v1"), False),
        "leer": ("", False),
        "nur Kennung": ("HSLU-hindsight-v2.", False),
        "zu kurz": (gut[:-1], False),
        "zu lang": (gut + "0", False),
        "Sonderzeichen": (gut[:-3] + "!!!", False),
        "Leerzeichen im Code": (gut[:20] + " " + gut[20:], False),
        "Buchstabe im Datenteil": (gut.replace(".", ".q", 1)[:-1], False),
    }
    bad = []
    for name, (code, soll) in faelle.items():
        ist = pg.evaluate("(c) => P3.codeLesen(c).ok", code)
        if ist != soll:
            bad.append(name)
    check("Syntax-Grenzfälle des Codes (%d Fälle, darunter alter v1-Code)" % len(faelle), not bad, ", ".join(bad))
    r = pg.evaluate("(c) => P3.codeLesen(c)", alt_v1)
    check("Alter v1-Code wird mit klarem Grund abgelehnt: «%s»" % r["grund"],
          (not r["ok"]) and r.get("alt") is True and "v1" in r["grund"] and "nicht ausgewertet" in r["grund"])
    r = pg.evaluate("(c) => P3.codeLesen(c)", gut.replace("v2", "v3"))
    check("Ungültigkeitsgrund wird genannt: «%s»" % r["grund"], "v3" in r["grund"])

    # ------------------------------------------------------------ Gruppenauswertung
    abw_gr = []
    for t in range(80):
        n_pers = random.randint(0, 8)
        zeilen = []
        for _ in range(n_pers):
            zu = random.choice(muster)
            werte = [random.randint(1, 5) if random.random() > (0.4 if random.random() < 0.3 else 0.0) else None for _ in range(N)]
            zeilen.append(C.py_encode(list(zu), werte, "".join(random.choice(C.ALPHA) for _ in range(3))))
        extra = []
        if zeilen and random.random() < 0.6:
            extra.append(random.choice(zeilen))           # Duplikat
        if random.random() < 0.6:
            extra.append("HSLU-hindsight-v2.kaputt")      # ungültig
        if random.random() < 0.4:
            extra.append("irgendein Text")                # ungültig
        if random.random() < 0.5:
            extra.append(alt_v1)                          # alter v1-Code
        alle = zeilen + extra
        random.shuffle(alle)
        mit_leer = []
        for z in alle:
            mit_leer.append(z)
            if random.random() < 0.3:
                mit_leer.append("   ")
        text = random.choice(["\n", "\r\n"]).join(mit_leer)
        js = pg.evaluate("(t) => { const r = P3.auswerten(t); return { personen: r.personen.length, ungueltig: r.ungueltig.length, alte: r.alte, duplikate: r.duplikate, unvoll: r.unvollstaendig.length, pro: r.pro, gesamt: r.gesamt }; }", text)
        py = C.py_gruppe(mit_leer)
        if (js["personen"], js["ungueltig"], js["duplikate"], js["unvoll"], js["alte"]) != (py["personen"], py["ungueltig"], py["duplikate"], py["unvollstaendig"], py["alte"]):
            abw_gr.append("Lauf %d Zähler: %s vs %s" % (t, (js["personen"], js["ungueltig"], js["duplikate"], js["unvoll"], js["alte"]), py))
            continue
        for i in range(N):
            for v in "AB":
                w = py["pro"][i][v]
                o = js["pro"][i][v]
                mw_ok = (o["mittel"] is None and not w) or (w and abs(o["mittel"] - sum(w) / len(w)) < 1e-12)
                if o["n"] != len(w) or not mw_ok:
                    abw_gr.append("Lauf %d Befund %d %s" % (t, i + 1, v))
        for v in "AB":
            w = py["gesamt"][v]
            o = js["gesamt"][v]
            if o["n"] != len(w) or (w and abs(o["mittel"] - sum(w) / len(w)) > 1e-12):
                abw_gr.append("Lauf %d Gesamt %s" % (t, v))
    check("80 zufällige Gruppen (0 bis 8 Personen, Duplikate, ungültige Zeilen, alte v1-Codes, Leerzeilen, unvollständige Personen): "
          "JS == Python für Zähler, n und Mittelwerte; Abweichungen: %d" % len(abw_gr), not abw_gr, "; ".join(abw_gr[:5]))

    check("Keine Konsolenfehler, keine externen oder fehlgeschlagenen Anfragen", not wacht.fehler, "; ".join(wacht.fehler))
    b.close()

httpd.shutdown()
fehler = [e for e in ergebnisse if not e[1]]
print("\n%d Prüfungen, %d bestanden, %d fehlgeschlagen" % (len(ergebnisse), len(ergebnisse) - len(fehler), len(fehler)))
sys.exit(1 if fehler else 0)
