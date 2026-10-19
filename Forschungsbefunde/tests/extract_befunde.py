"""Erzeugt befunde.js aus dem Wiederholungsauftrag Einführung 2 (nur lesen).

Aufruf:  python3 -I tests/extract_befunde.py
Quelle:  ../quellen/dokumente/10_einfuehrung2.md  (Aktivität 1, 9 Befunde mit Version A und B)
Ziel:    befunde.js (klassisches Skript, setzt window.BEFUNDE, 5 ausgewählte Befunde)

Von den 9 Befunden des Auftrags kommen fünf in die Seite (Auswahl und Reihenfolge: AUSWAHL).
Begründung der Auswahl: README, Abschnitt «Auswahl der fünf Befunde».

Die Texte (Titel, Studie, Erklärung, A und B) werden Zeichen für Zeichen aus dem Auftrag übernommen.
Einzige Umformung: das Markdown-Escape  \\$  wird zu  $  (reines Satzzeichen-Escape).
Die Hervorhebung *wort* bleibt als Markierung im Text und wird von der Seite als Kursivschrift gezeigt.

Nicht aus dem Auftrag stammen nur die Felder `quelle` und `vorbehalt` (Tabelle META unten). Sie sind
für die Auflösung gedacht und enthalten nur Angaben, die bei der Prüfung an Quellen belegt wurden
(Belege: README, Abschnitt «Fachliche Hinweise zur Prüfung»). Leer lassen, was nicht belegt ist.
"""
import json
import re
import sys
from pathlib import Path

PROJ = Path(__file__).resolve().parents[1]
QUELLE = PROJ.parent / "quellen" / "dokumente" / "10_einfuehrung2.md"
ZIEL = PROJ / "befunde.js"

START_MARKER = "## Aktivität 1: Hindsight Bias"
ENDE_MARKER = "**Durchführung:**"

# Nummern im Auftrag, in der Reihenfolge der Seite (Seite: Befund 1 bis 5).
# Befund 4 (Gruppengrösse und Hilfeverhalten) steht absichtlich zuletzt: Er ist der Klassiker, den
# Studierende am ehesten aus der Sozialpsychologie kennen. Kommt er zuletzt, kann ein Erkennen die
# ersten vier Urteile nicht beeinflussen.
AUSWAHL = [5, 3, 7, 9, 4]

# Nur für die Auflösung. Alles hier ist an Quellen geprüft (siehe README); sonst leer.
META = {
    5: {
        "quelle": "Langlois & Roggman (1990), Psychological Science, 1(2), 115–121.",
        "vorbehalt": "Gemittelte Gesichter wirken attraktiv, sind aber nicht die attraktivsten: Die gemittelte "
                     "Form besonders attraktiver Gesichter wurde dem Durchschnitt aller Gesichter vorgezogen "
                     "(Perrett, May & Yoshikawa, 1994, Nature, 368, 239–242). Warum Durchschnittsgesichter "
                     "attraktiv wirken, ist offen: Langlois und Roggman nennen evolutionäre und kognitive Gründe.",
    },
    3: {
        "quelle": "Lepper, Greene & Nisbett (1973), Journal of Personality and Social Psychology, 28(1), 129–137; "
                  "Metaanalyse: Deci, Koestner & Ryan (1999), Psychological Bulletin, 125(6), 627–668.",
        "vorbehalt": "Der Effekt zeigt sich bei erwarteter, an die Tätigkeit geknüpfter Belohnung, nicht bei "
                     "unerwarteter (Deci, Koestner & Ryan, 1999). Wie allgemein er gilt, ist umstritten "
                     "(Cameron & Pierce, 1994, Review of Educational Research, 64(3), 363–423).",
    },
    7: {
        "quelle": "Zajonc (1965), Science, 149(3681), 269–274; Metaanalyse über 241 Studien: "
                  "Bond & Titus (1983), Psychological Bulletin, 94(2), 265–292.",
        "vorbehalt": "Eine vorregistrierte Replikation der bekannten Kakerlaken-Studie (Zajonc, Heingartner & "
                     "Herman, 1969) fand keinen Unterschied zwischen einfacher und schwieriger Aufgabe: Das "
                     "Publikum verlangsamte die Tiere bei beiden Aufgaben (Halfmann, Bredehöft & Häusser, 2020, "
                     "Psychological Science, 31(3)).",
    },
    9: {
        "quelle": "Gilovich, Medvec & Savitsky (2000), Journal of Personality and Social Psychology, 78(2), 211–222.",
        "vorbehalt": "",
    },
    4: {
        "quelle": "Darley & Latané (1968), Journal of Personality and Social Psychology, 8(4), 377–383; "
                  "Metaanalyse: Fischer et al. (2011), Psychological Bulletin, 137(4), 517–537.",
        "vorbehalt": "Die Metaanalyse findet den Effekt im Mittel (g = -0.35), aber abgeschwächt in gefährlichen "
                     "Notfällen (Fischer et al., 2011). In Überwachungsvideos realer öffentlicher Konflikte "
                     "(N = 219) griff in etwa 9 von 10 Fällen mindestens eine Person ein, und mit mehr Anwesenden "
                     "stieg die Wahrscheinlichkeit dafür (Philpot et al., 2020, American Psychologist).",
    },
}

