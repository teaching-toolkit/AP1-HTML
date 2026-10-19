"""Gemeinsame Hilfen für die Tests von P3 (wird per importlib geladen, weil python3 -I
das Skriptverzeichnis nicht in sys.path legt).

Enthält:
- lokalen Testserver (Wurzel = Ordner html-projekte, damit ../shared/base.css gilt)
- unabhängige Python-Referenz für Ergebnis-Code und Gruppenstatistik
- unabhängigen Parser für die Befunde im Auftrag (anderes Verfahren als extract_befunde.py)
- Ablauf-Helfer für Playwright (Klick, Touch, Tastatur)
"""
import sys
sys.dont_write_bytecode = True
import functools
import http.server
import re
import threading
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

PROJ = Path(__file__).resolve().parents[1]
ROOT = PROJ.parent
QUELLE = ROOT / "quellen" / "dokumente" / "10_einfuehrung2.md"
SHOTS = PROJ / "screenshots"
N = 5
# Unabhängige Erwartung: welche Befunde des Auftrags (Nummern im Auftrag) in welcher Reihenfolge auf der Seite stehen.
AUSWAHL = [5, 3, 7, 9, 4]
VERWORFEN = [1, 2, 6, 8]


# ---------------------------------------------------------------- Server
class _Leise(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a):
        pass


def start_server():
    handler = functools.partial(_Leise, directory=str(ROOT))
    httpd = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler)
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    return httpd, "http://127.0.0.1:%d/p3-hindsight/index.html" % httpd.server_address[1]


def file_url():
    return (PROJ / "index.html").as_uri()


# ---------------------------------------------------------------- Ergebnis-Code (Referenz, Format v2)
ALPHA = "0123456789abcdefghijklmnopqrstuvwxyz"
GEW = [1, 5, 7, 11, 13, 17, 19, 23]
KENNUNG = "HSLU-hindsight-v2"


def py_pruef(p8):
    return ALPHA[sum(g * ALPHA.index(c) for g, c in zip(GEW, p8)) % 36]


def py_encode(zu, werte, nonce):
    d = ""
    for v, w in zip(zu, werte):
        d += "x" if w is None else str((0 if v == "A" else 5) + w - 1)
    p = d + nonce
    return KENNUNG + "." + p + py_pruef(p)


def py_decode(code):
    """Liefert Liste (version, wert) oder None je Befund, oder None bei ungültigem Code."""
    m = re.fullmatch(r"HSLU-hindsight-v2\.([0-9a-z]{9})", code.strip(), re.I)
    if not m:
        return None
    p = m.group(1).lower()
    if not re.fullmatch(r"[0-9x]{5}[0-9a-z]{4}", p) or py_pruef(p[:8]) != p[8]:
        return None
    out = []
    for c in p[:5]:
        if c == "x":
            out.append(None)
        else:
            d = int(c)
            out.append(("A", d + 1) if d < 5 else ("B", d - 4))
    return out


def py_gruppe(codes):
    """Unabhängige Gruppenstatistik: Duplikate (gleicher Code) ignorieren, ungültige zählen."""
    gesehen, personen, ungueltig, dup, alte = set(), [], 0, 0, 0
    for c in codes:
        if not c.strip():
            continue
        dec = py_decode(c)
        if dec is None:
            ungueltig += 1
            if re.match(r"HSLU-hindsight-v1\.", c.strip(), re.I):
                alte += 1
            continue
        k = c.strip().lower()
        if k in gesehen:
            dup += 1
            continue
        gesehen.add(k)
        personen.append(dec)
    pro = [{"A": [], "B": []} for _ in range(N)]
    for p in personen:
        for i, e in enumerate(p):
            if e:
                pro[i][e[0]].append(e[1])
    gesamt = {"A": [w for r in pro for w in r["A"]], "B": [w for r in pro for w in r["B"]]}
    return {"personen": len(personen), "ungueltig": ungueltig, "duplikate": dup, "alte": alte,
            "unvollstaendig": sum(1 for p in personen if any(e is None for e in p)),
            "pro": pro, "gesamt": gesamt}


def fmt2(werte):
    """Anzeige wie auf der Seite: Mittel mit 2 Nachkommastellen (kaufmännisch), '–' ohne Werte."""
    if not werte:
        return "–"
    m = Decimal(sum(werte)) / Decimal(len(werte))
    return str(m.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))


