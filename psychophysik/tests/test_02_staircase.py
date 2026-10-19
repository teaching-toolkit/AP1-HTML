"""Adaptives Verfahren 2-down-1-up (schwelle.html): Simulation und Randfälle.

1. Unabhängige Python-Referenz gegen die JS-Klasse Staircase auf identischen Antwortfolgen (Level für Level).
2. Simulation eines Hörers mit psychometrischer Funktion (Weibull, Rateschwelle 50 %, optional Lapse):
   >= 1000 Läufe je Szenario in JS und in Python; Mittel, Streuung, Verzerrung gegenüber dem Level mit 70.7 % Treffern.
3. Analytische Kontrolle über eine Markov-Kette (stationärer Anteil richtiger Antworten).
4. Randfälle: Hörer nie richtig, immer richtig, Ratehörer (50 %), Abbruch durch Höchstzahl der Durchgänge.
Start: python3 -I tests/test_02_staircase.py
"""
import math
import os
import sys
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from playwright.sync_api import sync_playwright

import _helpers as H

C = H.Checker("Adaptives Verfahren (2-down-1-up)")

CFG = dict(startMs=20.0, minMs=0.25, maxMs=50.0, nDown=2, stepLarge=2.0, stepSmall=1.25, switchAfterReversals=2,
           reversalsTarget=12, meanLast=8, maxTrials=100, ceilingLimit=4, floorLimit=3, boundaryShare=0.5)
TARGET = 0.5 ** 0.5   # 0.7071...


# ----------------------------------------------------------------------
# Unabhängige Referenzumsetzung (aus der Spezifikation geschrieben)
# ----------------------------------------------------------------------
def run_ref(cfg, answer):
    """answer(level, n) -> bool. Gibt Verlauf und Ergebnis zurück."""
    level = cfg["startMs"]
    streak = 0
    moves = []          # Richtung jeder Pegeländerung (+1 / -1)
    revs = []           # (Durchgang, Level)
    levels, answers = [], []
    up_at_max = 0
    down_at_min = 0
    n = 0
    while True:
        n += 1
        ok = bool(answer(level, n))
        levels.append(level)
        answers.append(ok)
        up_at_max = up_at_max + 1 if (not ok and level >= cfg["maxMs"]) else 0
        direction = 0
        if ok:
            streak += 1
            if streak == cfg["nDown"]:
                direction, streak = -1, 0
        else:
            streak, direction = 0, +1
        if direction == -1 and level <= cfg["minMs"]:
            down_at_min += 1
        elif direction == +1:
            down_at_min = 0
        if direction:
            if moves and moves[-1] != direction:
                revs.append((n, level))
            moves.append(direction)
            step = cfg["stepSmall"] if len(revs) >= cfg["switchAfterReversals"] else cfg["stepLarge"]
            level = level / step if direction < 0 else level * step
            level = min(cfg["maxMs"], max(cfg["minMs"], level))
        if len(revs) >= cfg["reversalsTarget"]:
            used = [r[1] for r in revs[-cfg["meanLast"]:]]
            at_max = sum(1 for v in used if v >= cfg["maxMs"])
            at_min = sum(1 for v in used if v <= cfg["minMs"])
            if at_max >= cfg["boundaryShare"] * len(used):
                return dict(status="ceiling", thr=None, n=n, levels=levels, answers=answers, revs=revs, bcount=at_max + at_min)
            if at_min >= cfg["boundaryShare"] * len(used):
                return dict(status="floor", thr=None, n=n, levels=levels, answers=answers, revs=revs, bcount=at_max + at_min)
            thr = math.exp(sum(math.log(v) for v in used) / len(used))
            return dict(status="ok", thr=thr, n=n, levels=levels, answers=answers, revs=revs, bcount=at_max + at_min)
        if up_at_max >= cfg["ceilingLimit"]:
            return dict(status="ceiling", thr=None, n=n, levels=levels, answers=answers, revs=revs, bcount=0)
        if down_at_min >= cfg["floorLimit"]:
            return dict(status="floor", thr=None, n=n, levels=levels, answers=answers, revs=revs, bcount=0)
        if n >= cfg["maxTrials"]:
            return dict(status="maxtrials", thr=None, n=n, levels=levels, answers=answers, revs=revs, bcount=0)


