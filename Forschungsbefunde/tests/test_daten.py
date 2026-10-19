"""Prüft, dass die Daten der Seite mit dem Auftrag übereinstimmen (wörtlich), dass die Auswahl der
fünf Befunde wie dokumentiert ist, und statische Regeln (neutrale Namen, kein Eszett, keine externen
Verweise, Dateigrössen).

Gleichwertiger Datenabgleich: Die Seite enthält nur noch 5 der 9 Befunde des Auftrags. befunde.js wird
weiterhin maschinell aus dem Auftrag erzeugt (extract_befunde.py, Auswahl AUSWAHL). Dieser Test prüft
unabhängig davon mit einem zweiten Parser (common.py) und mit einer Teilstring-Suche im Roh-Markdown.

Aufruf:  python3 -I tests/test_daten.py
"""
import sys
sys.dont_write_bytecode = True
import hashlib
import importlib.util
import json
import re
import subprocess
from pathlib import Path

spec = importlib.util.spec_from_file_location("common", Path(__file__).with_name("common.py"))
C = importlib.util.module_from_spec(spec)
spec.loader.exec_module(C)

from playwright.sync_api import sync_playwright

PROJ = C.PROJ
ergebnisse = []


def check(name, ok, detail=""):
    ergebnisse.append((name, ok, detail))
    print(("OK    " if ok else "FEHLER"), name, ("- " + detail) if detail else "")


# 1. Erzeugung ist reproduzierbar (zweiter Lauf ergibt dieselbe Datei)
h1 = hashlib.sha256((PROJ / "befunde.js").read_bytes()).hexdigest()
subprocess.run([sys.executable, "-I", str(PROJ / "tests" / "extract_befunde.py")], check=True, capture_output=True)
h2 = hashlib.sha256((PROJ / "befunde.js").read_bytes()).hexdigest()
check("befunde.js wird beim erneuten Erzeugen byte-identisch", h1 == h2)

# 2. Daten per Node laden (reine JS-Engine, unabhängig vom Browser)
node = subprocess.run(
    ["node", "-e",
     "const vm=require('vm'),fs=require('fs');const w={};"
     "vm.runInNewContext(fs.readFileSync(process.argv[1],'utf8'),{window:w});"
     "console.log(JSON.stringify(w.BEFUNDE))", str(PROJ / "befunde.js")],
    capture_output=True, text=True, check=True)
daten = json.loads(node.stdout)

alle_neun = C.quelle_befunde()
auswahl = C.auswahl_befunde()
check("Auftrag enthält 9 Befunde, die Seite 5", len(alle_neun) == 9 and len(daten) == 5, "%d / %d" % (len(alle_neun), len(daten)))
check("Auswahl laut Dokumentation: Befunde %s des Auftrags in dieser Reihenfolge, verworfen %s" % (C.AUSWAHL, C.VERWORFEN),
      sorted(C.AUSWAHL + C.VERWORFEN) == list(range(1, 10)) and len(C.AUSWAHL) == 5)
check("Seitennummern sind 1 bis 5", [b["nr"] for b in daten] == [1, 2, 3, 4, 5])

felder_ok = all(set(b.keys()) == {"nr", "titel", "A", "B", "quelle", "vorbehalt"} for b in daten)
check("Felder je Befund exakt nr, titel, A, B, quelle, vorbehalt", felder_ok)
check("Jeder Befund hat eine Quelle (nicht leer); vorbehalt ist Text (leer erlaubt)",
      all(isinstance(b["quelle"], str) and b["quelle"].strip() and isinstance(b["vorbehalt"], str) for b in daten))
check("Vorbehalt vorhanden bei 4 von 5 Befunden (leer nur bei Befund 4, Spotlight)",
      [bool(b["vorbehalt"]) for b in daten] == [True, True, True, False, True])

roh = C.QUELLE.read_text(encoding="utf-8")


