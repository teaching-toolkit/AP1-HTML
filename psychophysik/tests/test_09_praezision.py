"""Präzision von d' und c bei der gewählten Durchgangszahl (signalentdeckung.html).

Simulierte Beobachter mit bekanntem d' und c (Gauss-Modell, H = Phi(d'/2 - c), FA = Phi(-d'/2 - c)). Die Schätzung läuft über
die echte Funktion computeSDT der Seite (mit Korrektur bei Rate 0 oder 1). Je Zeile mindestens 2000 Läufe (hier 20000).
Berichtet werden
 - SD der Schätzungen von d' und c je Block,
 - Anteil der Blöcke bzw. Personen, in denen die Korrektur wegen Rate 0 oder 1 greift,
 - ob 'Verpasser teuer' gegenüber 'Fehlalarm teuer' pro Person noch erkennbar ist: Differenz der c-Werte (Delta c = c_F - c_V)
   im Verhältnis zu ihrer Streuung, Anteil der Personen mit Delta c > 0 und mit Delta c > 0.3,
 - den Vergleich verschiedener Durchgangszahlen je Block (20, 30, 40, 50) und die Gruppe aus 5 Personen,
 - die Rechendauer-Seite der Abwägung steht in test_08_dauer.py.
Wahre Verschiebung: 'optimal' = ln(beta)/d' mit beta = 0.4 bzw. 2.5 (aus der Auszahlungsmatrix, gleiche Häufigkeit Signal/Catch),
'halb' = die Hälfte davon (Menschen verschieben meist weniger als optimal; das ist eine Annahme, keine Messung), 'keine' = 0.
Start: python3 -I tests/test_09_praezision.py
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from scipy.stats import norm
from playwright.sync_api import sync_playwright

import _helpers as H

C = H.Checker("Präzision der Schätzungen (Simulation)")
rng = np.random.default_rng(20261015)
R = 20000

SDT_JS = """(rows) => rows.map(r => { const o = window.__test.computeSDT(r[0], r[1], r[2], r[3]); return [o.dprime, o.c, o.corrected ? 1 : 0]; })"""


def ref(h, nS, f, nN):
    """Unabhängige numpy-Referenz derselben Schätzung."""
    H0, F0 = h / nS, f / nN
    corr = (H0 == 0) | (H0 == 1) | (F0 == 0) | (F0 == 1)
    Hh = np.where(corr, (h + .5) / (nS + 1), H0)
    Ff = np.where(corr, (f + .5) / (nN + 1), F0)
    zH, zF = norm.ppf(Hh), norm.ppf(Ff)
    return zH - zF, -.5 * (zH + zF), corr


with sync_playwright() as pw:
    browser = pw.chromium.launch()
    page = browser.new_page()
    errors, external = [], []
    H.attach_collectors(page, errors, external)
    page.goto("file://" + H.PROJECT + "/signalentdeckung.html")
    assert page.evaluate("!!window.__test && window.__test.ready")
    NB = page.evaluate("window.__test.CONFIG.trialsPerBlock")
    PAY = page.evaluate("window.__test.CONFIG.payoff")

    def beta(p):
        return (p["cr"] - p["fa"]) / (p["hit"] - p["miss"])

    LNB_V, LNB_F = math.log(beta(PAY["liberal"])), math.log(beta(PAY["konservativ"]))
    C.info("Auszahlung: beta(Verpasser teuer) = %.2f, beta(Fehlalarm teuer) = %.2f, ln beta = %.3f / %.3f" % (beta(PAY["liberal"]), beta(PAY["konservativ"]), LNB_V, LNB_F))

    def block(d, c, n):
        nS = nN = n // 2
        h = rng.binomial(nS, norm.cdf(d / 2 - c), R)
        f = rng.binomial(nN, norm.cdf(-d / 2 - c), R)
        out = np.array(page.evaluate(SDT_JS, [[int(a), int(nS - a), int(b), int(nN - b)] for a, b in zip(h, f)]))
        rd, rc, rk = ref(h, nS, f, nN)
        assert np.max(np.abs(out[:, 0] - rd)) < 1e-9 and np.max(np.abs(out[:, 1] - rc)) < 1e-9 and np.all(out[:, 2] == rk)
        return out[:, 0], out[:, 1], out[:, 2] == 1

    results = {}

    def scenario(n, d, mode):
        s = {"optimal": 1.0, "halb": 0.5, "keine": 0.0}[mode]
        cV, cF = s * LNB_V / d, s * LNB_F / d      # Verpasser teuer: negativ (liberal), Fehlalarm teuer: positiv
        dV, cVe, kV = block(d, cV, n)
        dF, cFe, kF = block(d, cF, n)
        dc = cFe - cVe
        return dict(n=n, d=d, mode=mode, shift=abs(cF), sd_d=np.r_[dV, dF].std(ddof=1), sd_c=np.r_[cVe, cFe].std(ddof=1),
                    bias_d=np.r_[dV, dF].mean() - d, corr_block=np.r_[kV, kF].mean(), corr_any=(kV | kF).mean(),
                    dc_mean=dc.mean(), dc_sd=dc.std(ddof=1), dc_ratio=dc.mean() / dc.std(ddof=1), p_pos=(dc > 0).mean(), p_03=(dc > 0.3).mean(), dc=dc, dV=dV, dF=dF)

    print()
    print("Gewählte Durchgangszahl: %d je Block (%d Signal + %d Catch), %d Läufe je Zeile" % (NB, NB // 2, NB // 2, R))
    print("%4s %4s %-8s %5s | %6s %6s | %8s %9s | %7s %6s %6s | %7s %8s" % ("n", "d'", "Verschieb", "|c|", "SD d'", "SD c", "korr/Blk", "korr>=1/2", "mittl.", "SD", "mittl/SD", "dc>0", "dc>0.3"))
    for d in (1.0, 1.5, 2.0):
        for mode in ("optimal", "halb", "keine"):
            r = scenario(NB, d, mode)
            results[(NB, d, mode)] = r
            print("%4d %4.1f %-8s %5.2f | %6.2f %6.2f | %7.1f%% %8.1f%% | %7.2f %6.2f %6.2f | %6.1f%% %7.1f%%" % (r["n"], d, mode, r["shift"], r["sd_d"], r["sd_c"], 100 * r["corr_block"], 100 * r["corr_any"], r["dc_mean"], r["dc_sd"], r["dc_ratio"], 100 * r["p_pos"], 100 * r["p_03"]))

    print()
    print("Vergleich der Durchgangszahl je Block (d' = 1.5):")
    print("%4s %-8s | %6s %6s | %8s %9s | %6s %8s | %7s | %s" % ("n", "Verschieb", "SD d'", "SD c", "korr/Blk", "korr>=1/2", "mittl/SD", "dc>0", "Dauer*", "(*Aufgabenzeit, 2.4 s je Durchgang + Probelauf 16)"))
    for n in (20, 30, 40, 50):
        for mode in ("optimal", "halb"):
            r = results.get((n, 1.5, mode)) or scenario(n, 1.5, mode)
            results[(n, 1.5, mode)] = r
            t = (16 + 2 * n) * 2.4 / 60
            print("%4d %-8s | %6.2f %6.2f | %7.1f%% %8.1f%% | %6.2f %7.1f%% | %5.1f min" % (n, mode, r["sd_d"], r["sd_c"], 100 * r["corr_block"], 100 * r["corr_any"], r["dc_ratio"], 100 * r["p_pos"], t))

    # Gruppe aus 5 Personen: Mittelung verkleinert die Streuung
    print()
    r = results[(NB, 1.5, "halb")]
    k = len(r["dc"]) // 5
    g_dc = r["dc"][:k * 5].reshape(k, 5).mean(axis=1)
    g_d = np.r_[r["dV"], r["dF"]][:2 * (len(r["dV"]) // 5) * 5]
    g_dm = np.r_[r["dV"][:k * 5].reshape(k, 5).mean(axis=1)]
    print("Gruppe aus 5 Personen (d' = 1.5, halbe Verschiebung, %d Gruppen): SD des Gruppenmittels von d' (Block V) %.2f (Einzelperson %.2f), Gruppenmittel von Delta c: %.2f +- %.2f, in %.1f %% der Gruppen > 0" % (k, g_dm.std(ddof=1), r["dV"].std(ddof=1), g_dc.mean(), g_dc.std(ddof=1), 100 * (g_dc > 0).mean()))

    # ------------------------------------------------------------------
    # Prüfungen (Toleranzen dokumentieren die erwartete Grössenordnung, sie sind keine Qualitätsurteile)
    # ------------------------------------------------------------------
    r = results[(NB, 1.5, "optimal")]
    C.check("Streuung (SD) einer Einzelschätzung bei %d + %d Durchgängen, d' = 1.5: d' %.2f (Erwartung 0.4 bis 0.6), c %.2f (0.2 bis 0.75, wächst mit der Verschiebung)" % (NB // 2, NB // 2, r["sd_d"], r["sd_c"]), 0.4 < r["sd_d"] < 0.6 and 0.2 < r["sd_c"] < 0.75)
    C.check("Bei wahrem c = 0 greift die Korrektur selten: %.1f %% der Blöcke (d' = 1.5), %.1f %% (d' = 1.0)" % (100 * results[(NB, 1.5, "keine")]["corr_block"], 100 * results[(NB, 1.0, "keine")]["corr_block"]), results[(NB, 1.5, "keine")]["corr_block"] < 0.05)
    C.check("Bei voller (optimaler) Verschiebung greift die Korrektur in %.1f %% der Blöcke und bei %.1f %% der Personen in mindestens einem Block (d' = 1.5)" % (100 * r["corr_block"], 100 * r["corr_any"]), 0.08 < r["corr_block"] < 0.30)
    h = results[(NB, 1.5, "halb")]
    C.check("Unterschied zwischen den Blöcken pro Person (halbe Verschiebung, d' = 1.5): mittleres Delta c %.2f, SD %.2f, Verhältnis %.2f; in %.1f %% der Personen hat Delta c das richtige Vorzeichen, in %.1f %% ist es grösser als 0.3" % (h["dc_mean"], h["dc_sd"], h["dc_ratio"], 100 * h["p_pos"], 100 * h["p_03"]), h["p_pos"] > 0.93 and h["dc_ratio"] > 1.5)
    o = results[(NB, 1.5, "optimal")]
    C.check("Bei voller Verschiebung wird der Unterschied pro Person fast immer erkannt: Verhältnis %.2f, richtiges Vorzeichen bei %.1f %%" % (o["dc_ratio"], 100 * o["p_pos"]), o["p_pos"] > 0.99)
    k0 = results[(NB, 1.5, "keine")]
    C.check("Ohne wahre Verschiebung (c gleich in beiden Blöcken): Delta c im Mittel %.3f, richtiges Vorzeichen bei %.1f %% (Zufall), Delta c > 0.3 bei %.1f %% (so oft würde man einen Unterschied zu Unrecht sehen)" % (k0["dc_mean"], 100 * k0["p_pos"], 100 * k0["p_03"]), abs(k0["dc_mean"]) < 0.02 and 0.45 < k0["p_pos"] < 0.52)
    C.check("Gruppe aus 5 Personen: SD des Mittels von d' %.2f statt %.2f je Person (Faktor %.2f, erwartet 1/sqrt(5) = %.2f)" % (g_dm.std(ddof=1), r["dV"].std(ddof=1), g_dm.std(ddof=1) / h["dV"].std(ddof=1), 1 / math.sqrt(5)), abs(g_dm.std(ddof=1) / h["dV"].std(ddof=1) - 1 / math.sqrt(5)) < 0.03)
    C.check("Mehr Durchgänge verkleinern die Streuung: SD von d' bei n = 20 / 30 / 40 / 50: %s" % " / ".join("%.2f" % results[(n, 1.5, "halb")]["sd_d"] for n in (20, 30, 40, 50)),
            all(results[(a, 1.5, "halb")]["sd_d"] > results[(b, 1.5, "halb")]["sd_d"] for a, b in ((20, 30), (30, 40), (40, 50))))
    C.check("Die Korrekturhäufigkeit sinkt mit n (volle Verschiebung, d' = 1.5): %s" % " / ".join("%.0f %%" % (100 * results[(n, 1.5, "optimal")]["corr_block"]) for n in (20, 30, 40, 50)),
            all(results[(a, 1.5, "optimal")]["corr_block"] > results[(b, 1.5, "optimal")]["corr_block"] for a, b in ((20, 30), (30, 40), (40, 50))))

    # ------------------------------------------------------------------
    # Ideal-Beobachter mit unbekanntem Ort (Begründung der Reglerstartstellung 40)
    # ------------------------------------------------------------------
    try:
        from scipy.signal import fftconvolve
        rg = np.random.default_rng(7)
        size, sig, sb = 160, 28.0, 14.0
        cen = (size - 1) / 2
        yy, xx = np.mgrid[0:size, 0:size]
        kk = 60
        ky, kx = np.mgrid[-kk:kk + 1, -kk:kk + 1]
        ker = np.exp(-(kx ** 2 + ky ** 2) / (2 * sb ** 2))
        E = float(np.sum(ker ** 2))
        cand = np.array([(int(round(cen + r_ * math.cos(t))), int(round(cen + r_ * math.sin(t)))) for t in np.linspace(0, 2 * math.pi, 72, endpoint=False) for r_ in (44, 48, 52)])
        CF = page.evaluate("window.__test.CONFIG")

        def ideal(a, n=1200):
            ks, kn, us, un = [], [], [], []
            for _ in range(n):
                th = rg.uniform(0, 2 * math.pi)
                r_ = math.sqrt(rg.uniform(CF["bandMin"] ** 2, CF["bandMax"] ** 2))
                px, py = int(round(cen + r_ * math.cos(th))), int(round(cen + r_ * math.sin(th)))
                for sf in (0, 1):
                    img = rg.normal(0, sig, (size, size))
                    if sf:
                        img = img + a * np.exp(-((xx - (cen + r_ * math.cos(th))) ** 2 + (yy - (cen + r_ * math.sin(th))) ** 2) / (2 * sb ** 2))
                    m = fftconvolve(img, ker, mode="same")
                    llr = math.log(np.mean(np.exp(a * m[cand[:, 1], cand[:, 0]] / sig ** 2 - a * a * E / (2 * sig ** 2))))
                    (ks if sf else kn).append(m[py, px]); (us if sf else un).append(llr)
            dk = (np.mean(ks) - np.mean(kn)) / math.sqrt(.5 * (np.var(ks) + np.var(kn)))
            du = (np.mean(us) - np.mean(un)) / math.sqrt(.5 * (np.var(us) + np.var(un)))
            return dk, du

        amp = lambda v: CF["ampMax"] * (CF["ampMin"] / CF["ampMax"]) ** ((v - 1) / 99)
        old_known = amp(50) * math.sqrt(E) / sig
        dk40, du40 = ideal(amp(CF["defaultSlider"]))
        dk50, du50 = ideal(amp(50))
        print()
        print("Idealbeobachter (Modell, keine Menschen): Reglerstellung 50: Ort bekannt d' = %.2f, Ort unbekannt (Ring) %.2f; Reglerstellung %d: Ort bekannt %.2f, unbekannt %.2f; frühere Startstellung 50 mit Fleck in der Mitte: d' = %.2f" % (dk50, du50, CF["defaultSlider"], dk40, du40, old_known))
        C.check("Startstellung %d des Reglers hält die Schwierigkeit für einen Idealbeobachter mit unbekanntem Fleckort (d' %.2f) nahe an der früheren Startstellung 50 mit Fleck in der Mitte (d' %.2f), Toleranz 0.5" % (CF["defaultSlider"], du40, old_known), abs(du40 - old_known) < 0.5)
        C.check("Unbekannter Ort senkt die Entdeckbarkeit bei gleicher Amplitude (Reglerstellung 50: d' %.2f statt %.2f, Faktor %.2f)" % (du50, dk50, du50 / dk50), du50 < 0.8 * dk50)
    except Exception as e:
        C.check("Idealbeobachter-Simulation lief durch: %r" % e, False)

    C.check("Keine Konsolenfehler, keine externen oder fehlgeschlagenen Anfragen", not errors and not external, errors + external)
    browser.close()

C.finish()