def weibull_pc(gref, beta, lapse):
    Fn = (TARGET - 0.5) / (0.5 - lapse)
    alpha = gref / (-math.log(1 - Fn)) ** (1 / beta)
    return lambda g: 0.5 + (0.5 - lapse) * (1 - math.exp(-((g / alpha) ** beta)))


def gref_of(pc, lo=1e-3, hi=1e3):
    for _ in range(200):
        mid = math.sqrt(lo * hi)
        if pc(mid) < TARGET:
            lo = mid
        else:
            hi = mid
    return math.sqrt(lo * hi)


def markov_stationary(pc, cfg):
    """Stationäre Verteilung der Kette über (Level-Index, Streak) bei gleichen Schritten stepSmall.
    Gibt den trial-gewichteten Anteil richtiger Antworten und den mittleren log-Level zurück."""
    K = 120
    g0 = cfg["minMs"]
    lv = g0 * cfg["stepSmall"] ** np.arange(K)
    lv = lv[lv <= cfg["maxMs"] * 1.0001]
    K = len(lv)
    p = np.array([pc(g) for g in lv])
    S = 2 * K
    P = np.zeros((S, S))
    for i in range(K):
        up = min(K - 1, i + 1)
        dn = max(0, i - 1)
        P[2 * i, 2 * i + 1] += p[i]          # erste richtige Antwort: Level bleibt, Streak 1
        P[2 * i, 2 * up] += 1 - p[i]         # falsch: hoch
        P[2 * i + 1, 2 * dn] += p[i]         # zweite richtige: runter, Streak 0
        P[2 * i + 1, 2 * up] += 1 - p[i]     # falsch: hoch
    w, v = np.linalg.eig(P.T)
    k = np.argmin(np.abs(w - 1))
    pi = np.real(v[:, k])
    pi = pi / pi.sum()
    prob_state = np.repeat(p, 2)
    prop = float(np.sum(pi * prob_state))
    pl = pi.reshape(K, 2).sum(axis=1)
    meanlog = float(np.sum(pl * np.log(lv)))
    return prop, math.exp(meanlog), lv, pl