def vergleich(d):
    """Gibt (Abweichungen gegen den zweiten Parser, Texte, die nicht buchstäblich im Auftrag stehen) zurück."""
    abw, fehlt = [], []
    for b, q in zip(d, auswahl):
        if b["titel"] != q["titel"]:
            abw.append("Titel %s" % b["nr"])
        for v in "AB":
            for f in ("studie", "erklaerung"):
                if b[v][f] != q[v][f]:
                    abw.append("Befund %d (Auftrag %d) %s %s" % (b["nr"], q["auftrag_nr"], v, f))
                # dritte Methode: der Text steht (bis auf das Escape \$) buchstäblich im Auftrag
                if b[v][f].replace("$", "\\$") not in roh:
                    fehlt.append("Befund %d %s %s" % (b["nr"], v, f))
    return abw, fehlt


abw, verbatim_fehlt = vergleich(daten)
check("Titel, Studie und Erklärung (A und B) aller 5 Befunde stimmen mit dem Auftrag überein (20 Texte + 5 Titel)",
      not abw, "; ".join(abw))
check("Jeder Text steht buchstäblich im Auftrag (Teilstring-Suche)", not verbatim_fehlt, "; ".join(verbatim_fehlt))

# Mutationstest: absichtlich veränderte Daten müssen auffallen (sonst hätte der Abgleich keine Aussagekraft)
import copy
mut = copy.deepcopy(daten)
mut[2]["B"]["erklaerung"] = mut[2]["B"]["erklaerung"].replace("motiviert", "motivierte")
mut[4]["A"]["studie"] = mut[4]["A"]["studie"].replace("*mehr*", "*weniger*")
mut[0]["titel"] = mut[0]["titel"] + "."
a_m, f_m = vergleich(mut)
check("Negativkontrolle: 3 absichtlich veränderte Texte werden erkannt (%d Abweichungen, %d nicht im Auftrag)" % (len(a_m), len(f_m)),
      len(a_m) == 3 and len(f_m) == 2)

ersetzt = sum(b[v][f].count("$") for b in daten for v in "AB" for f in ("studie", "erklaerung"))
check("Kein Befund mit «$» gewählt, also keine Umformung nötig (Anzahl $ in den Daten: %d)" % ersetzt, ersetzt == 0)

# Version A ist im Auftrag als ECHT gekennzeichnet (Grundlage der Auflösung), B nicht
auftrag_a_echt = all(re.search(r"\*\*Forschungsbefund %d: .+?\*\*\s*\n\s*\n\s*-\s+\*\*Version A \(ECHT\):\*\*" % q["auftrag_nr"], roh) for q in auswahl)
check("Im Auftrag ist bei allen 5 gewählten Befunden Version A als «(ECHT)» gekennzeichnet (A = tatsächliche Aussage)", auftrag_a_echt)

# Die vier verworfenen Befunde stehen nirgends in der öffentlichen Seite
verworfen = [b for b in alle_neun if b["nr"] in C.VERWORFEN]
quelltexte = {"index.html": (PROJ / "index.html").read_text(encoding="utf-8"),
              "befunde.js": (PROJ / "befunde.js").read_text(encoding="utf-8")}
rest = []
for b in verworfen:
    kennwoerter = [b["titel"]] + [b[v][f] for v in "AB" for f in ("studie", "erklaerung")]
    for n, t in quelltexte.items():
        for k in kennwoerter:
            if k.replace("*", "") in t.replace("*", "") or k in t:
                rest.append("%s enthält Text aus Befund %d" % (n, b["nr"]))
for n, t in quelltexte.items():
    for stichwort in ("Schokolade", "75.000", "75'000", "Geräusche", "Auflistungsaufgaben", "Lebensereignisse", "Lebenszufriedenheit"):
        if stichwort in t:
            rest.append("%s enthält «%s»" % (n, stichwort))
check("Die 4 verworfenen Befunde (1, 2, 6, 8 des Auftrags) stehen nicht in index.html und befunde.js", not rest, "; ".join(rest))

# 3. Im Browser geladene Daten = Node-Daten (klassisches Skript, auch über file://)
with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page()
    pg.goto(C.file_url())
    im_browser = pg.evaluate("JSON.parse(JSON.stringify(window.BEFUNDE))")
    check("Im Browser (file://) geladene Daten == Node-Daten", im_browser == daten)
    b.close()

