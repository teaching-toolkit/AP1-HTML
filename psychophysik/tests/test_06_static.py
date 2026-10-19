"""Statische Prüfungen und file://-Lauf: Eszett, externe Verweise, Module, Grösse, Links, Konsole.
Start: python3 -I tests/test_06_static.py
"""
import os
import re
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from playwright.sync_api import sync_playwright

import _helpers as H

C = H.Checker("Statisch und file://")
files = ["index.html", "schwelle.html", "signalentdeckung.html"]
texts = {f: open(os.path.join(H.PROJECT, f), encoding="utf-8").read() for f in files}

# Eszett im ganzen Projektordner (Befehl aus 0.3)
r = subprocess.run(["grep", "-rnP", r"\xC3\x9F", H.PROJECT], capture_output=True, text=True)
C.check("Kein Eszett im Projektordner (grep -rnP \"\\xC3\\x9F\")", r.stdout.strip() == "", r.stdout[:200])
C.check("Genau drei HTML-Seiten, je Seite ein eigenes Skript, keine gemeinsame JS-Datei", sorted(f for f in os.listdir(H.PROJECT) if f.endswith(".html") or f.endswith(".js")) == sorted(files))
for f, t in texts.items():
    C.check("%s: lang=\"de\", viewport, bindet ../shared/base.css relativ ein" % f, 'lang="de"' in t and 'name="viewport"' in t and 'href="../shared/base.css"' in t)
    C.check("%s: keine ES-Module, kein fetch/XMLHttpRequest/sendBeacon/WebSocket, kein localStorage/cookie" % f,
            'type="module"' not in t and not re.search(r"\b(fetch|XMLHttpRequest|sendBeacon|WebSocket|localStorage|sessionStorage|document\.cookie)\b", t))
    urls = re.findall(r"(?:src|href)=\"(https?:[^\"]+)\"|url\(\s*['\"]?(https?:[^)'\"]+)", t)
    C.check("%s: keine externen Skripte, Schriften, Bilder oder Stylesheets (%s)" % (f, urls), not urls and not re.search(r"<script[^>]+src=|<img|<link[^>]+(?!shared)href=\"http", t))
    C.check("%s: Dateigrösse %.1f KB (< 300 KB)" % (f, len(t.encode()) / 1024), len(t.encode()) < 300 * 1024)
C.check("Gesamtgrösse der drei Seiten %.1f KB" % (sum(len(t.encode()) for t in texts.values()) / 1024), True)
C.check("Keine Abfrage von Alter, Geschlecht o. Ä. (keine <input> ausser Regler und Textfeld für Codes)", all(set(re.findall(r'<input[^>]*type="(\w+)"', t)) <= {"range"} for t in texts.values()))
C.check("Audio nur nach Nutzerklick: AudioContext wird nur in ensureAudio() erzeugt", texts["schwelle.html"].count("new AC(") == 2 and "function ensureAudio" in texts["schwelle.html"] and "new AudioContext" not in texts["schwelle.html"].replace("new AC(", ""))

with sync_playwright() as pw:
    browser = pw.chromium.launch()
    with H.serve() as base:
        for label, root in (("file://", "file://" + H.PROJECT), ("http://127.0.0.1", base)):
            pg = browser.new_page()
            errs, ext = [], []
            H.attach_collectors(pg, errs, ext)
            reqs = []
            pg.on("request", lambda rq: reqs.append(rq.url))
            pg.goto(root + "/index.html")
            hrefs = pg.evaluate("Array.from(document.querySelectorAll('a')).map(a => a.getAttribute('href'))")
            C.check("[%s] index.html: zwei Kacheln mit Dauer und Links %s" % (label, hrefs), pg.locator(".tile").count() == 2 and "Dauer" in pg.inner_text("body") and hrefs == ["schwelle.html", "schwelle.html#gruppe", "signalentdeckung.html", "signalentdeckung.html#gruppe"])
            for a in ("schwelle.html", "signalentdeckung.html"):
                pg.goto(root + "/index.html")
                pg.click("a[href='%s']" % a)
                pg.wait_for_load_state()
                C.check("[%s] Link von der Übersicht öffnet %s, Stylesheet geladen (Body-Schrift %s)" % (label, a, pg.evaluate("getComputedStyle(document.body).fontSize")), a in pg.url and pg.evaluate("getComputedStyle(document.body).fontSize") == "16px" and pg.is_visible("#view-setup"))
                pg.click(".crumb a")
                C.check("[%s] 'Übersicht'-Link führt zurück" % label, pg.url.split("?")[0].endswith("index.html"))
            C.check("[%s] Anfragen nur an Projektdateien und shared/base.css: %s" % (label, sorted({u.split("p5-psychophysik")[-1].split("/html-projekte")[-1] for u in reqs})), all(u.startswith(("file://", "http://127.0.0.1")) for u in reqs) and not ext and not errs, errs + ext)
            pg.close()
        # Funktionsprobe über file://: kompletter Lauf beider Seiten
        for page_name, flow in (("schwelle.html", "s"), ("signalentdeckung.html", "d")):
            pg = browser.new_page()
            errs, ext = [], []
            H.attach_collectors(pg, errs, ext)
            if flow == "s":
                pg.add_init_script(H.MULBERRY_JS + """window.__test={instant:true,seed:1}; (function(){const r=mulberry32(5); window.__test.listener=t=>r()<0.5+0.5*(1-Math.exp(-Math.pow(t.gapMs/3.5,3)))?t.gapInterval:3-t.gapInterval;})();""")
                pg.goto("file://" + H.PROJECT + "/schwelle.html")
                pg.click("#btn-to-practice"); pg.click("#btn-go"); pg.wait_for_selector("#view-practice-done:not([hidden])"); pg.click("#btn-start-test")
                pg.wait_for_selector("#view-result:not([hidden])")
                ok = "Schwelle:" in pg.inner_text("#res-main")
            else:
                pg.add_init_script(H.MULBERRY_JS + """window.__test={instant:true,seed:1}; (function(){const r=mulberry32(5); window.__test.observer=t=>r()<(t.signal?0.8:0.2);})();""")
                pg.goto("file://" + H.PROJECT + "/signalentdeckung.html")
                pg.click("#btn-probe"); pg.wait_for_selector("#probe-res:not([hidden])"); pg.click("#btn-lock"); pg.click("#btn-block-start")
                pg.wait_for_selector("#view-pre:not([hidden])"); pg.click("#btn-block-start"); pg.wait_for_selector("#view-result:not([hidden])")
                ok = "HSLU-sdt-v2" in pg.inner_text("#res-code")
            C.check("[file://] %s: kompletter Durchlauf bis zum Ergebnis-Code, keine Konsolenfehler" % page_name, ok and not errs and not ext, errs + ext)
            pg.close()
    browser.close()

C.finish()
