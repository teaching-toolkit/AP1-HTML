"""UI-Durchlauf schwelle.html: Desktop, Handy (Touch), Tastatur, Fehlerfälle, Gruppenansicht, Echtzeit-Lauf.

Aufruf: python3 -I tests/test_04_ui_schwelle.py [--realtime]
Ohne --realtime laufen alle schnellen Tests (Testhaken instant). Mit --realtime zusätzlich ein Echtzeit-Lauf
(ca. 3 Minuten) auf dem Handy-Viewport mit Touch, echter Audiopfad, gemessene Zeiten.
Echtes Hören kann nicht getestet werden.
"""
import math
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from playwright.sync_api import sync_playwright

import _helpers as H

C = H.Checker("UI schwelle.html")
REALTIME = "--realtime" in sys.argv

src = open(os.path.join(H.HERE, "test_02_staircase.py"), encoding="utf-8").read()
ns = {"math": math, "np": np}
exec(src[src.index("CFG = dict("):src.index("def weibull_pc")], ns)
run_ref, CFG = ns["run_ref"], ns["CFG"]


def init_js(g70, rngseed, seed=None, instant=True, listener=True):
    s = "window.__test = {instant:%s%s};\n" % ("true" if instant else "false", (", seed:%d" % seed) if seed is not None else "")
    if listener:
        s += H.MULBERRY_JS + """
(function(){ const rng = mulberry32(%d), g70=%f, beta=3;
 const alpha=g70/Math.pow(-Math.log(1-0.41421356237),1/beta);
 const pc=g=>0.5+0.5*(1-Math.exp(-Math.pow(g/alpha,beta)));
 window.__test.listener=function(tr){ return rng()<pc(tr.gapMs) ? tr.gapInterval : 3-tr.gapInterval; }; })();""" % (rngseed, g70)
    return s


def new_page(browser, kind, init=None, **kw):
    if kind == "phone":
        ctx = browser.new_context(viewport={"width": 390, "height": 844}, has_touch=True, is_mobile=True, **kw)
    else:
        ctx = browser.new_context(viewport={"width": 1280, "height": 800}, **kw)
    pg = ctx.new_page()
    errors, external = [], []
    H.attach_collectors(pg, errors, external)
    if init:
        pg.add_init_script(init)
    return ctx, pg, errors, external


def click(pg, sel, kind):
    if kind == "phone":
        pg.tap(sel)
    else:
        pg.click(sel)


def flow(pg, kind):
    click(pg, "#btn-testtone", kind)
    pg.wait_for_function("window.__test.audio.ctx && window.__test.audio.ctx.state==='running'")
    click(pg, "#btn-to-practice", kind)
    click(pg, "#btn-go", kind)
    pg.wait_for_selector("#view-practice-done:not([hidden])", timeout=20000)
    click(pg, "#btn-start-test", kind)
    pg.wait_for_selector("#view-result:not([hidden])", timeout=30000)


def no_hscroll(pg):
    return pg.evaluate("document.documentElement.scrollWidth <= window.innerWidth + 0")


def small_targets(pg):
    return pg.evaluate("""() => { const bad = [];
      document.querySelectorAll('button, a.btn, a.link, summary, input[type=range], .crumb a').forEach(e => {
        const r = e.getBoundingClientRect(); if (r.width === 0 && r.height === 0) return;
        if (r.height < 43.5 || r.width < 43.5) bad.push((e.id || e.textContent.trim().slice(0, 20)) + ':' + Math.round(r.width) + 'x' + Math.round(r.height)); });
      return bad; }""")