# 4. Neutralität: im Code keine Kennzeichnung echt/falsch ausser in den zwei Auflösungstexten
muster = re.compile(r"\b(echt\w*|falsch\w*|fake\w*|real|genuine|authentic\w*|correct\w*|truth\w*|ground_?truth|original\w*)\b", re.I)
treffer = []
for n, t in quelltexte.items():
    if n == "befunde.js":
        t = re.sub(r'"(?:[^"\\]|\\.)*"', '""', t)          # Befundtexte, Quelle, Vorbehalt ausnehmen
    else:
        # Ausnahme zu Regel 0.2 Punkt 8, vom Dozenten gewollt: die Auflösung steht im Code.
        # Erlaubt sind genau diese zwei Zeichenketten der Auflösung in «Gruppe auswerten».
        for erlaubt in ('"Version A (echt)"', "Version A ist die tatsächliche Aussage (echt), Version B die gegenteilige."):
            assert erlaubt in t, "erlaubte Auflösungsstelle fehlt: " + erlaubt
            t = t.replace(erlaubt, '""')
    for i, z in enumerate(t.splitlines(), 1):
        for m in muster.finditer(z):
            treffer.append("%s:%d %s" % (n, i, m.group(0)))
check("Keine Kennzeichnung wie echt/falsch/real/fake in Schlüsseln, Bezeichnern und Kommentaren (Ausnahme: 2 Auflösungstexte)", not treffer, "; ".join(treffer))

# 5. Anrede: kein «Sie», «Ihr», «euch», «eure» in der Oberfläche (Befundtexte ausgenommen)
ui = quelltexte["index.html"]
anrede = [m.group(0) for m in re.finditer(r"\b(Sie|Ihnen|Ihre[mnrs]?|Ihr|euch|eure[mnrs]?|euer)\b", ui)]
check("Kein «Sie»/«Ihr»/«euch» im Quelltext der Seite", not anrede, ", ".join(anrede))
bef_anrede = [m.group(0) for b in daten for v in "AB" for f in ("studie", "erklaerung")
              for m in re.finditer(r"\b(Sie|Ihnen|Ihre[mnrs]?|euch|eure[mnrs]?|euer)\b", b[v][f])]
check("Kein Siezen/Ihrzen in den Befundtexten (kleines «ihr/ihre» ist dort Possessivum der 3. Person)", not bef_anrede)

# 6. Eszett und externe Verweise
esz = []
for f in PROJ.rglob("*"):
    if f.is_file() and b"\xc3\x9f" in f.read_bytes():      # alle Dateien, auch Bilder (wie grep -rnP "\xC3\x9F")
        esz.append(str(f.relative_to(PROJ)))
check("Kein Eszett in Projektdateien (inklusive README, TESTBERICHT, Tests, Screenshots)", not esz, ", ".join(esz))
ext = [n for n, t in quelltexte.items() if re.search(r"https?://", t)]
check("Keine http(s)-Verweise in index.html und befunde.js", not ext, ", ".join(ext))
ext2 = [n for n, t in quelltexte.items() if re.search(r"\b(import\s|type=\"module\"|fetch\(|XMLHttpRequest|CDN)", t)]
check("Keine Module, kein fetch/XHR in index.html und befunde.js", not ext2, ", ".join(ext2))
check("Skripte sind klassisch (kein type=module)", 'type="module"' not in quelltexte["index.html"])
check("base.css relativ eingebunden (../shared/base.css)", '<link rel="stylesheet" href="../shared/base.css">' in quelltexte["index.html"])

# 7. Gewicht
gross = {n: (PROJ / n).stat().st_size for n in ("index.html", "befunde.js")}
check("Gewicht index.html + befunde.js unter 300 KB (%d Byte)" % sum(gross.values()), sum(gross.values()) < 300 * 1024)

fehler = [e for e in ergebnisse if not e[1]]
print("\n%d Prüfungen, %d bestanden, %d fehlgeschlagen" % (len(ergebnisse), len(ergebnisse) - len(fehler), len(fehler)))
sys.exit(1 if fehler else 0)
