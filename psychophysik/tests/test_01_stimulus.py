"""Stimulus-Genauigkeit der Lückenerkennung (schwelle.html).

Prüft den Generator über den Testhaken window.__test (generateBurst, generateTrial,
renderOffline = Wiedergabeweg über einen OfflineAudioContext):
- Lückenlänge in Samples exakt, Pegel in der Lücke exakt 0
- Rauschpegel ausserhalb (RMS), Verteilung, Weissheit, keine Übersteuerung
- Rampen vorhanden, Hüllkurve gegen unabhängige Python-Formel, kein Sprung grösser als die Rampe erlaubt
- Negativkontrolle: ohne Rampe schlägt die Sprung-Prüfung an
- Trial-Puffer: Zeitachse, Lückenposition, Intervallzuordnung, Reproduzierbarkeit mit Seed
- Offline-Rendering entspricht Puffer x Gain
Start: python3 -I tests/test_01_stimulus.py
"""
import base64
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from scipy import signal as sps
from scipy import stats as sst
from playwright.sync_api import sync_playwright

import _helpers as H

C = H.Checker("Stimulus-Generator")
SIGMA = 0.15
RAMP_MS = 0.5
EDGE_MS = 10.0


def rnd(x):  # wie Math.round in JS (Halbwerte nach oben)
    return int(math.floor(x + 0.5))


def env_ref(total, E, gs, G, R):
    env = np.ones(total)
    k = np.arange(E)
    w = 0.5 * (1 - np.cos(np.pi * (k + 0.5) / E))
    env[:E] = w
    env[total - E:] = w[::-1]
    if G > 0:
        k = np.arange(R)
        d = 0.5 * (1 + np.cos(np.pi * (k + 0.5) / R))
        env[gs - R:gs] = d
        env[gs + G:gs + G + R] = 1 - d
        env[gs:gs + G] = 0
    return env


B64_JS = """(f32) => { const u8 = new Uint8Array(f32.buffer, f32.byteOffset, f32.byteLength); let s = '';
  for (let i = 0; i < u8.length; i += 0x8000) s += String.fromCharCode.apply(null, u8.subarray(i, i + 0x8000)); return btoa(s); }"""


def f32(b64):
    return np.frombuffer(base64.b64decode(b64), dtype="<f4").astype(np.float64)


