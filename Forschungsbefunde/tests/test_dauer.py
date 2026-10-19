"""Misst die Dauer eines Durchlaufs (Teil 1 und Teil 2, 5 Befunde) in Echtzeit mit einem simulierten Nutzer.

Aufruf:  python3 -I tests/test_dauer.py [zuegig|sorgfaeltig]

Der Nutzer ist ein Modell, KEINE echte Person: Er liest die angezeigten Texte mit fester
Lesegeschwindigkeit (Wörter pro Minute), denkt vor dem Schreiben der Stichworte eine feste Zeit nach,
tippt sie mit fester Anschlagzahl pro Sekunde, überfliegt in Teil 2 Aussage und eigene Stichworte kurz
(feste Zeit), liest die Erklärung und braucht eine feste Zeit, um die Plausibilität zu bewerten.
Gemessen wird die echte Wartezeit (Wanduhr) vom Laden der Seite (inklusive Lesen der Startseite) bis zur
Zusammenfassung. Die Zahlen sind daher eine Schätzung unter Modellannahmen und ersetzen keinen
Versuch mit Studierenden.

Profile:
  zuegig       250 Wörter/min, 15 s Nachdenken, 5 Anschläge/s, 3 s Überfliegen, 8 s Bewerten
  sorgfaeltig  150 Wörter/min, 30 s Nachdenken, 3 Anschläge/s, 5 s Überfliegen, 15 s Bewerten
"""
import sys
sys.dont_write_bytecode = True
import importlib.util
import json
import time
from pathlib import Path

spec = importlib.util.spec_from_file_location("common", Path(__file__).with_name("common.py"))
C = importlib.util.module_from_spec(spec)
spec.loader.exec_module(C)

from playwright.sync_api import sync_playwright

PROFILE = {
    "zuegig": {"wpm": 250, "denken": 15.0, "cps": 5.0, "ueberfliegen": 3.0, "bewerten": 8.0},
    "sorgfaeltig": {"wpm": 150, "denken": 30.0, "cps": 3.0, "ueberfliegen": 5.0, "bewerten": 15.0},
}
profil = sys.argv[1] if len(sys.argv) > 1 else "zuegig"
P = PROFILE[profil]
STICHWORT = "Anstrengung, Gewohnheit"      # 2 Stichworte, 23 Zeichen

httpd, url = C.start_server()
quelle = C.auswahl_befunde()


def woerter(s):
    return len(s.split())


with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_context(viewport={"width": 390, "height": 844}, has_touch=True, is_mobile=True).new_page()
    t0 = time.time()
    pg.goto(url + "?seed=dauer")
    intro_w = woerter(pg.inner_text("main"))
    pg.wait_for_timeout(1000 * intro_w * 60 / P["wpm"])               # Startseite lesen
    t_start = time.time()
    pg.tap("#start")
    pg.wait_for_selector("#form-p1")
    t_teil1 = []
    w_gesamt = 0
    ts = time.time()
    for i in range(C.N):
        z = C.zustand(pg)
        v = z["zuteilung"][i]
        ws = woerter(quelle[i][v]["studie"])
        w_gesamt += ws
        pg.wait_for_timeout(1000 * ws * 60 / P["wpm"])                # Aussage lesen
        pg.wait_for_timeout(1000 * P["denken"])                        # nachdenken
        pg.focus("#stichworte")
        pg.keyboard.type(STICHWORT, delay=1000 / P["cps"])             # tippen
        pg.keyboard.press("Enter")
        if i < C.N - 1:
            pg.wait_for_selector("#form-p1")
    t_teil1 = round(time.time() - ts, 1)
    pg.wait_for_selector("#start-p2")
    ue_w = woerter(pg.inner_text("main"))
    pg.wait_for_timeout(1000 * ue_w * 60 / P["wpm"])                   # Übergangsseite lesen
    pg.tap("#start-p2")
    pg.wait_for_selector("#form-p2")
    ts = time.time()
    for i in range(C.N):
        z = C.zustand(pg)
        v = z["zuteilung"][i]
        we = woerter(quelle[i][v]["erklaerung"])
        w_gesamt += we
        pg.wait_for_timeout(1000 * P["ueberfliegen"])                  # Aussage und eigene Stichworte kurz ansehen
        pg.wait_for_timeout(1000 * we * 60 / P["wpm"])                 # Erklärung lesen
        pg.wait_for_timeout(1000 * P["bewerten"])                      # Plausibilität abwägen
        pg.tap(".skala-opt:nth-child(%d)" % (1 + i % 5))
        pg.tap("#weiter-p2")
        if i < C.N - 1:
            pg.wait_for_selector("#form-p2")
    t_teil2 = round(time.time() - ts, 1)
    pg.wait_for_selector("#berichte")
    gesamt = time.time() - t0
    ab_start = time.time() - t_start
    b.close()

httpd.shutdown()
ergebnis = {
    "profil": profil, "modell": P,
    "dauer_inkl_startseite_s": round(gesamt, 1),
    "dauer_inkl_startseite_min": round(gesamt / 60, 1),
    "dauer_ab_klick_starten_s": round(ab_start, 1),
    "dauer_ab_klick_starten_min": round(ab_start / 60, 1),
    "teil1_s": t_teil1,
    "teil2_s": t_teil2,
    "woerter_gelesen_aussagen_und_erklaerungen": w_gesamt,
    "woerter_startseite": intro_w,
    "woerter_uebergang": ue_w,
}
print(json.dumps(ergebnis, ensure_ascii=False, indent=1))
