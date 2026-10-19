"""Ende-zu-Ende-Tests der Seite (Playwright, Chromium) auf Desktop und Handy.

Aufruf:  python3 -I tests/test_ui.py [--ohne-screenshots]

Prüft: vollständige Durchläufe (Klick, Touch, Tastatur) über http und file:// (Teil 1: Aussagen beurteilen,
Teil 2: Erklärungen einordnen), Texte der Seite gegen den Auftrag, kein Hinweis auf Fassungen vor der Auflösung,
Randfälle (leere Stichworte, Zurück in Teil 1, kein Zurück in Teil 2, Bewertung ohne Auswahl, Neuladen,
ohne Speicher, Code-Rundreise, Gruppenansicht, v1-Code, Auflösung nur nach Klick), Layout (kein horizontaler
Scroll, Klickflächen) bei 360/390/768/1280 px, hell und dunkel, und Screenshots.
"""
import sys
sys.dont_write_bytecode = True
import importlib.util
import random
import re
from pathlib import Path

spec = importlib.util.spec_from_file_location("common", Path(__file__).with_name("common.py"))
C = importlib.util.module_from_spec(spec)
spec.loader.exec_module(C)

from playwright.sync_api import sync_playwright

MIT_SHOTS = "--ohne-screenshots" not in sys.argv
ergebnisse = []
random.seed(20261015)
N = C.N
QUELLE = C.auswahl_befunde()
TEXTE = ["Normalität", "", "Gewohnheit, Druck", "Spotlight", "Verantwortung"]
ALT_V1 = "HSLU-hindsight-v1.139572570kg07"


def check(name, ok, detail=""):
    ergebnisse.append((name, ok, detail))
    print(("OK    " if ok else "FEHLER"), name, ("- " + detail) if detail else "")


def shot_el(page, sel, name):
    """Bild nur von einem Element (z. B. der Auflösungskarte), damit lange Seiten lesbar bleiben."""
    if not MIT_SHOTS:
        return
    C.SHOTS.mkdir(exist_ok=True)
    q = 66
    daten = page.locator(sel).screenshot(type="jpeg", quality=q)
    while b"\xc3\x9f" in daten and q > 40:
        q -= 1
        daten = page.locator(sel).screenshot(type="jpeg", quality=q)
    (C.SHOTS / name).write_bytes(daten)


def shot(page, name, voll=False, clip_h=None):
    if not MIT_SHOTS:
        return
    C.SHOTS.mkdir(exist_ok=True)
    kw = {"type": "jpeg", "quality": 66, "full_page": voll}
    if clip_h:
        kw["clip"] = {"x": 0, "y": 0, "width": page.viewport_size["width"], "height": clip_h}
        kw["full_page"] = True
    daten = page.screenshot(**kw)
    # Zufällig kann ein Bild die Bytefolge C3 9F enthalten; die Eszett-Prüfung aus 0.3 (grep -rnP) würde
    # dann «binary file matches» melden. Dann mit etwas anderer Qualität neu speichern.
    while b"\xc3\x9f" in daten and kw["quality"] > 40:
        kw["quality"] -= 1
        daten = page.screenshot(**kw)
    (C.SHOTS / name).write_bytes(daten)


ALLE_TEXTE = sorted({C.norm(C.ohne_stern(q[v][f])) for q in QUELLE for v in "AB" for f in ("studie", "erklaerung")}, key=len, reverse=True)


def ohne_befundtexte(s):
    """Entfernt die wörtlichen Befundtexte, damit nur die Oberfläche auf verbotene Wörter geprüft wird
    (ein Befundtext darf Wörter wie «falsche Reaktion» enthalten, das ist kein Hinweis auf Fassungen)."""
    s = C.norm(s)
    for x in ALLE_TEXTE:
        s = s.replace(x, " ")
    return s


def decode_ok(code, zu, werte):
    dec = C.py_decode(code)
    if dec is None:
        return False
    for i in range(N):
        if werte[i] is None:
            if dec[i] is not None:
                return False
        elif dec[i] != (zu[i], werte[i]):
            return False
    return True


def neuer_kontext(b, art, **kw):
    if art == "desktop":
        return b.new_context(viewport={"width": 1280, "height": 800}, **kw)
    if art == "handy":
        return b.new_context(viewport={"width": 390, "height": 844}, has_touch=True, is_mobile=True, **kw)
    if art == "handy360":
        return b.new_context(viewport={"width": 360, "height": 740}, has_touch=True, is_mobile=True, **kw)
    if art == "tablet":
        return b.new_context(viewport={"width": 768, "height": 1024}, has_touch=True, is_mobile=True, **kw)
    raise ValueError(art)


def person(b, url, seed, werte, art="desktop", texte=None, modus="klick"):
    """Ein Teilnehmer in eigenem Tab: vollständiger Durchlauf. Gibt (Code, Zustand) zurück."""
    ctx = neuer_kontext(b, art)
    pg = ctx.new_page()
    pg.goto(url + "?seed=" + seed)
    code = C.durchlauf(pg, texte or TEXTE, werte, modus=modus, quelle=QUELLE)
    z = C.zustand(pg)
    ctx.close()
    return code, z


def tabelle_lesen(page):
    return page.evaluate("""() => Array.from(document.querySelectorAll('#gruppe-tabelle tr')).filter(r => r.querySelector('td')).map(r =>
        Array.from(r.querySelectorAll('td')).map(td => [td.querySelector('.mw').textContent, td.querySelector('.n').textContent]))""")


def gruppe_ausfuellen(page, text):
    page.fill("#codes", text)
    page.click("#auswerten")
    page.wait_for_selector("#gruppe-chips")


def layout_pruefen(page, label, fehler):
    if not C.kein_horizontaler_scroll(page):
        fehler.append("%s: horizontaler Scroll (scrollWidth %s > %s)" % (
            label, page.evaluate("document.documentElement.scrollWidth"), page.evaluate("document.documentElement.clientWidth")))
    klein = C.zu_kleine_ziele(page)
    if klein:
        fehler.append("%s: Klickfläche < 44 px: %s" % (label, ", ".join(klein)))
    kon = C.kontrast_probleme(page)
    if kon:
        fehler.append("%s: Kontrast unter AA: %s" % (label, "; ".join(kon[:4])))
    ueber = C.inhalt_ueberlauf(page)
    if ueber:
        fehler.append("%s: Inhalt läuft über seinen Kasten: %s" % (label, "; ".join(ueber[:4])))


