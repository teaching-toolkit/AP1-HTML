"""Ort des Flecks (signalentdeckung.html): nie in der Ausschlusszone um das Fixationskreuz.

Die Rückmeldung des Dozenten: Das Kreuz erzeugt ein helles Nachbild an seinem Ort. Der Fleck darf dort nie erscheinen.

Geprüft wird
 A. über 600 Seeds und alle Signal-Durchgänge (Probelauf 16 + zwei Blöcke zu 40 = 8 + 20 + 20 = 48 Signal-Durchgänge je Seed):
    Abstand zur Kreuzmitte >= Ausschlussradius, Lage im Ring, Mindestabstand zum Rand;
 B. Verteilung: Winkel gleichmässig (Chi-Quadrat), Radius gleichverteilt nach Fläche (KS), gleiche Verteilung in Probelauf,
    Block 1 und Block 2 (KS-Zweistichprobentest), jede Himmelsrichtung wird in jedem Block bedient;
 C. gerenderte Bilder: Der Fleck im Pixelbild liegt dort, wo die Position sagt, und hat im Kreuzbereich und in der
    Nachbild-Umgebung höchstens den dokumentierten Anteil seiner Amplitude;
 D. Rauschen und Maske sehen am Ort des Kreuzes nicht anders aus als sonst;
 E. das Kreuz selbst (Geometrie, Grauwert) und die dokumentierte Rechnung zum Radius;
 F. kompletter Lauf in der Oberfläche: gezeichneter Reiz stimmt mit dem Protokoll überein, Beispielbilder gleiche Regel.
Start: python3 -I tests/test_07_position.py
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from scipy import stats as sst
from scipy.ndimage import gaussian_filter
from playwright.sync_api import sync_playwright

import _helpers as H

C = H.Checker("Ort des Flecks und Ausschlusszone")

with sync_playwright() as pw:
    browser = pw.chromium.launch()
    page = browser.new_page()
    errors, external = [], []
    H.attach_collectors(page, errors, external)
    page.goto("file://" + H.PROJECT + "/signalentdeckung.html")
    assert page.evaluate("!!window.__test && window.__test.ready")
    CF = page.evaluate("window.__test.CONFIG")
    SIZE, EXCL, BMIN, BMAX, EDGE, ARM, CW, CGRAY, BW = CF["size"], CF["exclR"], CF["bandMin"], CF["bandMax"], CF["edgeMin"], CF["crossArm"], CF["crossWidth"], CF["crossGray"], CF["blobW"]
    NP, NB = CF["probeTrials"], CF["trialsPerBlock"]
    CEN = (SIZE - 1) / 2
    C.info("Konfiguration: Bild %d px, Ausschlussradius %d, Ring %d bis %d, Randabstand >= %d, Kreuz Arm %s Breite %s Grau %d, Probelauf %d, Block %d" % (SIZE, EXCL, BMIN, BMAX, EDGE, ARM, CW, CGRAY, NP, NB))

    # ------------------------------------------------------------------
    # A. Alle Signal-Positionen über viele Seeds
    # ------------------------------------------------------------------
    PLAN_JS = """([seeds, sizes]) => { const T = window.__test, out = [];
      for (const s of seeds) { sizes.forEach((n, k) => { const plan = T.makePlan(n, s * 7 + k * 1000003);
          const nsig = plan.filter(p => p.signal).length, ncatch = plan.filter(p => !p.signal && p.pos === null).length;
          out.push({ seed: s, kind: k, n: plan.length, nsig: nsig, ncatch: ncatch,
                     pos: plan.filter(p => p.signal).map(p => [p.pos.x, p.pos.y, p.pos.r, p.pos.theta, T.positionOk(p.pos) ? 1 : 0])}); }); }
      return out; }"""
    SEEDS = list(range(1, 601))
    plans = page.evaluate(PLAN_JS, [SEEDS, [NP, NB, NB]])
    allpos = np.array([p for pl in plans for p in pl["pos"]])
    dist = np.hypot(allpos[:, 0] - CEN, allpos[:, 1] - CEN)
    edge = np.minimum.reduce([allpos[:, 0] + 0.5, SIZE - 0.5 - allpos[:, 0], allpos[:, 1] + 0.5, SIZE - 0.5 - allpos[:, 1]])
    n_sig_expected = len(SEEDS) * (NP // 2 + 2 * (NB // 2))
    C.check("A1. %d Seeds x (Probelauf + 2 Blöcke): %d Signal-Positionen erzeugt (erwartet %d), je Plan genau die Hälfte Signal, Catch-Durchgänge ohne Position" % (len(SEEDS), len(allpos), n_sig_expected),
            len(allpos) == n_sig_expected and all(pl["nsig"] == pl["n"] // 2 and pl["ncatch"] == pl["n"] - pl["nsig"] for pl in plans))
    C.check("A2. Kein Fleck in der Ausschlusszone: kleinster Abstand zur Kreuzmitte %.2f px (Ausschlussradius %d); Anzahl Positionen mit Abstand < Radius: %d" % (dist.min(), EXCL, int((dist < EXCL).sum())), (dist < EXCL).sum() == 0 and dist.min() >= EXCL)
    C.check("A3. Alle Positionen im Ring: Abstand %.2f bis %.2f px (erlaubt %d bis %d); Sicherheitsabstand zwischen Zone und kleinstem Abstand %.2f px" % (dist.min(), dist.max(), BMIN, BMAX, dist.min() - EXCL), dist.min() >= BMIN - 1e-9 and dist.max() <= BMAX + 1e-9)
    C.check("A4. Mindestabstand zum Bildrand eingehalten: kleinster Randabstand %.2f px (>= %d, das sind %.1f Sigma des Flecks)" % (edge.min(), EDGE, edge.min() / BW), edge.min() >= EDGE - 1e-9)
    C.check("A5. positionOk() der Seite meldet für alle %d Positionen 'zulässig'" % len(allpos), bool(np.all(allpos[:, 4] == 1)))
    # Gegenprobe: positionOk lehnt Positionen in der Zone ab
    bad = page.evaluate("""() => { const T = window.__test, c = T.centerOf(%d); return [ T.positionOk({x: c, y: c}), T.positionOk({x: c + %d - 1, y: c}), T.positionOk({x: c + %d, y: c}), T.positionOk({x: c + %d, y: c}), T.positionOk({x: c + %d + 1, y: c}), T.positionOk({x: c + 60, y: c + 60}) ]; }""" % (SIZE, EXCL, BMIN, (BMIN + BMAX) // 2, BMAX))
    C.check("A6. positionOk als Gegenprobe: Mitte, Rand der Zone und Positionen ausserhalb des Rings werden abgelehnt, Ringpositionen angenommen: %s" % bad, bad == [False, False, True, True, False, False])

    # ------------------------------------------------------------------
    # B. Verteilung
    # ------------------------------------------------------------------
    ang = np.mod(allpos[:, 3], 2 * np.pi)
    nb = 12
    obs, _ = np.histogram(ang, bins=nb, range=(0, 2 * np.pi))
    chi = sst.chisquare(obs)
    C.check("B1. Winkel gleichmässig: Chi-Quadrat über %d Sektoren, p = %.3f (> 0.001), kleinster/grösster Sektor %d / %d von %d" % (nb, chi.pvalue, obs.min(), obs.max(), len(ang)), chi.pvalue > 0.001)
    a2, b2 = BMIN ** 2, BMAX ** 2
    ks = sst.kstest(dist, lambda r: np.clip((r ** 2 - a2) / (b2 - a2), 0, 1))
    C.check("B2. Radius im Ring gleichverteilt nach Fläche: KS p = %.3f (> 0.001), Mittel %.2f px (erwartet %.2f)" % (ks.pvalue, dist.mean(), (2 / 3) * (BMAX ** 3 - BMIN ** 3) / (BMAX ** 2 - BMIN ** 2)), ks.pvalue > 0.001)
    mc, ms = np.cos(ang).mean(), np.sin(ang).mean()
    C.check("B3. Kein Richtungsbias: Mittel von cos = %.4f, Mittel von sin = %.4f (Grenze 0.015)" % (mc, ms), abs(mc) < 0.015 and abs(ms) < 0.015)
    # Verteilung je Phase
    kinds = {0: "Probelauf", 1: "Block 1", 2: "Block 2"}
    by = {k: np.array([p for pl in plans if pl["kind"] == k for p in pl["pos"]]) for k in kinds}
    worst_p = 1.0
    for ka, kb in ((0, 1), (0, 2), (1, 2)):
        a_, b_ = by[ka], by[kb]
        pa = sst.ks_2samp(np.mod(a_[:, 3], 2 * np.pi), np.mod(b_[:, 3], 2 * np.pi)).pvalue
        pr = sst.ks_2samp(np.hypot(a_[:, 0] - CEN, a_[:, 1] - CEN), np.hypot(b_[:, 0] - CEN, b_[:, 1] - CEN)).pvalue
        worst_p = min(worst_p, pa, pr)
        C.info("   %s gegen %s: KS Winkel p = %.3f, KS Radius p = %.3f" % (kinds[ka], kinds[kb], pa, pr))
    C.check("B4. Gleiche Verteilung in Probelauf, Block 1 und Block 2 (KS-Zweistichprobentest, kleinstes p = %.3f > 0.001)" % worst_p, worst_p > 0.001)
    # Abdeckung: jede Himmelsrichtung wird in jedem Plan bedient (Sektoren-Aufteilung)
    qmin = {}
    for k in kinds:
        mins = []
        for pl in plans:
            if pl["kind"] != k:
                continue
            th = np.mod(np.array([p[3] for p in pl["pos"]]), 2 * np.pi)
            q, _ = np.histogram(th, bins=4, range=(0, 2 * np.pi))
            mins.append(q.min())
        qmin[k] = min(mins)
    C.check("B5. In jedem Plan kommen alle vier Quadranten vor (kleinste Anzahl je Quadrant: Probelauf %d, Block 1 %d, Block 2 %d; Erwartung bei Gleichverteilung %d bzw. %d)" % (qmin[0], qmin[1], qmin[2], NP // 8, NB // 8),
            qmin[0] >= 1 and qmin[1] >= (NB // 2) // 5 - 1 and qmin[2] >= (NB // 2) // 5 - 1)
    # Reihenfolge innerhalb eines Plans: keine feste Abfolge (Positionen nacheinander nicht sortiert)
    sorted_runs = 0
    for pl in plans:
        if pl["kind"] == 1:
            th = [p[3] % (2 * math.pi) for p in pl["pos"]]
            sorted_runs += all(th[i] <= th[i + 1] for i in range(len(th) - 1)) or all(th[i] >= th[i + 1] for i in range(len(th) - 1))
    C.check("B6. Reihenfolge der Positionen im Block ist gemischt (in %d von %d Blöcken nach Winkel sortiert)" % (sorted_runs, len([1 for pl in plans if pl['kind'] == 1])), sorted_runs == 0)
    # Gleiche Verteilung gilt auch für einzelne Durchgänge: erste Signal-Position jedes Blocks
    first = np.array([pl["pos"][0][3] % (2 * math.pi) for pl in plans if pl["kind"] in (1, 2)])
    obs1, _ = np.histogram(first, bins=8, range=(0, 2 * np.pi))
    C.check("B7. Auch die erste Fleckposition je Block ist über den Kreis gleichverteilt (Chi-Quadrat über 8 Sektoren, n = %d, p = %.3f > 0.001)" % (len(first), sst.chisquare(obs1).pvalue), sst.chisquare(obs1).pvalue > 0.001)

    # ------------------------------------------------------------------
    # C. Gerenderte Bilder: Fleck dort, wo die Position sagt; im Kreuzbereich praktisch nichts
    # ------------------------------------------------------------------
    AMP = 16.0
    RENDER_JS = """([seeds, amp, n]) => { const T = window.__test, out = [];
      for (const s of seeds) { const plan = T.makePlan(n, s);
        const p = plan.find(x => x.signal);
        const noise = T.makeStimulus(s, false, 0), sig = T.makeStimulus(s, true, amp, {pos: p.pos});
        const size = %d, diff = new Float32Array(size * size);
        for (let i = 0; i < size * size; i++) diff[i] = sig[4 * i] - noise[4 * i];
        out.push({pos: [p.pos.x, p.pos.y], diff: Array.from(diff)}); }
      return out; }""" % SIZE
    seeds_r = list(range(1, 301))
    ren = page.evaluate(RENDER_JS, [seeds_r, AMP, NB])
    yy, xx = np.mgrid[0:SIZE, 0:SIZE]
    rr = np.hypot(xx - CEN, yy - CEN)
    cross_mask = ((np.abs(xx - CEN) <= ARM) & (np.abs(yy - CEN) <= CW / 2 + 0.5)) | ((np.abs(yy - CEN) <= ARM) & (np.abs(xx - CEN) <= CW / 2 + 0.5))
    worst_cross, worst_zone22, max_loc_err = 0.0, 0.0, 0.0
    for r_ in ren:
        d = np.array(r_["diff"]).reshape(SIZE, SIZE)
        worst_cross = max(worst_cross, float(np.abs(d[cross_mask]).max()))
        worst_zone22 = max(worst_zone22, float(np.abs(d[rr <= 22]).max()))
        # Schwerpunkt des Flecks im Differenzbild (Differenz = Amplitude x Profil, nur Rundung als Rauschen)
        w = np.clip(d, 0, None) * (d > 0.25 * AMP)
        cx = (w * xx).sum() / w.sum()
        cy = (w * yy).sum() / w.sum()
        max_loc_err = max(max_loc_err, math.hypot(cx - r_["pos"][0], cy - r_["pos"][1]))
    C.check("C1. Gerendertes Signalbild (300 Seeds, Amplitude %.0f): Schwerpunkt des Flecks liegt höchstens %.2f px neben der angegebenen Position" % (AMP, max_loc_err), max_loc_err < 1.0)
    C.check("C2. Im Bereich des Kreuzes (%d Pixel) beträgt die Fleckhelligkeit höchstens %.2f Grauwerte (%.1f %% der Amplitude %.0f; Rundung auf 8 Bit eingerechnet)" % (int(cross_mask.sum()), worst_cross, 100 * worst_cross / AMP, AMP), worst_cross <= 0.03 * AMP + 1.0)
    C.check("C3. In der Nachbild-Umgebung (Radius 22 px um die Kreuzmitte = Kreuzarm + angenommenes Verschmieren) bleibt der Fleck unter der halben Amplitude (grösster Wert %.2f von %.0f)" % (worst_zone22, AMP), worst_zone22 < 0.5 * AMP)

    # ------------------------------------------------------------------
    # D. Rauschen und Maske am Ort des Kreuzes
    # ------------------------------------------------------------------
    NOISE_JS = """(seeds) => { const T = window.__test, c = %d, out = [];
      for (const s of seeds) { const im = T.makeStimulus(s, false, 0), size = %d;
        let sc = 0, nc = 0, s2 = 0, no = 0, so = 0, ss2 = 0;
        for (let y = 0; y < size; y++) for (let x = 0; x < size; x++) { const v = im[4 * (y * size + x)], d = Math.hypot(x - c, y - c);
          if (d <= 12) { sc += v; s2 += v * v; nc++; } else if (d >= 30) { so += v; ss2 += v * v; no++; } }
        out.push([sc, s2, nc, so, ss2, no]); }
      return out; }""" % (CEN, SIZE)
    nz = np.array(page.evaluate(NOISE_JS, list(range(1, 401))))
    mc_, vc_ = nz[:, 0].sum() / nz[:, 2].sum(), nz[:, 1].sum() / nz[:, 2].sum() - (nz[:, 0].sum() / nz[:, 2].sum()) ** 2
    mo_, vo_ = nz[:, 3].sum() / nz[:, 5].sum(), nz[:, 4].sum() / nz[:, 5].sum() - (nz[:, 3].sum() / nz[:, 5].sum()) ** 2
    se_m = math.sqrt(vo_ / nz[:, 2].sum())
    C.check("D1. Rauschbild: Mittel am Ort des Kreuzes (r <= 12) %.2f, sonst (r >= 30) %.2f, Unterschied %.2f (Standardfehler %.2f); SD %.2f gegenüber %.2f" % (mc_, mo_, mc_ - mo_, se_m, math.sqrt(vc_), math.sqrt(vo_)),
            abs(mc_ - mo_) < 4 * se_m and abs(math.sqrt(vc_) / math.sqrt(vo_) - 1) < 0.02)
    MASK_JS = """(seeds) => { const T = window.__test, c = %d, out = [];
      for (const s of seeds) { const im = T.makeMask(s), size = %d; let sc = 0, nc = 0, so = 0, no = 0;
        for (let y = 0; y < size; y++) for (let x = 0; x < size; x++) { const v = im[4 * (y * size + x)], d = Math.hypot(x - c, y - c);
          if (d <= 12) { sc += v; nc++; } else if (d >= 30) { so += v; no++; } }
        out.push([sc / nc, so / no]); }
      return out; }""" % (CEN, SIZE)
    mk = np.array(page.evaluate(MASK_JS, list(range(1, 1201))))
    diffm = mk[:, 0].mean() - mk[:, 1].mean()
    se_mask = math.sqrt(mk[:, 0].var(ddof=1) / len(mk) + mk[:, 1].var(ddof=1) / len(mk))
    C.check("D2. Maske (1200 Seeds): mittlere Helligkeit am Ort des Kreuzes %.2f, sonst %.2f, Unterschied %.2f (Standardfehler %.2f); die Maske enthält keinen Fleck und keine Sonderstelle in der Mitte" % (mk[:, 0].mean(), mk[:, 1].mean(), diffm, se_mask), abs(diffm) < 4 * se_mask)

    # ------------------------------------------------------------------
    # E. Das Kreuz und die dokumentierte Rechnung
    # ------------------------------------------------------------------
    cross_px = page.evaluate("""() => { const c = document.getElementById('cv-ex'), g = c.getContext('2d').getImageData(0, 0, %d, %d).data, out = [];
      for (let y = 0; y < %d; y++) for (let x = 0; x < %d; x++) { const v = g[4 * (y * %d + x)]; if (v !== %d) out.push([x, y, v]); }
      return out; }""" % (SIZE, SIZE, SIZE, SIZE, SIZE, CF["meanGray"]))
    cp = np.array(cross_px)
    ok_cross = len(cp) > 0 and np.all(cp[:, 2] == CGRAY) and np.max(np.hypot(cp[:, 0] - CEN, cp[:, 1] - CEN)) <= ARM + 0.8 and cp[:, 0].min() >= SIZE / 2 - ARM and cp[:, 0].max() <= SIZE / 2 + ARM - 1
    C.check("E1. Beispielbild im Ruhezustand zeigt nur das Kreuz: %d Pixel, alle Grau %d, Ausdehnung x %d..%d, y %d..%d (Bildmitte %.1f), %.1f %% der Fläche" % (len(cp), CGRAY, cp[:, 0].min(), cp[:, 0].max(), cp[:, 1].min(), cp[:, 1].max(), CEN, 100 * len(cp) / SIZE ** 2), ok_cross)
    SMEAR = 17.0   # Annahme (README): Nachbild-Verschmieren durch Augenbewegungen, ca. 0.5 Grad am Desktop
    half_max = math.sqrt(2 * math.log(2)) * BW
    need = ARM + SMEAR + half_max
    C.check("E2. Rechnung zum Radius: Kreuzarm %s + Verschmieren (Annahme) %.0f + Halbwertsradius des Flecks %.1f = %.1f px <= Ausschlussradius %d <= Ringbeginn %d" % (ARM, SMEAR, half_max, need, EXCL, BMIN), need <= EXCL <= BMIN)
    C.check("E3. Kreuz ist zurückhaltend: Kontrast %+d Grauwerte (alt: Schwarz, %d), Fläche %d Pixel (alt: Glyph 28 px fett, ca. 130 Pixel), Dauer %d ms (alt 500)" % (CGRAY - CF["meanGray"], 0 - CF["meanGray"], len(cp), CF["fixMs"]), CGRAY > CF["meanGray"] and CF["fixMs"] <= 400)
    C.check("E4. Der Fleck ist nie die Mitte: Ringradius %d..%d px entspricht %.0f bis %.0f %% der halben Bildkante" % (BMIN, BMAX, 100 * BMIN / (SIZE / 2), 100 * BMAX / (SIZE / 2)), BMIN > EXCL)

    # ------------------------------------------------------------------
    # F. Oberfläche: gezeichneter Reiz stimmt mit dem Protokoll überein
    # ------------------------------------------------------------------
    CAPTURE_JS = H.MULBERRY_JS + """
