"""UI-Durchlauf signalentdeckung.html: Desktop, Handy (Touch), Tastatur, Randfälle, Gruppenansicht, Echtzeit.

Aufruf: python3 -I tests/test_05_ui_sdt.py
Simulierte Beobachter geben die Antworten über den Testhaken vor (Gauss-Modell: Ja, wenn x > d'/2 + c).
Echte Wahrnehmung kann nicht getestet werden.
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from scipy.stats import norm
from playwright.sync_api import sync_playwright

import _helpers as H

C = H.Checker("UI signalentdeckung.html")
PAY = {"liberal": dict(hit=1, cr=1, miss=-4, fa=-1), "konservativ": dict(hit=1, cr=1, miss=-1, fa=-4)}


def sdt_ref(h, m, fa, cr):
    nS, nN = h + m, fa + cr
    Hh, Ff, corr = h / nS, fa / nN, False
    if Hh in (0.0, 1.0) or Ff in (0.0, 1.0):
        Hh, Ff, corr = (h + 0.5) / (nS + 1), (fa + 0.5) / (nN + 1), True
    zH, zF = norm.ppf(Hh), norm.ppf(Ff)
    return dict(d=zH - zF, c=-0.5 * (zH + zF), H=Hh, F=Ff, corr=corr, H0=h / nS, F0=fa / nN)


def init_js(d, cl, ck, rngseed, seed=None, mode="gauss", order=None):
    """mode: gauss | yes | no | perfect"""
    s = "window.__test = {instant:true%s%s};\n" % ((", seed:%d" % seed) if seed is not None else "", (", order:%s" % order) if order else "")
    s += H.MULBERRY_JS + """