def tour(page, url, label, fehler, lange_woerter=True):
    """Geht alle Bildschirme durch und prüft Layout. Rückgabe: Zahl geprüfter Bildschirme."""
    n = 0
    touch = page.evaluate("'ontouchstart' in window")

    def tap(sel):
        page.tap(sel) if touch else page.click(sel)

    page.goto(url + "?seed=layout&neu=1")
    layout_pruefen(page, label + " Start", fehler); n += 1
    tap("#start")
    layout_pruefen(page, label + " Teil 1 Befund 1", fehler); n += 1
    langes = "W" * 200 if lange_woerter else "kurz"
    page.keyboard.press("Tab")
    page.keyboard.type(langes)
    page.keyboard.press("Enter")
    page.wait_for_selector("#zurueck-p1")
    layout_pruefen(page, label + " Teil 1 Befund 2 (mit Zurück)", fehler); n += 1
    for i in range(1, N):
        page.fill("#stichworte", "x" if i != 3 else "Ein kurzer Halbsatz zur Erklärung dieses Befunds")
        if i == N - 1:
            layout_pruefen(page, label + " Teil 1 letzter Befund", fehler); n += 1
        page.press("#stichworte", "Enter")
    page.wait_for_selector("#start-p2")
    layout_pruefen(page, label + " Übergang", fehler); n += 1
    tap("#start-p2")
    page.wait_for_selector("#form-p2")
    layout_pruefen(page, label + " Teil 2 (lange Stichworte)", fehler); n += 1
    page.keyboard.press("5"); page.keyboard.press("Enter")
    for i in range(1, N):
        page.wait_for_selector("#form-p2")
        page.keyboard.press(str(1 + i % 5)); page.keyboard.press("Enter")
    page.wait_for_selector("#berichte")
    layout_pruefen(page, label + " Zusammenfassung", fehler); n += 1
    tap("#aufloesung-zeigen")
    layout_pruefen(page, label + " Zusammenfassung mit Auflösung", fehler); n += 1
    tap("#zur-gruppe")
    layout_pruefen(page, label + " Gruppe leer", fehler); n += 1
    codes = []
    for k in range(5):
        zu = list(random.choice(["AABBA", "BABAB", "ABABB", "BBAAB", "BAABA"]))
        werte = [random.randint(1, 5) if (k != 4 or i < 3) else None for i in range(N)]
        codes.append(C.py_encode(zu, werte, "ab" + str(k)))
    codes += [codes[0], "HSLU-hindsight-v2.ungueltig" + "x" * 60, "<b>fett</b>", ALT_V1]
    gruppe_ausfuellen(page, "\n".join(codes))
    layout_pruefen(page, label + " Gruppe mit Ergebnis", fehler); n += 1
    tap("#gruppe-aufloesung-zeigen")
    layout_pruefen(page, label + " Gruppe mit Auflösung", fehler); n += 1
    return n


httpd, url = C.start_server()
furl = C.file_url()