# ---------------------------------------------------------------- Befunde aus dem Auftrag (unabhängiger Parser)
def quelle_befunde():
    text = QUELLE.read_text(encoding="utf-8")
    sec = text.split("## Aktivität 1: Hindsight Bias", 1)[1].split("**Durchführung:**", 1)[0]
    teile = re.split(r"\*\*Forschungsbefund (\d+): (.+?)\*\*", sec)
    # teile = [vorspann, nr, titel, rest, nr, titel, rest, ...]
    res = []
    for k in range(1, len(teile), 3):
        nr, titel, rest = int(teile[k]), teile[k + 1], teile[k + 2]
        studien = re.findall(r"\*\*Studie:\*\*\s*(.+)", rest)
        erkl = re.findall(r"\*\*Erklärung:\*\*\s*(.+)", rest)
        assert len(studien) == 2 and len(erkl) == 2, "Befund %d: unerwartete Struktur" % nr
        un = lambda s: s.strip().replace("\\$", "$")
        res.append({"nr": nr, "titel": un(titel),
                    "A": {"studie": un(studien[0]), "erklaerung": un(erkl[0])},
                    "B": {"studie": un(studien[1]), "erklaerung": un(erkl[1])}})
    return res


def auswahl_befunde():
    """Die fünf Befunde der Seite in Seitenreihenfolge (Seite: nr 1..5), Texte aus dem Auftrag."""
    alle = {b["nr"]: b for b in quelle_befunde()}
    res = []
    for neu, alt in enumerate(AUSWAHL, start=1):
        b = dict(alle[alt])
        b["auftrag_nr"] = alt
        b["nr"] = neu
        res.append(b)
    return res


def ohne_stern(s):
    return re.sub(r"\*([^*]+)\*", r"\1", s)


def norm(s):
    return re.sub(r"\s+", " ", s).strip()


# ---------------------------------------------------------------- Playwright-Hilfen
VERBOTEN = re.compile(r"\b(version|versionen|variante|varianten|fassung|fassungen|echt|echte|falsch|falsche|"
                      r"gegenteil|gegenteilig|gegensatz|gegensätze|unterschiedlich\w*|zwei\s+arten)\b", re.I)


class Fehlerwaechter:
    """Sammelt Konsolenfehler, pageerror und fehlgeschlagene/externe Anfragen."""

    def __init__(self, page, erlaubt=("http://127.0.0.1", "file://", "data:", "about:", "blob:")):
        self.fehler = []
        self.anfragen = []
        page.on("console", lambda m: self.fehler.append("console: " + m.text) if m.type == "error" else None)
        page.on("pageerror", lambda e: self.fehler.append("pageerror: " + str(e)))
        page.on("requestfailed", lambda r: self.fehler.append("FAILED " + r.url))

        def anfrage(r):
            self.anfragen.append(r.url)
            if not r.url.startswith(erlaubt):
                self.fehler.append("EXTERN " + r.url)
        page.on("request", anfrage)


def zustand(page):
    return page.evaluate("P3.zustand()")


def klick(page, sel, modus):
    if modus == "tap":
        page.tap(sel)
    else:
        page.click(sel)


def sichtbarer_text(page):
    return page.inner_text("body")


def schritt_p1(page, i, text, modus, quelle, texte_log):
    """Teil 1, Befund i (0-basiert): prüft die Aussage, trägt Stichworte ein, geht weiter."""
    z = zustand(page)
    v = z["zuteilung"][i]
    erwartet = norm(ohne_stern(quelle[i][v]["studie"]))
    assert page.is_visible("#stichworte"), "Befund %d: Teil 1 nicht sichtbar" % (i + 1)
    angezeigt = norm(page.inner_text(".karte-befund .text-gross"))
    assert angezeigt == erwartet, "Befund %d Studienaussage weicht ab:\n%r\n%r" % (i + 1, angezeigt, erwartet)
    assert norm(page.inner_text("h2.befund-titel")) == "Befund %d: %s" % (i + 1, quelle[i]["titel"])
    assert page.locator(".karte-befund .text-gross").count() == 1, "Teil 1 zeigt eine Erklärung"
    texte_log.append(sichtbarer_text(page))
    if modus == "tastatur":
        page.keyboard.press("Tab")
        assert page.evaluate("document.activeElement.id") == "stichworte", "Tab erreicht das Feld nicht"
        if text:
            page.keyboard.type(text)
        page.keyboard.press("Enter")
    else:
        if text:
            page.fill("#stichworte", text)
        klick(page, "#weiter-p1", modus)


