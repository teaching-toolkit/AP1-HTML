"""Screenshots der wichtigsten Zustände von signalentdeckung.html (Beispielbilder, Reiz, Fixation, Layout).
Die übrigen Zustände (Setup, Matrix, Block, Ergebnis, Gruppe) schreibt test_05_ui_sdt.py.
Start: python3 -I tests/test_10_screenshots.py
"""
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from PIL import Image, ImageDraw
from playwright.sync_api import sync_playwright

import _helpers as H

C = H.Checker("Screenshots Signalentdeckung")
with sync_playwright() as pw:
    browser = pw.chromium.launch()
    with H.serve() as base:
        for kind, vp, name in (("desktop", {"width": 1000, "height": 900}, "desktop"), ("phone", {"width": 390, "height": 844}, "handy")):
            ctx = browser.new_context(viewport=vp, has_touch=(kind == "phone"), is_mobile=(kind == "phone"))
            pg = ctx.new_page()
            errs, ext = [], []
            H.attach_collectors(pg, errs, ext)
            pg.add_init_script("window.__test = {seed: 21};")
            pg.goto(base + "/signalentdeckung.html")
            (pg.tap if kind == "phone" else pg.click)("#btn-ex-sig")
            pg.evaluate("document.getElementById('cv-ex').scrollIntoView({block: 'center'})")
            path = os.path.join(H.SHOTS, "sdt_beispiel_%s.png" % name)
            pg.screenshot(path=path)
            # Fixation im Durchgang (Echtzeit): kurz nach dem Start des Probelaufs
            (pg.tap if kind == "phone" else pg.click)("#btn-probe")
            time.sleep(0.2)
            pg.screenshot(path=os.path.join(H.SHOTS, "sdt_fixation_%s.png" % name))
            c_ = pg.evaluate("(() => { const d = document.getElementById('cv').getContext('2d').getImageData(0,0,160,160).data; let n = 0; for (let i = 0; i < d.length; i += 4) if (d[i] !== 128) n++; return n; })()")
            C.check("[%s] Fixationskreuz im Durchgang sichtbar (%d helle Pixel), Beispielbild und Fixation gespeichert" % (name, c_), 20 < c_ < 80)
            C.check("[%s] Keine Konsolenfehler" % name, not errs and not ext, errs + ext)
            ctx.close()
        # Reiz: gleicher Seed und gleiche Position, drei Stärken
        pg = browser.new_page()
        pg.add_init_script("window.__test = {seed: 3};")
        pg.goto(base + "/signalentdeckung.html")
        res = pg.evaluate("""() => { const T = window.__test, plan = T.makePlan(40, 4), p = plan.find(x => x.signal).pos;
          return { pos: p, a40: T.sliderToAmp(40), a1: T.sliderToAmp(1),
                   sig40: T.makeStimulus(9, true, T.sliderToAmp(40), {pos: p}), sig1: T.makeStimulus(9, true, T.sliderToAmp(1), {pos: p}), none: T.makeStimulus(9, false, 0) }; }""")
        panels = []
        for key, cap in (("sig40", "Reglerstellung 40 (Startwert), Amplitude %.1f" % res["a40"]), ("sig1", "Reglerstellung 1 (leicht), Amplitude %.0f" % res["a1"]), ("none", "ohne Signal")):
            arr = np.array(res[key], dtype=np.uint8).reshape(160, 160, 4)[:, :, :3]
            im = Image.fromarray(arr).resize((320, 320), Image.NEAREST)
            canvas = Image.new("RGB", (320, 350), (246, 247, 249))
            canvas.paste(im, (0, 30))
            ImageDraw.Draw(canvas).text((4, 8), cap, fill=(28, 35, 48))
            panels.append(canvas)
        W = Image.new("RGB", (3 * 320 + 2 * 10, 350), (246, 247, 249))
        for i, p_ in enumerate(panels):
            W.paste(p_, (i * 330, 0))
        W.save(os.path.join(H.SHOTS, "sdt_reiz_signal.png"))
        C.check("Reizbilder gespeichert (Fleck bei x = %.0f, y = %.0f, Abstand zur Mitte %.1f px)" % (res["pos"]["x"], res["pos"]["y"], res["pos"]["r"]), res["pos"]["r"] >= 44)
        pg.close()
    browser.close()
C.finish()