(function(){ const rng = mulberry32(%d), d=%f, cl=%f, ck=%f, mode=%r;
 function g(){ let u=0; while(u===0)u=rng(); const v=rng(); return Math.sqrt(-2*Math.log(u))*Math.cos(2*Math.PI*v); }
 window.__test.observer=function(tr){ if(mode==='yes') return true; if(mode==='no') return false; if(mode==='perfect') return tr.signal;
   const c = tr.block==='liberal' ? cl : (tr.block==='konservativ' ? ck : 0); const x = g() + (tr.signal ? d : 0); return x > d/2 + c; }; })();""" % (rngseed, d, cl, ck, mode)
    return s


def new_page(browser, kind, init=None, w=None, h=None, **kw):
    if kind == "phone":
        ctx = browser.new_context(viewport={"width": w or 390, "height": h or 844}, has_touch=True, is_mobile=True, **kw)
    else:
        ctx = browser.new_context(viewport={"width": w or 1280, "height": h or 800}, **kw)
    pg = ctx.new_page()
    errors, external = [], []
    H.attach_collectors(pg, errors, external)
    if init:
        pg.add_init_script(init)
    return ctx, pg, errors, external


def act(pg, sel, kind):
    pg.tap(sel) if kind == "phone" else pg.click(sel)


def hscroll_ok(pg):
    return pg.evaluate("document.documentElement.scrollWidth <= window.innerWidth")


def small(pg):
    return pg.evaluate("""() => { const bad = [];
      document.querySelectorAll('button, a.btn, a.link, summary, input[type=range], .crumb a').forEach(e => {
        const r = e.getBoundingClientRect(); if (r.width === 0 && r.height === 0) return;
        if (r.height < 43.5 || r.width < 43.5) bad.push((e.id || e.textContent.trim().slice(0, 20)) + ':' + Math.round(r.width) + 'x' + Math.round(r.height)); });
      return bad; }""")


def set_slider(pg, v):
    pg.evaluate("(v) => { const e = document.getElementById('diff'); e.value = v; e.dispatchEvent(new Event('input')); }", v)


def full_flow(pg, kind, slider=50):
    set_slider(pg, slider)
    act(pg, "#btn-probe", kind)
    pg.wait_for_selector("#probe-res:not([hidden])", timeout=20000)
    act(pg, "#btn-lock", kind)
    act(pg, "#btn-block-start", kind)
    pg.wait_for_selector("#view-pre:not([hidden])", timeout=30000)
    act(pg, "#btn-block-start", kind)
    pg.wait_for_selector("#view-result:not([hidden])", timeout=30000)


def table_values(pg):
    """Liest die Ergebnistabelle: {Zeilenname: [Spalte1, Spalte2]}"""
    return pg.evaluate("""() => { const o = {}; document.querySelectorAll('#res-table tbody tr').forEach(tr => {
      o[tr.querySelector('th').textContent] = Array.from(tr.querySelectorAll('td')).map(td => td.textContent); }); return o; }""")


def num(s):
    return float(s.replace("−", "-").replace("*", "").strip())


NB = 40          # Durchgänge je Block (Standard der App, wird unten aus der Seite gelesen)
NP = 16          # Probelauf


def verify(pg, label, check_roc=True):
    d = pg.evaluate("() => { const T = window.__test, r = T.lastResult; return {order: r.order, amp: r.amp, code: r.code, log: T.log, id: r.id}; }")
    log = [x for x in d["log"] if x.get("phase") == "block"]
    tv = table_values(pg)
    ok_all = True
    msgs = []
    for col, kind in enumerate(d["order"]):
        ent = [x for x in log if x["block"] == kind]
        cnt = {k: sum(1 for x in ent if x["outcome"] == k) for k in ("hit", "miss", "fa", "cr")}
        sig = sum(1 for x in ent if x["signal"])
        pts = sum(PAY[kind][x["outcome"]] for x in ent)
        ref = sdt_ref(cnt["hit"], cnt["miss"], cnt["fa"], cnt["cr"])
        shown = dict(hit=int(tv["Treffer"][col]), miss=int(tv["Verpasser"][col]), fa=int(tv["Fehlalarme"][col]), cr=int(tv["Korrekte Ablehnungen"][col]))
        ok = (len(ent) == NB and sig == NB // 2 and shown == cnt and abs(num(tv["d′"][col]) - ref["d"]) < 0.0051 and abs(num(tv["Kriterium c"][col]) - ref["c"]) < 0.0051
              and abs(num(tv["Trefferrate"][col]) - ref["H0"]) < 0.0051 and abs(num(tv["Fehlalarmrate"][col]) - ref["F0"]) < 0.0051 and num(tv["Punkte"][col]) == pts
              and all(x["amp"] == d["amp"] for x in ent) and all(x["points"] == PAY[kind][x["outcome"]] for x in ent)
              and ("*" in tv["d′"][col]) == ref["corr"])
        ok_all &= ok
        msgs.append("%s: %s, d'=%.2f c=%.2f Punkte %d" % (kind, cnt, ref["d"], ref["c"], pts))
    C.check("[%s] Ergebnistabelle = Python-Rechnung aus dem Protokoll (je Block %d Durchgänge, %d mit Signal, gleiche Amplitude %.2f in beiden Blöcken, Punkte nach Matrix): %s" % (label, NB, NB // 2, d["amp"], "; ".join(msgs)), ok_all)
    pos_ok = pg.evaluate("() => window.__test.log.filter(x => x.signal).every(x => x.pos && window.__test.positionOk(x.pos)) && window.__test.log.filter(x => !x.signal).every(x => x.pos === null)")
    C.check("[%s] Protokoll: jeder Signal-Durchgang (Probelauf und Blöcke) hat eine Fleckposition ausserhalb der Ausschlusszone, Catch-Durchgänge keine" % label, pos_ok)
    if check_roc:
        n_l = pg.locator("#roc-wrap svg circle.mL").count()
        n_k = pg.locator("#roc-wrap svg path.mK").count()
        C.check("[%s] ROC-Diagramm: 1 Punkt je Block, Kurve, Diagonale (%d + %d Marken)" % (label, n_l, n_k), n_l == 1 and n_k == 1 and pg.locator("#roc-wrap svg path.curve").count() == 1 and pg.locator("#roc-wrap svg line.diag").count() == 1)
    p = pg.evaluate("(c) => window.__test.parseCode(c)", pg.inner_text("#res-code"))
    c_ok = p["ok"] and p["order"] == d["order"]
    for kind in ("liberal", "konservativ"):
        ent = [x for x in log if x["block"] == kind]
        c_ok &= all(p[kind][k] == sum(1 for x in ent if x["outcome"] == k) for k in ("hit", "miss", "fa", "cr"))
    C.check("[%s] Ergebnis-Code %s: Rundreise enthält Zählwerte und Reihenfolge" % (label, d["code"]), c_ok and d["code"] == pg.inner_text("#res-code"))
    return d, log


with sync_playwright() as pw:
    browser = pw.chromium.launch()
    with H.serve() as base:
        # ---------------- Desktop ----------------
        ctx, pg, errs, ext = new_page(browser, "desktop", init_js(1.5, -0.6, 0.6, 3, seed=5))
        ctx.grant_permissions(["clipboard-read", "clipboard-write"], origin=base.rsplit("/", 1)[0])
        pg.goto(base + "/signalentdeckung.html")
        NB = pg.evaluate("window.__test.CONFIG.trialsPerBlock"); NP = pg.evaluate("window.__test.CONFIG.probeTrials")
        C.check("Standardwerte: %d Durchgänge je Block, %d im Probelauf, Code-Version v2" % (NB, NP), (NB, NP) == (40, 16) and pg.evaluate("window.__test.buildCode('abcd', ['liberal','konservativ'], {hit:1,miss:1,fa:1,cr:1}, {hit:1,miss:1,fa:1,cr:1})").startswith("HSLU-sdt-v2."))
        C.check("[Desktop] Setup: kein horizontales Scrollen, Klickflächen >= 44 px %s, 'Festlegen' gesperrt bis Probelauf" % small(pg), hscroll_ok(pg) and not small(pg) and pg.is_disabled("#btn-lock"))
        pg.screenshot(path=os.path.join(H.SHOTS, "sdt_setup_desktop.png"), full_page=True)
        pg.click("#btn-ex-sig")
        ex1 = pg.evaluate("window.__test.lastExample")
        pg.click("#btn-ex-sig")
        ex2 = pg.evaluate("window.__test.lastExample")
        okx = pg.evaluate("(p) => window.__test.positionOk(p)", ex1["pos"]) and pg.evaluate("(p) => window.__test.positionOk(p)", ex2["pos"])
        dth = abs(((ex2["pos"]["theta"] - ex1["pos"]["theta"] + 3 * math.pi) % (2 * math.pi)) - math.pi)
        C.check("Beispiel mit Signal: Fleck ausserhalb der Ausschlusszone (Abstand %.1f und %.1f px, Zone 40), zwei aufeinanderfolgende Beispiele an verschiedenen Stellen (Winkelabstand %.0f Grad)" % (ex1["pos"]["r"], ex2["pos"]["r"], math.degrees(dth)), okx and dth > math.radians(79))
        pg.click("#btn-ex-no")
        C.check("Beispiel ohne Signal: kein Fleck (pos null), Hinweistext nennt 'nie in der Mitte'", pg.evaluate("window.__test.lastExample.pos") is None and "nie in der Mitte" in pg.inner_text("#view-setup"))
        set_slider(pg, 50)
        pg.click("#btn-probe")
        C.check("Probelauf: Trial-Ansicht ohne Matrix und ohne Punktestand", pg.is_visible("#view-run") and pg.is_hidden("#run-matrix") and pg.is_hidden("#run-score"))
        pg.wait_for_selector("#probe-res:not([hidden])", timeout=20000)
        txt = pg.inner_text("#probe-res")
        C.check("Probelauf-Ergebnis: '%s'" % txt.splitlines()[0], "von %d richtig" % NP in txt and "65 bis 85" in txt and pg.is_enabled("#btn-lock"))
        set_slider(pg, 60)
        C.check("Schwierigkeit nach dem Probelauf geändert: 'Festlegen' wieder gesperrt, Hinweis erscheint", pg.is_disabled("#btn-lock") and "neuen Probelauf" in pg.inner_text("#probe-res"))
        set_slider(pg, 50)
        C.check("Regler zurück auf den Probelauf-Wert: 'Festlegen' wieder aktiv", pg.is_enabled("#btn-lock"))
        pg.click("#btn-lock")
        C.check("Nach 'Festlegen' ist die Schwierigkeit gesperrt (Regler und Probelauf deaktiviert)", pg.is_disabled("#diff") and pg.is_disabled("#btn-probe") and pg.is_visible("#view-pre"))
        pre_txt = pg.inner_text("#pre-matrix")
        first_kind = pg.evaluate("window.__test.state.order[0]")
        pg.screenshot(path=os.path.join(H.SHOTS, "sdt_matrix_desktop.png"))
        C.check("Matrix vor Block 1 sichtbar (%s)" % pre_txt.replace("\n", " ")[:80], "Treffer" in pre_txt and "Verpasser" in pre_txt and "Fehlalarm" in pre_txt and "Korrekte Ablehnung" in pre_txt and pg.inner_text("#h-pre") == "Block 1 von 2")
        pg.click("#btn-block-start")
        C.check("Im Block: Matrix und Punktestand sichtbar, Zähler 'Durchgang x von %d'" % NB, pg.is_visible("#run-matrix") and pg.is_visible("#run-score") and ("von %d" % NB) in pg.inner_text("#run-count"))
        pg.wait_for_selector("#view-pre:not([hidden])", timeout=30000)
        C.check("Zwischenbildschirm: 'Block 2 von 2', Punkte von Block 1 genannt, andere Matrix (%s)" % pg.inner_text("#pre-prev"), pg.inner_text("#h-pre") == "Block 2 von 2" and "Punkte" in pg.inner_text("#pre-prev"))
        matrix2 = pg.inner_text("#pre-matrix")
        C.check("Matrix von Block 2 unterscheidet sich von Block 1", matrix2 != pre_txt)
        pg.click("#btn-block-start")
        pg.wait_for_selector("#view-result:not([hidden])", timeout=30000)
        d, log = verify(pg, "Desktop")
        C.check("[Desktop] Ergebnis: kein horizontales Scrollen, Klickflächen >= 44 px %s" % small(pg), hscroll_ok(pg) and not small(pg))
        pg.screenshot(path=os.path.join(H.SHOTS, "sdt_ergebnis_desktop.png"), full_page=True)
        pg.click("#btn-copy")
        pg.wait_for_timeout(300)
        C.check("Kopieren: Zwischenablage = Code", pg.evaluate("navigator.clipboard.readText()") == d["code"] and pg.inner_text("#copy-msg") == "Kopiert.")
        ords = d["order"]
        C.check("Neutrale Benennung: keine Deutung ('liberal', 'konservativ', 'warst') im sichtbaren Text", not any(w in pg.inner_text("body").lower() for w in ("liberal", "konservativ", "du warst", "vorsichtig")))
        C.check("Keine Konsolenfehler/externen Anfragen (Desktop)", not errs and not ext, errs + ext)
        code_d = d["code"]
        ctx.close()

        # ---------------- Block-Reihenfolge zufällig, beide Reihenfolgen ----------------
        orders = set()
        for sd in range(1, 9):
            c_, p_, e_, x_ = new_page(browser, "desktop", init_js(1.5, -0.6, 0.6, sd, seed=sd))
            p_.goto(base + "/signalentdeckung.html")
            set_slider(p_, 50); p_.click("#btn-probe"); p_.wait_for_selector("#probe-res:not([hidden])"); p_.click("#btn-lock")
            orders.add(p_.evaluate("window.__test.state.order[0]"))
            c_.close()
        C.check("Reihenfolge der Blöcke ist zufällig (Seeds 1-8 ergeben %s)" % sorted(orders), orders == {"liberal", "konservativ"})

        # ---------------- Gruppe: 5 simulierte Personen ----------------
        people, codes = [], []
        for i, (d_, cl, ck) in enumerate([(1.0, -0.4, 0.5), (1.5, -0.6, 0.6), (2.0, -0.8, 0.7), (1.2, -0.3, 0.3), (1.8, -0.5, 0.9)]):
            c_, p_, e_, x_ = new_page(browser, "desktop", init_js(d_, cl, ck, 50 + i, seed=20 + i))
            p_.goto(base + "/signalentdeckung.html")
            full_flow(p_, "desktop")
            codes.append(p_.inner_text("#res-code"))
            people.append(p_.evaluate("(() => { const r = window.__test.lastResult; return ['liberal','konservativ'].map(k => r.blocks[k].sdt); })()"))
            c_.close()
        ctx, pg, errs, ext = new_page(browser, "desktop")
        pg.goto(base + "/signalentdeckung.html#gruppe")
        bad_code = codes[4][:-1] + ("0" if codes[4][-1] != "0" else "1")
        pg.fill("#group-in", "\n".join([codes[0], "", codes[1], codes[1], codes[2], "kein Code hier", codes[3], bad_code, codes[0]]))
        pg.click("#btn-group-run")
        out = pg.inner_text("#group-out")
        G = pg.evaluate("window.__test.lastGroup.summary")
        dl = np.array([sdt_ref(p[0]["hits"], p[0]["misses"], p[0]["fas"], p[0]["crs"])["d"] for p in people[:4]])
        dk = np.array([sdt_ref(p[1]["hits"], p[1]["misses"], p[1]["fas"], p[1]["crs"])["d"] for p in people[:4]])
        cl_ = np.array([sdt_ref(p[0]["hits"], p[0]["misses"], p[0]["fas"], p[0]["crs"])["c"] for p in people[:4]])
        ck_ = np.array([sdt_ref(p[1]["hits"], p[1]["misses"], p[1]["fas"], p[1]["crs"])["c"] for p in people[:4]])
        C.check("Gruppe: 4 gültige Codes, 2 Duplikate ignoriert, 2 ungültige Zeilen benannt (Zeile 6 und 8): %s" % out.splitlines()[0],
                "4 gültige" in out and "2 doppelte" in out and "2 ungültig" in out and "Zeile 6" in out and "Zeile 8" in out)
        e = max(abs(G["sum"]["liberal"]["d"]["mean"] - dl.mean()), abs(G["sum"]["konservativ"]["d"]["mean"] - dk.mean()), abs(G["sum"]["liberal"]["c"]["mean"] - cl_.mean()), abs(G["sum"]["konservativ"]["c"]["mean"] - ck_.mean()),
                abs(G["sum"]["liberal"]["d"]["sd"] - dl.std(ddof=1)), abs(G["sum"]["konservativ"]["c"]["sd"] - ck_.std(ddof=1)))
        C.check("Gruppe: Mittelwerte und SD von d' und c je Block = Python (max. Abweichung %.1e); mittleres c: Verpasser-teuer %.2f, Fehlalarm-teuer %.2f" % (e, cl_.mean(), ck_.mean()), e < 1e-9)
        rows = pg.locator("#group-out table").first.locator("tbody tr").count()
        n_l = pg.locator("#group-roc svg circle.mL").count()
        n_k = pg.locator("#group-roc svg path.mK").count()
        C.check("Gruppe: Tabelle mit 4 Personen + 2 Zeilen (Mittelwert, SD); Gruppen-ROC mit je 4 Einzelpunkten + 1 Mittelpunkt je Block (%d Kreise, %d Rauten)" % (n_l, n_k), rows == 6 and n_l == 5 and n_k == 5)
        pg.screenshot(path=os.path.join(H.SHOTS, "sdt_gruppe_desktop.png"), full_page=True)
        pg.fill("#group-in", "Quatsch")
        pg.click("#btn-group-run")
        C.check("Gruppe: nur Ungültiges -> 0 gültige, Zeile benannt, keine Tabelle", "0 gültige" in pg.inner_text("#group-out") and "Zeile 1" in pg.inner_text("#group-out") and pg.locator("#group-out table").count() == 0)
        pg.fill("#group-in", codes[0])
        pg.click("#btn-group-run")
        C.check("Gruppe: eine Person -> SD '–', ROC wird gezeichnet", "–" in pg.inner_text("#group-out") and pg.locator("#group-roc svg").count() == 1)
        pg.fill("#group-in", "")
        pg.click("#btn-group-run")
        C.check("Gruppe: leere Eingabe -> '0 gültige Codes', kein Fehler", "0 gültige" in pg.inner_text("#group-out") and not errs, errs)
        ctx.close()

        # ---------------- Kantenbeobachter ----------------
        for mode, lab in (("yes", "immer Ja (H = 1, FA = 1)"), ("no", "immer Nein (H = 0, FA = 0)"), ("perfect", "perfekt (H = 1, FA = 0)")):
            c_, p_, e_, x_ = new_page(browser, "desktop", init_js(1.5, 0, 0, 1, seed=3, mode=mode))
            p_.goto(base + "/signalentdeckung.html")
            full_flow(p_, "desktop")
            verify(p_, "Kantenfall " + lab, check_roc=True)
            C.check("[Kantenfall %s] Hinweis zur log-linearen Korrektur und Sternchen sichtbar, ROC ohne NaN" % lab, "log-linear korrigiert" in p_.inner_text("#res-table") and "NaN" not in p_.inner_html("#roc-wrap") and not e_, e_)
            if mode == "yes":
                p_.screenshot(path=os.path.join(H.SHOTS, "sdt_kantenfall_immer_ja.png"), full_page=True)
            c_.close()

        # ---------------- Handy: Touch, Tippen ----------------
        ctx, pg, errs, ext = new_page(browser, "phone", "window.__test = {instant:true, seed:9};")
        pg.goto(base + "/signalentdeckung.html")
        C.check("[Handy 390x844] Setup: kein horizontales Scrollen, Klickflächen >= 44 px %s" % small(pg), hscroll_ok(pg) and not small(pg))
        pg.screenshot(path=os.path.join(H.SHOTS, "sdt_setup_handy.png"), full_page=True)
        rng = np.random.default_rng(4)

        def tap_loop(done_sel):
            n = 0
            while True:
                pg.wait_for_function("!document.getElementById('btn-yes').disabled || !document.querySelector('%s').hidden" % done_sel, timeout=20000)
                if pg.is_visible(done_sel) or (done_sel == "#probe-res" and pg.is_visible("#view-setup")):
                    return n
                cur = pg.evaluate("window.__test.current")
                c = {"liberal": -0.6, "konservativ": 0.6}.get(cur["block"], 0.0)
                x = rng.normal() + (1.5 if cur["signal"] else 0)
                pg.tap("#btn-yes" if x > 0.75 + c else "#btn-no")
                n += 1
        set_slider(pg, 50)
        pg.tap("#btn-probe")
        n0 = tap_loop("#probe-res")
        pg.tap("#btn-lock")
        pg.tap("#btn-block-start")
        n1 = tap_loop("#view-pre")
        pg.screenshot(path=os.path.join(H.SHOTS, "sdt_matrix_handy.png"))
        pg.tap("#btn-block-start")
        pg.wait_for_function("!document.getElementById('btn-yes').disabled")
        pg.screenshot(path=os.path.join(H.SHOTS, "sdt_block_handy.png"))
        n2 = tap_loop("#view-result")
        C.check("[Handy] Durchlauf per Tippen: %d (Probe) + %d + %d Antworten bis zum Ergebnis" % (n0, n1, n2), (n0, n1, n2) == (NP, NB, NB) and pg.is_visible("#view-result"))
        verify(pg, "Handy")
        C.check("[Handy] Ergebnis: kein horizontales Scrollen, Klickflächen >= 44 px %s" % small(pg), hscroll_ok(pg) and not small(pg))
        pg.screenshot(path=os.path.join(H.SHOTS, "sdt_ergebnis_handy.png"), full_page=True)
        w = pg.evaluate("document.querySelector('#roc-wrap svg').getBoundingClientRect().width")
        C.check("[Handy] ROC passt in die Breite (%.0f px)" % w, w <= 390)
        pg.tap("#link-group2")
        pg.fill("#group-in", "\n".join(codes[:3]))
        pg.tap("#btn-group-run")
        C.check("[Handy] Gruppenansicht: 3 Personen, kein horizontales Scrollen", pg.locator("#group-out table").first.locator("tbody tr").count() == 5 and hscroll_ok(pg))
        pg.screenshot(path=os.path.join(H.SHOTS, "sdt_gruppe_handy.png"), full_page=True)
        C.check("Keine Konsolenfehler (Handy)", not errs and not ext, errs + ext)
        ctx.close()

        for (w_, h_, nm) in ((360, 640, "360x640"), (768, 1024, "Tablet 768x1024")):
            ctx, pg, errs, ext = new_page(browser, "phone", init_js(1.5, -0.6, 0.6, 2, seed=1), w=w_, h=h_)
            pg.goto(base + "/signalentdeckung.html")
            s_ok = hscroll_ok(pg)
            set_slider(pg, 50); pg.tap("#btn-probe"); pg.wait_for_selector("#probe-res:not([hidden])"); pg.tap("#btn-lock"); pg.tap("#btn-block-start")
            pg.wait_for_selector("#view-pre:not([hidden])")
            pg.tap("#btn-block-start")
            pg.wait_for_selector("#view-result:not([hidden])")
            C.check("[%s] Setup und Ergebnis ohne horizontales Scrollen, ROC %.0f px" % (nm, pg.evaluate("document.querySelector('#roc-wrap svg').getBoundingClientRect().width")), s_ok and hscroll_ok(pg) and not errs, errs)
            if w_ == 360:
                pg.screenshot(path=os.path.join(H.SHOTS, "sdt_ergebnis_360.png"), full_page=True)
            ctx.close()
        ctx, pg, errs, ext = new_page(browser, "desktop", init_js(1.5, -0.6, 0.6, 2, seed=1), color_scheme="dark")
        pg.goto(base + "/signalentdeckung.html")
        full_flow(pg, "desktop")
        pg.screenshot(path=os.path.join(H.SHOTS, "sdt_ergebnis_dunkel.png"), full_page=True)
        C.check("Dunkelmodus: Durchlauf ohne Fehler, Hintergrund %s" % pg.evaluate("getComputedStyle(document.body).backgroundColor"), not errs, errs)
        ctx.close()

        # ---------------- Tastatur ----------------
        ctx, pg, errs, ext = new_page(browser, "desktop", "window.__test = {instant:true, seed:4};")
        pg.goto(base + "/signalentdeckung.html")

        def tab_to(sel, maxn=40):
            for _ in range(maxn):
                if pg.evaluate("document.activeElement && document.activeElement.matches(%r)" % sel):
                    return True
                pg.keyboard.press("Tab")
            return False
        k_ok = tab_to("#diff")
        v0 = int(pg.evaluate("document.getElementById('diff').value"))
        for _ in range(3):
            pg.keyboard.press("ArrowRight")
        k_ok &= v0 == 40 and pg.evaluate("document.getElementById('diff').value") == str(v0 + 3)
        k_ok &= tab_to("#btn-probe")
        pg.keyboard.press("Enter")
        rng = np.random.default_rng(12)

        def key_loop(done_sel):
            n = 0
            while True:
                pg.wait_for_function("!document.getElementById('btn-yes').disabled || !document.querySelector('%s').hidden" % done_sel, timeout=20000)
                if pg.is_visible(done_sel) or (done_sel == "#probe-res" and pg.is_visible("#view-setup")):
                    return n
                cur = pg.evaluate("window.__test.current")
                x = rng.normal() + (1.5 if cur["signal"] else 0)
                pg.keyboard.press("j" if x > 0.75 else "n")
                n += 1
        n0 = key_loop("#probe-res")
        k_ok &= tab_to("#btn-lock")
        pg.keyboard.press("Enter")
        k_ok &= tab_to("#btn-block-start")
        pg.keyboard.press("Enter")
        n1 = key_loop("#view-pre")
        k_ok &= tab_to("#btn-block-start")
        pg.keyboard.press("Space")
        n2 = key_loop("#view-result")
        C.check("Reine Tastaturbedienung: Regler mit Pfeiltasten, Knöpfe mit Tab/Enter/Leertaste, Antworten mit J und N (%d + %d + %d Antworten) bis zum Ergebnis" % (n0, n1, n2), k_ok and (n0, n1, n2) == (NP, NB, NB) and pg.is_visible("#view-result"))
        verify(pg, "Tastatur", check_roc=False)
        C.check("Keine Konsolenfehler (Tastatur)", not errs and not ext, errs + ext)
        ctx.close()

        # ---------------- Abbrechen, Noch einmal ----------------
        ctx, pg, errs, ext = new_page(browser, "desktop", init_js(1.5, -0.6, 0.6, 2, seed=1))
        pg.goto(base + "/signalentdeckung.html")
        full_flow(pg, "desktop")
        pg.click("#btn-again")
        C.check("'Noch einmal': Setup wieder frei (Regler aktiv, Probelauf neu nötig)", pg.is_visible("#view-setup") and pg.is_enabled("#diff") and pg.is_disabled("#btn-lock") and pg.is_hidden("#probe-res"))
        ctx.close()
        ctx, pg, errs, ext = new_page(browser, "desktop", "window.__test = {instant:false};")
        pg.goto(base + "/signalentdeckung.html")
        pg.click("#btn-probe")
        pg.wait_for_function("!document.getElementById('btn-yes').disabled", timeout=10000)
        pg.click("#btn-cancel")
        l1 = pg.inner_text("#btn-cancel")
        pg.click("#btn-cancel")
        C.check("Abbrechen ist zweistufig ('%s' -> zurück zum Setup)" % l1, l1 == "Wirklich abbrechen?" and pg.is_visible("#view-setup") and pg.is_enabled("#btn-probe") and not errs, errs)
        # ---------------- Echtzeit: Anzeigedauer, Unterbrechung ----------------
        ctx.close()
        ctx, pg, errs, ext = new_page(browser, "phone", "window.__test = {instant:false, seed:8};")
        pg.goto(base + "/signalentdeckung.html")
        rng = np.random.default_rng(2)
        set_slider(pg, 50)
        pg.tap("#btn-probe")
        pg.wait_for_function("window.__test.state.inTrial === true", timeout=5000)
        pg.evaluate("() => { Object.defineProperty(document, 'hidden', {get(){return true;}, configurable:true}); document.dispatchEvent(new Event('visibilitychange')); }")
        pg.wait_for_function("document.getElementById('run-fb').textContent.includes('unterbrochen')", timeout=10000)
        pg.evaluate("() => { Object.defineProperty(document, 'hidden', {get(){return false;}, configurable:true}); }")
        n = 0
        while True:
            pg.wait_for_function("!document.getElementById('btn-yes').disabled || !document.getElementById('probe-res').hidden", timeout=20000)
            if pg.is_visible("#probe-res"):
                break
            cur = pg.evaluate("window.__test.current")
            pg.tap("#btn-yes" if (rng.normal() + (1.5 if cur["signal"] else 0)) > 0.75 else "#btn-no")
            n += 1
        ex = pg.evaluate("window.__test.exposures")
        lg = pg.evaluate("window.__test.log")
        C.check("Echtzeit-Probelauf (Handy, Touch): %d Antworten; unterbrochener Durchgang verworfen und wiederholt (Protokoll: %d ungültig); Signal-Anzeige %d Messungen: Mittel %.1f ms, min %.1f, max %.1f (Soll 300, 60-Hz-Bildraster)" % (n, sum(1 for x in lg if x.get("invalid")), len(ex), np.mean(ex), min(ex), max(ex)),
                n == NP and any(x.get("invalid") for x in lg) and abs(np.mean(ex) - 300) < 12 and min(ex) >= 280 and max(ex) <= 330)
        pg.screenshot(path=os.path.join(H.SHOTS, "sdt_probe_ergebnis_handy.png"), full_page=True)
        pg.tap("#btn-lock")
        pg.tap("#btn-block-start")
        for _ in range(4):
            pg.wait_for_function("!document.getElementById('btn-yes').disabled", timeout=10000)
            pg.tap("#btn-yes")
            pg.wait_for_function("document.getElementById('btn-yes').disabled")
        txt = pg.inner_text("#run-score")
        C.check("Echtzeit-Block: nach 4 Antworten zeigt der Punktestand '%s' und die Matrix bleibt sichtbar" % txt, txt.startswith("Punkte:") and pg.is_visible("#run-matrix"))
        C.check("Keine Konsolenfehler (Echtzeit)", not errs and not ext, errs + ext)
        ctx.close()
    browser.close()

C.finish()