BURST_JS = """([sr, gapMs, gapStartMs, seed, rampMs]) => {
  const T = window.__test;
  const b64 = %s;
  const o = {gapMs, gapStartMs, seed};
  if (rampMs !== null) o.rampMs = rampMs;
  const b = T.generateBurst(sr, o);
  return {data: b64(b.data), env: b64(b.env), total: b.total, gapSamples: b.gapSamples,
          gapStart: b.gapStart, rampSamples: b.rampSamples, edgeSamples: b.edgeSamples};
}""" % B64_JS

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page()
    errors, external = [], []
    H.attach_collectors(page, errors, external)
    page.goto("file://" + H.PROJECT + "/schwelle.html")
    assert page.evaluate("!!window.__test && window.__test.ready")

    # ------------------------------------------------------------------
    # 1. Einzelner Burst: Raster aus Abtastraten x Lückenlängen
    # ------------------------------------------------------------------
    rates = [44100, 48000, 96000]
    gaps = [0.25, 0.5, 1, 2, 3, 5, 10, 20, 50]
    rng = np.random.default_rng(123)
    n_cases = 0
    bad = {"len": [], "zero": [], "outside_zero": [], "env": [], "rms": [], "ramp": [], "step": [], "clip": [], "noise_same": []}
    worst_rms = 0.0
    worst_env = 0.0
    for sr in rates:
        for g in gaps:
            for rep in range(3):
                gs_ms = float(rng.uniform(120, 220))
                seed = int(rng.integers(1, 2**31 - 1))
                r = page.evaluate(BURST_JS, [sr, g, gs_ms, seed, None])
                d = f32(r["data"])
                e = f32(r["env"])
                n_cases += 1
                G_exp = max(1, rnd(g * sr / 1000))
                R_exp = max(2, rnd(RAMP_MS * sr / 1000))
                E_exp = rnd(EDGE_MS * sr / 1000)
                total_exp = rnd(400 * sr / 1000)
                gs_exp = rnd(gs_ms * sr / 1000)
                if not (r["gapSamples"] == G_exp and r["rampSamples"] == R_exp and r["edgeSamples"] == E_exp and r["total"] == total_exp and len(d) == total_exp and r["gapStart"] == gs_exp):
                    bad["len"].append((sr, g, r["gapSamples"], G_exp))
                gs, G, R = r["gapStart"], r["gapSamples"], r["rampSamples"]
                # exakt G Nullsamples, lückenfrei zusammenhängend
                if not np.all(d[gs:gs + G] == 0):
                    bad["zero"].append((sr, g))
                if np.count_nonzero(d == 0) != G:
                    bad["outside_zero"].append((sr, g, int(np.count_nonzero(d == 0)), G))
                # Hüllkurve gegen Python-Formel
                er = env_ref(total_exp, E_exp, gs_exp, G_exp, R_exp)
                err = float(np.max(np.abs(e - er)))
                worst_env = max(worst_env, err)
                if err > 1e-6:
                    bad["env"].append((sr, g, err))
                # Rampen vorhanden: R Samples vor und nach der Lücke liegen strikt zwischen 0 und 1 und sind monoton
                pre = e[gs - R:gs]
                post = e[gs + G:gs + G + R]
                if not (np.all(np.diff(pre) < 0) and np.all(np.diff(post) > 0) and 0 < pre.min() and pre.max() < 1 and 0 < post.min() and post.max() < 1):
                    bad["ramp"].append((sr, g))
                # Sprunggrenze der Hüllkurve: sin(pi/(2R)) für Lückenränder, sin(pi/(2E)) für Burstränder
                step = np.abs(np.diff(e))
                lim_gap = math.sin(math.pi / (2 * R)) + 3e-7   # 3e-7: Float32-Rundung der Hüllkurve
                lim_edge = math.sin(math.pi / (2 * E_exp)) + 3e-7
                allowed = np.zeros(len(step), bool)
                allowed[gs - R - 1: gs + G + R + 1] = True
                allowed[:E_exp + 1] = True
                allowed[-(E_exp + 1):] = True
                ok_step = (step[gs - R - 1: gs + G + R + 1].max() <= lim_gap and step[:E_exp + 1].max() <= lim_edge
                           and step[-(E_exp + 1):].max() <= lim_edge and np.all(step[~allowed] == 0))
                if not ok_step:
                    bad["step"].append((sr, g))
                # Pegel: RMS auf dem Plateau (Hüllkurve = 1)
                plateau = d[e == 1.0]
                rms = float(np.sqrt(np.mean(plateau ** 2)))
                worst_rms = max(worst_rms, abs(rms / SIGMA - 1))
                if abs(rms / SIGMA - 1) > 0.03:
                    bad["rms"].append((sr, g, rms))
                if np.max(np.abs(d)) >= 1.0:
                    bad["clip"].append((sr, g))
                # Rauschen unabhängig von der Lücke: gleiche Seed ohne Lücke
                r0 = page.evaluate(BURST_JS, [sr, 0, gs_ms, seed, None])
                d0 = f32(r0["data"])
                e0 = f32(r0["env"])
                noise0 = d0 / e0
                if not np.allclose(d, noise0 * e, atol=1e-6, rtol=0):
                    bad["noise_same"].append((sr, g))
    C.check("Burst-Raster: %d Fälle (3 Abtastraten x 9 Lückenlängen x 3 Wiederholungen)" % n_cases, True)
    C.check("Lückenlänge in Samples = round(ms*sr/1000) (min. 1), Gesamtlänge, Rampenlänge, Lückenbeginn exakt", not bad["len"], bad["len"][:3])
    C.check("Pegel in der Lücke exakt 0.0 in allen G Samples", not bad["zero"], bad["zero"][:3])
    C.check("Im ganzen Burst gibt es genau G Null-Samples (keine weiteren Nullen)", not bad["outside_zero"], bad["outside_zero"][:3])
    C.check("Hüllkurve entspricht der Python-Formel (max. Abweichung %.2e)" % worst_env, not bad["env"], bad["env"][:3])
    C.check("Rampen vorhanden: je R Samples streng monoton zwischen 0 und 1 vor und nach der Lücke", not bad["ramp"], bad["ramp"][:3])
    C.check("Kein Hüllkurven-Sprung grösser als sin(pi/(2R)) an den Lückenrändern bzw. sin(pi/(2E)) an den Burstrandern, sonst konstant 1", not bad["step"], bad["step"][:3])
    C.check("RMS auf dem Plateau = sigma 0.15 +-3 %% (grösste Abweichung %.2f %%)" % (100 * worst_rms), not bad["rms"], bad["rms"][:3])
    C.check("Keine Übersteuerung (|x| < 1)", not bad["clip"], bad["clip"][:3])
    C.check("Gleiches Rauschen mit/ohne Lücke bei gleichem Seed: Ausgabe = Rauschen x Hüllkurve", not bad["noise_same"], bad["noise_same"][:3])

    # ------------------------------------------------------------------
    # 2. Statistik des Rauschens (Verteilung, Weissheit)
    # ------------------------------------------------------------------
    r = page.evaluate(BURST_JS, [44100, 0, 150, 2024, None])
    x = f32(r["data"])
    e = f32(r["env"])
    plat = x[e == 1.0]
    N = len(plat)
    mean = float(np.mean(plat))
    sk = float(sst.skew(plat))
    ku = float(sst.kurtosis(plat))
    C.check("Rauschen: Mittelwert ~ 0 (|m| < 4*sigma/sqrt(N))", abs(mean) < 4 * SIGMA / math.sqrt(N), "m=%.5f N=%d" % (mean, N))
    C.check("Rauschen: Schiefe und Exzess ~ 0 (gaussförmig)", abs(sk) < 4 * math.sqrt(6 / N) and abs(ku) < 4 * math.sqrt(24 / N), "skew=%.3f kurt=%.3f" % (sk, ku))
    ks = sst.kstest(plat / SIGMA, "norm")
    C.check("Rauschen: Kolmogorov-Smirnov gegen N(0,1), p > 0.01", ks.pvalue > 0.01, "p=%.3f" % ks.pvalue)
    ac = [float(np.corrcoef(plat[:-k], plat[k:])[0, 1]) for k in range(1, 11)]
    C.check("Rauschen: Autokorrelation Lag 1..10 klein (weiss)", max(abs(a) for a in ac) < 4 / math.sqrt(N), "max |r|=%.4f Grenze %.4f" % (max(abs(a) for a in ac), 4 / math.sqrt(N)))
    f, pxx = sps.welch(plat, fs=44100, nperseg=512)
    lo = pxx[(f > 500) & (f < 5000)].mean()
    hi = pxx[(f > 10000) & (f < 20000)].mean()
    C.check("Rauschen: Spektrum flach (Leistung 0.5-5 kHz / 10-20 kHz = 1 +-10 %)", abs(lo / hi - 1) < 0.10, "Verhältnis=%.3f" % (lo / hi))

    # ------------------------------------------------------------------
    # 3. Negativkontrolle: ohne Rampe muss die Sprung-Prüfung anschlagen
    # ------------------------------------------------------------------
    r = page.evaluate(BURST_JS, [44100, 5, 150, 5, 0])
    e = f32(r["env"])
    max_step = float(np.max(np.abs(np.diff(e))))
    C.check("Negativkontrolle: harte Lücke (Rampe 0) hat Hüllkurven-Sprung 1.0 > sin(pi/(2R)) und würde die Prüfung nicht bestehen",
            max_step > math.sin(math.pi / (2 * 22)) * 5 and r["rampSamples"] == 0, "max Sprung=%.2f" % max_step)
    C.check("Mit Rampe (0.5 ms) ist der grösste Hüllkurven-Sprung %.3f" % math.sin(math.pi / 44), True)
    too_big = page.evaluate("""() => { try { window.__test.generateBurst(44100, {gapMs: 400, gapStartMs: 150, seed: 1}); return 'kein Fehler'; } catch (e) { return e.message; } }""")
    C.check("Lücke, die nicht in den Burst passt, wird abgelehnt (Fehlermeldung)", too_big == "Lücke passt nicht in den Burst", too_big)

    # ------------------------------------------------------------------
    # 4. Trial-Puffer (beide Intervalle) und Wiedergabeweg
    # ------------------------------------------------------------------
    TRIAL_JS = """([sr, gapMs, gapInterval, seed, gain]) => {
      const T = window.__test;
      const b64 = %s;
      const rng = T.mulberry32(seed);
      const tr = T.generateTrial(sr, {gapMs, gapInterval, rng});
      return T.renderOffline(sr, tr, gain).then(out => ({
        data: b64(tr.data), out: b64(Float32Array.from(out)), total: tr.total, starts: tr.starts, burst: tr.burstSamples,
        gapInterval: tr.gapInterval, gapSamples: tr.gapSamples, gapStartAbs: tr.gapStartAbs,
        gapStartInBurst: tr.gapStartInBurst, ramp: tr.rampSamples, edge: tr.edgeSamples}));
    }""" % B64_JS
    lead, isi, tail = 150, 500, 100
    bad_t = {"layout": [], "silence": [], "gapiv": [], "nogap": [], "pos": [], "off": [], "dur": []}
    positions = []
    worst_off = 0.0
    cnt = 0
    for sr in (44100, 48000):
        for g in (0.5, 1, 2.5, 4, 8, 20, 50):
            for iv in (1, 2):
                for rep in range(4):
                    seed = int(rng.integers(1, 2**31 - 1))
                    gain = [0.0, 0.05, 0.128, 0.8][rep]
                    t = page.evaluate(TRIAL_JS, [sr, g, iv, seed, gain])
                    cnt += 1
                    d = f32(t["data"])
                    out = f32(t["out"])
                    L, B, I, Tl = rnd(lead * sr / 1000), rnd(400 * sr / 1000), rnd(isi * sr / 1000), rnd(tail * sr / 1000)
                    if not (t["total"] == L + B + I + B + Tl == len(d) and t["starts"] == [L, L + B + I] and t["burst"] == B):
                        bad_t["layout"].append((sr, g, iv))
                    s1, s2 = t["starts"]
                    if not (np.all(d[:s1] == 0) and np.all(d[s1 + B:s2] == 0) and np.all(d[s2 + B:] == 0)):
                        bad_t["silence"].append((sr, g, iv))
                    ivstart = [s1, s2][iv - 1]
                    other = [s2, s1][iv - 1]
                    G_exp = max(1, rnd(g * sr / 1000))
                    if t["gapInterval"] != iv or t["gapSamples"] != G_exp or t["gapStartAbs"] != ivstart + t["gapStartInBurst"]:
                        bad_t["gapiv"].append((sr, g, iv))
                    a = t["gapStartAbs"]
                    if not (np.all(d[a:a + G_exp] == 0) and np.count_nonzero(d[ivstart:ivstart + B] == 0) == G_exp):
                        bad_t["gapiv"].append(("zero", sr, g, iv))
                    if np.count_nonzero(d[other:other + B] == 0) != 0:
                        bad_t["nogap"].append((sr, g, iv))
                    pos_ms = t["gapStartInBurst"] * 1000 / sr
                    positions.append(pos_ms)
                    if not (119.9 <= pos_ms <= 220.1):
                        bad_t["pos"].append((sr, g, iv, pos_ms))
                    # Offline-Rendering = Puffer x Gain (Float32)
                    off = float(np.max(np.abs(out - d * np.float32(gain))))
                    worst_off = max(worst_off, off)
                    if off > 1e-6:
                        bad_t["off"].append((sr, g, iv, gain, off))
                    if len(out) != len(d):
                        bad_t["dur"].append((sr, len(out), len(d)))
    C.check("Trial-Puffer: %d Fälle, Aufbau lead 150 ms + Burst 400 ms + ISI 500 ms + Burst 400 ms + tail 100 ms (in Samples exakt)" % cnt, not bad_t["layout"], bad_t["layout"][:3])
    C.check("Stille vor, zwischen und nach den Bursts besteht aus exakten Nullen", not bad_t["silence"], bad_t["silence"][:3])
    C.check("Lücke liegt im gewählten Intervall, mit exakt G Null-Samples; Position stimmt mit Metadaten", not bad_t["gapiv"], bad_t["gapiv"][:3])
    C.check("Das andere Intervall enthält keine Null-Samples (keine Lücke)", not bad_t["nogap"], bad_t["nogap"][:3])
    C.check("Lückenbeginn liegt in [120, 220] ms ab Burst-Beginn (Mittel %.1f ms)" % float(np.mean(positions)), not bad_t["pos"] and 160 < float(np.mean(positions)) < 180, bad_t["pos"][:3])
    C.check("OfflineAudioContext-Rendering = Puffer x Gain, max. Abweichung %.2e (Wiedergabeweg ändert die Samples nicht)" % worst_off, not bad_t["off"] and not bad_t["dur"], bad_t["off"][:3])

    # Reproduzierbarkeit mit Seed und Unabhängigkeit der Lücken-Intervalle
    rep = page.evaluate("""() => { const T = window.__test;
      const a = T.generateTrial(44100, {gapMs: 3, gapInterval: 2, rng: T.mulberry32(5)});
      const b = T.generateTrial(44100, {gapMs: 3, gapInterval: 2, rng: T.mulberry32(5)});
      const c = T.generateTrial(44100, {gapMs: 3, gapInterval: 2, rng: T.mulberry32(6)});
      let same = true, diff = false;
      for (let i = 0; i < a.data.length; i++) { if (a.data[i] !== b.data[i]) same = false; if (a.data[i] !== c.data[i]) diff = true; }
      return {same, diff}; }""")
    C.check("Gleicher Seed erzeugt identischen Puffer, anderer Seed einen anderen", rep["same"] and rep["diff"], rep)

    # Pegel der beiden Intervalle gleich (kein Lautstärkehinweis)
    ratios = []
    for i in range(60):
        seed = int(rng.integers(1, 2**31 - 1))
        t = page.evaluate(TRIAL_JS, [44100, 20, 1 + (i % 2), seed, 0.128])
        d = f32(t["data"])
        s1, s2 = t["starts"]
        B = t["burst"]
        r1 = np.sqrt(np.mean(d[s1:s1 + B] ** 2))
        r2 = np.sqrt(np.mean(d[s2:s2 + B] ** 2))
        ratios.append(20 * math.log10(r1 / r2) * (1 if t["gapInterval"] == 1 else -1))
    # Lücke 20 ms (+Rampen) in 400 ms: erwarteter Pegelunterschied ca. -0.22 dB
    exp_db = 10 * math.log10(1 - (rnd(20 * 44.1) + 22) / 17640)
    C.check("Pegelunterschied zwischen Lücken- und Nullintervall bei 20 ms Lücke: %.2f dB (erwartet %.2f dB, statistische Streuung ca. 0.07 dB)" % (float(np.mean(ratios)), exp_db),
            abs(float(np.mean(ratios)) - exp_db) < 0.1, "Mittel über 60 Trials")

    C.check("Keine Konsolenfehler, keine externen oder fehlgeschlagenen Anfragen", not errors and not external, errors + external)
    browser.close()

C.finish()