def verify_result(pg, label):
    r = pg.evaluate("() => { const T = window.__test, x = T.lastResult; return {st: x.status, thr: x.thresholdMs, n: x.nTrials, k: x.nCorrect, revs: x.reversals.map(a => [a.trial, a.level]), used: x.used.length, log: T.log}; }")
    main = pg.inner_text("#res-main")
    ok_main = (r["st"] == "ok") and main == "Schwelle: %s ms" % (("%.2f" % r["thr"]) if r["thr"] < 10 else ("%.1f" % r["thr"]))
    used = [v for _, v in r["revs"][-8:]]
    thr_ref = math.exp(sum(math.log(v) for v in used) / len(used))
    C.check("[%s] Schwelle angezeigt (%s) = geometrisches Mittel der letzten 8 von 12 Umkehrpunkten (Python %.4f)" % (label, main, thr_ref), ok_main and abs(thr_ref - r["thr"]) < 1e-9 and len(r["revs"]) == 12)
    test_log = [t for t in r["log"] if t.get("phase") == "test" and not t.get("interrupted")]
    prac = [t for t in r["log"] if t.get("phase") == "practice"]
    ans = [t["correct"] for t in test_log]
    it = iter(ans)
    ref = run_ref(CFG, lambda g, n: next(it))
    lv_ok = len(test_log) == r["n"] == ref["n"] and all(abs(a["level"] / b - 1) < 1e-12 for a, b in zip(test_log, ref["levels"]))
    C.check("[%s] Ablauf der Seite (%d Test-Durchgänge) Level für Level gleich der Python-Referenz; Übung: Level %s" % (label, r["n"], [t["level"] for t in prac]), lv_ok and [t["level"] for t in prac] == [30, 25, 20])
    C.check("[%s] Protokoll konsistent: richtig = (Antwort == Lückenintervall); Trefferquote %d von %d; Statistik-Kachel zeigt sie" % (label, r["k"], r["n"]),
            all(t["correct"] == (t["answer"] == t["gapInterval"]) for t in test_log) and sum(ans) == r["k"] and ("%d von %d" % (r["k"], r["n"])) in pg.inner_text("#res-stats"))
    n_ok = pg.locator("#chart-wrap svg circle.ok").count()
    n_no = pg.locator("#chart-wrap svg path.no").count()
    n_rev = pg.locator("#chart-wrap svg circle.rev").count()
    C.check("[%s] Diagramm: %d richtige + %d falsche Marken = %d Durchgänge, %d Umkehrpunkt-Ringe, 1 Schwellenlinie" % (label, n_ok, n_no, r["n"], n_rev), n_ok + n_no == r["n"] and n_no == r["n"] - r["k"] and n_rev == 12 and pg.locator("#chart-wrap svg line.thr").count() == 1)
    code = pg.inner_text("#res-code")
    p = pg.evaluate("(c) => window.__test.parseCode(c)", code)
    C.check("[%s] Ergebnis-Code %s: Rundreise (Schwelle %.2f, %d Durchgänge, %d richtig)" % (label, code, p.get("thresholdMs") or -1, p.get("n", 0), p.get("k", 0)),
            p["ok"] and abs(p["thresholdMs"] - round(r["thr"] * 100) / 100) < 1e-9 and p["n"] == r["n"] and p["k"] == r["k"])
    return code, r


