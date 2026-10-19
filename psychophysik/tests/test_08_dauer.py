"""Dauer des Ablaufs von signalentdeckung.html (Ziel: gesamt etwa 6 Minuten, reine Aufgabe unter 4 Minuten).

1. Rechnung aus der Konfiguration (Fixation + Reiz + Maske + Antwortzeit + Rückmeldung je Durchgang).
2. Messung in Echtzeit mit simuliertem, zügigem Beobachter (Antwortzeit gleichverteilt 0.8 bis 1.2 s):
   - Standard: nur der Probelauf (rund 40 s), daraus die Zeit je Durchgang;
   - mit --full: kompletter Durchlauf Probelauf + beide Blöcke (rund 4 Minuten).
3. Lesezeiten sind Annahmen (siehe READING), keine Messung.
Zum Vergleich: gemessene Werte vor der Änderung (50 Durchgänge je Block, Probelauf 20, Fixation 500, Maske 200, Rückmeldung 800,
Pause 250 ms): Aufgabe 372.4 s = 6.2 min bei derselben Antwortzeit (Mittel 3.10 s je Durchgang).
Start: python3 -I tests/test_08_dauer.py [--full]
"""
import os
import random
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from playwright.sync_api import sync_playwright

import _helpers as H

FULL = "--full" in sys.argv
C = H.Checker("Dauer des Ablaufs")

BASE_TASK_S = 372.4          # vor der Änderung gemessen (Echtzeit, Antwortzeit 0.8 bis 1.2 s, 120 Durchgänge)
BASE_PER_TRIAL_S = 3.103
RT_LO, RT_HI = 0.8, 1.2
OVERHEAD_S = 0.05            # Rendern, Zeitgeber (aus der Messung des alten Stands: 3.103 - 3.05)
# Annahmen für Zeiten, in denen Menschen lesen oder einstellen (Sekunden)
READING = [("Aufgabe lesen und Beispiele ansehen", 40), ("Regler einstellen", 10), ("Probelauf-Ergebnis lesen, Festlegen", 12),
           ("Matrix vor Block 1 lesen, starten", 10), ("Matrix vor Block 2 lesen, starten", 10), ("Ergebnis ansehen, Code kopieren", 30)]
READ_S = sum(t for _, t in READING)

