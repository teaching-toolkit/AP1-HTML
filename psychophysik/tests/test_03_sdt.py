"""Signalentdeckung (signalentdeckung.html): Rechnung, Reizgenerator, Zeitplan, Ergebnis-Code, Gruppenwerte.

- qnorm/pnorm gegen scipy
- computeSDT gegen unabhängige Python-Rechnung (Raster, Zufallszählwerte, Kantenfälle H=0, H=1, FA=0, FA=1)
- simulierte Beobachter mit bekanntem d' und c (grosse und kleine Stichproben)
- Reizbild: Pixelstatistik, Fleck, Matched-Filter-d'
- Zeitplan: genau die Hälfte Signal
- Code (Version v2): Rundreise, Prüfsumme, ungültige Eingaben, alte v1-Codes werden mit klarer Meldung abgelehnt; Gruppenauswertung gegen Python
Start: python3 -I tests/test_03_sdt.py
"""
import itertools
import math
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from scipy import stats as sst
from scipy.stats import norm
from playwright.sync_api import sync_playwright

import _helpers as H

C = H.Checker("Signalentdeckung (Rechnung und Generatoren)")


def sdt_ref(h, m, fa, cr):
    nS, nN = h + m, fa + cr
    if nS <= 0 or nN <= 0:
        return None
    Hh, Ff, corr = h / nS, fa / nN, False
    if Hh in (0.0, 1.0) or Ff in (0.0, 1.0):
        Hh, Ff, corr = (h + 0.5) / (nS + 1), (fa + 0.5) / (nN + 1), True
    zH, zF = norm.ppf(Hh), norm.ppf(Ff)
    return dict(d=zH - zF, c=-0.5 * (zH + zF), H=Hh, F=Ff, corr=corr)


SDT_JS = """(rows) => rows.map(r => { const o = window.__test.computeSDT(r[0], r[1], r[2], r[3]);
  return o === null ? null : [o.dprime, o.c, o.H, o.F, o.corrected, o.H0, o.F0]; })"""