with sync_playwright() as pw:
    browser = pw.chromium.launch()
    with H.serve() as base:
        # ---------------- Desktop: Durchlauf, Ergebnis, Kopieren, Layout ----------------
        ctx, pg, errs, ext = new_page(browser, "desktop", init_js(4.0, 11, seed=42))
        ctx.grant_permissions(["clipboard-read", "clipboard-write"], origin=base.rsplit("/", 1)[0])
        pg.goto(base + "/schwelle.html")
        C.check("Einstieg: Setup sichtbar, kein Audio-Hinweis, Start-Knopf aktiv", pg.is_visible("#view-setup") and pg.is_hidden("#audio-problem") and pg.is_enabled("#btn-to-practice"))
        C.check("[Desktop] Setup: kein horizontales Scrollen, Klickflächen >= 44 px %s" % small_targets(pg), no_hscroll(pg) and not small_targets(pg))
        pg.screenshot(path=os.path.join(H.SHOTS, "schwelle_setup_desktop.png"))
        pg.fill("#vol", "70") if False else pg.evaluate("() => { const v = document.getElementById('vol'); v.value = 70; v.dispatchEvent(new Event('input')); }")
        click(pg, "#btn-testtone", "desktop")
        pg.wait_for_function("window.__test.audio.ctx && window.__test.audio.ctx.state==='running'")
        pg.wait_for_timeout(200)
        g = pg.evaluate("[window.__test.audio.master.gain.value, window.__test.volToGain(70)]")
        C.check("Testton: AudioContext läuft, Lautstärkeregler setzt den Gain (%.4f, erwartet %.4f = 0.8 x 0.7^2)" % tuple(g), abs(g[0] - g[1]) < 1e-3 and abs(g[1] - 0.392) < 1e-9)
        click(pg, "#btn-to-practice", "desktop")
        C.check("Übung: Trial-Ansicht mit Start-Knopf, Antwortknöpfe zunächst gesperrt", pg.is_visible("#view-trial") and pg.is_disabled("#ans1") and pg.is_visible("#btn-go"))
        click(pg, "#btn-go", "desktop")
        pg.wait_for_selector("#view-practice-done:not([hidden])", timeout=20000)
        C.check("Übung beendet: Text '%s'" % pg.inner_text("#pd-text")[:40], "von 3" in pg.inner_text("#pd-text"))
        click(pg, "#btn-start-test", "desktop")
        pg.wait_for_selector("#view-result:not([hidden])", timeout=30000)
        code1, r1 = verify_result(pg, "Desktop")
        C.check("Hinweis zu 70.7 %% steht im Ergebnis", "70.7" in pg.inner_text("#res-note") and "nicht bei 50" in pg.inner_text("#res-note"))
        C.check("[Desktop] Ergebnis: kein horizontales Scrollen, Klickflächen >= 44 px %s" % small_targets(pg), no_hscroll(pg) and not small_targets(pg))
        pg.screenshot(path=os.path.join(H.SHOTS, "schwelle_ergebnis_desktop.png"), full_page=True)
        click(pg, "#btn-copy", "desktop")
        pg.wait_for_timeout(300)
        clip = pg.evaluate("navigator.clipboard.readText()")
        C.check("Kopieren: Zwischenablage enthält den Code, Meldung '%s'" % pg.inner_text("#copy-msg"), clip == code1 and pg.inner_text("#copy-msg") == "Kopiert.")
        C.check("Keine Konsolenfehler/externen Anfragen (Desktop-Lauf)", not errs and not ext, errs + ext)
        # gleicher Seed + gleicher Hörer -> gleicher Code
        ctx2, pg2, e2, x2 = new_page(browser, "desktop", init_js(4.0, 11, seed=42))
        pg2.goto(base + "/schwelle.html")
        flow(pg2, "desktop")
        C.check("?seed reproduzierbar: zweiter Lauf mit gleichem Seed und Hörer liefert denselben Code (%s)" % pg2.inner_text("#res-code"), pg2.inner_text("#res-code") == code1)
        ctx2.close()
        # Seed per URL
        ctx2, pg2, e2, x2 = new_page(browser, "desktop", init_js(4.0, 11))
        pg2.goto(base + "/schwelle.html?seed=42")
        flow(pg2, "desktop")
        C.check("?seed=42 in der URL wirkt wie T.seed (gleicher Code)", pg2.inner_text("#res-code") == code1)
        ctx2.close()
        ctx.close()

        # ---------------- Gruppe: vier Läufe + Randfälle ----------------
        codes, thrs = [], []
        for i, g70 in enumerate((2.0, 3.0, 5.0, 8.0)):
            c_, p_, e_, x_ = new_page(browser, "desktop", init_js(g70, 100 + i, seed=7 + i))
            p_.goto(base + "/schwelle.html")
            flow(p_, "desktop")
            codes.append(p_.inner_text("#res-code"))
            thrs.append(p_.evaluate("window.__test.lastResult.thresholdMs"))
            c_.close()
        ceil_code = "HSLU-schwelle-v1.zz01.c.0.6.2"
        ceil_code += "." + H.checksum(ceil_code)
        ctx, pg, errs, ext = new_page(browser, "desktop")
        pg.goto(base + "/schwelle.html#gruppe")
        C.check("Direktlink #gruppe öffnet die Gruppenansicht", pg.is_visible("#view-group"))
        text = "\n".join([codes[0], "", codes[1], codes[1], codes[2].upper(), "Das ist kein Code", codes[3][:-1] + ("0" if codes[3][-1] != "0" else "1"), ceil_code, codes[0]])
        pg.fill("#group-in", text)
        pg.click("#btn-group-run")
        out = pg.inner_text("#group-out")
        rows = pg.locator("#group-out table tbody tr").count()
        valid_thr = thrs[:3]
        exp = np.array(valid_thr)
        # angezeigte Gruppenwerte
        stats = pg.evaluate("window.__test.lastGroup.stats")
        # Schwellen im Code sind auf 0.01 ms gerundet
        exp_r = np.round(exp * 100) / 100
        C.check("Gruppe: 4 gültige Codes (3 mit Schwelle, 1 'nicht bestimmbar'), 2 Duplikate ignoriert, 2 ungültige Zeilen benannt (Zeile 7 und 8 im Text: %s)" % out.splitlines()[0],
                rows == 4 and "4 gültige" in out and "2 doppelte" in out and "2 ungültig" in out and "Zeile 6" in out and "Zeile 7" in out and "nicht bestimmbar" in out)
        C.check("Gruppe: Mittelwert %.3f, Median %.3f, SD %.3f, Min/Max stimmen mit Python über die Codes (%.3f / %.3f / %.3f)" % (stats["mean"], stats["median"], stats["sd"], exp_r.mean(), np.median(exp_r), exp_r.std(ddof=1)),
                stats["n"] == 3 and abs(stats["mean"] - exp_r.mean()) < 1e-9 and abs(stats["median"] - np.median(exp_r)) < 1e-9 and abs(stats["sd"] - exp_r.std(ddof=1)) < 1e-9 and abs(stats["min"] - exp_r.min()) < 1e-9 and abs(stats["max"] - exp_r.max()) < 1e-9)
        C.check("Gruppe: Punktdiagramm gezeichnet (3 Punkte)", pg.locator("#group-chart svg circle.ok").count() == 3)
        pg.screenshot(path=os.path.join(H.SHOTS, "schwelle_gruppe_desktop.png"), full_page=True)
        pg.fill("#group-in", "Quatsch\nnoch mehr")
        pg.click("#btn-group-run")
        o2 = pg.inner_text("#group-out")
        C.check("Gruppe: nur ungültige Eingabe -> 0 gültige, beide Zeilen benannt, keine Tabelle", "0 gültige" in o2 and "Zeile 1" in o2 and "Zeile 2" in o2 and pg.locator("#group-out table").count() == 0)
        pg.fill("#group-in", codes[0])
        pg.click("#btn-group-run")
        C.check("Gruppe: eine Person -> SD '–'", "–" in pg.inner_text("#group-out") and pg.locator("#group-out table tbody tr").count() == 1)
        pg.fill("#group-in", ceil_code)
        pg.click("#btn-group-run")
        C.check("Gruppe: nur nicht bestimmbare Schwelle -> Hinweis statt Kennzahlen", "Keine bestimmbare Schwelle" in pg.inner_text("#group-out"))
        pg.fill("#group-in", "")
        pg.click("#btn-group-run")
        C.check("Gruppe: leere Eingabe -> '0 gültige Codes', kein Fehler", "0 gültige" in pg.inner_text("#group-out"))
        C.check("Keine Konsolenfehler (Gruppenansicht)", not errs and not ext, errs + ext)
        ctx.close()

        # ---------------- Handy: Touch, Antworten per Tap (Orakel), instant ----------------
        def phone_oracle_run(pg, noise_seed):
            rng = np.random.default_rng(noise_seed)
            pg.tap("#btn-testtone")
            pg.wait_for_function("window.__test.audio.ctx && window.__test.audio.ctx.state==='running'")
            pg.tap("#btn-to-practice")
            pg.tap("#btn-go")
            def answer_loop(final_sel):
                n = 0
                while pg.is_hidden(final_sel):
                    try:
                        pg.wait_for_function("!document.getElementById('ans1').disabled || !document.querySelector('%s').hidden" % final_sel, timeout=15000)
                    except Exception:
                        break
                    if pg.is_visible("#ans1") and not pg.is_disabled("#ans1"):
                        cur = pg.evaluate("window.__test.current")
                        g70 = 4.0
                        alpha = g70 / (-math.log(1 - 0.41421356237)) ** (1 / 3)
                        pcor = 0.5 + 0.5 * (1 - math.exp(-((cur["gapMs"] / alpha) ** 3)))
                        a = cur["gapInterval"] if rng.random() < pcor else 3 - cur["gapInterval"]
                        pg.tap("#ans%d" % a)
                        n += 1
                return n
            n1 = answer_loop("#view-practice-done")
            pg.tap("#btn-start-test")
            n2 = answer_loop("#view-result")
            return n1, n2
        ctx, pg, errs, ext = new_page(browser, "phone", "window.__test = {instant:true};")
        pg.goto(base + "/schwelle.html")
        C.check("[Handy 390x844] Setup: kein horizontales Scrollen, Klickflächen >= 44 px %s" % small_targets(pg), no_hscroll(pg) and not small_targets(pg))
        pg.screenshot(path=os.path.join(H.SHOTS, "schwelle_setup_handy.png"))
        n1, n2 = phone_oracle_run(pg, 5)
        C.check("[Handy] Durchlauf per Tippen auf die Antwortknöpfe: %d Übungs- und %d Test-Antworten bis zum Ergebnis" % (n1, n2), n1 == 3 and pg.is_visible("#view-result") and n2 > 20)
        pg.screenshot(path=os.path.join(H.SHOTS, "schwelle_ergebnis_handy.png"), full_page=True)
        verify_result(pg, "Handy")
        C.check("[Handy] Ergebnis: kein horizontales Scrollen, Klickflächen >= 44 px %s" % small_targets(pg), no_hscroll(pg) and not small_targets(pg))
        svgw = pg.evaluate("document.querySelector('#chart-wrap svg').getBoundingClientRect().width")
        C.check("[Handy] Diagramm passt in die Breite (%.0f px <= 390)" % svgw, svgw <= 390)
        pg.tap("#link-group2")
        pg.fill("#group-in", codes[0] + "\n" + codes[1])
        pg.tap("#btn-group-run")
        C.check("[Handy] Gruppenansicht per Tippen, kein horizontales Scrollen", pg.locator("#group-out table tbody tr").count() == 2 and no_hscroll(pg))
        pg.screenshot(path=os.path.join(H.SHOTS, "schwelle_gruppe_handy.png"), full_page=True)
        C.check("Keine Konsolenfehler (Handy)", not errs and not ext, errs + ext)
        ctx.close()

        # Kleines Handy 360 x 640 und Tablet
        for (w, h, nm) in ((360, 640, "360x640"), (768, 1024, "Tablet 768x1024")):
            ctx = browser.new_context(viewport={"width": w, "height": h}, has_touch=True, is_mobile=(w < 700))
            pg = ctx.new_page()
            pg.add_init_script(init_js(4.0, 3, seed=1))
            pg.goto(base + "/schwelle.html")
            ok_setup = no_hscroll(pg)
            flow(pg, "phone")
            C.check("[%s] Setup und Ergebnis ohne horizontales Scrollen, Diagramm %.0f px breit" % (nm, pg.evaluate("document.querySelector('#chart-wrap svg').getBoundingClientRect().width")), ok_setup and no_hscroll(pg))
            if w == 360:
                pg.screenshot(path=os.path.join(H.SHOTS, "schwelle_ergebnis_360.png"), full_page=True)
            ctx.close()

        # Dunkelmodus
        ctx = browser.new_context(viewport={"width": 1280, "height": 800}, color_scheme="dark")
        pg = ctx.new_page()
        pg.add_init_script(init_js(4.0, 3, seed=1))
        pg.goto(base + "/schwelle.html")
        flow(pg, "desktop")
        pg.screenshot(path=os.path.join(H.SHOTS, "schwelle_ergebnis_dunkel.png"), full_page=True)
        bg = pg.evaluate("getComputedStyle(document.body).backgroundColor")
        C.check("Dunkelmodus: Hintergrund %s, Durchlauf ohne Fehler" % bg, bg == "rgb(17, 21, 28)")
        ctx.close()

        # ---------------- Tastatur ----------------
        ctx, pg, errs, ext = new_page(browser, "desktop", "window.__test = {instant:true};")
        pg.goto(base + "/schwelle.html")

        def tab_to(sel, maxn=25):
            for _ in range(maxn):
                if pg.evaluate("document.activeElement && document.activeElement.matches(%r)" % sel):
                    return True
                pg.keyboard.press("Tab")
            return False
        okk = tab_to("#btn-testtone")
        pg.keyboard.press("Enter")
        okk &= tab_to("#btn-to-practice")
        pg.keyboard.press("Enter")
        okk &= tab_to("#btn-go")
        pg.keyboard.press("Enter")
        rng = np.random.default_rng(8)
        nk = 0
        while True:
            pg.wait_for_function("!document.getElementById('ans1').disabled || !document.getElementById('view-practice-done').hidden", timeout=15000)
            if pg.is_visible("#view-practice-done"):
                break
            cur = pg.evaluate("window.__test.current")
            pg.keyboard.press(str(cur["gapInterval"]))
            nk += 1
        okk &= tab_to("#btn-start-test")
        pg.keyboard.press("Space")
        while pg.is_hidden("#view-result"):
            pg.wait_for_function("!document.getElementById('ans1').disabled || !document.getElementById('view-result').hidden", timeout=15000)
            if pg.is_visible("#view-result"):
                break
            cur = pg.evaluate("window.__test.current")
            alpha = 4.0 / (-math.log(1 - 0.41421356237)) ** (1 / 3)
            pcor = 0.5 + 0.5 * (1 - math.exp(-((cur["gapMs"] / alpha) ** 3)))
            pg.keyboard.press(str(cur["gapInterval"] if rng.random() < pcor else 3 - cur["gapInterval"]))
        r = pg.evaluate("window.__test.lastResult")
        C.check("Reine Tastaturbedienung: Tab/Enter/Leertaste für Knöpfe, Tasten 1 und 2 für Antworten, bis zum Ergebnis (Status %s, %d Durchgänge)" % (r["status"], r["nTrials"]), okk and nk == 3 and r["status"] == "ok")
        okk = tab_to("#btn-copy")
        C.check("Tastatur: Kopieren-Knopf per Tab erreichbar, sichtbarer Fokus (outline %s)" % pg.evaluate("getComputedStyle(document.activeElement).outlineStyle"), okk and pg.evaluate("getComputedStyle(document.activeElement).outlineStyle") != "none")
        C.check("Keine Konsolenfehler (Tastatur)", not errs and not ext, errs + ext)
        ctx.close()

        # ---------------- Fehlerfälle ----------------
        ctx, pg, errs, ext = new_page(browser, "desktop", "delete window.AudioContext; delete window.webkitAudioContext;")
        pg.goto(base + "/schwelle.html")
        t = pg.inner_text("#audio-problem")
        C.check("Audio nicht unterstützt: verständliche Meldung, Knöpfe gesperrt (%s)" % t[:50], pg.is_visible("#audio-problem") and "unterstützt Web Audio nicht" in t and pg.is_disabled("#btn-to-practice") and pg.is_disabled("#btn-testtone"))
        pg.screenshot(path=os.path.join(H.SHOTS, "schwelle_audio_fehlt.png"))
        C.check("Audio nicht unterstützt: keine Konsolenfehler", not errs, errs)
        ctx.close()

        blocked = """window.__flag = {run:false};
          Object.defineProperty(AudioContext.prototype, 'state', {get(){ return window.__flag.run ? 'running' : 'suspended'; }, configurable:true});
          AudioContext.prototype.resume = function(){ return Promise.resolve(); };"""
        ctx, pg, errs, ext = new_page(browser, "desktop", blocked)
        pg.goto(base + "/schwelle.html")
        pg.click("#btn-to-practice")
        pg.wait_for_timeout(300)
        t = pg.inner_text("#audio-problem")
        C.check("Audio blockiert: Meldung '%s...' mit Knopf 'Audio freigeben', Übung startet nicht" % t[:30], pg.is_visible("#audio-problem") and "blockiert" in t and pg.is_visible("#btn-audio-retry") and pg.is_visible("#view-setup"))
        pg.screenshot(path=os.path.join(H.SHOTS, "schwelle_audio_blockiert.png"))
        pg.evaluate("window.__flag.run = true")
        pg.click("#btn-audio-retry")
        pg.wait_for_timeout(200)
        pg.click("#btn-to-practice")
        C.check("Audio freigegeben: Meldung verschwindet, Übung lässt sich starten", pg.is_hidden("#audio-problem") and pg.is_visible("#view-trial"))
        C.check("Audio blockiert: keine Konsolenfehler", not errs, errs)
        ctx.close()

        # Abbrechen (zweistufig) und Unterbrechung (Echtzeit)
        ctx, pg, errs, ext = new_page(browser, "desktop", "window.__test = {instant:false};")
        pg.goto(base + "/schwelle.html")
        pg.click("#btn-to-practice")
        pg.click("#btn-go")
        pg.wait_for_function("document.getElementById('trial-status').textContent.includes('Hör zu')")
        pg.click("#btn-cancel")
        lab1 = pg.inner_text("#btn-cancel")
        still = pg.is_visible("#view-trial")
        pg.click("#btn-cancel")
        C.check("Abbrechen ist zweistufig ('%s' -> zurück zum Setup, Antworten gesperrt)" % lab1, lab1 == "Wirklich abbrechen?" and still and pg.is_visible("#view-setup") and pg.evaluate("window.__test.state.awaiting") is None)
        pg.click("#btn-to-practice")
        pg.click("#btn-go")
        pg.wait_for_function("window.__test.state.inTrial === true")
        pg.evaluate("""() => { Object.defineProperty(document, 'hidden', {get(){return true;}, configurable:true}); document.dispatchEvent(new Event('visibilitychange')); }""")
        pg.wait_for_function("document.getElementById('trial-status').textContent.includes('unterbrochen')", timeout=10000)
        pg.evaluate("() => { Object.defineProperty(document, 'hidden', {get(){return false;}, configurable:true}); }")
        pg.wait_for_function("!document.getElementById('ans1').disabled", timeout=10000)
        lg = pg.evaluate("window.__test.log")
        C.check("Unterbrochener Durchgang (Tab im Hintergrund) wird verworfen und wiederholt (Protokoll: %s)" % [("unterbrochen" if x.get("interrupted") else "ok") for x in lg], any(x.get("interrupted") for x in lg) and pg.is_enabled("#ans1"))
        C.check("Abbrechen/Unterbrechen: keine Konsolenfehler", not errs, errs)
        ctx.close()

        # Übung wiederholen
        ctx, pg, errs, ext = new_page(browser, "desktop", init_js(4.0, 1, seed=3))
        pg.goto(base + "/schwelle.html")
        pg.click("#btn-to-practice"); pg.click("#btn-go")
        pg.wait_for_selector("#view-practice-done:not([hidden])")
        pg.click("#btn-practice-again"); pg.click("#btn-go")
        pg.wait_for_selector("#view-practice-done:not([hidden])")
        npr = len([x for x in pg.evaluate("window.__test.log") if x["phase"] == "practice"])
        C.check("'Nochmal üben' startet erneut 3 Übungsdurchgänge (Protokoll %d Übungsdurchgänge)" % npr, npr == 6 and not errs, errs)
        ctx.close()

        # ---------------- Echtzeit (optional) ----------------
        if REALTIME:
            init = """window.__test = {instant:false, seed:5}; window.__boxlog = [];
              document.addEventListener('DOMContentLoaded', () => { const f = () => { const a = document.getElementById('ibox1'), b = document.getElementById('ibox2');
                const rec = () => window.__boxlog.push([Math.round(performance.now()), a.classList.contains('on') ? 1 : (b.classList.contains('on') ? 2 : 0)]);
                new MutationObserver(rec).observe(a, {attributes:true, attributeFilter:['class']}); new MutationObserver(rec).observe(b, {attributes:true, attributeFilter:['class']}); }; f(); });"""
            ctx, pg, errs, ext = new_page(browser, "phone", init)
            pg.goto(base + "/schwelle.html")
            rng = np.random.default_rng(21)
            pg.tap("#btn-testtone")
            pg.wait_for_function("window.__test.audio.ctx && window.__test.audio.ctx.state==='running'")
            sr = pg.evaluate("window.__test.audio.ctx.sampleRate")
            pg.tap("#btn-to-practice"); pg.tap("#btn-go")
            t_enable = []
            n = 0
            phase_done = False
            while True:
                pg.wait_for_function("!document.getElementById('ans1').disabled || !document.getElementById('view-practice-done').hidden || !document.getElementById('view-result').hidden", timeout=20000)
                if pg.is_visible("#view-result"):
                    break
                if pg.is_visible("#view-practice-done"):
                    pg.tap("#btn-start-test")
                    continue
                cur = pg.evaluate("window.__test.current")
                t_enable.append(time.time())
                alpha = 4.0 / (-math.log(1 - 0.41421356237)) ** (1 / 3)
                pcor = 0.5 + 0.5 * (1 - math.exp(-((cur["gapMs"] / alpha) ** 3)))
                a = cur["gapInterval"] if rng.random() < pcor else 3 - cur["gapInterval"]
                pg.tap("#ans%d" % a)
                n += 1
            code, r = verify_result(pg, "Echtzeit Handy")
            bl = pg.evaluate("window.__boxlog")
            # Intervall-Leuchten: Folge 1 an, aus, 2 an, aus; Dauer ~400 ms
            durs1, durs2, gaps_ = [], [], []
            i = 0
            seq = [(t, s) for t, s in bl]
            for j in range(len(seq) - 3):
                if seq[j][1] == 1 and seq[j + 1][1] == 0 and seq[j + 2][1] == 2 and seq[j + 3][1] == 0:
                    durs1.append(seq[j + 1][0] - seq[j][0]); durs2.append(seq[j + 3][0] - seq[j + 2][0]); gaps_.append(seq[j + 2][0] - seq[j + 1][0])
            C.check("Echtzeit: Abtastrate %d Hz; Intervall-Anzeige in %d Durchgängen: 1 an %.0f ms (Soll 400), Pause %.0f ms (Soll 500), 2 an %.0f ms (Soll 400)" % (sr, len(durs1), np.mean(durs1), np.mean(gaps_), np.mean(durs2)),
                    len(durs1) >= n - 1 and abs(np.mean(durs1) - 400) < 40 and abs(np.mean(durs2) - 400) < 40 and abs(np.mean(gaps_) - 500) < 40)
            C.check("Echtzeit-Lauf (Touch, echter AudioContext): %d Antworten bis zum Ergebnis, keine Konsolenfehler" % n, not errs and not ext, errs + ext)
            ctx.close()
    browser.close()

C.finish()