with sync_playwright() as pw:
    browser = pw.chromium.launch()
    page = browser.new_page()
    errors, external = [], []
    H.attach_collectors(page, errors, external)
    page.goto("file://" + H.PROJECT + "/signalentdeckung.html")
    CF = page.evaluate("window.__test.CONFIG")
    NP, NB = CF["probeTrials"], CF["trialsPerBlock"]
    fixed_s = (CF["fixMs"] + CF["stimMs"] + CF["maskMs"] + CF["feedbackMs"] + CF["itiMs"]) / 1000.0
    per_trial = fixed_s + (RT_LO + RT_HI) / 2 + OVERHEAD_S
    n_all = NP + 2 * NB
    task_s = n_all * per_trial
    total_s = task_s + READ_S
    C.info("Konfiguration: Probelauf %d, Block %d, Fixation %d ms, Reiz %d ms, Maske %d ms, Rückmeldung %d ms, Pause %d ms" % (NP, NB, CF["fixMs"], CF["stimMs"], CF["maskMs"], CF["feedbackMs"], CF["itiMs"]))
    C.info("Rechnung: feste Zeit je Durchgang %.2f s + Antwortzeit %.1f s + Overhead %.2f s = %.2f s; %d Durchgänge = %.0f s = %.2f min" % (fixed_s, (RT_LO + RT_HI) / 2, OVERHEAD_S, per_trial, n_all, task_s, task_s / 60))
    C.info("Lesezeiten (Annahmen): %s = %d s" % ("; ".join("%s %d s" % x for x in READING), READ_S))
    C.check("Rechnung: reine Aufgabe (Probelauf + beide Blöcke) %.2f min < 4 min" % (task_s / 60), task_s < 240)
    C.check("Rechnung: gesamter Ablauf inkl. Einführung, Einstellen, Matrizen, Ergebnis %.2f min <= 6 min (bei einem Probelauf)" % (total_s / 60), total_s <= 360)
    second_probe = NP * per_trial + 25
    C.info("Mit zweitem Probelauf (Schwierigkeit nachstellen): +%.0f s = %.2f min gesamt" % (second_probe, (total_s + second_probe) / 60))
    C.check("Rechnung: ein zweiter Probelauf verlängert den Ablauf auf %.2f min (Grenze der Prüfung 7 min; über den Sollwert von 6 min hinaus, siehe README)" % ((total_s + second_probe) / 60), total_s + second_probe <= 420)
    slow = n_all * (fixed_s + 1.2 + OVERHEAD_S)
    C.info("Langsamer Beobachter (Antwortzeit 1.2 s): Aufgabe %.0f s = %.2f min" % (slow, slow / 60))
    C.check("Reizdauer bleibt bei 300 ms, Rückmeldung >= 500 ms, Fixation <= 400 ms (Vorgaben der Aufgabe)", CF["stimMs"] == 300 and CF["feedbackMs"] >= 500 and CF["fixMs"] <= 400)
    C.check("Gegenüber vorher (%.0f s = %.1f min) ist die reine Aufgabe um %.0f %% kürzer (Rechnung)" % (BASE_TASK_S, BASE_TASK_S / 60, 100 * (1 - task_s / BASE_TASK_S)), task_s < 0.7 * BASE_TASK_S)

    # ------------------------------------------------------------------
    # Messung in Echtzeit
    # ------------------------------------------------------------------
    rnd = random.Random(5)

    def respond_loop(pg, done_sel, counter):
        while True:
            pg.wait_for_function("!document.getElementById('btn-yes').disabled || !document.querySelector('%s').hidden || ('%s' === '#probe-res' && !document.getElementById('view-setup').hidden)" % (done_sel, done_sel), polling=5, timeout=60000)
            if pg.is_visible(done_sel) or (done_sel == "#probe-res" and pg.is_visible("#view-setup")):
                return
            cur = pg.evaluate("window.__test.current")
            x = rnd.gauss(0, 1) + (1.5 if cur["signal"] else 0)
            time.sleep(rnd.uniform(RT_LO, RT_HI))
            pg.click("#btn-yes" if x > 0.75 else "#btn-no")
            counter[0] += 1

    with H.serve() as base:
        pg = browser.new_page(viewport={"width": 1280, "height": 800})
        errs, ext = [], []
        H.attach_collectors(pg, errs, ext)
        pg.add_init_script("window.__test = {seed: 5};")
        pg.goto(base + "/signalentdeckung.html")
        pg.evaluate("(() => { const e = document.getElementById('diff'); e.value = 40; e.dispatchEvent(new Event('input')); })()")
        cnt = [0]
        t0 = time.time()
        pg.click("#btn-probe")
        respond_loop(pg, "#probe-res", cnt)
        probe_s = time.time() - t0
        pt = probe_s / cnt[0]
        C.info("Gemessen (Echtzeit, Probelauf): %d Durchgänge in %.1f s = %.2f s je Durchgang (Rechnung %.2f s)" % (cnt[0], probe_s, pt, per_trial))
        C.check("Messung Probelauf: %d Durchgänge, Zeit je Durchgang %.2f s weicht höchstens 0.15 s von der Rechnung %.2f s ab" % (cnt[0], pt, per_trial), cnt[0] == NP and abs(pt - per_trial) < 0.15)
        meas_task = pt * n_all
        C.check("Hochrechnung aus dem Probelauf: reine Aufgabe %.0f s = %.2f min < 4 min; gesamt mit Lesezeiten %.2f min <= 6 min" % (meas_task, meas_task / 60, (meas_task + READ_S) / 60), meas_task < 240 and meas_task + READ_S <= 360)
        if FULL:
            pg.click("#btn-lock")
            t1 = time.time()
            pg.click("#btn-block-start")
            respond_loop(pg, "#view-pre", cnt)
            b1 = time.time() - t1
            t2 = time.time()
            pg.click("#btn-block-start")
            respond_loop(pg, "#view-result", cnt)
            b2 = time.time() - t2
            task_meas = probe_s + b1 + b2
            C.info("Gemessen (Echtzeit, kompletter Durchlauf): Probelauf %.1f s, Block 1 %.1f s, Block 2 %.1f s, Aufgabe %.1f s = %.2f min, %d Durchgänge, %.2f s je Durchgang; mit Lesezeiten %.2f min" % (probe_s, b1, b2, task_meas, task_meas / 60, cnt[0], task_meas / cnt[0], (task_meas + READ_S) / 60))
            C.check("Messung kompletter Durchlauf: %d Antworten (%d + 2 x %d), reine Aufgabe %.1f s = %.2f min < 4 min" % (cnt[0], NP, NB, task_meas, task_meas / 60), cnt[0] == n_all and task_meas < 240)
            C.check("Messung kompletter Durchlauf: gesamt mit Lesezeiten (Annahmen) %.2f min <= 6 min; gegenüber vorher (%.1f min Aufgabe) %.0f %% kürzer" % ((task_meas + READ_S) / 60, BASE_TASK_S / 60, 100 * (1 - task_meas / BASE_TASK_S)), task_meas + READ_S <= 360)
            ex = pg.evaluate("window.__test.exposures")
            C.check("Reizdauer in der Messung: Mittel %.1f ms (min %.0f, max %.0f), Soll 300 ms" % (np.mean(ex), min(ex), max(ex)), abs(np.mean(ex) - 300) < 12 and min(ex) >= 280 and max(ex) <= 330)
        C.check("Keine Konsolenfehler, keine externen oder fehlgeschlagenen Anfragen", not errs and not ext and not errors and not external, errs + ext + errors + external)
        pg.close()
    browser.close()

C.finish()