with sync_playwright() as pw:
    browser = pw.chromium.launch()
    page = browser.new_page()
    errors, external = [], []
    H.attach_collectors(page, errors, external)
    page.goto("file://" + H.PROJECT + "/signalentdeckung.html")
    assert page.evaluate("!!window.__test && window.__test.ready")
    rng = np.random.default_rng(99)

    # ------------------------------------------------------------------
    # 1. Normalverteilung
    # ------------------------------------------------------------------
    ps = np.concatenate([np.linspace(1e-12, 1 - 1e-12, 4001), np.array([1e-300, 1e-100, 1e-20, 0.5, 0.425 + 0.5, 0.075, 0.0001, 0.9999])])
    q = page.evaluate("(ps) => ps.map(p => window.__test.qnorm(p))", ps.tolist())
    err = np.max(np.abs(np.array(q) - norm.ppf(ps)) / np.maximum(1, np.abs(norm.ppf(ps))))
    C.check("qnorm (AS 241) gegen scipy.stats.norm.ppf auf %d Stellen, max. relative Abweichung %.1e (Toleranz 1e-9)" % (len(ps), err), err < 1e-9)
    edge_raw = page.evaluate("() => { const T = window.__test; return [T.qnorm(0) === -Infinity, T.qnorm(1) === Infinity, Number.isNaN(T.qnorm(-0.1)), Number.isNaN(T.qnorm(1.1))]; }")
    C.check("qnorm an den Rändern: -Infinity, +Infinity, NaN, NaN", edge_raw == [True, True, True, True], edge_raw)
    xs = np.linspace(-8, 8, 3201)
    pv = page.evaluate("(xs) => xs.map(x => window.__test.pnorm(x))", xs.tolist())
    perr = float(np.max(np.abs(np.array(pv) - norm.cdf(xs))))
    C.check("pnorm (nur für Kurven) gegen scipy.stats.norm.cdf, max. Abweichung %.1e (Toleranz 2e-7)" % perr, perr < 2e-7)

    # ------------------------------------------------------------------
    # 2. computeSDT gegen Python
    # ------------------------------------------------------------------
    rows = []
    for n in (10, 25, 50, 100, 1000):
        for h in sorted({0, 1, n // 2, n - 1, n}):
            for f in sorted({0, 1, n // 3, n - 1, n}):
                rows.append((h, n - h, f, n - f))
    for _ in range(3000):
        nS, nN = int(rng.integers(1, 120)), int(rng.integers(1, 120))
        h, f = int(rng.integers(0, nS + 1)), int(rng.integers(0, nN + 1))
        rows.append((h, nS - h, f, nN - f))
    js = page.evaluate(SDT_JS, [list(r) for r in rows])
    worst = 0.0
    bad = []
    n_corr = 0
    for r, o in zip(rows, js):
        ref = sdt_ref(*r)
        e = max(abs(o[0] - ref["d"]), abs(o[1] - ref["c"]), abs(o[2] - ref["H"]), abs(o[3] - ref["F"]))
        worst = max(worst, e)
        if e > 1e-9 or bool(o[4]) != ref["corr"]:
            bad.append(r)
        n_corr += ref["corr"]
    C.check("computeSDT gegen unabhängige Python-Rechnung: %d Zählwert-Kombinationen (Raster mit allen Kantenfällen und Zufall), max. Abweichung %.1e; %d davon mit Korrektur" % (len(rows), worst, n_corr), not bad, bad[:3])
    # Handgerechnete Kantenfälle
    zc = norm.ppf(25.5 / 26)
    cases = [
        ("H = 1 und FA = 0 (25/25): beide Raten korrigiert", (25, 0, 0, 25), 2 * zc, 0.0, True),
        ("H = 0 und FA = 1: d' negativ, c = 0", (0, 25, 25, 0), -2 * zc, 0.0, True),
        ("H = 1 und FA = 1: d' = 0, c negativ (immer Ja)", (25, 0, 25, 0), 0.0, -zc, True),
        ("H = 0 und FA = 0: d' = 0, c positiv (immer Nein)", (0, 25, 0, 25), 0.0, zc, True),
        ("nur H = 1 (FA = 0.2): beide Raten korrigiert", (25, 0, 5, 20), norm.ppf(25.5 / 26) - norm.ppf(5.5 / 26), -0.5 * (norm.ppf(25.5 / 26) + norm.ppf(5.5 / 26)), True),
        ("nur FA = 0 (H = 0.8): beide Raten korrigiert", (20, 5, 0, 25), norm.ppf(20.5 / 26) - norm.ppf(0.5 / 26), -0.5 * (norm.ppf(20.5 / 26) + norm.ppf(0.5 / 26)), True),
        ("innere Raten H = 0.8, FA = 0.2: keine Korrektur", (20, 5, 5, 20), 2 * norm.ppf(0.8), 0.0, False),
        ("H = FA = 0.5: d' = 0, c = 0", (10, 10, 10, 10), 0.0, 0.0, False),
        ("H = 0.9, FA = 0.1 bei 100 je Klasse", (90, 10, 10, 90), 2 * norm.ppf(0.9), 0.0, False),
    ]
    jsc = page.evaluate(SDT_JS, [list(c[1]) for c in cases])
    for (label, r, d_exp, c_exp, corr_exp), o in zip(cases, jsc):
        ok = abs(o[0] - d_exp) < 1e-9 and abs(o[1] - c_exp) < 1e-9 and bool(o[4]) == corr_exp
        C.check("Kantenfall: %s -> d' = %.4f, c = %.4f" % (label, o[0], o[1]), ok, "erwartet d'=%.4f c=%.4f korrigiert=%s" % (d_exp, c_exp, corr_exp))
    nulls = page.evaluate(SDT_JS, [[0, 0, 5, 5], [5, 5, 0, 0], [0, 0, 0, 0]])
    C.check("Leere Klasse (keine Signal- oder keine Catch-Durchgänge) liefert null statt NaN", nulls == [None, None, None], nulls)
    # Invarianzen: Umbenennen von Signal und Nichtsignal (Treffer <-> Korrekte Ablehnung, Verpasser <-> Fehlalarm)
    sym = page.evaluate(SDT_JS, [[40, 10, 15, 35], [10, 40, 35, 15], [35, 15, 10, 40], [15, 35, 40, 10]])
    C.check("Symmetrie: Ja/Nein vertauscht kehrt d' und c um; Signal/Nichtsignal umbenannt lässt d' gleich und kehrt c um (d' = %.3f, c = %.3f)" % (sym[0][0], sym[0][1]),
            abs(sym[1][0] + sym[0][0]) < 1e-12 and abs(sym[1][1] + sym[0][1]) < 1e-12
            and abs(sym[2][0] - sym[0][0]) < 1e-12 and abs(sym[2][1] + sym[0][1]) < 1e-12
            and abs(sym[3][0] + sym[2][0]) < 1e-12 and abs(sym[3][1] + sym[2][1]) < 1e-12)

    # ------------------------------------------------------------------
    # 3. Simulierte Beobachter mit bekanntem d' und c
    # ------------------------------------------------------------------
    def counts_for(d, c, nS, nN, size):
        Hp = norm.cdf(d / 2 - c)
        Fp = norm.cdf(-d / 2 - c)
        h = rng.binomial(nS, Hp, size)
        f = rng.binomial(nN, Fp, size)
        return [[int(a), int(nS - a), int(b), int(nN - b)] for a, b in zip(h, f)]

    worst_d = worst_c = 0.0
    big_rows = []
    for d in (0.5, 1.0, 1.5, 2.5):
        for c in (-1.0, -0.5, 0.0, 0.5, 1.0):
            cnt = counts_for(d, c, 100000, 100000, 1)
            o = page.evaluate(SDT_JS, cnt)[0]
            worst_d = max(worst_d, abs(o[0] - d))
            worst_c = max(worst_c, abs(o[1] - c))
            big_rows.append((d, c, o[0], o[1]))
    C.check("Grosse Stichprobe (je 100000 Signal- und Catch-Durchgänge), 20 Kombinationen d' in {0.5, 1, 1.5, 2.5} x c in {-1, -0.5, 0, 0.5, 1}: max. Abweichung d' %.3f, c %.3f (Toleranz 0.03)" % (worst_d, worst_c), worst_d < 0.03 and worst_c < 0.03)

    print()
    NB = page.evaluate("window.__test.CONFIG.trialsPerBlock") // 2
    print("Kleine Stichprobe wie in der App: %d Signal- und %d Catch-Durchgänge, 5000 simulierte Beobachter je Zeile" % (NB, NB))
    print("%5s %5s | %8s %7s %7s | %8s %7s %7s | %9s" % ("d'", "c", "Mw d'", "Bias", "SD", "Mw c", "Bias", "SD", "korrigiert"))
    small_worst_c = 0.0
    small_worst_d = 0.0
    small_rows = []
    for d in (1.0, 1.5, 2.0):
        for c in (-0.5, 0.0, 0.5):
            cnt = counts_for(d, c, NB, NB, 5000)
            res = page.evaluate(SDT_JS, cnt)
            dh = np.array([r[0] for r in res])
            ch = np.array([r[1] for r in res])
            corr = np.mean([r[4] for r in res])
            small_rows.append((d, c, dh.mean(), dh.std(ddof=1), ch.mean(), ch.std(ddof=1), corr))
            print("%5.1f %5.1f | %8.3f %+7.3f %7.3f | %8.3f %+7.3f %7.3f | %8.1f %%" % (d, c, dh.mean(), dh.mean() - d, dh.std(ddof=1), ch.mean(), ch.mean() - c, ch.std(ddof=1), 100 * corr))
            small_worst_d = max(small_worst_d, abs(dh.mean() - d))
            small_worst_c = max(small_worst_c, abs(ch.mean() - c))
    print()
    C.check("Kleine Stichprobe (%d + %d): mittlere Schätzung von d' weicht höchstens %.2f, von c höchstens %.2f vom wahren Wert ab (Toleranz 0.25 bzw. 0.06; Streuung einer Einzelschätzung siehe Tabelle)" % (NB, NB, small_worst_d, small_worst_c), small_worst_d < 0.25 and small_worst_c < 0.06)
    # Der Block-Effekt: Unterschied der c-Schätzungen zwischen zwei Kriterien wird erkannt
    cl = np.array([r[1] for r in page.evaluate(SDT_JS, counts_for(1.5, -0.6, NB, NB, 3000))])
    ck = np.array([r[1] for r in page.evaluate(SDT_JS, counts_for(1.5, 0.6, NB, NB, 3000))])
    C.check("Beobachter d' = 1.5 mit c = -0.6 bzw. +0.6 (%d + %d): geschätzte c-Werte unterscheiden sich im Mittel um %.2f (wahr 1.20); in %.1f %% der Paare ist c(Verpasser teuer) < c(Fehlalarm teuer)" % (NB, NB, ck.mean() - cl.mean(), 100 * np.mean(cl < ck)),
            abs((ck.mean() - cl.mean()) - 1.2) < 0.12)

    # ------------------------------------------------------------------
    # 4. Reizbild
    # ------------------------------------------------------------------
    size, sigma, mean_g, bw = 160, 28.0, 128.0, 14.0
    amps = [0.5, 2.8, 8.0, 16.0]
    N = size * size
    r_noise = np.array(page.evaluate("() => window.__test.makeStimulus(11, false, 0)"), dtype=float).reshape(N, 4)
    gray = r_noise[:, 0]
    C.check("Bild: 160 x 160 Pixel, RGBA, Grau (R=G=B), Alpha 255", r_noise.shape == (N, 4) and np.all(r_noise[:, 0] == r_noise[:, 1]) and np.all(r_noise[:, 0] == r_noise[:, 2]) and np.all(r_noise[:, 3] == 255))
    C.check("Rauschbild: Mittelwert %.2f (erwartet 128 +- %.2f), SD %.2f (erwartet 28)" % (gray.mean(), 4 * sigma / math.sqrt(N), gray.std()), abs(gray.mean() - mean_g) < 4 * sigma / math.sqrt(N) and abs(gray.std() - sigma) < 0.6)
    jit = gray + np.random.default_rng(5).uniform(-0.5, 0.5, gray.shape)   # hebt die 8-Bit-Rundung auf
    ks = sst.kstest((jit - jit.mean()) / jit.std(), "norm")
    C.check("Rauschbild: Pixelwerte normalverteilt (KS nach Aufheben der 8-Bit-Rundung: p = %.3f > 0.01), Wertebereich %d bis %d innerhalb 0..255" % (ks.pvalue, gray.min(), gray.max()), ks.pvalue > 0.01 and gray.min() >= 0 and gray.max() <= 255)
    img = gray.reshape(size, size)
    ac_x = np.corrcoef(img[:, :-1].ravel(), img[:, 1:].ravel())[0, 1]
    ac_y = np.corrcoef(img[:-1, :].ravel(), img[1:, :].ravel())[0, 1]
    C.check("Rauschbild: Nachbarpixel unabhängig (Korrelation horizontal %.3f, vertikal %.3f, Grenze 0.025)" % (ac_x, ac_y), abs(ac_x) < 0.025 and abs(ac_y) < 0.025)
    prof = np.array(page.evaluate("() => window.__test.blobProfile(160, 14)")).reshape(size, size)
    C.check("Fleck: Profil exp(-r^2 / (2*14^2)), Maximum %.4f in der Mitte, Rand < 1e-3" % prof.max(), prof.max() > 0.9985 and prof[0, 0] < 1e-3 and prof[80, 80] > 0.99 and prof[79, 79] > 0.99)
    worst_fleck = 0.0
    for a in amps:
        s = np.array(page.evaluate("(a) => window.__test.makeStimulus(11, true, a)", a), dtype=float).reshape(N, 4)[:, 0].reshape(size, size)
        diff = s - img
        worst_fleck = max(worst_fleck, float(np.max(np.abs(diff - a * prof))))
    C.check("Signalbild = gleiches Rauschbild (gleicher Seed) + Amplitude x Fleckprofil, max. Abweichung %.2f Grauwerte (Rundung, Toleranz 1.0)" % worst_fleck, worst_fleck <= 1.0)
    cm = diff[75:85, 75:85].mean()
    C.check("Generator ohne Positionsangabe setzt den Fleck in die Bildmitte (nur Testzweck, die App übergibt immer eine Position ausserhalb der Ausschlusszone, siehe test_07): Mittel der zentralen 10 x 10 Pixel erhöht um %.2f (Amplitude 16 x Profil ~ %.2f)" % (cm, 16 * prof[75:85, 75:85].mean()), abs(cm - 16 * prof[75:85, 75:85].mean()) < 0.5)
    # Matched-Filter-d' der Bilder
    sumsq = float(np.sum(prof ** 2))
    d_ideal_expected = {a: a * math.sqrt(sumsq) / sigma for a in amps}
    MF_JS = """([amp, n]) => { const T = window.__test; const out = [];
      const prof = T.blobProfile(160, 14);
      for (let i = 0; i < n; i++) { for (const sig of [false, true]) { const im = T.makeStimulus(1000 + 2 * i + (sig ? 1 : 0), sig, amp);
        let s = 0; for (let k = 0; k < 25600; k++) s += (im[4 * k] - 128) * prof[k]; out.push(s); } }
      return out; }"""
    rows_mf = []
    for a in (2.8, 8.0):
        stat = np.array(page.evaluate(MF_JS, [a, 400]))
        noise_s, sig_s = stat[0::2], stat[1::2]
        d_emp = (sig_s.mean() - noise_s.mean()) / math.sqrt(0.5 * (sig_s.var(ddof=1) + noise_s.var(ddof=1)))
        rows_mf.append((a, d_emp, d_ideal_expected[a]))
        C.check("Matched-Filter-d' der erzeugten Bilder bei Amplitude %.1f: gemessen %.2f, erwartet %.2f (Toleranz 15 %%, 400 + 400 Bilder)" % (a, d_emp, d_ideal_expected[a]), abs(d_emp / d_ideal_expected[a] - 1) < 0.15)
    C.info("Idealbeobachter-d' bei Amplitude 0.5 / 2.8 / 8 / 16: %s (Menschen liegen darunter; die Reglerskala ist nicht an Menschen kalibriert)" % ", ".join("%.2f" % d_ideal_expected[a] for a in amps))
    # Regler -> Amplitude
    sl = page.evaluate("() => [1, 25, 50, 75, 100].map(v => window.__test.sliderToAmp(v))")
    C.check("Regler -> Amplitude: 1 -> 16, 100 -> 0.5, Mitte (50) -> %.2f, streng monoton fallend (%s)" % (sl[2], ", ".join("%.2f" % x for x in sl)),
            abs(sl[0] - 16) < 1e-9 and abs(sl[4] - 0.5) < 1e-9 and all(a > b for a, b in zip(sl, sl[1:])))
    mk = np.array(page.evaluate("() => window.__test.makeMask(3)"), dtype=float).reshape(N, 4)[:, 0].reshape(size, size)
    blocks_const = all(len(np.unique(mk[i:i + 8, j:j + 8])) == 1 for i in range(0, size, 8) for j in range(0, size, 8))
    C.check("Maske: 8 x 8-Blöcke mit konstantem Grauwert, Werte %d bis %d in [30, 225]" % (mk.min(), mk.max()), blocks_const and mk.min() >= 30 and mk.max() <= 225)

    # ------------------------------------------------------------------
    # 5. Zeitplan
    # ------------------------------------------------------------------
    SCH_JS = """([n, reps]) => { const out = []; for (let s = 1; s <= reps; s++) out.push(window.__test.makeSchedule(n, s).map(x => x ? 1 : 0)); return out; }"""
    for n in (40, 16, 50, 60):
        sc = np.array(page.evaluate(SCH_JS, [n, 600]))
        sums = sc.sum(axis=1)
        pos = sc.mean(axis=0)
        longest = max(max((len(list(g)) for k, g in itertools.groupby(row)), default=0) for row in sc)
        C.check("Zeitplan n = %d (600 Seeds): immer genau %d Signal-Durchgänge; Anteil je Position %.2f bis %.2f (erwartet 0.5 +-0.09); längste Serie gleicher Durchgänge %d" % (n, n // 2, pos.min(), pos.max(), longest),
                np.all(sums == n // 2) and pos.min() > 0.41 and pos.max() < 0.59)

    # ------------------------------------------------------------------
    # 6. Ergebnis-Code
    # ------------------------------------------------------------------
    CODE_JS = """(items) => items.map(it => { const T = window.__test;
      const code = T.buildCode(it.id, it.order, it.L, it.K); const p = T.parseCode(code); return [code, p]; })"""
    items = []
    for _ in range(3000):
        nS, nN = int(rng.integers(1, 100)), int(rng.integers(1, 100))
        L = {"hit": int(rng.integers(0, nS + 1)), "fa": int(rng.integers(0, nN + 1))}
        L["miss"], L["cr"] = nS - L["hit"], nN - L["fa"]
        K = {"hit": int(rng.integers(0, nS + 1)), "fa": int(rng.integers(0, nN + 1))}
        K["miss"], K["cr"] = nS - K["hit"], nN - K["fa"]
        idc = "".join(rng.choice(list("0123456789abcdefghijklmnopqrstuvwxyz"), 4))
        items.append({"id": idc, "order": ["liberal", "konservativ"] if rng.random() < 0.5 else ["konservativ", "liberal"], "L": L, "K": K})
    res = page.evaluate(CODE_JS, items)
    bad = 0
    fmt_bad = 0
    for it, (code, p) in zip(items, res):
        order = "lk" if it["order"][0] == "liberal" else "kl"
        blk = lambda c: "%d-%d-%d-%d" % (c["hit"], c["miss"], c["fa"], c["cr"])
        payload = "HSLU-sdt-v2.%s.%s.%s.%s" % (it["id"], order, blk(it["L"]), blk(it["K"]))
        expected = payload + "." + H.checksum(payload)
        if code != expected:
            fmt_bad += 1
        if not (p["ok"] and p["id"] == it["id"] and p["order"] == it["order"] and p["liberal"] == it["L"] and p["konservativ"] == it["K"]):
            bad += 1
    lens = [len(c) for c, _ in res]
    C.check("Code-Rundreise (3000 Zufallsergebnisse): Kodieren -> Dekodieren liefert dieselben Zählwerte, Reihenfolge und Kennung", bad == 0, bad)
    C.check("Code-Format entspricht der unabhängigen Python-Berechnung (Präfix HSLU-sdt-v2, Prüfsumme Basis 36 mod 46656); Länge %d bis %d Zeichen, nur [A-Za-z0-9.-]" % (min(lens), max(lens)),
            fmt_bad == 0 and all(re.fullmatch(r"[A-Za-z0-9.\-]+", c) for c, _ in res), fmt_bad)
    good = res[0][0]
    flip = good[:-1] + ("0" if good[-1] != "0" else "1")
    cases = [
        ("gültig", good, True, None),
        ("gültig in Grossbuchstaben und mit Leerzeichen", "  " + good.upper() + "  ", True, None),
        ("Prüfsumme geändert", flip, False, "Prüfsumme"),
        ("Zahl verändert (Tippfehler)", good.replace(".lk.", ".lk.1").replace(".kl.", ".kl.1"), False, "Prüfsumme"),
        ("abgeschnitten", good[:-6], False, "Format"),
        ("alter Code Version v1 (50 Durchgänge, Fleck in der Mitte)", "HSLU-sdt-v1.abcd.lk.20-5-3-22.18-7-9-16.xyz", False, "veraltet"),
        ("alter v1-Code mit gültiger Prüfsumme", "HSLU-sdt-v1.abcd.lk.20-5-3-22.18-7-9-16." + H.checksum("HSLU-sdt-v1.abcd.lk.20-5-3-22.18-7-9-16"), False, "nicht mit v2 vergleichbar"),
        ("noch unbekannte Version (v3)", good.replace("-v2.", "-v3."), False, "Version v3"),
        ("Code der Schwellenseite", "HSLU-schwelle-v1.abcd.o.421.49.36.7tc", False, "anderen Seite"),
        ("kein Code", "hallo welt", False, "kein Ergebnis-Code"),
        ("negativer Wert", "HSLU-sdt-v2.abcd.lk.-1-2-3-4.1-2-3-4.abc", False, "Format"),
        ("zu grosse Zahl", "HSLU-sdt-v2.abcd.lk.1234-2-3-4.1-2-3-4.abc", False, "Format"),
    ]
    pr = page.evaluate("(cs) => cs.map(c => window.__test.parseCode(c))", [c[1] for c in cases])
    for (label, text, ok_exp, why), p in zip(cases, pr):
        okk = (p["ok"] == ok_exp) and (ok_exp or why in p["reason"])
        C.check("Code prüfen: %s -> %s" % (label, "akzeptiert" if p["ok"] else "abgelehnt (%s)" % p.get("reason")), okk)
    # Null Durchgänge in einer Klasse
    zero = "HSLU-sdt-v2.abcd.lk.0-0-3-4.1-2-3-4"
    zero += "." + H.checksum(zero)
    pz = page.evaluate("(c) => window.__test.parseCode(c)", zero)
    C.check("Code mit leerer Signal-Klasse (0 Treffer, 0 Verpasser) wird als unplausibel abgelehnt", (not pz["ok"]) and "unplausibel" in pz["reason"], pz)

    # ------------------------------------------------------------------
    # 7. Gruppenauswertung: Zeilen und Zahlen gegen Python
    # ------------------------------------------------------------------
    people = []
    codes = []
    for i in range(6):
        d = float(rng.uniform(0.8, 2.2))
        cL, cK = float(rng.uniform(-1.0, -0.2)), float(rng.uniform(0.2, 1.0))
        L = counts_for(d, cL, NB, NB, 1)[0]
        K = counts_for(d, cK, NB, NB, 1)[0]
        order = ["liberal", "konservativ"] if i % 2 == 0 else ["konservativ", "liberal"]
        people.append((L, K, order))
    # eine Person mit Kantenfall (H = 1, FA = 0)
    people.append(([25, 0, 0, 25], [20, 5, 1, 24], ["konservativ", "liberal"]))
    text = page.evaluate("""(people) => { const T = window.__test; return people.map((p, i) => T.buildCode('u0' + String(i).padStart(2, '0'), p[2],
        {hit: p[0][0], miss: p[0][1], fa: p[0][2], cr: p[0][3]}, {hit: p[1][0], miss: p[1][1], fa: p[1][2], cr: p[1][3]})); }""", people)
    codes = text
    block = "\r\n".join([codes[0], "", codes[1], codes[1], "  " + codes[2].upper(), "Müll in Zeile 6", codes[3], codes[0], codes[4] + " " + codes[5], codes[6][:-1] + "z", "HSLU-schwelle-v1.abcd.o.421.49.36.7tc"])
    pl = page.evaluate("(t) => { const r = window.__test.parseLines(t); return {valid: r.valid.length, invalid: r.invalid.map(x => [x.line, x.reason]), dup: r.duplicates}; }", block)
    C.check("parseLines: 6 gültige Codes (inkl. zwei Codes in einer Zeile und Grossschreibung), 2 Duplikate ignoriert (inkl. Zeilenende CRLF und Leerzeile), 3 ungültige Zeilen benannt: %s" % pl["invalid"],
            pl["valid"] == 6 and pl["dup"] == 2 and [x[0] for x in pl["invalid"]] == [6, 10, 11], pl)
    gs = page.evaluate("""(cs) => { const T = window.__test; const v = cs.map(c => T.parseCode(c)); const g = T.groupSummary(v);
      return {rows: g.rows.map(r => [r.liberal.dprime, r.liberal.c, r.konservativ.dprime, r.konservativ.c, r.liberal.H, r.liberal.F, r.konservativ.H, r.konservativ.F]),
              sum: {lib: [g.sum.liberal.d.mean, g.sum.liberal.d.sd, g.sum.liberal.c.mean, g.sum.liberal.c.sd, g.sum.liberal.H.mean, g.sum.liberal.F.mean],
                    kon: [g.sum.konservativ.d.mean, g.sum.konservativ.d.sd, g.sum.konservativ.c.mean, g.sum.konservativ.c.sd, g.sum.konservativ.H.mean, g.sum.konservativ.F.mean]},
              dAll: [g.dAll.mean, g.dAll.n]}; }""", codes)
    ref = [(sdt_ref(*p[0]), sdt_ref(*p[1])) for p in people]
    dl = np.array([r[0]["d"] for r in ref])
    cl_ = np.array([r[0]["c"] for r in ref])
    dk = np.array([r[1]["d"] for r in ref])
    ck_ = np.array([r[1]["c"] for r in ref])
    exp = {"lib": [dl.mean(), dl.std(ddof=1), cl_.mean(), cl_.std(ddof=1), np.mean([r[0]["H"] for r in ref]), np.mean([r[0]["F"] for r in ref])],
           "kon": [dk.mean(), dk.std(ddof=1), ck_.mean(), ck_.std(ddof=1), np.mean([r[1]["H"] for r in ref]), np.mean([r[1]["F"] for r in ref])]}
    e1 = max(abs(a - b) for a, b in zip(gs["sum"]["lib"], exp["lib"]))
    e2 = max(abs(a - b) for a, b in zip(gs["sum"]["kon"], exp["kon"]))
    e3 = max(max(abs(a - b) for a, b in zip(row, [r[0]["d"], r[0]["c"], r[1]["d"], r[1]["c"], r[0]["H"], r[0]["F"], r[1]["H"], r[1]["F"]])) for row, r in zip(gs["rows"], ref))
    e4 = abs(gs["dAll"][0] - np.mean(np.concatenate([dl, dk])))
    C.check("Gruppenwerte (7 Personen, eine mit Kantenfall): Einzelwerte, Mittelwerte und SD von d' und c je Block, Mittel der Raten, Gesamt-d' stimmen mit Python überein (max. Abweichung %.1e)" % max(e1, e2, e3, e4), max(e1, e2, e3, e4) < 1e-9 and gs["dAll"][1] == 14)

    C.check("Keine Konsolenfehler, keine externen oder fehlgeschlagenen Anfragen", not errors and not external, errors + external)
    browser.close()

C.finish()