def uebergang(page, modus, texte_log):
    page.wait_for_selector("#start-p2")
    texte_log.append(sichtbarer_text(page))
    if modus == "tastatur":
        page.keyboard.press("Tab")
        assert page.evaluate("document.activeElement.id") == "start-p2"
        page.keyboard.press("Enter")
    else:
        klick(page, "#start-p2", modus)
    page.wait_for_selector("#form-p2")


def schritt_p2(page, i, wert, modus, quelle, texte_log, stichwort=None):
    """Teil 2, Befund i: prüft Aussage, Stichworte, Erklärung; bewertet; geht weiter."""
    z = zustand(page)
    v = z["zuteilung"][i]
    erwartet = norm(quelle[i][v]["erklaerung"])
    angezeigt = norm(page.inner_text("#erklaerung"))
    assert angezeigt == erwartet, "Befund %d Erklärung weicht ab:\n%r\n%r" % (i + 1, angezeigt, erwartet)
    st = norm(page.inner_text(".karte-befund.zweit .text-mittel"))
    assert st == norm(ohne_stern(quelle[i][v]["studie"])), "Befund %d: Studienaussage in Teil 2 weicht ab" % (i + 1)
    if stichwort is not None:
        eig = norm(page.inner_text("#eigene-stichworte"))
        assert eig == "Deine Stichworte: " + (stichwort if stichwort else "(leer gelassen)"), "Stichworte in Teil 2: %r" % eig
    assert norm(page.inner_text("h2.befund-titel")) == "Befund %d: %s" % (i + 1, quelle[i]["titel"])
    assert page.is_disabled("#weiter-p2"), "Weiter nicht gesperrt ohne Auswahl"
    assert page.evaluate("document.querySelectorAll('input[name=wert]:checked').length") == 0
    texte_log.append(sichtbarer_text(page))
    if modus == "tastatur":
        page.keyboard.press(str(wert))
        page.keyboard.press("Enter")
    else:
        klick(page, ".skala-opt:nth-child(%d)" % wert, modus)
        assert not page.is_disabled("#weiter-p2")
        klick(page, "#weiter-p2", modus)


def durchlauf(page, texte, werte, modus="klick", quelle=None, texte_log=None, start=True):
    """Kompletter Ablauf ab Startseite bis zur Zusammenfassung. Gibt den Ergebnis-Code zurück."""
    quelle = quelle or auswahl_befunde()
    texte_log = texte_log if texte_log is not None else []
    if start:
        texte_log.append(sichtbarer_text(page))
        if modus == "tastatur":
            page.keyboard.press("Tab")
            page.keyboard.press("Enter")
        else:
            klick(page, "#start", modus)
        page.wait_for_selector("#form-p1")
    for i in range(N):
        schritt_p1(page, i, texte[i], modus, quelle, texte_log)
        if i < N - 1:
            page.wait_for_selector("#form-p1")
    uebergang(page, modus, texte_log)
    for i in range(N):
        schritt_p2(page, i, werte[i], modus, quelle, texte_log, stichwort=texte[i].strip())
        if i < N - 1:
            page.wait_for_selector("#form-p2")
    page.wait_for_selector("#berichte")
    texte_log.append(sichtbarer_text(page))
    return page.inner_text("#code").strip()


def kein_horizontaler_scroll(page):
    return page.evaluate("document.documentElement.scrollWidth <= document.documentElement.clientWidth + 0")


def zu_kleine_ziele(page, minimum=44):
    """Sichtbare Bedienelemente mit Fläche unter minimum x minimum (Breite oder Höhe)."""
    return page.evaluate("""(min) => {
      const sel = 'button, input[type=text], input[type=radio], textarea, summary, label.skala-opt, a[href]';
      const out = [];
      document.querySelectorAll(sel).forEach(e => {
        let r = e.getBoundingClientRect();
        if (e.type === 'radio') r = e.parentElement.getBoundingClientRect();
        const cs = getComputedStyle(e);
        if (cs.visibility === 'hidden' || cs.display === 'none') return;
        if (e.closest('[hidden]')) return;
        if (r.width === 0 || r.height === 0) return;
        if (r.width < min - 0.5 || r.height < min - 0.5) out.push((e.id || e.className || e.tagName) + ' ' + Math.round(r.width) + 'x' + Math.round(r.height));
      });
      return out;
    }""", minimum)