with sync_playwright() as pw:
    browser = pw.chromium.launch()
    page = browser.new_page()
    errors, external = [], []
    H.attach_collectors(page, errors, external)
    page.goto("file://" + H.PROJECT + "/schwelle.html")
    assert page.evaluate("!!window.__test && window.__test.ready")

    # Konfiguration der Seite = dokumentierte Werte
    jscfg = page.evaluate("() => window.__test.CONFIG")
    same = all(abs(jscfg[k] - v) < 1e-12 for k, v in CFG.items())
    C.check("Konfiguration der Seite entspricht den dokumentierten Werten (Start 20 ms, Min 0.25, Max 50, Schritte 2 und 1.25, 12 Umkehrpunkte, Mittel der letzten 8, max. 100 Durchgänge)", same, {k: jscfg[k] for k in CFG})

    # ------------------------------------------------------------------
    # 1. Kreuzprüfung JS gegen Python-Referenz auf identischen Antwortfolgen
    # ------------------------------------------------------------------
    rng = np.random.default_rng(2024)
    seqs, refs = [], []
    kinds = Counter()
    for i in range(2500):
        k = i % 5
        if k == 0:
            gref = float(np.exp(rng.uniform(math.log(0.4), math.log(30))))
            pc = weibull_pc(gref, float(rng.uniform(1.5, 6)), float(rng.choice([0, 0.03])))
        elif k == 1:
            c = float(rng.choice([0.0, 0.2, 0.5, 0.8, 0.95, 1.0]))
            pc = (lambda c: (lambda g: c))(c)
        elif k == 2:
            pc = weibull_pc(float(np.exp(rng.uniform(math.log(0.05), math.log(0.4)))), 3.0, 0.0)   # unter der Untergrenze
        elif k == 3:
            pc = weibull_pc(float(np.exp(rng.uniform(math.log(40), math.log(200)))), 3.0, 0.0)      # über der Obergrenze
        else:
            gref = float(np.exp(rng.uniform(math.log(1), math.log(10))))
            pc = weibull_pc(gref, 3.0, 0.0)
        kinds[k] += 1
        r = run_ref(CFG, lambda g, n, pc=pc: rng.random() < pc(g))
        refs.append(r)
        seqs.append([1 if a else 0 for a in r["answers"]])
    js = page.evaluate("""(seqs) => { const T = window.__test; return seqs.map(seq => {
      const st = new T.Staircase(T.CONFIG); const levels = []; let early = false;
      for (let i = 0; i < seq.length; i++) { if (st.done) { early = true; break; } levels.push(st.level); st.record(!!seq[i]); }
      return {done: st.done, early, status: st.status, thr: st.thresholdMs, n: st.nTrials, revs: st.reversals.map(r => [r.trial, r.level]), levels, b: st.boundaryCount}; }); }""", seqs)
    mism = []
    maxrel = 0.0
    for i, (r, j) in enumerate(zip(refs, js)):
        okk = (j["done"] and not j["early"] and j["status"] == r["status"] and j["n"] == r["n"] and len(j["revs"]) == len(r["revs"])
               and all(a[0] == b[0] for a, b in zip(j["revs"], r["revs"])) and j["b"] == r["bcount"])
        if okk:
            rel = max(abs(a / b - 1) for a, b in zip(j["levels"], r["levels"]))
            rel = max([rel] + [abs(a[1] / b[1] - 1) for a, b in zip(j["revs"], r["revs"])])
            if r["thr"] is not None:
                rel = max(rel, abs(j["thr"] / r["thr"] - 1))
            elif j["thr"] is not None:
                okk = False
            maxrel = max(maxrel, rel)
            okk = okk and rel < 1e-12
        if not okk:
            mism.append(i)
    st_counts = Counter(r["status"] for r in refs)
    C.check("Kreuzprüfung: %d Antwortfolgen (zufällige Hörer, konstante p, Schwellen unter/über den Grenzen) gleich in JS und Python: Level jedes Durchgangs, Umkehrpunkte, Status, Schwelle (max. rel. Abweichung %.1e)" % (len(seqs), maxrel), not mism, "Abweichungen: %d  Stati: %s" % (len(mism), dict(st_counts)))

    # Eigenschaftsprüfungen am JS-Verlauf (unabhängig von der Referenz)
    viol = Counter()
    for r, j in zip(refs, js):
        lv, an = j["levels"], r["answers"]
        if abs(lv[0] - 20.0) > 1e-12:
            viol["start"] += 1
        if min(lv) < 0.25 - 1e-12 or max(lv) > 50 + 1e-12:
            viol["range"] += 1
        streak = 0
        for t in range(len(lv) - 1):
            ok, a, b = an[t], lv[t], lv[t + 1]
            if not ok:
                streak = 0
                if not (b > a or (a >= 50 and b == a)):
                    viol["wrong_not_up"] += 1
            else:
                streak += 1
                if streak == 2:
                    streak = 0
                    if not (b < a or (a <= 0.25 and b == a)):
                        viol["two_correct_not_down"] += 1
                elif b != a:
                    viol["single_correct_changed"] += 1
    C.check("Eigenschaften je Durchgang: Start 20 ms, Level in [0.25, 50], falsch -> länger, zwei richtige -> kürzer, eine richtige -> unverändert", not viol, dict(viol))
    ok_runs = [(r, j) for r, j in zip(refs, js) if r["status"] == "ok"]
    C.check("Bei Status ok sind es genau 12 Umkehrpunkte und der letzte fällt auf den letzten Durchgang (Abbruch greift sofort)",
            all(len(j["revs"]) == 12 and j["revs"][-1][0] == j["n"] for r, j in ok_runs), "%d Läufe" % len(ok_runs))
    C.check("Alle %d Läufe enden (max. Durchgänge %d <= 100)" % (len(js), max(j["n"] for j in js)), all(j["n"] <= 100 for j in js))

    # ------------------------------------------------------------------
    # 2. Psychometrische Hörer, >= 1000 Läufe je Szenario in JS und Python
    # ------------------------------------------------------------------
    SIM_JS = """([gref, beta, lapse, n, seed0]) => {
      const T = window.__test; const Ft = 0.7071067811865476; const Fn = (Ft - 0.5) / (0.5 - lapse);
      const alpha = gref / Math.pow(-Math.log(1 - Fn), 1 / beta);
      const pc = g => 0.5 + (0.5 - lapse) * (1 - Math.exp(-Math.pow(g / alpha, beta)));
      const out = [];
      for (let i = 0; i < n; i++) { const r = T.simulate(pc, seed0 + i);
        let c = 0, m = 0, k4 = r.reversals.length >= 4 ? r.reversals[3].trial : 1e9;
        for (let j = 0; j < r.trials.length; j++) { if (j + 1 >= k4) { m++; c += r.trials[j][1]; } }
        const used = r.reversals.slice(-8).map(x => x.level);
        const arith = used.reduce((a, b) => a + b, 0) / used.length;
        out.push([r.status, r.thresholdMs, r.nTrials, r.nCorrect, r.reversals.length, m ? c / m : null, arith]); }
      return out; }"""
    scen = [("Beispiel der Aufgabe: 4 ms, Steilheit 3", 4.0, 3.0, 0.0),
            ("kurze Schwelle 1.5 ms", 1.5, 3.0, 0.0),
            ("lange Schwelle 8 ms", 8.0, 3.0, 0.0),
            ("flache Funktion (Steilheit 1.5)", 4.0, 1.5, 0.0),
            ("steile Funktion (Steilheit 6)", 4.0, 6.0, 0.0),
            ("mit Lapse 3 %", 4.0, 3.0, 0.03)]
    NRUN = 1000
    summary = []
    for name, gref, beta, lapse in scen:
        pc = weibull_pc(gref, beta, lapse)
        assert abs(pc(gref) - TARGET) < 1e-9
        res_js = page.evaluate(SIM_JS, [gref, beta, lapse, NRUN, 10000])
        prng = np.random.default_rng(777 + int(gref * 10))
        res_py = []
        for i in range(NRUN):
            r = run_ref(CFG, lambda g, n: prng.random() < pc(g))
            k4 = r["revs"][3][0] if len(r["revs"]) >= 4 else 10**9
            tail = [a for t, a in enumerate(r["answers"], start=1) if t >= k4]
            res_py.append((r["status"], r["thr"], r["n"], sum(r["answers"]), len(r["revs"]), (sum(tail) / len(tail)) if tail else None))
        thr_js = np.array([r[1] for r in res_js if r[0] == "ok"])
        thr_py = np.array([r[1] for r in res_py if r[0] == "ok"])
        ar_js = np.array([r[6] for r in res_js if r[0] == "ok"])
        fc_js = float(np.mean([r[5] for r in res_js if r[0] == "ok" and r[5] is not None]))
        fc_py = float(np.mean([r[5] for r in res_py if r[0] == "ok" and r[5] is not None]))
        ntr = np.array([r[2] for r in res_js])
        ratio = float(thr_js.mean() / gref)
        ratio_py = float(thr_py.mean() / gref)
        cv = float(thr_js.std(ddof=1) / thr_js.mean())
        se = float(thr_js.std(ddof=1) / math.sqrt(len(thr_js)))
        se_py = float(thr_py.std(ddof=1) / math.sqrt(len(thr_py)))
        diff_z = abs(thr_js.mean() - thr_py.mean()) / math.sqrt(se ** 2 + se_py ** 2)
        mk_prop, mk_level, _, _ = markov_stationary(pc, CFG)
        summary.append((name, gref, ratio, ratio_py, float(np.median(thr_js) / gref), float(ar_js.mean() / gref), cv, float(ntr.mean()), fc_js, fc_py, mk_prop, diff_z, len(thr_js), int(ntr.min()), int(ntr.max())))
        C.check("[%s] %d JS-Läufe: alle mit Status ok, 12 Umkehrpunkte" % (name, NRUN), len(thr_js) == NRUN and all(r[4] == 12 for r in res_js), Counter(r[0] for r in res_js))
        C.check("[%s] Mittel der Schätzung / Level bei 70.7 %% = %.3f (Toleranz 0.88 bis 1.12); Median %.3f" % (name, ratio, np.median(thr_js) / gref), 0.88 <= ratio <= 1.12)
        C.check("[%s] JS und Python-Referenz stimmen statistisch überein (|Differenz der Mittel| = %.2f Standardfehler < 3)" % (name, diff_z), diff_z < 3, "JS %.3f Py %.3f" % (ratio, ratio_py))
        C.check("[%s] Anteil richtiger Antworten ab 4. Umkehrpunkt im Standardlauf: JS %.3f, Py %.3f (Anlaufphase, Bereich 0.69 bis 0.76); stationärer Wert nach Markov-Kette %.3f" % (name, fc_js, fc_py, mk_prop), 0.69 <= fc_js <= 0.76 and 0.69 <= fc_py <= 0.76 and abs(fc_js - fc_py) < 0.01)
    print()
    print("Zusammenfassung der Szenarien (%d Läufe je Szenario und Implementierung)" % NRUN)
    print("%-42s %6s %8s %8s %8s %8s %7s %7s %8s" % ("Szenario", "g70", "JS Mw/g", "Py Mw/g", "Median", "arith.", "CV", "Durchg.", "Anteil r."))
    for s in summary:
        print("%-42s %6.2f %8.3f %8.3f %8.3f %8.3f %7.3f %7.1f %8.3f" % (s[0], s[1], s[2], s[3], s[4], s[5], s[6], s[7], s[8]))
    print("Durchgänge je Lauf (JS): min %d, max %d" % (min(s[13] for s in summary), max(s[14] for s in summary)))
    print()

    # Konvergenz im Langlauf: 400 Umkehrpunkte, Anteil richtiger Antworten ab dem 4. Umkehrpunkt
    LONG_JS = """([gref, beta, n]) => { const T = window.__test; const Fn = (0.7071067811865476 - 0.5) / 0.5;
      const alpha = gref / Math.pow(-Math.log(1 - Fn), 1 / beta); const pc = g => 0.5 + 0.5 * (1 - Math.exp(-Math.pow(g / alpha, beta)));
      const out = []; for (let i = 0; i < n; i++) { const r = T.simulate(pc, 50000 + i, {reversalsTarget: 400, maxTrials: 100000});
        const k = r.reversals[3].trial; let c = 0, m = 0; for (let j = k - 1; j < r.trials.length; j++) { m++; c += r.trials[j][1]; }
        out.push([c / m, r.reversals.slice(-300).map(x => Math.log(x.level)).reduce((a, b) => a + b, 0) / 300]); }
      return out; }"""
    for gref, beta in ((4.0, 3.0), (4.0, 1.5), (4.0, 6.0)):
        lr = np.array(page.evaluate(LONG_JS, [gref, beta, 40]))
        pcw = weibull_pc(gref, beta, 0.0)
        mk, mk_lvl, _, _ = markov_stationary(pcw, CFG)
        frac = float(lr[:, 0].mean())
        mean_rev = math.exp(float(lr[:, 1].mean()))
        C.check("Langlauf (40 Läufe x 400 Umkehrpunkte, g70 = %.0f ms, Steilheit %.1f): Anteil richtiger Antworten %.4f, Markov-Kette %.4f, Theorie 0.7071 (Toleranz +-0.01); geometrisches Mittel der Umkehrpunkte %.2f ms" % (gref, beta, frac, mk, mean_rev),
                abs(frac - mk) < 0.01 and abs(frac - TARGET) < 0.012)

    # ------------------------------------------------------------------
    # 3. Randfälle
    # ------------------------------------------------------------------
    EDGE_JS = """([p, n, seed0, cfg]) => { const T = window.__test; const o = [];
      for (let i = 0; i < n; i++) { const r = T.simulate(() => p, seed0 + i, cfg); o.push([r.status, r.thresholdMs, r.nTrials, r.reversals.length, r.boundaryCount, r.trials.length]); } return o; }"""
    never = page.evaluate(EDGE_JS, [0.0, 500, 1, None])
    cn = Counter(r[0] for r in never)
    C.check("Hörer nie richtig (500 Läufe): immer Status ceiling, keine Schwelle, endet nach %d Durchgängen (20 -> 40 -> 50 ms, dann 4 Fehler bei 50 ms)" % never[0][2],
            cn == {"ceiling": 500} and all(r[1] is None for r in never) and len({r[2] for r in never}) == 1, dict(cn))
    always = page.evaluate(EDGE_JS, [1.0, 500, 1, None])
    ca = Counter(r[0] for r in always)
    C.check("Hörer immer richtig (500 Läufe): immer Status floor, keine Schwelle, endet nach %d Durchgängen (20 ms halbiert bis 0.25 ms, dann 3 weitere Schritte bei 0.25 ms)" % always[0][2],
            ca == {"floor": 500} and all(r[1] is None for r in always) and len({r[2] for r in always}) == 1, dict(ca))
    guess = page.evaluate(EDGE_JS, [0.5, 1000, 1, None])
    cg = Counter(r[0] for r in guess)
    thr_g = np.array([r[1] for r in guess if r[0] == "ok"])
    C.check("Ratehörer p = 0.5 (1000 Läufe): jeder Lauf endet (max. %d Durchgänge), kein Lauf mit Status ok hat weniger als 12 Umkehrpunkte" % max(r[2] for r in guess),
            max(r[2] for r in guess) <= 100 and all(r[3] == 12 for r in guess if r[0] == "ok"), dict(cg))
    below10 = int(np.sum(thr_g < 10))
    C.check("Ratehörer: höchstens 2 %% der Läufe liefern eine Schwelle unter 10 ms (%d von 1000; kleinster Wert %.1f ms). Anteil mit Schwelle überhaupt: %.0f %% (Median %.1f ms), Rest ceiling" % (below10, thr_g.min(), 100 * cg["ok"] / 1000, np.median(thr_g)),
            below10 <= 20, "bekannte Grenze: ein Ratehörer erhält in etwa einem Drittel der Läufe trotzdem eine Schwelle")
    py_guess = Counter()
    grng = np.random.default_rng(31)
    for _ in range(1000):
        py_guess[run_ref(CFG, lambda g, n: grng.random() < 0.5)["status"]] += 1
    C.check("Ratehörer: Verteilung der Stati in JS (%s) und Python (%s) ähnlich (Anteil ceiling +-6 Prozentpunkte)" % (dict(cg), dict(py_guess)),
            abs(cg["ceiling"] - py_guess["ceiling"]) < 60)
    # Höchstzahl der Durchgänge als Abbruchgrund
    mt = page.evaluate(SIM_JS.replace("T.simulate(pc, seed0 + i)", "T.simulate(pc, seed0 + i, {maxTrials: 12})"), [4.0, 3.0, 0.0, 200, 1])
    cm = Counter(r[0] for r in mt)
    C.check("Abbruch durch Höchstzahl (maxTrials auf 12 gesetzt, 200 Läufe): Status maxtrials, keine Schwelle, genau 12 Durchgänge", cm == {"maxtrials": 200} and all(r[1] is None and r[2] == 12 for r in mt), dict(cm))
    # Schwelle ausserhalb des Bereichs mit psychometrischem Hörer
    hi = page.evaluate(SIM_JS, [120.0, 3.0, 0.0, 300, 1])
    lo = page.evaluate(SIM_JS, [0.05, 3.0, 0.0, 300, 1])
    c_hi, c_lo = Counter(r[0] for r in hi), Counter(r[0] for r in lo)
    C.check("Schwelle weit über der Obergrenze (120 ms; Hörer rät im ganzen Bereich bis 50 ms): alle Läufe enden, Verteilung wie beim Ratehörer (%s)" % dict(c_hi),
            max(r[2] for r in hi) <= 100 and 0.55 * 300 <= c_hi["ceiling"] <= 0.85 * 300)
    C.check("Schwelle weit unter der Untergrenze (0.05 ms): Läufe enden mit floor (%s), keine Schwelle über 1 ms" % dict(c_lo),
            c_lo["floor"] > 0.9 * 300 and all(r[0] != "ok" or r[1] < 1 for r in lo))

    # Arithmetisches Mittel als Alternative (nur Information)
    C.info("Arithmetisches statt geometrisches Mittel liegt im Szenario 'Beispiel' bei %.3f statt %.3f (Verhältnis zur 70.7-%%-Lückendauer)" % (summary[0][5], summary[0][2]))
    C.info("Markov-Kette, Szenario 'Beispiel': stationärer Anteil richtiger Antworten %.3f, mittlerer log-Level %.2f ms (g70 = 4)" % (markov_stationary(weibull_pc(4.0, 3.0, 0.0), CFG)[0], markov_stationary(weibull_pc(4.0, 3.0, 0.0), CFG)[1]))

    C.check("Keine Konsolenfehler, keine externen oder fehlgeschlagenen Anfragen", not errors and not external, errors + external)
    browser.close()

C.finish()