window.__cap = [];
(function () { const orig = CanvasRenderingContext2D.prototype.putImageData;
  CanvasRenderingContext2D.prototype.putImageData = function (img, x, y) {
    if (this.canvas && this.canvas.id === 'cv') { const n = img.width, b = 8, g = n / b, m = new Array(g * g).fill(0);
      for (let yy = 0; yy < n; yy++) for (let xx = 0; xx < n; xx++) m[Math.floor(yy / b) * g + Math.floor(xx / b)] += img.data[4 * (yy * n + xx)] / (b * b);
      window.__cap.push(m); }
    return orig.apply(this, arguments); }; })();
"""
    n_ok = n_tot = n_catch_ok = n_catch = 0
    worst_err = 0.0
    max_catch = 0.0
    NOISE_SD_F = 3.5 * math.sqrt(1 / (4 * math.pi * 1.75 ** 2))   # SD der geglätteten Blockmittel bei reinem Rauschen (Grauwerte)
    seeds_ui = list(range(101, 113))
    for sd in seeds_ui:
        ctx = browser.new_context(viewport={"width": 1000, "height": 900})
        pg = ctx.new_page()
        errs, ext = [], []
        H.attach_collectors(pg, errs, ext)
        pg.add_init_script("window.__test = {instant:true, seed:%d, observer: function(t){ return t.signal; }};\n" % sd + CAPTURE_JS)
        pg.goto("file://" + H.PROJECT + "/signalentdeckung.html")
        pg.evaluate("(() => { const e = document.getElementById('diff'); e.value = 1; e.dispatchEvent(new Event('input')); })()")
        pg.click("#btn-probe"); pg.wait_for_selector("#probe-res:not([hidden])", timeout=20000)
        pg.click("#btn-lock"); pg.click("#btn-block-start"); pg.wait_for_selector("#view-pre:not([hidden])", timeout=30000)
        pg.click("#btn-block-start"); pg.wait_for_selector("#view-result:not([hidden])", timeout=30000)
        log = pg.evaluate("window.__test.log")
        cap = pg.evaluate("window.__cap")
        stims = cap[0::2]
        masks = cap[1::2]
        if len(stims) != len(log) or len(masks) != len(log):
            C.check("F0. Seed %d: %d Reize und %d Masken gezeichnet, %d Protokolleinträge" % (sd, len(stims), len(masks), len(log)), False)
            continue
        for lg, m in zip(log, stims):
            # angepasster Filter: 8x8-Blockmittel (20 x 20) mit Gauss (sigma 14 px = 1.75 Blöcke) glätten
            f = gaussian_filter(np.array(m).reshape(20, 20) - 128.0, sigma=1.75, mode="constant", cval=0.0)
            cy_, cx_ = np.unravel_index(np.argmax(f), f.shape)
            bx, by_ = cx_ * 8 + 3.5, cy_ * 8 + 3.5
            if lg["signal"]:
                n_tot += 1
                e = math.hypot(bx - lg["pos"]["x"], by_ - lg["pos"]["y"])
                worst_err = max(worst_err, e)
                n_ok += e <= 12
            else:
                n_catch += 1
                max_catch = max(max_catch, f.max())
                n_catch_ok += f.max() < 5 * NOISE_SD_F
        C.check("F1. Seed %d: Fehlermeldungen/externe Anfragen leer" % sd, not errs and not ext, errs + ext)
        ctx.close()
    C.check("F2. In der Oberfläche gezeichnete Reize (%d Signal-Durchgänge aus %d Läufen, Amplitude 16): Das Maximum des angepassten Filters liegt bei %.1f %% höchstens 12 px neben der protokollierten Fleckposition (grösster Abstand %.1f px)" % (n_tot, len(seeds_ui), 100 * n_ok / max(1, n_tot), worst_err), n_ok / max(1, n_tot) >= 0.995)
    C.check("F3. Gezeichnete Catch-Bilder (%d): Filtermaximum höchstens %.2f Grauwerte (5 Standardabweichungen des Rauschens = %.2f; ein Fleck der Amplitude 16 ergibt etwa 8), also kein verstecktes Signal, auch nicht in der Mitte" % (n_catch, max_catch, 5 * NOISE_SD_F), n_catch_ok == n_catch)

    # Beispielbilder: gleiche Regel, 200 Klicks
    pg = browser.new_page()
    errs, ext = [], []
    H.attach_collectors(pg, errs, ext)
    pg.add_init_script("window.__test = {instant:true, seed:7};")
    pg.goto("file://" + H.PROJECT + "/signalentdeckung.html")
    ex = []
    for _ in range(200):
        pg.click("#btn-ex-sig")
        ex.append(pg.evaluate("window.__test.lastExample.pos"))
    d_ex = np.array([math.hypot(p["x"] - CEN, p["y"] - CEN) for p in ex])
    ok_all = all(pg.evaluate("(p) => window.__test.positionOk(p)", p) for p in ex[:50])
    th = np.array([p["theta"] for p in ex])
    dth = np.abs(((np.diff(th) + 3 * np.pi) % (2 * np.pi)) - np.pi)
    C.check("F4. Beispielbilder (200 Klicks): Abstand zur Mitte %.1f bis %.1f px (Zone %d), alle zulässig; aufeinanderfolgende Beispiele mindestens %.0f Grad auseinander" % (d_ex.min(), d_ex.max(), EXCL, math.degrees(dth.min())), d_ex.min() >= EXCL and ok_all and dth.min() >= math.radians(79))
    C.check("F5. Keine Konsolenfehler, keine externen oder fehlgeschlagenen Anfragen", not errors and not errs and not external and not ext, errors + errs + external + ext)
    pg.close()

    # ------------------------------------------------------------------
    # Bilder für den Testbericht (Ausschlusszone, Verteilung)
    # ------------------------------------------------------------------
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        from matplotlib.patches import Circle, Rectangle

        fig, ax = plt.subplots(1, 2, figsize=(9.6, 4.6), dpi=110)
        a = ax[0]
        a.set_aspect("equal"); a.set_xlim(0, SIZE); a.set_ylim(SIZE, 0)
        a.add_patch(Rectangle((0, 0), SIZE, SIZE, fc="#808080", ec="#333", lw=1))
        a.add_patch(Rectangle((EDGE, EDGE), SIZE - 2 * EDGE, SIZE - 2 * EDGE, fc="none", ec="#ffd966", lw=1, ls=":"))
        a.add_patch(Circle((CEN + .5, CEN + .5), BMAX, fc="none", ec="#7fd1ae", lw=1.5))
        a.add_patch(Circle((CEN + .5, CEN + .5), BMIN, fc="none", ec="#7fd1ae", lw=1.5))
        a.add_patch(Circle((CEN + .5, CEN + .5), EXCL, fc="#c0392b", alpha=.35, ec="#c0392b", lw=1.5))
        a.add_patch(Circle((CEN + .5, CEN + .5), 22, fc="none", ec="#ffffff", lw=1, ls="--"))
        a.plot([SIZE / 2 - ARM, SIZE / 2 + ARM], [SIZE / 2, SIZE / 2], color="white", lw=2)
        a.plot([SIZE / 2, SIZE / 2], [SIZE / 2 - ARM, SIZE / 2 + ARM], color="white", lw=2)
        one = np.array(plans[0]["pos"] + plans[1]["pos"] + plans[2]["pos"])
        a.scatter(one[:, 0], one[:, 1], s=16, c="#1f5fbf", zorder=5)
        a.set_title("Ein Lauf: 48 Fleckpositionen (blau)\nrot: Ausschlusszone r = %d, grün: Ring %d bis %d,\ngelb: Randabstand %d, weiss gestrichelt: r = 22" % (EXCL, BMIN, BMAX, EDGE), fontsize=8)
        a.tick_params(labelsize=7)
        b = ax[1]
        b.set_aspect("equal"); b.set_xlim(0, SIZE); b.set_ylim(SIZE, 0)
        b.add_patch(Rectangle((0, 0), SIZE, SIZE, fc="#f0f0f0", ec="#333", lw=1))
        b.scatter(allpos[::6, 0], allpos[::6, 1], s=2, c="#1f5fbf", alpha=.5)
        b.add_patch(Circle((CEN + .5, CEN + .5), EXCL, fc="#c0392b", alpha=.35, ec="#c0392b", lw=1))
        b.set_title("%d Positionen aus %d Seeds (jede 6. gezeigt)" % (len(allpos), len(SEEDS)), fontsize=8)
        b.tick_params(labelsize=7)
        fig.tight_layout()
        fig.savefig(os.path.join(H.SHOTS, "sdt_ausschlusszone.png"))
        C.info("Bild geschrieben: screenshots/sdt_ausschlusszone.png")
    except Exception as e:  # nur Dokumentationsbild
        C.info("Bild nicht geschrieben: %r" % e)
    browser.close()

C.finish()