def inhalt_ueberlauf(page):
    """Elemente, deren Inhalt breiter ist als ihr Kasten (Text läuft in den Nachbarn oder aus dem Kasten)."""
    return page.evaluate("""() => {
      const out = [];
      document.querySelectorAll('main *, #fuss *').forEach(e => {
        if (['INPUT', 'TEXTAREA', 'SCRIPT', 'STYLE', 'OPTION'].includes(e.tagName)) return;
        const cs = getComputedStyle(e);
        if (cs.display === 'inline' || cs.display === 'none' || cs.visibility === 'hidden') return;
        if (e.closest('[hidden]') || e.closest('.sr-only')) return;
        if (e.scrollWidth > e.clientWidth + 1 && e.clientWidth > 0) {
          out.push(e.tagName.toLowerCase() + (e.id ? '#' + e.id : '') + '.' + (e.className || '') + ' [' + (e.textContent || '').trim().slice(0, 30) + '] ' + e.scrollWidth + '>' + e.clientWidth);
        }
      });
      return out;
    }""")


def kontrast_probleme(page, minimum=4.5, gross=3.0):
    """WCAG-Kontrast aller sichtbaren Textknoten (Vordergrund gegen den tatsächlichen Hintergrund,
    inklusive Deckkraft). Deaktivierte Bedienelemente sind ausgenommen. Gibt Verstösse zurück."""
    return page.evaluate("""([min, gross]) => {
      const parse = c => { const m = c.match(/rgba?\\(([^)]+)\\)/); const p = m[1].split(',').map(parseFloat); return { r: p[0], g: p[1], b: p[2], a: p.length > 3 ? p[3] : 1 }; };
      const lin = v => { v /= 255; return v <= 0.03928 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4); };
      const lum = c => 0.2126 * lin(c.r) + 0.7152 * lin(c.g) + 0.0722 * lin(c.b);
      const over = (f, b) => ({ r: f.r * f.a + b.r * (1 - f.a), g: f.g * f.a + b.g * (1 - f.a), b: f.b * f.a + b.b * (1 - f.a), a: 1 });
      const bg = e => { const layers = []; for (let n = e; n; n = n.parentElement) { const c = parse(getComputedStyle(n).backgroundColor); if (c.a > 0) { layers.push(c); if (c.a >= 1) break; } }
        let res = { r: 255, g: 255, b: 255, a: 1 }; while (layers.length) res = over(layers.pop(), res); return res; };
      const opa = e => { let o = 1; for (let n = e; n; n = n.parentElement) o *= parseFloat(getComputedStyle(n).opacity); return o; };
      const out = [];
      const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
      let node;
      while ((node = walker.nextNode())) {
        if (!node.nodeValue.trim()) continue;
        const e = node.parentElement;
        if (!e || ['SCRIPT', 'STYLE', 'NOSCRIPT', 'OPTION'].includes(e.tagName)) continue;
        const cs = getComputedStyle(e);
        if (cs.visibility === 'hidden' || cs.display === 'none') continue;
        if (e.closest('[hidden]') || e.closest('.sr-only')) continue;
        if (e.closest('button:disabled')) continue;
        const r = e.getBoundingClientRect(); if (r.width === 0 || r.height === 0) continue;
        const b = bg(e);
        let f = parse(cs.color); f.a = f.a * opa(e);
        const fg = over(f, b);
        const l1 = lum(fg), l2 = lum(b);
        const ratio = (Math.max(l1, l2) + 0.05) / (Math.min(l1, l2) + 0.05);
        const px = parseFloat(cs.fontSize), fett = parseInt(cs.fontWeight) >= 700;
        const grossText = px >= 24 || (px >= 18.66 && fett);
        if (ratio < (grossText ? gross : min)) out.push(e.tagName.toLowerCase() + '.' + e.className + ' [' + node.nodeValue.trim().slice(0, 25) + '] ' + ratio.toFixed(2));
      }
      return out;
    }""", [minimum, gross])


def rahmenkontrast(page, sel):
    """Kontrast zwischen Rahmenfarbe von sel und dem Hintergrund der Karte (WCAG 1.4.11 verlangt 3:1)."""
    return page.evaluate("""(sel) => {
      const parse = c => { const m = c.match(/rgba?\\(([^)]+)\\)/); return m[1].split(',').slice(0, 3).map(parseFloat); };
      const lin = v => { v /= 255; return v <= 0.03928 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4); };
      const lum = c => 0.2126 * lin(c[0]) + 0.7152 * lin(c[1]) + 0.0722 * lin(c[2]);
      const e = document.querySelector(sel);
      const rand = parse(getComputedStyle(e).borderTopColor);
      const karte = parse(getComputedStyle(e.closest('.card')).backgroundColor);
      const a = lum(rand), b = lum(karte);
      return (Math.max(a, b) + 0.05) / (Math.min(a, b) + 0.05);
    }""", sel)