RE_TITEL = re.compile(r"^\s*-\s+\*\*Forschungsbefund\s+(\d+):\s*(.+?)\*\*\s*$")
RE_VERSION = re.compile(r"^\s*-\s+\*\*Version\s+([AB])\b.*\*\*\s*$")
RE_FELD = re.compile(r"^\s*-\s+\*\*(Studie|Erklärung):\*\*\s*(.+?)\s*$")


def unescape(s):
    return s.replace("\\$", "$")


def lesen():
    zeilen = QUELLE.read_text(encoding="utf-8").splitlines()
    try:
        a = next(i for i, z in enumerate(zeilen) if z.strip() == START_MARKER)
        e = next(i for i, z in enumerate(zeilen) if i > a and z.strip() == ENDE_MARKER)
    except StopIteration:
        sys.exit("FEHLER: Start- oder Endmarke im Auftrag nicht gefunden")
    befunde, cur, ver = {}, None, None
    for nr, z in enumerate(zeilen[a:e], start=a + 1):
        m = RE_TITEL.match(z)
        if m:
            cur = {"auftrag_nr": int(m.group(1)), "titel": unescape(m.group(2)), "A": {}, "B": {}}
            befunde[cur["auftrag_nr"]] = cur
            ver = None
            continue
        m = RE_VERSION.match(z)
        if m:
            ver = m.group(1)
            continue
        m = RE_FELD.match(z)
        if m:
            if cur is None or ver is None:
                sys.exit("FEHLER: Feld ohne Befund/Version: " + z)
            key = "studie" if m.group(1) == "Studie" else "erklaerung"
            if key in cur[ver]:
                sys.exit("FEHLER: Feld doppelt: " + z)
            cur[ver][key] = unescape(m.group(2))
    return befunde


def pruefen(befunde):
    if sorted(befunde) != list(range(1, 10)):
        sys.exit("FEHLER: erwartet Befunde 1 bis 9 im Auftrag, gefunden: %s" % sorted(befunde))
    for b in befunde.values():
        for v in "AB":
            if set(b[v]) != {"studie", "erklaerung"}:
                sys.exit("FEHLER: Befund %d Version %s unvollständig: %s" % (b["auftrag_nr"], v, list(b[v])))
    if sorted(AUSWAHL) != sorted(META) or len(set(AUSWAHL)) != 5:
        sys.exit("FEHLER: AUSWAHL und META passen nicht zusammen")


def js(s):
    return json.dumps(s, ensure_ascii=False)


def schreiben(befunde):
    out = []
    out.append("/* befunde.js: Daten der fünf Forschungsbefunde (klassisches Skript, kein Modul).")
    out.append("   Erzeugt durch tests/extract_befunde.py aus dem Wiederholungsauftrag Einführung 2,")
    out.append("   Aktivität 1 (fünf von neun Befunden, Auswahl im Skript). Nicht von Hand ändern, sondern neu erzeugen.")
    out.append("   Pro Befund zwei Fassungen A und B mit je Studie und Erklärung.")
    out.append("   *wort* markiert ein hervorgehobenes Wort (wird kursiv angezeigt).")
    out.append("   quelle und vorbehalt werden nur in der Auflösung angezeigt (Knopf «Auflösung anzeigen»). */")
    out.append("window.BEFUNDE = [")
    teile = []
    for neu, alt in enumerate(AUSWAHL, start=1):
        b = befunde[alt]
        t = ["  {"]
        t.append("    nr: %d," % neu)
        t.append("    titel: %s," % js(b["titel"]))
        for v in "AB":
            t.append("    %s: {" % v)
            t.append("      studie: %s," % js(b[v]["studie"]))
            t.append("      erklaerung: %s" % js(b[v]["erklaerung"]))
            t.append("    },")
        t.append("    quelle: %s," % js(META[alt]["quelle"]))
        t.append("    vorbehalt: %s" % js(META[alt]["vorbehalt"]))
        t.append("  }")
        teile.append("\n".join(t))
    out.append(",\n".join(teile))
    out.append("];")
    ZIEL.write_text("\n".join(out) + "\n", encoding="utf-8")


if __name__ == "__main__":
    befunde = lesen()
    pruefen(befunde)
    schreiben(befunde)
    print("befunde.js geschrieben: %d Befunde (Auftrag Nr. %s), %d Bytes" % (len(AUSWAHL), AUSWAHL, ZIEL.stat().st_size))