with sync_playwright() as p:
    b = p.chromium.launch()

    # =====================================================================================
    # 1. Vollständige Durchläufe: Desktop/Klick, Handy/Touch, Tastatur; http und file://
    # =====================================================================================
    for art, modus, basis, bez in (("desktop", "klick", url, "Desktop Klick http"),
                                   ("handy", "tap", url, "Handy 390x844 Touch http"),
                                   ("desktop", "tastatur", url, "Desktop Tastatur http"),
                                   ("desktop", "klick", furl, "Desktop Klick file://"),
                                   ("handy", "tap", furl, "Handy 390x844 Touch file://"),
                                   ("desktop", "tastatur", furl, "Desktop Tastatur file://")):
        ctx = neuer_kontext(b, art)
        pg = ctx.new_page()
        wacht = C.Fehlerwaechter(pg)
        pg.goto(basis + "?seed=" + bez.replace(" ", "_"))
        werte = [random.randint(1, 5) for _ in range(N)]
        log = []
        try:
            code = C.durchlauf(pg, TEXTE, werte, modus=modus, quelle=QUELLE, texte_log=log)
            z = C.zustand(pg)
            na = z["zuteilung"].count("A")
            check("[%s] vollständiger Durchlauf (Teil 1, Übergang, Teil 2), alle Texte stimmen mit dem Auftrag, Stichworte in Teil 2 wiederholt, Code lesbar (%d x A)" % (bez, na),
                  na in (2, 3) and decode_ok(code, z["zuteilung"], werte), code)
            gesamttext = "\n".join(log)
            treffer = sorted(set(m.group(0).lower() for m in C.VERBOTEN.finditer(ohne_befundtexte(gesamttext))))
            check("[%s] kein Hinweis auf Versionen/echt/falsch auf einem der %d Bildschirme (vor der Auflösung)" % (bez, len(log)), not treffer, ", ".join(treffer))
            ohne_code = gesamttext.replace(code, "")
            check("[%s] «hindsight» kommt nur im Code vor" % bez, "hindsight" not in ohne_code.lower())
            reste = re.findall(r"\b(Sie|Ihnen|Ihre|Ihr|euch|eure|euer)\b", gesamttext)
            check("[%s] Anrede: kein «Sie»/«Ihr»/«euch» sichtbar" % bez, not reste, ",".join(reste))
            check("[%s] Zusammenfassung zeigt 5 Berichte und «Deine fünf Berichte»" % bez,
                  pg.locator("#berichte > li").count() == 5 and "Deine fünf Berichte" in pg.inner_text("main"))
            # Auflösung nur nach Klick
            vor = pg.evaluate("document.getElementById('main').textContent")
            check("[%s] Vor dem Klick steht nichts von der Auflösung im DOM (kein «tatsächlich», keine Quelle, kein Vorbehalt)" % bez,
                  "tatsächlich" not in vor and "Quelle:" not in vor and "Vorbehalt" not in vor and not pg.is_visible("#aufloesung")
                  and pg.locator("#aufl-liste").count() == 0)
            check("[%s] Knopf «Auflösung anzeigen» und Hinweis «erst nach dem Vergleich in der Gruppe» sichtbar" % bez,
                  pg.is_visible("#aufloesung-zeigen") and pg.inner_text("#aufloesung-zeigen") == "Auflösung anzeigen"
                  and "erst, nachdem du deine Berichte in der Gruppe verglichen hast" in pg.inner_text("#aufloesung-karte"))
            C.klick(pg, "#aufloesung-zeigen", "tap" if modus == "tap" else "klick")
            pg.wait_for_selector("#aufl-liste")
            ok_aufl = pg.locator("#aufl-liste > li").count() == 5
            for i in range(N):
                li = pg.locator("#aufl-liste > li").nth(i)
                t = C.norm(li.inner_text())
                tats = C.norm(C.ohne_stern(QUELLE[i]["A"]["studie"]))
                eigene = z["zuteilung"][i] == "A"
                soll = "Deine Version: die tatsächliche Aussage" if eigene else "Deine Version: die gegenteilige Aussage"
                ok_aufl = ok_aufl and tats in t and C.norm(QUELLE[i]["A"]["erklaerung"]) in t and soll in t \
                    and ("Deine Plausibilität: %d von 5" % werte[i]) in t
                if not eigene:
                    ok_aufl = ok_aufl and C.norm(C.ohne_stern(QUELLE[i]["B"]["studie"])) not in t
            check("[%s] Auflösung nach Klick: pro Befund tatsächliche Aussage (Version A) mit Erklärung, eigene Version (%d tatsächlich, %d gegenteilig), eigene Bewertung" % (bez, na, N - na), ok_aufl)
            daten = pg.evaluate("window.BEFUNDE")
            sichtbar = pg.inner_text("#aufl-liste")
            ok_qv = all((d["quelle"] in sichtbar) and (not d["vorbehalt"] or d["vorbehalt"] in sichtbar) for d in daten)
            check("[%s] Auflösung zeigt Quelle bei allen 5 und Vorbehalt bei den 4, die einen haben" % bez, ok_qv)
            C.klick(pg, "#aufloesung-zeigen", "tap" if modus == "tap" else "klick")
            check("[%s] «Auflösung verbergen» blendet sie wieder aus" % bez, not pg.is_visible("#aufloesung") and pg.inner_text("#aufloesung-zeigen") == "Auflösung anzeigen")
        except AssertionError as e:
            check("[%s] vollständiger Durchlauf" % bez, False, str(e)[:300])
        check("[%s] keine Konsolenfehler, kein pageerror, keine externe/fehlgeschlagene Anfrage" % bez, not wacht.fehler, "; ".join(wacht.fehler))
        namen = sorted(set(re.sub(r"\?.*", "", a).rsplit("/", 1)[-1] for a in wacht.anfragen))
        check("[%s] nur 3 Dateien geladen: %s" % (bez, ", ".join(namen)), namen == ["base.css", "befunde.js", "index.html"])
        ctx.close()

    # =====================================================================================
    # 2. Screenshots wichtiger Zustände (Desktop, Handy, dunkel)
    # =====================================================================================
    # Welche Bilder je Variante gespeichert werden (die dunklen nur in Auswahl, damit der Ordner klein bleibt)
    NUR = {"handy-dunkel": {"1", "4", "6", "7"}, "desktop-dunkel": {"4", "6", "7"}}

    def reise(pg, tap, pre):
        """Geht den Ablauf bis zur Gruppenansicht durch und macht Bilder (ganze Seite)."""
        def bild(key, name, sel=None):
            if key in NUR.get(pre, {key}):
                if sel:
                    shot_el(pg, sel, "%s-%s.jpg" % (pre, name))
                else:
                    shot(pg, "%s-%s.jpg" % (pre, name), voll=True)
        bild("1", "1-start")
        tap("#start")
        pg.fill("#stichworte", "Normalität, Durchschnitt")
        bild("2", "2-teil1")
        pg.press("#stichworte", "Enter")
        pg.fill("#stichworte", "")
        pg.press("#stichworte", "Enter")
        bild("2b", "2b-teil1-befund3")
        for t in ["Druck, Gewohnheit", "Spotlight", "Verantwortung"]:
            pg.fill("#stichworte", t)
            pg.press("#stichworte", "Enter")
        pg.wait_for_selector("#start-p2")
        bild("3", "3-uebergang")
        tap("#start-p2")
        tap(".skala-opt:nth-child(4)")
        bild("4", "4-teil2")
        tap("#weiter-p2")
        for i in range(1, N):
            pg.keyboard.press(str(1 + (i * 2) % 5)); pg.keyboard.press("Enter")
        pg.wait_for_selector("#berichte")
        bild("5", "5-zusammenfassung")
        tap("#aufloesung-zeigen")
        pg.wait_for_selector("#aufl-liste")
        bild("6", "6-aufloesung", "#aufloesung-karte")
        codes = []
        for k, zu in enumerate(["AABBA", "BABAB", "ABABB", "BBAAB", "BAABA"]):
            werte = [random.randint(1, 5) if (k != 4 or i < 3) else None for i in range(N)]
            codes.append(C.py_encode(list(zu), werte, "ab" + str(k)))
        codes += [codes[1], "HSLU-hindsight-v2.abcdefghi", ALT_V1]
        tap("#zur-gruppe")
        pg.fill("#codes", "\n".join(codes))
        tap("#auswerten")
        bild("7", "7-gruppe")
        tap("#gruppe-aufloesung-zeigen")
        bild("8", "8-gruppe-aufloesung", "#gruppe-aufloesung-karte")

    for art, pre, farbe in (("desktop", "desktop", "light"), ("handy", "handy", "light"),
                            ("handy", "handy-dunkel", "dark"), ("desktop", "desktop-dunkel", "dark")):
        ctx = neuer_kontext(b, art, color_scheme=farbe)
        pg = ctx.new_page()
        pg.goto(url + "?seed=42")
        touch = art == "handy"
        reise(pg, (lambda s, pg=pg, touch=touch: pg.tap(s) if touch else pg.click(s)), pre)
        ctx.close()

    ctx = neuer_kontext(b, "handy", color_scheme="dark")
    pg = ctx.new_page()
    pg.goto(url + "?seed=42")
    pg.tap("#start")
    for _ in range(N):
        pg.fill("#stichworte", "Anstrengung"); pg.press("#stichworte", "Enter")
    pg.tap("#start-p2"); pg.keyboard.press("2")
    rk_dunkel = C.rahmenkontrast(pg, ".skala-opt span")
    ctx.close()
    ctx = neuer_kontext(b, "desktop")
    pg = ctx.new_page()
    pg.goto(url + "?seed=42"); pg.click("#start")
    for _ in range(N):
        pg.fill("#stichworte", "a"); pg.press("#stichworte", "Enter")
    pg.click("#start-p2")
    rk_hell = C.rahmenkontrast(pg, ".skala-opt span")
    ctx.close()
    check("Rahmen der Skalenknöpfe: Kontrast zum Hintergrund hell %.1f:1, dunkel %.1f:1 (WCAG 1.4.11 verlangt 3:1)" % (rk_hell, rk_dunkel),
          rk_hell >= 3 and rk_dunkel >= 3)

    # =====================================================================================
    # 3. Layout: sechs Viewports
    # =====================================================================================
    for art, bez, farbe in (("handy360", "360x740 Touch", "light"), ("handy", "390x844 Touch", "light"), ("tablet", "768x1024 Touch", "light"),
                            ("desktop", "1280x800 Maus", "light"), ("handy", "390x844 Touch dunkel", "dark"), ("desktop", "1280x800 Maus dunkel", "dark")):
        ctx = neuer_kontext(b, art, color_scheme=farbe)
        pg = ctx.new_page()
        fehler = []
        n = tour(pg, url, bez, fehler)
        check("[Layout %s] %d Bildschirme: kein horizontaler Scroll, alle Klickflächen >= 44 px, kein Text läuft aus seinem Kasten (auch 200 Zeichen ohne Leerzeichen), Textkontrast >= AA" % (bez, n), not fehler, "; ".join(fehler))
        ctx.close()

    # Negativkontrolle der Layout-Prüfung: absichtlich zu kleiner Knopf und zu breites Element müssen auffallen
    ctx = neuer_kontext(b, "handy360")
    pg = ctx.new_page()
    pg.goto(url + "?seed=neg&neu=1")
    pg.evaluate("""() => { const k = document.createElement('button'); k.id = 'zuklein'; k.textContent = 'x'; k.style.cssText = 'width:20px;height:20px;min-height:0;min-width:0;padding:0';
      document.getElementById('main').appendChild(k);
      const w = document.createElement('div'); w.style.cssText = 'width:900px;height:5px'; document.getElementById('main').appendChild(w);
      const u = document.createElement('div'); u.id = 'ueberlauf'; u.style.cssText = 'width:60px;overflow:visible;white-space:nowrap'; u.textContent = 'Auflistungsaufgabenlang'; document.getElementById('main').appendChild(u); }""")
    f_neg = []
    layout_pruefen(pg, "Negativkontrolle", f_neg)
    pg.evaluate("""() => { const k = document.createElement('p'); k.id = 'blass'; k.textContent = 'kaum lesbar'; k.style.cssText = 'color:#bbbbbb;background:#ffffff'; document.getElementById('main').appendChild(k); }""")
    f_neg = []
    layout_pruefen(pg, "Negativkontrolle", f_neg)
    check("Negativkontrolle: Kontrastprüfung erkennt hellgrauen Text auf Weiss (#bbb: 1.9:1)", any("Kontrast" in x and "kaum lesbar" in x for x in f_neg), "; ".join(x for x in f_neg if "Kontrast" in x))
    check("Negativkontrolle: Layout-Prüfung erkennt einen 20-px-Knopf, ein 900-px-Element und überlaufenden Text (%d Meldungen)" % len(f_neg),
          any("zuklein" in x for x in f_neg) and any("horizontaler Scroll" in x for x in f_neg) and any("läuft über" in x for x in f_neg), "; ".join(f_neg))
    ctx.close()

    # =====================================================================================
    # 4. Randfälle
    # =====================================================================================
    ctx = neuer_kontext(b, "desktop", permissions=["clipboard-read", "clipboard-write"])
    pg = ctx.new_page()
    wacht = C.Fehlerwaechter(pg)
    pg.goto(url + "?seed=rand1")

    # 4.1 Start
    start_text = pg.inner_text("body")
    check("Startseite: kein Link «Gruppe auswerten», kein Hinweis auf Versionen, nennt «Stichworte genügen», «6 bis 8 Minuten», Teil 1 und Teil 2",
          pg.locator("#zur-gruppe").count() == 0 and not C.VERBOTEN.search(start_text) and "Stichworte genügen" in start_text
          and "6 bis 8 Minuten" in start_text and "Teil 1" in start_text and "Teil 2" in start_text)
    check("Startseite: keine Rede von Google Forms, allocate.monster, neun Befunden, 10 bis 12 Minuten",
          not re.search(r"Google|allocate|neun|10 bis 12", start_text))
    pg.click("#start")

    # 4.2 Teil 1: Hinweis, Zähler, leere Eingabe, kein Zurück bei Befund 1
    t1 = pg.inner_text("main")
    check("Teil 1: Frage «Wie würdest du diesen Befund erklären?» und sichtbarer Hinweis «Stichworte genügen: ein bis zwei Wörter oder ein kurzer Halbsatz reichen.»",
          "Wie würdest du diesen Befund erklären?" in t1 and "Stichworte genügen: ein bis zwei Wörter oder ein kurzer Halbsatz reichen." in t1 and pg.is_visible("#p1-hilfe"))
    check("Teil 1, Befund 1: Fortschritt «Befund 1 von 5» und «Teil 1 von 2: Aussagen beurteilen», kein Zurück-Knopf",
          "Befund 1 von 5" in t1 and "Teil 1 von 2: Aussagen beurteilen" in t1 and pg.locator("#zurueck-p1").count() == 0
          and pg.get_attribute(".progress", "aria-valuetext") == "Befund 1 von 5")
    check("Teil 1 zeigt keine Erklärung und keine Skala", pg.locator("#erklaerung").count() == 0 and pg.locator("input[name=wert]").count() == 0)
    check("Zähler zeigt «0 Zeichen» bei leerem Feld", pg.inner_text("#zaehler") == "0 Zeichen")
    pg.keyboard.press("Tab"); pg.keyboard.type("abc")
    check("Zähler zeigt «3 Zeichen» nach Eingabe von abc", pg.inner_text("#zaehler") == "3 Zeichen")
    pg.fill("#stichworte", "")
    pg.keyboard.press("Enter")
    pg.wait_for_selector("#zurueck-p1")
    check("Leeres Stichwortfeld lässt sich abschicken (Befund 2 erscheint)", C.zustand(pg)["idx"] == 1 and C.zustand(pg)["schritt"] == "p1")
    check("Leer wird als leer gespeichert", C.zustand(pg)["antworten"][0]["text"] == "")
    check("Befund 2: «Zurück» vorhanden, Fortschritt «Befund 2 von 5»", pg.is_visible("#zurueck-p1") and "Befund 2 von 5" in pg.inner_text(".fortschritt"))

    # 4.3 Zurück in Teil 1 (Knopf und Browser-Zurück) erhält die Texte
    pg.fill("#stichworte", "zweiter Text")
    pg.click("#zurueck-p1")
    pg.wait_for_selector("#form-p1")
    check("Knopf «Zurück» geht zu Befund 1 und zeigt dessen (leere) Eingabe", C.zustand(pg)["idx"] == 0 and pg.input_value("#stichworte") == "")
    pg.fill("#stichworte", "erster Text"); pg.press("#stichworte", "Enter")
    check("Zurück und wieder vor: Text von Befund 2 blieb erhalten (auch ohne Abschicken)", pg.input_value("#stichworte") == "zweiter Text")
    pg.press("#stichworte", "Enter")          # Befund 3
    pg.fill("#stichworte", "dritter Text")
    pg.go_back(); pg.wait_for_timeout(150)
    check("Browser-Zurück in Teil 1 geht einen Befund zurück (wie der Knopf), Text von Befund 2 steht da",
          C.zustand(pg)["idx"] == 1 and pg.input_value("#stichworte") == "zweiter Text" and pg.locator("#hinweis").count() == 0)
    pg.go_back(); pg.wait_for_timeout(150)
    check("Browser-Zurück ein zweites Mal: Befund 1 mit dem Text «erster Text»", C.zustand(pg)["idx"] == 0 and pg.input_value("#stichworte") == "erster Text")
    pg.go_back(); pg.wait_for_timeout(150)
    check("Browser-Zurück bei Befund 1: bleibt dort, Hinweis «Das war die erste Aussage»",
          C.zustand(pg)["idx"] == 0 and pg.is_visible("#hinweis") and "erste Aussage" in pg.inner_text("#hinweis"))
    # Entwurf überlebt Neuladen
    pg.fill("#stichworte", "Entwurf bleibt")
    pg.reload(); pg.wait_for_selector("#form-p1")
    check("Teil 1: Entwurf bleibt nach Neuladen erhalten, Fortschritt wiederhergestellt", pg.input_value("#stichworte") == "Entwurf bleibt" and "wiederhergestellt" in pg.inner_text("main"))

    # 4.4 Teil 1 abschliessen, Übergang
    for i in range(N):
        pg.fill("#stichworte", ["Entwurf bleibt", "", "Gewohnheit", "Druck, Sog", "Verantwortung"][i])
        if i == N - 1:
            check("Letzter Befund: Knopf «Teil 1 abschliessen» und Hinweis «Danach kannst du Teil 1 nicht mehr ändern.»",
                  pg.inner_text("#weiter-p1") == "Teil 1 abschliessen" and "Danach kannst du Teil 1 nicht mehr ändern." in pg.inner_text("main"))
        pg.press("#stichworte", "Enter")
        if i < N - 1:
            pg.wait_for_function("(n) => document.querySelector('.fortschritt').textContent.includes('Befund ' + n + ' von')", arg=i + 2)
    pg.wait_for_selector("#start-p2")
    check("Übergang: «Teil 1 ist abgeschlossen», erklärt Teil 2, Knopf «Weiter zu Teil 2», kein Zurück-Knopf",
          "Teil 1 ist abgeschlossen" in pg.inner_text("main") and "Teil 2" in pg.inner_text("main") and pg.locator("main button").count() == 1)
    for _ in range(3):
        pg.go_back(); pg.wait_for_timeout(120)
    check("Übergang: Browser-Zurück (3 Mal) bleibt auf dem Übergang und zeigt den Hinweis", pg.is_visible("#start-p2") and pg.is_visible("#hinweis") and pg.locator("#form-p1").count() == 0)
    pg.click("#start-p2")
    pg.wait_for_selector("#form-p2")

    # 4.5 Teil 2: Inhalte, Sperre, Skala
    t2 = pg.inner_text("main")
    z = C.zustand(pg)
    check("Teil 2: Aussage, eigene Stichworte, Erklärung und Frage «Wie plausibel wirkt diese Erklärung jetzt auf dich?», Skalenenden «1 = gar nicht plausibel» und «5 = sehr plausibel»",
          "Deine Stichworte: Entwurf bleibt" in t2 and "Wie plausibel wirkt diese Erklärung jetzt auf dich?" in t2
          and "1 = gar nicht plausibel" in t2 and "5 = sehr plausibel" in t2 and "Teil 2 von 2: Erklärungen einordnen" in t2 and "Befund 1 von 5" in t2)
    check("Teil 2: «Weiter» ist ohne Auswahl gesperrt, keine Option vorgewählt",
          pg.is_disabled("#weiter-p2") and pg.evaluate("document.querySelectorAll('input[name=wert]:checked').length") == 0)
    pg.keyboard.press("Enter")
    check("Enter ohne Auswahl springt nicht weiter", pg.is_visible("#form-p2") and C.zustand(pg)["antworten"][0]["wert"] is None)
    pg.evaluate("document.getElementById('weiter-p2').click()")
    check("Klick auf gesperrtes «Weiter» springt nicht weiter", pg.is_visible("#form-p2"))
    pg.evaluate("document.getElementById('form-p2').requestSubmit()")
    check("Formular-Submit ohne Auswahl springt nicht weiter", pg.is_visible("#form-p2") and C.zustand(pg)["antworten"][0]["wert"] is None)
    check("Teil 2: kein Zurück-Knopf, kein Link, nur ein Knopf",
          pg.locator("main a").count() == 0 and not re.search(r"zur(ü|u)ck", t2, re.I) and pg.locator("main button").count() == 1)
    for _ in range(3):
        pg.go_back(); pg.wait_for_timeout(120)
    check("Teil 2: Browser-Zurück (3 Mal) bleibt auf Teil 2 mit Hinweis, Teil 1 nicht erreichbar",
          pg.is_visible("#form-p2") and pg.is_visible("#hinweis") and "Teil 2" in pg.inner_text("#hinweis") and pg.locator("#form-p1").count() == 0)
    pg.reload(); pg.wait_for_selector("#form-p2")
    check("Neuladen in Teil 2: Teil 2 desselben Befunds, Teil 1 nicht erreichbar, Zuteilung unverändert, Stichworte noch da",
          pg.locator("#form-p1").count() == 0 and C.zustand(pg)["schritt"] == "p2" and C.zustand(pg)["zuteilung"] == z["zuteilung"]
          and "Deine Stichworte: Entwurf bleibt" in pg.inner_text("main"))
    # Pfeiltasten
    pg.keyboard.press("Tab")        # vom h2 auf die Skala
    erste = pg.evaluate("document.activeElement.name + ':' + document.activeElement.value")
    pg.keyboard.press("ArrowRight"); pg.keyboard.press("ArrowRight")
    gew = pg.evaluate("document.querySelector('input[name=wert]:checked').value")
    check("Skala per Tab/Pfeiltasten: Fokus startet bei «%s», nach 2x Pfeil rechts ist 3 gewählt, Weiter freigegeben" % erste,
          gew == "3" and not pg.is_disabled("#weiter-p2"))
    pg.keyboard.press("Tab")
    pg.keyboard.press("Space")
    pg.wait_for_function("document.querySelector('.fortschritt').textContent.includes('Befund 2 von')")
    check("Weiter per Tab + Leertaste", C.zustand(pg)["antworten"][0]["wert"] == 3 and C.zustand(pg)["idx"] == 1)
    # Ziffern 1 bis 5
    ok_ziffern = True
    for ziffer in "52":
        pg.keyboard.press(ziffer)
        ok_ziffern = ok_ziffern and pg.evaluate("document.querySelector('input[name=wert]:checked').value") == ziffer \
            and pg.evaluate("document.activeElement.value") == ziffer
    check("Ziffern 5 und 2 wählen die Bewertung und setzen den Fokus", ok_ziffern)
    pg.keyboard.press("Enter")
    pg.wait_for_function("document.querySelector('.fortschritt').textContent.includes('Befund 3 von')")
    check("Enter nach Ziffer schickt ab (Wert 2 gespeichert, weiter bei Befund 3)", C.zustand(pg)["antworten"][1]["wert"] == 2 and C.zustand(pg)["idx"] == 2)
    # Leer gelassene Stichworte werden in Teil 2 als «(leer gelassen)» gezeigt: Befund 2 war leer, Befund 3 «Gewohnheit»
    check("Teil 2 zeigt eigene Stichworte von Befund 3 («Gewohnheit»)", "Deine Stichworte: Gewohnheit" in pg.inner_text("#eigene-stichworte"))
    for w in "134":
        pg.keyboard.press(w); pg.keyboard.press("Enter")
        pg.wait_for_timeout(60)
    pg.wait_for_selector("#berichte")
    t_end = pg.inner_text("main")
    check("Befund 2 mit leerem Feld erscheint in der Zusammenfassung als «(leer gelassen)»", "(leer gelassen)" in t_end)
    check("Kein Knopf «Vorzeitig beenden» im ganzen Ablauf (gestrichen)", "Vorzeitig" not in t_end and "Vorzeitig" not in t1 and "Vorzeitig" not in t2 and "Vorzeitig" not in start_text)
    code_ende = pg.inner_text("#code").strip()
    check("Code ist gültig (v2, 5 Befunde, alle bewertet)", C.py_decode(code_ende) is not None and C.py_decode(code_ende).count(None) == 0 and code_ende.startswith("HSLU-hindsight-v2."), code_ende)

    # 4.6 Neuladen am Ende, Zurück am Ende, Kopieren
    pg.reload(); pg.wait_for_selector("#berichte")
    check("Neuladen am Ende zeigt dieselbe Zusammenfassung und denselben Code", pg.inner_text("#code").strip() == code_ende)
    check("Nach dem Neuladen ist die Auflösung wieder verborgen", not pg.is_visible("#aufloesung") and pg.locator("#aufl-liste").count() == 0)
    pg.click("#kopieren")
    pg.wait_for_function("document.getElementById('kopiert').textContent.length > 0")
    zwischen = pg.evaluate("navigator.clipboard.readText()")
    check("«Code kopieren» legt den Code in die Zwischenablage (http)", zwischen == code_ende and "kopiert" in pg.inner_text("#kopiert"), pg.inner_text("#kopiert"))
    pg.go_back(); pg.wait_for_timeout(150)
    check("Am Ende: Browser-Zurück löst keine Sperre mehr aus (kein Hinweis, Seite bleibt vorerst)", pg.locator("#hinweis").count() == 0 and pg.is_visible("#berichte"))
    check("«Gruppe auswerten» steht nur auf der Zusammenfassung", pg.is_visible("#zur-gruppe"))
    check("Randfälle Ablauf: keine Konsolenfehler", not wacht.fehler, "; ".join(wacht.fehler))
    ctx.close()

    # 4.7 ?neu=1 und Seed wechseln, alter Speicherstand (v1) wird ignoriert
    ctx = neuer_kontext(b, "desktop")
    pg = ctx.new_page()
    pg.goto(url + "?seed=aaa"); pg.click("#start")
    za = C.zustand(pg)["zuteilung"]
    pg.goto(url + "?seed=aaa")
    check("Gleicher Seed in gleichem Tab: Fortschritt wird wiederhergestellt, gleiche Zuteilung", C.zustand(pg) is not None and C.zustand(pg)["zuteilung"] == za)
    pg.goto(url + "?seed=bbb")
    check("Anderer Seed im selben Tab beginnt neu (Startseite)", pg.is_visible("#start") and C.zustand(pg) is None)
    pg.click("#start"); pg.goto(url + "?seed=bbb&neu=1")
    check("?neu=1 beginnt neu (Startseite)", pg.is_visible("#start"))
    pg.evaluate("""() => { const alt = JSON.stringify({ v: 1, seed: null, zuteilung: ['A','B','A','B','A','B','A','B','A'],
        antworten: Array.from({length: 9}, () => ({ text: 'alt', wert: 3 })), schritt: 'bewertung', idx: 4, kennung: 'abc' });
        sessionStorage.setItem('hsluP3Zustand', alt); sessionStorage.setItem('hsluP3ZustandV2', alt); }""")
    pg.goto(url)
    check("Alter Speicherstand der früheren Seitenversion (v1) wird ignoriert (Startseite)", pg.is_visible("#start") and C.zustand(pg) is None)
    ctx.close()

    # 4.8 Ohne Speicher (sessionStorage nicht nutzbar)
    ctx = neuer_kontext(b, "desktop")
    ctx.add_init_script("Object.defineProperty(window, 'sessionStorage', { get() { throw new Error('gesperrt'); } });")
    pg = ctx.new_page()
    wacht = C.Fehlerwaechter(pg)
    pg.goto(url + "?seed=ohne")
    werte = [random.randint(1, 5) for _ in range(N)]
    code = C.durchlauf(pg, TEXTE, werte, quelle=QUELLE)
    z = C.zustand(pg)
    check("Ohne sessionStorage: vollständiger Durchlauf funktioniert, Code gültig", decode_ok(code, z["zuteilung"], werte))
    pg2 = ctx.new_page()
    pg2.goto(url + "?seed=ohne"); pg2.click("#start")
    pg2.fill("#stichworte", "a"); pg2.press("#stichworte", "Enter"); pg2.wait_for_selector("#zurueck-p1")
    pg2.reload()
    check("Ohne sessionStorage startet Neuladen den Ablauf neu (dokumentiertes Verhalten)", pg2.is_visible("#start"))
    check("Ohne sessionStorage: keine Konsolenfehler/pageerror", not wacht.fehler, "; ".join(wacht.fehler))
    ctx.close()

    # 4.9 Zurück und Neuladen über file://
    ctx = neuer_kontext(b, "desktop")
    pg = ctx.new_page()
    pg.goto(furl + "?seed=fileback"); pg.click("#start")
    for i in range(N):
        pg.fill("#stichworte", "f"); pg.press("#stichworte", "Enter")
    pg.wait_for_selector("#start-p2"); pg.click("#start-p2"); pg.wait_for_selector("#form-p2")
    za = C.zustand(pg)["zuteilung"]
    pg.go_back(); pg.wait_for_timeout(150)
    ok_back = pg.is_visible("#form-p2") and pg.is_visible("#hinweis")
    pg.reload(); pg.wait_for_selector("#form-p2")
    check("file://: Browser-Zurück bleibt in Teil 2 (Hinweis), Neuladen stellt Teil 2 mit gleicher Zuteilung wieder her",
          ok_back and pg.locator("#form-p1").count() == 0 and C.zustand(pg)["zuteilung"] == za)
    ctx.close()

    # 4.10 befunde.js fehlt
    ctx = neuer_kontext(b, "desktop")
    pg = ctx.new_page()
    seitenfehler = []
    pg.on("pageerror", lambda e: seitenfehler.append(str(e)))
    pg.route("**/befunde.js", lambda r: r.abort())
    pg.goto(url)
    check("Fehlende befunde.js: verständliche Meldung statt leerer Seite, kein JS-Fehler",
          pg.is_visible("#fehler") and "befunde.js" in pg.inner_text("#fehler") and not seitenfehler, "; ".join(seitenfehler))
    ctx.close()

    # 4.11 Sicherheit: Eingaben werden nie als HTML gedeutet
    ctx = neuer_kontext(b, "handy")
    pg = ctx.new_page()
    pg.goto(url + "?seed=xss")
    pg.tap("#start")
    pg.fill("#stichworte", "<img src=x onerror=alert(1)><b>fett</b>")
    pg.press("#stichworte", "Enter")
    for i in range(1, N):
        pg.fill("#stichworte", ""); pg.press("#stichworte", "Enter")
    pg.tap("#start-p2")
    stich_teil2 = pg.inner_text("#eigene-stichworte")
    check("HTML in den Stichworten erscheint in Teil 2 als Text, es entsteht kein Element",
          pg.locator("#eigene-stichworte img, #eigene-stichworte b").count() == 0 and "<img src=x" in stich_teil2)
    for i in range(N):
        pg.keyboard.press("3"); pg.keyboard.press("Enter")
    pg.wait_for_selector("#berichte")
    check("HTML in den Stichworten erscheint in der Zusammenfassung als Text, es entsteht kein Element",
          pg.locator("#berichte img, #berichte b").count() == 0 and "<img src=x" in pg.inner_text("#berichte"))
    pg.tap("#zur-gruppe")
    gruppe_ausfuellen(pg, "<img src=x onerror=alert(1)>\n   \nHSLU-hindsight-v2.")
    check("HTML in ungültigen Zeilen erscheint als Text, es entsteht kein Element",
          pg.locator("#gruppe-ungueltig img").count() == 0 and "<img src=x" in pg.inner_text("#gruppe-ungueltig"))
    ctx.close()

    # =====================================================================================
    # 5. Code-Rundreise und Gruppenansicht
    # =====================================================================================
    # 5.1 Rundreise: Person -> Code -> Gruppenansicht zeigt genau diese Daten
    ctx = neuer_kontext(b, "desktop")
    pg = ctx.new_page()
    pg.goto(url + "?seed=rundreise")
    werte = [4, 2, 5, 1, 3]
    code = C.durchlauf(pg, TEXTE, werte, quelle=QUELLE)
    z = C.zustand(pg)
    pg.click("#zur-gruppe")
    check("Gruppenansicht vor der Eingabe: kein Wort «Version» im Text (ausser Platzhalter), kein «echt/tatsächlich/gegenteil»",
          not re.search(r"Version|echt|tatsächlich|gegenteil", pg.inner_text("main")))
    check("Gruppenansicht vor der Eingabe: keine Tabelle, Ergebnisfeld verborgen", pg.locator("#gruppe-tabelle").count() == 0 and not pg.is_visible("#gruppe-karte"))
    gruppe_ausfuellen(pg, code)
    tab = tabelle_lesen(pg)
    py = C.py_gruppe([code])
    ok = True
    for i in range(N):
        for k, v in enumerate("AB"):
            erw_mw = C.fmt2(py["pro"][i][v]); erw_n = "n = %d" % len(py["pro"][i][v])
            if tab[i][k] != [erw_mw, erw_n]:
                ok = False
        k = 0 if z["zuteilung"][i] == "A" else 1
        if tab[i][k] != ["%.2f" % werte[i], "n = 1"] or tab[i][1 - k] != ["–", "n = 0"]:
            ok = False
    check("Code-Rundreise: eigene Daten erscheinen unverändert in «Gruppe auswerten» (5 Befunde, richtige Version, gleiche Bewertung)", ok, str(tab[:2]))
    kopf_text = pg.inner_text("#gruppe-tabelle thead")
    check("Ohne Klick nennt die Auswertung nur neutral «Version A» und «Version B» (Kopfzeile: %s), mit «Alle Befunde»-Zeile" % kopf_text.replace("\n", " | "),
          pg.inner_text("#kopf-a") == "Version A" and pg.inner_text("#kopf-b") == "Version B" and "Alle Befunde" in pg.inner_text("#gruppe-tabelle"))
    check("Ohne Klick: keine Angabe, welche Version echt ist (kein «echt», «tatsächlich», «gegenteilig», «falsch»)",
          not re.search(r"\b(echt|falsch|tatsächlich|gegenteilig)\w*", pg.inner_text("main"), re.I) and pg.locator("#gruppe-zuordnung").count() == 0
          and pg.locator("#aufl-liste-gruppe").count() == 0 and not pg.is_visible("#gruppe-aufloesung"))
    vor = pg.evaluate("document.getElementById('main').textContent")
    check("Ohne Klick steht nichts von der Auflösung im DOM der Gruppenansicht (keine Quelle, kein Vorbehalt, kein «echt»)",
          "Quelle:" not in vor and "Vorbehalt" not in vor and "(echt)" not in vor)
    pg.click("#gruppe-aufloesung-zeigen")
    pg.wait_for_selector("#gruppe-zuordnung")
    tab2 = tabelle_lesen(pg)
    li_text = [C.norm(pg.locator("#aufl-liste-gruppe > li").nth(i).inner_text()) for i in range(pg.locator("#aufl-liste-gruppe > li").count())]
    check("Nach Klick auf «Auflösung anzeigen»: Köpfe «Version A (echt)» und «Version B (gegenteilig)», Zuordnung genannt",
          pg.inner_text("#kopf-a") == "Version A (echt)" and pg.inner_text("#kopf-b") == "Version B (gegenteilig)"
          and "Version A ist die tatsächliche Aussage (echt), Version B die gegenteilige." in pg.inner_text("#gruppe-zuordnung"))
    check("Nach Klick: Zahlen der Tabelle unverändert, 5 Einträge mit der tatsächlichen Aussage (A) und Quelle, ohne «Deine Version»",
          tab2 == tab and len(li_text) == 5
          and all(C.norm(C.ohne_stern(QUELLE[i]["A"]["studie"])) in li_text[i] and "Deine Version" not in li_text[i] for i in range(N)))
    check("Knopf wechselt zu «Auflösung verbergen» und blendet die Auflösung wieder aus",
          pg.inner_text("#gruppe-aufloesung-zeigen") == "Auflösung verbergen")
    pg.click("#gruppe-aufloesung-zeigen")
    check("Verbergen: Köpfe wieder neutral, Auflösungsliste weg", pg.inner_text("#kopf-a") == "Version A" and pg.locator("#aufl-liste-gruppe").count() == 0)
    pg.click("#leeren")
    check("«Leeren» setzt die Ansicht zurück", pg.input_value("#codes") == "" and pg.locator("#gruppe-tabelle").count() == 0)
    pg.click("#zurueck-ablauf")
    check("«Zurück zu meinen Berichten» führt zur Zusammenfassung", pg.is_visible("#berichte") and pg.inner_text("#code").strip() == code)
    ctx.close()

    # 5.2 Gruppe aus 5 Personen (4 per UI, 1 unvollständig) + ungültiger Code + Duplikat + v1-Code + Leerzeilen
    personen = []
    zv = [[4, 2, 5, 1, 3], [3, 3, 4, 2, 2], [5, 1, 2, 4, 4], [2, 4, 3, 3, 5]]
    for k, werte in enumerate(zv):
        code, z = person(b, url, "gruppe%d" % k, werte, art="desktop" if k % 2 == 0 else "handy", modus="klick" if k % 2 == 0 else "tap")
        personen.append((code, z, werte))
    # Die Seite erzeugt nur vollständige Codes. Die unvollständige Person kommt über den Testhaken (Code mit «x»).
    ctx = neuer_kontext(b, "desktop")
    pg = ctx.new_page()
    pg.goto(url)
    zu5 = ["A", "B", "B", "A", "B"]
    w5 = [1, 5, 4, None, None]
    code5 = pg.evaluate("([z, w]) => P3.codeErzeugen(z, w, 'q9m')", [zu5, w5])
    ctx.close()
    personen.append((code5, {"zuteilung": zu5}, w5))
    codes = [c for c, _, _ in personen]
    check("5 Personen: 4 per UI erzeugt (2 Desktop/Maus, 2 Handy/Touch), 1 unvollständig (3 von 5)",
          [c.split(".")[1][:5].count("x") for c in codes] == [0, 0, 0, 0, 2], " | ".join(codes))
    for c, z, w in personen:
        if not decode_ok(c, z["zuteilung"], w):
            check("Code stimmt mit Zustand überein", False, c)
    falsch_pz = "0" if C.py_pruef("00000xxx") != "0" else "1"
    schlecht = "HSLU-hindsight-v2.00000xxx" + falsch_pz        # richtige Länge, falsches Prüfzeichen
    eingabe = "\n".join([codes[0], "", codes[1], "   ", schlecht, ALT_V1, codes[2],
                         codes[1].upper().replace("HSLU-HINDSIGHT-V2", "HSLU-hindsight-v2"), codes[3], "", codes[4], ""])
    ctx = neuer_kontext(b, "desktop")
    pg = ctx.new_page()
    wacht = C.Fehlerwaechter(pg)
    pg.goto(url + "?gruppe=1")
    check("?gruppe=1 öffnet direkt «Gruppe auswerten»", pg.is_visible("#codes") and pg.is_visible("#zurueck-start"))
    gruppe_ausfuellen(pg, eingabe)
    chips = pg.inner_text("#gruppe-chips").replace("\n", " | ")
    check("Chips: 5 Personen, 1 Duplikat, 2 ungültige Zeilen (inkl. v1), 1 unvollständig (Anzeige: %s)" % chips,
          pg.inner_text("#chip-personen") == "5 Personen ausgewertet" and pg.inner_text("#chip-duplikate") == "1 Duplikat ignoriert"
          and pg.inner_text("#chip-ungueltig") == "2 ungültige Zeilen" and pg.inner_text("#chip-unvollstaendig") == "1 Person unvollständig")
    u = pg.inner_text("#gruppe-ungueltig")
    check("Ungültige Zeile wird mit Zeilennummer, Text und Grund benannt: «%s»" % u.replace("\n", " "),
          "Zeile 5" in u and schlecht in u and "Prüfzeichen" in u)
    check("Alter v1-Code wird klar zurückgewiesen (eigener Hinweis, Zeile 6, Grund «frühere Seitenversion»)",
          pg.is_visible("#gruppe-v1") and "1 Code der früheren Seitenversion (v1) nicht ausgewertet" in pg.inner_text("#gruppe-v1")
          and "Zeile 6" in u and "frühere" in u and "v1" in u)
    uv = pg.inner_text("#gruppe-unvollstaendig")
    check("Unvollständige Person wird benannt: «%s»" % uv.replace("\n", " "), "3 von 5" in uv)
    tab = tabelle_lesen(pg)
    py = C.py_gruppe(eingabe.split("\n"))
    ok = True; abw = []
    for i in range(N):
        for k, v in enumerate("AB"):
            erw = [C.fmt2(py["pro"][i][v]), "n = %d" % len(py["pro"][i][v])]
            if tab[i][k] != erw:
                ok = False; abw.append((i + 1, v, tab[i][k], erw))
    tot = tab[N]
    for k, v in enumerate("AB"):
        erw = [C.fmt2(py["gesamt"][v]), "n = %d" % len(py["gesamt"][v])]
        if tot[k] != erw:
            ok = False; abw.append(("gesamt", v, tot[k], erw))
    check("Gruppentabelle (5 Befunde x A/B + Gesamt): Mittelwert und n stimmen mit unabhängiger Python-Rechnung überein", ok, str(abw[:3]))
    ns = [int(tab[i][0][1][4:]) + int(tab[i][1][1][4:]) for i in range(N)]
    check("Pro Befund ist n(A) + n(B) = Zahl der Personen, die den Befund bewertet haben (5,5,5,4,4)", ns == [5, 5, 5, 4, 4], str(ns))
    check("Gesamt: n(A) + n(B) = 23 Bewertungen", int(tot[0][1][4:]) + int(tot[1][1][4:]) == 23)
    # Gesamtmittel A und B von Hand aus den Personen
    sa, na_, sb, nb = 0, 0, 0, 0
    for c, z, w in personen:
        for i in range(N):
            if w[i] is None:
                continue
            if z["zuteilung"][i] == "A":
                sa += w[i]; na_ += 1
            else:
                sb += w[i]; nb += 1
    check("Gesamtmittel A (%.2f, n=%d) und B (%.2f, n=%d) aus den Rohwerten der Personen nachgerechnet" % (sa / na_, na_, sb / nb, nb),
          tot[0][0] == C.fmt2([w for r in py["pro"] for w in r["A"]]) and tot[1][0] == C.fmt2([w for r in py["pro"] for w in r["B"]])
          and abs(float(tot[0][0]) - sa / na_) < 0.006 and abs(float(tot[1][0]) - sb / nb) < 0.006 and (na_, nb) == (int(tot[0][1][4:]), int(tot[1][1][4:])))
    check("Ohne Klick auf «Auflösung anzeigen» bleibt die Auswertung neutral («Version A / Version B»)",
          pg.inner_text("#kopf-a") == "Version A" and pg.inner_text("#kopf-b") == "Version B")
    check("Gruppenansicht: keine Konsolenfehler", not wacht.fehler, "; ".join(wacht.fehler))

    # 5.3 nur ungültige Codes, nur Leerzeilen, nur Duplikate, nur alte Codes
    gruppe_ausfuellen(pg, "foo\nbar\n\nHSLU-hindsight-v2.xxxxxxxxx")
    check("Nur ungültige Zeilen: «Keine gültigen Codes.», 3 ungültige genannt",
          "Keine gültigen Codes" in pg.inner_text("#gruppe-leer") and pg.inner_text("#chip-ungueltig") == "3 ungültige Zeilen"
          and pg.locator("#gruppe-tabelle").count() == 0)
    gruppe_ausfuellen(pg, ALT_V1 + "\n" + ALT_V1.replace("kg07", "aa07"))
    check("Nur alte v1-Codes: «Keine gültigen Codes.», Hinweis «2 Codes der früheren Seitenversion (v1) nicht ausgewertet»",
          "Keine gültigen Codes" in pg.inner_text("#gruppe-leer") and "2 Codes der früheren Seitenversion (v1) nicht ausgewertet" in pg.inner_text("#gruppe-v1"))
    gruppe_ausfuellen(pg, "\n \n\t\n")
    check("Nur Leerzeilen: keine Fehler, «Noch keine Codes eingefügt.»", "Noch keine Codes" in pg.inner_text("#gruppe-leer") and pg.locator("#gruppe-ungueltig").count() == 0)
    gruppe_ausfuellen(pg, "\n".join([codes[0]] * 4))
    check("Derselbe Code 4 Mal: 1 Person, 3 Duplikate", pg.inner_text("#chip-personen") == "1 Person ausgewertet" and pg.inner_text("#chip-duplikate") == "3 Duplikate ignoriert")
    pg.click("#zurueck-start")
    check("«Zurück zum Start» führt zur Startseite", pg.is_visible("#start"))
    ctx.close()

    # 5.4 Kopieren über file:// (Rückfall)
    ctx = neuer_kontext(b, "desktop")
    pg = ctx.new_page()
    pg.goto(furl + "?seed=filecopy")
    code = C.durchlauf(pg, TEXTE, [3] * N, quelle=QUELLE)
    pg.click("#kopieren")
    pg.wait_for_function("document.getElementById('kopiert').textContent.length > 0")
    check("«Code kopieren» über file://: Meldung erscheint (%s)" % pg.inner_text("#kopiert"), len(pg.inner_text("#kopiert")) > 5)
    ctx.close()

    b.close()

httpd.shutdown()
fehler = [e for e in ergebnisse if not e[1]]
print("\n%d Prüfungen, %d bestanden, %d fehlgeschlagen" % (len(ergebnisse), len(ergebnisse) - len(fehler), len(fehler)))
for f in fehler:
    print("  FEHLER:", f[0], "|", f[2])
sys.exit(1 if fehler else 0)
