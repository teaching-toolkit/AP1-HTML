# HTML-Projekte: Übersicht und Arbeitsaufträge

Stand: 13.10.2026 · Kurs: Allgemeine Psychologie 1 (HSLU) · Ordner: `Überarbeitung/`

**Zweck.** Alles Interaktive aus den Wiederholungsaufträgen soll als HTML5-Seite laufen, auf GitHub Pages gehostet werden und in den Dokumenten nur noch als Link stehen. Studierende laden nichts herunter und starten nichts lokal.

**Dieses Dokument** ist die Arbeitsgrundlage für fünf Projekte. Es sagt für jedes Projekt, wo die Informationen liegen (Dateien und Zeilen), was gebaut werden muss, welche Probleme aus der Analyse zu beheben sind und wie getestet wird. Jedes Projekt wird von einem eigenen Agenten bearbeitet.

> Annahme: «Marco File» = Markdown-Datei.

---

## 0. Gemeinsame Regeln (gelten für alle fünf Projekte)

### 0.1 Pfade und Ablage

| Was | Ort im Workspace |
|---|---|
| Projektliste (diese Datei) | `/home/claude/html-projekte/HTML-Projekte.md` |
| Quellen (Kopien, nur lesen) | `/home/claude/html-projekte/quellen/` |
| Dokumente (Aufträge, .md) | `/home/claude/html-projekte/quellen/dokumente/` |
| Gemeinsames CSS | `/home/claude/html-projekte/shared/base.css` (nicht ändern) |
| Ergebnis je Projekt | `/home/claude/html-projekte/<projektordner>/` (siehe Abschnitt je Projekt) |

Die Originale liegen im Ordner `Überarbeitung/` auf dem Computer des Dozenten. Die Kopien im Workspace sind identisch. **Auf den Computer des Dozenten wird nicht geschrieben.** Das übernimmt die Hauptsession nach der Abnahme.

### 0.2 Technik (Definition of Done, Teil 1)

1. **Statisch und eigenständig.** Reines HTML/CSS/JavaScript, kein Build-Schritt, keine Bibliotheken von CDNs, keine externen Schriften, Bilder oder Skripte, keine Netzwerkanfragen zur Laufzeit.
2. **Läuft über `file://` und über `http://`.** Keine ES-Module (`type="module"`), keine `fetch`-Aufrufe auf lokale Dateien. Skripte als klassische `<script>`. Alle Pfade relativ.
3. **Gemeinsame Basis.** Jede Seite bindet `../shared/base.css` ein (bei Unterordnern entsprechend `../../shared/base.css`). Projektspezifisches CSS steht lokal im Projekt. Beim Ausliefern kopiert die Hauptsession `shared/` in das Repo. Der relative Pfad muss daher stimmen.
4. **Mobil zuerst.** Funktioniert hochkant ab 360 px Breite, auf Tablet und Desktop. Bedienbar mit Touch, Maus und Tastatur. Keine Funktion nur per Hover oder nur per Tastatur. Klickflächen mindestens 44 × 44 px. Kein horizontales Scrollen der Seite.
5. **Barrierearm.** `lang="de"`, echte `<button>`, sichtbarer Fokus, Kontrast mindestens AA, Hell/Dunkel über `prefers-color-scheme`, `prefers-reduced-motion` respektieren.
6. **Keine Daten verlassen das Gerät.** Kein Tracking, keine Cookies, keine Server. `localStorage`/`sessionStorage` nur optional für Komfort und immer mit `try/catch`. Die Seite muss ohne Speicher vollständig funktionieren.
7. **Gering im Gewicht.** Pro Projekt ohne Bilder unter 300 KB. Bilder komprimieren (JPEG/WebP). Gesamtgrösse pro Projekt möglichst unter 3 MB.
8. **Keine Lösungen auf der öffentlichen Seite.** Keine Musterlösungen, keine Moderationsskripte, keine Pass/Fail-Kriterien. Die Seite zeigt nur, was Teilnehmende brauchen. Wo eine Lösung technisch nötig ist (z. B. richtige Reihenfolge), steht sie als reine Daten im Code und wird erst auf Wunsch genutzt.
9. **Testparameter per URL erlaubt**, z. B. `?dauer=10` zum Abkürzen, `?seed=42` für Reproduzierbarkeit. Sie sind im README dokumentiert.

### 0.3 Sprache

- Schweizer Hochdeutsch: **«ss» statt Eszett** (das Zeichen mit dem Bogen unten wird nirgends verwendet). Vor Abgabe mit `grep -rnP "\xC3\x9F" <projektordner>` prüfen (Ergebnis muss leer sein).
- Anrede in der Oberfläche: **«du»** (nicht «Sie», nicht «ihr»). Kurze, neutrale Sätze. Nicht dozieren, nicht Pointen vorwegnehmen.
- Fachbegriffe wie im Auftrag. Neue Fachaussagen nicht erfinden (siehe 0.5).

### 0.4 Gruppenergebnisse ohne Server (Konvention)

In Gruppen von 4 bis 5 Personen liefert eine einzelne Person oft kein klares Ergebnis. Wo ein Projekt «Gruppe» braucht, gilt:

- Am Ende erzeugt die Seite einen kurzen **Ergebnis-Code** (URL-sicher, nur ASCII, mit Kennung und Version, z. B. `HSLU-hindsight-v1.<daten>`). Mit Kopieren-Knopf.
- Eine Ansicht **«Gruppe auswerten»** nimmt mehrere Codes entgegen (ein Code pro Zeile, Leerzeilen und Duplikate werden ignoriert, ungültige Zeilen werden benannt) und zeigt die gemeinsame Auswertung.
- Der Code enthält nur Ergebnisse, keine Namen, keine Freitexte.
- Jede Seite implementiert das für sich. Es gibt keinen gemeinsamen JS-Code zwischen Projekten (damit die Agenten sich nicht in die Quere kommen).

### 0.5 Umgang mit fachlichen Zweifeln

Die Dokumente enthalten teils fachliche Fehler (aus der Analyse bekannt, pro Projekt unten vermerkt). Die Regel:

- **Eindeutige technische Fehler** (z. B. Tippfehler im Code, kaputte Logik) behebst du.
- **Fachliche Inhalte** übernimmst du wie im Auftrag und markierst Zweifel im README unter **«Fachliche Hinweise zur Prüfung»** (konkret: Stelle, Bedenken, Vorschlag). Du änderst fachlich nichts stillschweigend.
- **Nichts erfinden:** keine Quellenangaben, Studien, Zahlen oder Erklärungen hinzufügen, die nicht in den Quellen stehen.

### 0.6 Testen (Definition of Done, Teil 2)

Jeder Prototyp wird **selbst getestet, bevor er gemeldet wird.** «Funktioniert» heisst: Tests liefen und sind dokumentiert.

**Werkzeug.** Playwright für Python ist installiert, Chromium liegt unter `/opt/pw-browsers` (`playwright install` nicht ausführen). Grundgerüst:

```python
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b = p.chromium.launch()
    desktop = b.new_page(viewport={"width": 1280, "height": 800})
    phone = b.new_context(viewport={"width": 390, "height": 844},
                          has_touch=True, is_mobile=True).new_page()
    errors = []
    desktop.on("console", lambda m: errors.append(m.text) if m.type == "error" else None)
    desktop.on("pageerror", lambda e: errors.append(str(e)))
    desktop.on("requestfailed", lambda r: errors.append("FAILED " + r.url))
```

Seiten über einen lokalen Server prüfen (`python3 -m http.server 8000 --directory /home/claude/html-projekte`) **und** einmal über `file://`. Ein Python-Skript mit `python3 -I` starten, Skripte nicht im Projektordner ablegen, sondern in `<projektordner>/tests/`.

**Pflichtprüfungen für jedes Projekt:**

1. Kein Konsolenfehler, kein `pageerror`, keine fehlgeschlagene oder externe Anfrage (nur `file://`/`127.0.0.1`).
2. Vollständiger Durchlauf als Nutzer (alle Schritte bis zur Auswertung) auf Desktop **und** auf dem Handy-Viewport (Touch statt Klick).
3. Reine Tastaturbedienung der Kernaufgabe.
4. Screenshots der wichtigsten Zustände (Desktop und Handy). **Die Screenshots mit dem Read-Werkzeug ansehen** und Layoutfehler beheben (Überlauf, abgeschnittener Text, überlappende Elemente).
5. Randfälle des Projekts (siehe je Projekt).
6. Logik, die rechnet, wird gegen eine unabhängige Referenz geprüft (Python-Nachrechnung oder Simulation), nicht nur «sieht plausibel aus».
7. Die Eszett-Prüfung aus 0.3 liefert nichts. Keine Verweise auf `http://`/`https://` ausser in reinen Textlinks, die nicht geladen werden.

### 0.7 Ergebnisformat pro Projekt

Im Projektordner:

- `index.html` (bzw. die unten genannten Seiten) plus Assets.
- `README.md`: Zweck, Bedienung für Teilnehmende, Bedienung/Parameter für Fachpersonen, wie man Inhalte ändert (welche Datenstruktur wo), Link-Struktur für GitHub Pages, bekannte Grenzen, **Fachliche Hinweise zur Prüfung**, **Offene Fragen an den Dozenten**.
- `TESTBERICHT.md`: was getestet wurde (Tabelle: Test, Gerät, Ergebnis), gefundene und behobene Fehler, nicht getestete Dinge mit Grund, Screenshots-Liste.
- `tests/`: die Testskripte (laufen mit `python3 -I tests/<datei>.py`).
- `screenshots/`: die wichtigsten Bilder (klein halten).

**Schlussmeldung an die Hauptsession** (höchstens 200 Wörter): was gebaut ist, Ergebnis der Tests in Zahlen, was offen oder unsicher ist, was der Dozent entscheiden muss.

### 0.8 Nicht tun

- Nichts in `quellen/` oder `shared/` ändern. Brauchst du eine Änderung an `shared/base.css`, ergänze lokales CSS im Projekt und nenne den Wunsch im README.
- Keine anderen Projektordner anfassen.
- Keine `device_*`-Werkzeuge verwenden (kein Zugriff auf den Computer des Dozenten).
- Keine Dateien ausserhalb des Projektordners und von `/tmp` anlegen.

---

## Übersicht der fünf Projekte

| Nr. | Projekt | Ordner | Dokument(e) | Ersetzt / repariert |
|---|---|---|---|---|
| P1 | Motivation-2-Experimente (GoFundMe-Simulation, Mere-Exposure-Experiment) | `p1-motivation2/` | Motivation 2, Aktivität 1 | zwei HTML-Dateien «per Mail» |
| P2 | Glücksfaktoren-Spiel (Emotion) | `p2-emotion-spiel/` | Emotion, Aktivität 2 | Excel + Word-Umweg + unvollständiges HTML |
| P3 | Hindsight-Bias-Experiment | `p3-hindsight/` | Einführung 2, Aktivität 1 | 9 Google Forms + allocate.monster |
| P4 | Sortier-Engine mit drei Aufgaben (Sehprozess, Maslow, Flussmodell) | `p4-sortieren/` | Wahrnehmung 2 A1, Motivation 1 A1 und A3 | Kärtchen, Post-its, Handouts |
| P5 | Schwellentest (Lückenerkennung) und Signalentdeckung | `p5-psychophysik/` | Aufmerksamkeit und Psychophysik, A1 (+ Ziele zu SDT) | Padova-Test auf fremdem Server |

---

## P1: Motivation-2-Experimente

**Ordner:** `p1-motivation2/` mit den zwei Seiten `gofundme/index.html` und `mere-exposure/index.html` (je eigener Ordner mit `assets/`).

### Ziel
Die zwei bestehenden Experimente (Ähnlichkeit/Altruismus und Mere Exposure) laufen zuverlässig auf jedem Gerät, ohne Download, ohne CDN, und liefern verwertbare Gruppenergebnisse.

### Wo die Informationen liegen

| Was | Datei (Workspace) | Original im Ordner `Überarbeitung/` |
|---|---|---|
| Bestehende Seite GoFundMe | `quellen/p1/Aktivitaet1_GoFundMe.html` | `Material für die Aufträge/13. Motivation 2/Aktivität1.html` |
| Bestehende Seite Mere Exposure («Pfeil-Experiment») | `quellen/p1/Aktivitaet2_MereExposure.html` | `…/13. Motivation 2/Aktivität2.html` |
| 6 Profilbilder (je ca. 0.9 MB, 1024 × 1024) | `quellen/p1/images/*.jpg` | `…/13. Motivation 2/images/` |
| 49 Gesichter (je ca. 200 KB, 325 × 325) | `quellen/p1/bilder/1.png` bis `49.png` | `…/13. Motivation 2/bilder/` |
| Auftrag, Ziel, Durchführung, Musterlösung | `quellen/dokumente/13_motivation2.md`, Zeilen 119–276 | `13_Wiederholungsauftrag Motivation 2.md` |
| Vorbereitung und Fail-Kriterium zu HTML | `quellen/dokumente/13_motivation2.md`, Zeilen 53–62 und 89–118 (Zeilen 55, 99, 113) | dito |

Nicht verwenden: `Aktivität1 Original.psd` (28 MB), `Motivation 2.zip`, `bilder/Originale/` (Rohmaterial, nicht ins Repo).

### Ablauf im Unterricht (aus dem Auftrag)
Studierende öffnen ohne Erklärung zuerst die eine Seite, dann die andere. Erst danach wird erklärt und diskutiert. Die Seiten dürfen daher **nichts erklären oder deuten**, was die Diskussion vorwegnimmt (die bestehende Auflösung beim Mere-Exposure-Experiment ist ein Grenzfall: knapp halten, Begriff nennen ist in Ordnung, Erklärungen nicht).

### Verbindlich einzuarbeiten (Befunde aus der Analyse)

**GoFundMe-Simulation**
- **Fehler beheben:** In `attachChipGroup("residence-chips", …)` steht `getElementById("btn-show_results")` (Unterstrich statt Bindestrich). Folge: Wählt man Wohnort zuletzt und bewegt danach keinen Slider, bleibt «Auswertung anzeigen» deaktiviert. Aktivierungslogik in **eine** Funktion, die nach jeder Eingabe läuft. Testfall dafür ist Pflicht.
- **Kein Chart.js vom CDN.** Streudiagramme selbst zeichnen (SVG oder Canvas), ohne Bibliothek. Achsen, Beschriftung, Punkte mit Namen.
- **Handytauglich.** Heute zwei feste Spalten und 300-px-Bilder ohne Media Query. Einspaltig unter ca. 700 px, Bilder `max-width: 100%`.
- **Bilder komprimieren:** JPEG, längste Kante höchstens 640 px, ca. 70–120 KB je Bild. Dateinamen beibehalten. (Die Bilder sind KI-generiert. Hinweis dazu im README. Auf dem Bild «alex» hängen Plakate mit politischen Parolen, auf «mia» steht verzerrter Text. Beides im README erwähnen, Bilder nicht verändern.)
- **Titel und Anrede:** «GoFundMe-Simulation» (ohne «Prototyp»), konsequent «du».
- **Auswertung transparent machen.** Die berechnete «Eigenschaftsähnlichkeit» beruht auf Profilmerkmalen, die Teilnehmende nie sehen (Politik, Wohnort, Extraversion, Erregungssuche, Geschlecht). In der Auswertung eine Tabelle «Profilmerkmale» zeigen, damit die Berechnung nachvollziehbar ist.
- **Vorsichtige Deutung.** Mit nur 6 Punkten ist r sehr instabil. Statt willkürlicher Schwellen («klar positiv», «deutlich») neutrale Texte und ein Hinweis «mit 6 Profilen nur ein Diskussionsanstoss». Wenn r nicht berechenbar ist (z. B. alle Spenden gleich), «nicht berechenbar» anzeigen.
- **Budget:** 500 CHF, Schritte von 10. Mindestens ein Betrag grösser 0. Es muss nicht alles verteilt werden. Der Rest wird als «nicht verteilt» angezeigt.
- **Ergebnis-Code und «Gruppe auswerten»** (siehe 0.4): pro Person die Spenden, Sympathie, subjektive Ähnlichkeit, Selbstangaben. Gruppenansicht: gemeinsames Streudiagramm (alle Personen × 6 Profile, Punkte pro Person unterscheidbar) und r über alle Punkte.

**Mere-Exposure-Experiment**
- **Touch-Bedienung.** Heute reagiert die Seite nur auf Pfeiltasten. Auf Handy und Tablet bleibt sie stehen. Zwei grosse Knöpfe (links/rechts) zusätzlich zu den Tasten.
- **Häufige Gesichter zufällig wählen.** Heute sind es immer die Gesichter 1 bis 4, was den Effekt mit deren Attraktivität vermischt. Pro Durchlauf 4 häufige Gesichter zufällig aus 49. Anzahl und Gewichtung wie im Original (Faktor 10, 4 häufige, 6 seltene zur Bewertung), Bewertungsreihenfolge gemischt.
- **Nebenaufgabe klären.** Im Original soll man die Blickrichtung des Gesichts angeben und den Pfeil ignorieren. Die Bilder sind Fantasy-Porträts mit uneinheitlicher Blickrichtung (z. B. schaut Nr. 2 nach links, der Code nimmt «rechts» an), eine Richtigkeit wird nicht geprüft. Wähle eine **eindeutig definierte** Nebenaufgabe (Vorschlag: «In welche Richtung zeigt der Pfeil?» mit zufällig gespiegeltem Gesicht), erfasse die Trefferquote und halte die Änderung im README fest.
- **Bilder komprimieren:** 49 Bilder von je ca. 200 KB auf je höchstens 30 KB (WebP oder JPEG, 325 px). Vorladen mit Fortschrittsanzeige.
- **Dauer:** 120 s wie im Original. Per `?dauer=10` abkürzbar.
- **Auswertung pro Person:** Mittel häufig vs. selten, Differenz, plus Liste aller Bewertungen. Hinweis, dass 4 vs. 6 Bewertungen verrauscht sind.
- **Ergebnis-Code und «Gruppe auswerten»:** Mittelwertdifferenz je Person, Gruppenmittel, Anzahl Personen mit positiver Differenz.
- **Anrede «du»** statt «Sie».

### Randfälle für die Tests
GoFundMe: Wohnort zuletzt wählen ohne Slider; nur ein Profil bedacht; alle Spenden 0 (Weiter gesperrt); Summe über 500 (Warnung, gesperrt); alle Spenden gleich (r nicht berechenbar); Zurück-Navigation behält Eingaben; 360-px-Breite; Code erzeugen und in «Gruppe auswerten» einlesen (3 Personen, ein ungültiger Code, ein Duplikat).
Mere Exposure: Touch-Durchlauf komplett; `?dauer=5`; Tastatur; seltene Gesichter in der Bewertung waren zuvor mindestens einmal zu sehen oder nicht (dokumentieren, was zutrifft); Verteilung der häufigen Gesichter über 200 Durchläufe ist gleichmässig (nicht immer 1–4); Bewertung für alle 10 Gesichter lückenlos.

---

## P2: Glücksfaktoren-Spiel (Emotion, Aktivität 2)

**Ordner:** `p2-emotion-spiel/` mit `index.html`.

### Ziel
Ein vollständiges Entscheidungsspiel («Alexandra»), das die Fachperson mit der Gruppe auf einem Gerät spielt. Es ersetzt Excel, das Word-Dokument (der Word-Umweg zum Kopieren von Werten entfällt), den physischen Würfel und das bisherige unvollständige HTML.

### Wo die Informationen liegen

| Was | Datei (Workspace) | Original |
|---|---|---|
| **Regelwerk und Zahlen (massgebend)** | `quellen/p2/gluecksfaktoren.xlsx` (Blatt «Tabelle1», 38 Zeilen mit Episoden-Varianten ab Zeile 3, Formeln in Spalten Q, S–Y, AA–AF, AH–AN, AW) | `Material für die Aufträge/11. Emotion/11. Glücksfaktoren.xlsx` |
| **Texte** (Vorlesen, Optionen, «Unmittelbare Folge», Würfeltitel, Glücksfaktoren), Mikroszenen M1–M10, Spielregeln, Moderationshinweise | `quellen/p2/gluecksfaktor_spiel.docx` (mit `python-docx` lesen) | `…/11. Emotion/11. Glücksfaktor Spiel.docx` |
| Bestehende UI/Engine (Ausgangspunkt, **weicht vom Excel ab**) | `quellen/p2/wohlbefindens_faktoren_minimal.html` | `…/11. Emotion/11. wohlbefindens_faktoren_minimal.html` |
| Einbettung im Auftrag | `quellen/dokumente/11_emotion.md`, Zeilen 283–294 (Aktivität 2), 59–128 (Praktische Vorbereitung, u. a. Zeile 81, 83, 289) | `11_Wiederholungsauftrag Emotion.md` |

### Verbindlich einzuarbeiten (Befunde aus der Analyse)

- **Excel ist die Quelle der Wahrheit** für Zahlen und Formeln. Das bestehende HTML ist eine abweichende Teilumsetzung:
  - Startwerte: Excel Zeit 0, Energie 0, Soz 1, Erfüllung 1, Lebensstil 1, Finanzen 1, Stimmung 50. HTML: 0, 1, 1, 2, 0, −1, Stimmung 55.
  - Gewichte («Relevanz der Faktoren», Spalten AP–AU): Excel 0.25 / 0.30 / 0.20 / 0.55 / 0.45 / 0.25. HTML 0.4 / 0.5 / 0.3 / 0.4 / 0.2 / 0.4.
  - Excel kennt halbe Punkte (−0.5, +0.5, +1.5), das HTML nicht. Energie-Basis in Episode 1A: Excel 0, HTML −4.
  - **Die Krisen-Episoden 12A1, 12A2, 12B1, 12B2 sind im HTML leer** (Soll 10, keine Deltas, Start-Stimmung 0). Im Excel haben sie Soll-Werte (16–20), Deltas und Start-Stimmung −10.
  - Die **Mikroszenen M1–M10** stehen nur im Word.
- **Alle 19 Episoden** (1, 2A, 2B, 3, 4, 5A, 5B, 6, 7, 8A, 8B, 9, 10, 11A, 11B, 12A1, 12A2, 12B1, 12B2) mit den Verzweigungen aus dem Word («Weiter bei: …»).
- **Rechenlogik exakt wie im Excel**, aus den Formeln gelesen (Resultat: `max(0, round(2·Σ Beiträge + Würfel, 1))`, Stimmungsänderung, Energie-Anpassung durch Stimmung, Zeit −1 bei Finanzen < −2, Schranken). **Bekannte Auffälligkeit:** Die Formel `IF(G>2, w*2, IF(G>4, w*3, G*w))` hat einen toten Zweig (der zweite Fall ist nie erreichbar). Faktisch sättigt der positive Beitrag bei `2·w`, und zwar nur bei Zeit, Energie, Finanzen (nicht bei Soz, Erfüllung, Lebensstil), Negatives sättigt nicht. **Setze das Verhalten exakt so um** (Ergebnisse sollen mit dem Excel übereinstimmen), mache es in einer klar benannten Konfiguration sichtbar und nenne es im README als Frage an den Dozenten.
- **Würfel:** virtueller D20 mit Taste und **zusätzlich** Eingabe eines physischen Wurfs (1–20). `?seed=` für Reproduzierbarkeit in Tests.
- **Ablauf pro Episode** (wie im bestehenden HTML und im Word): Vorlesen-Text, Option A/B mit «Unmittelbare Folge», Wurf, Boost aus Attributen (Balken je Attribut), Ergebnis gegen Soll, Veränderungen, Stimmung, «Werte danach», Glücksfaktoren **erst nach** der Entscheidung, «Weiter».
- **Mikroszenen:** M1–M10 mit den Deltas aus dem Word als einschiebbare Szenen. Die Seite schlägt passende Szenen vor, wenn Zeit oder Energie unter −5 fallen oder ein Attribut vernachlässigt ist (Zuordnung steht im Word unter «Mikroszenen strategisch einsetzen»). Einschieben ist ein Knopf der Fachperson, nie automatisch.
- **Spielende:** Stimmung unter 0 beendet das Spiel. Das Word nennt zwei Möglichkeiten (direkt ins Debriefing oder «Rettungs-Mikroszene»). Biete beides an.
- **Rückgängig** für den letzten Schritt (Moderation macht Fehler). Zustand komplett im Speicher, optional sessionStorage.
- **Abschlussansicht:** Verlauf der Stimmung über die Episoden (eigene Grafik, ohne Bibliothek), gewählte Optionen je Episode, Endwerte. Keine Deutung, keine «Pädagogische Kernidee» (die ist laut Word erst am Schluss mündlich zu erklären).
- **Nicht auf die Seite:** Erklärungen der Wirkfaktoren für die Fachperson, Formulierungsbeispiele für das Mini-Debriefing, die «Wissenschaftliche Basis» als Liste. Das bleibt im Dokument.
- **Handy-/Tabletbetrieb** (der Auftrag nennt «Smartphone/Tablet»): grosse Knöpfe, ein Bildschirm pro Schritt, Texte gut lesbar zum Vorlesen.

### Prüfen gegen Excel (Pflicht)
Rechne die Excel-Formeln unabhängig in Python nach (`openpyxl` liest nur Formeln, nicht Werte. Entweder die Formeln selbst nachbauen oder, falls verfügbar, LibreOffice für die Neuberechnung nutzen) und vergleiche mit der Seite für mindestens **200 zufällige Zustände** über alle 38 Excel-Zeilen: Resultat, Stimmungsänderung, alle Attribute nach der Entscheidung. Abweichungen null. Dokumentiere im TESTBERICHT, welche Excel-Zellen welcher Funktion entsprechen.

### Randfälle für die Tests
Würfel 1 und 20; Resultat unter 0 (wird auf 0 begrenzt); Stimmung genau 0 und knapp unter 0; Attribute an den Grenzen −10 und +10; Finanzen unter −2; Rückgängig mehrfach; kompletter Durchlauf beider Pfade (BWL/Psychologie, Berater/Jugend, alle vier Krisen) mit je mindestens einem Lauf; Mikroszene einschieben und danach regulär weiter; Handy-Viewport.

---

## P3: Hindsight-Bias-Experiment (Einführung 2, Aktivität 1)

**Ordner:** `p3-hindsight/` mit `index.html` (und `befunde.js` für die Daten, klassisches Skript).

### Ziel
Ersetzt 9 Google Forms und 4 allocate.monster-Links durch **eine** Seite mit Zufallszuteilung im Browser.

### Wo die Informationen liegen

| Was | Datei (Workspace) | Original |
|---|---|---|
| Vorbereitung (Forms-Struktur) | `quellen/dokumente/10_einfuehrung2.md`, Zeilen 47–56 | `10_Wiederholungsauftrag Einführung 2.md` |
| Material, Forms-Struktur, **9 Forschungsbefunde mit Version A und B** | `…/10_einfuehrung2.md`, Zeilen 133–330 | dito |
| Durchführung, Leitfragen, Musterlösung | `…/10_einfuehrung2.md`, Zeilen 330–394 | dito |

### Didaktischer Ablauf (aus dem Auftrag, bindend)
Alle arbeiten **still für sich**. Jede Person erhält zufällig pro Befund entweder die **echte** Version (A) oder die **gegenteilige** (B) mit je passender Erklärung. **Die Teilnehmenden wissen nicht, dass es zwei Versionen gibt.** In der Gruppe vergleichen sie anschliessend ihre «Forschungsberichte» und entdecken die Gegensätze. **Die Seite darf deshalb nie verraten, welche Version echt ist, und nicht erwähnen, dass es Varianten gibt.**

### Verbindlich einzuarbeiten

- **Ablauf pro Befund:** Seite 1: Befund (Studie) zeigen, Freitextfeld «Wie würdest du diesen Befund erklären? (1–2 Stichworte)». Seite 2 (erst nach Abschicken von Seite 1, **kein Zurück** danach): die zugehörige Erklärung zeigen, Frage «Wie offensichtlich findest du diesen Befund jetzt, da du die Erklärung kennst?», Skala 1–5 (1 = gar nicht offensichtlich, 5 = völlig offensichtlich). Fortschrittsanzeige über 9 Befunde.
- **Zuteilung:** pro Person und Befund zufällig A oder B, mit der Nebenbedingung, dass insgesamt 4 oder 5 der 9 Befunde die Version A zeigen (wie die Beispielkombinationen im Auftrag). Zufallsquelle `crypto.getRandomValues`, `?seed=` für Tests.
- **Texte der 9 Befunde wörtlich** aus dem Auftrag (Version A und B, Studie und Erklärung). In `befunde.js` als Daten mit neutralen Feldern `v1`/`v2` bzw. `A`/`B`, **ohne Kennzeichnung «echt/falsch» im Code und in der Oberfläche**. Zusätzlich leere Felder `quelle` und `vorbehalt` pro Befund (für spätere Ergänzung, nicht angezeigt). Anrede im Formulartext auf «du» umstellen (Original teils «Sie»).
- **Ende:** Zusammenfassung «Deine neun Berichte» (Befundtitel, deine Studienaussage, deine Bewertung) in gut vergleichbarer Form, damit die Gruppe nebeneinander vergleichen kann. **Keine Auflösung, keine Deutung.** Ergebnis-Code und «Gruppe auswerten» (siehe 0.4).
- **Gruppe auswerten:** Pro Befund Mittelwert der Offensichtlichkeit für Version A und B getrennt, Anzahl je Version, Gesamtmittel A und B. Die Ansicht nennt neutral «Version A / Version B». Wer echt ist, weiss nur der Auftrag.
- **Zeit:** 9 × (Lesen, Erklären, Bewerten) soll in 10–12 Minuten machbar sein. Schreibe die tatsächliche Dauer eines zügigen Durchlaufs in den TESTBERICHT.
- **Fachliche Hinweise (README, nicht auf die Seite):** Bei mehreren Version-A-Befunden ist die «echt»-Einordnung fachlich umstritten oder durch neuere Befunde überholt. Trage dazu mindestens ein: Befund 6 (Einkommen 75'000 $: Kahneman und Deaton 2010 betrifft emotionales Wohlbefinden, nicht Lebenszufriedenheit; Killingsworth 2021 und die Zusammenarbeit von 2023 widersprechen für die meisten), Befund 2 (Wahlüberfluss: Metaanalyse mit Effekt nahe null), Befund 8 (Mere Exposure bei unangenehmen Geräuschen), Befund 1 (Leichtigkeit des Abrufens bei «Glück», Replikationslage gemischt), Befund 4 (Bystander-Effekt: Videodaten realer Konflikte zeigen häufiges Eingreifen), Befund 3 (Überrechtfertigungseffekt bei Belohnung, Replikationslage gemischt). **Nicht ändern.**

### Randfälle für die Tests
4er- und 5er-Zuteilung in 1000 Simulationen (Verteilung der Anzahl A, gleichmässig über Befunde); kein Zurück-Weg zur Studienseite nach Seite 2 (auch nicht über Browser-Zurück prüfbar? Verhalten dokumentieren); leere Stichworte erlaubt oder nicht (entscheide und dokumentiere: Vorschlag erlaubt, Zähler zeigt «0 Zeichen»); Bewertung ohne Auswahl blockiert Weiter; Ergebnis-Code Rundreise (erzeugen, einlesen, gleiche Daten); Gruppenansicht mit 5 Personen, einem ungültigen Code, einem Duplikat, einer unvollständigen Person; Handy-Viewport; Tastaturbedienung der Skala (Pfeiltasten oder Ziffern 1–5).

---

## P4: Sortier-Engine mit drei Aufgaben

**Ordner:** `p4-sortieren/` mit `engine.js`, `engine.css`, und den Einstiegsseiten `sehprozess.html`, `maslow.html`, `flussmodell.html` (jede Seite bindet `engine.js` und die jeweilige Datendatei `daten-*.js` als klassische Skripte). Dazu `index.html` als kleine Übersicht.

### Ziel
Eine wiederverwendbare Engine für **zwei Aufgabentypen** (später auch für andere Aufträge einsetzbar, z. B. Einführung 1, Vorhersagende Verarbeitung):

1. **Reihenfolge** (Karten in die richtige Sequenz bringen).
2. **Zuordnung** (Karten Behältern zuordnen, optional mehrfach).

### Wo die Informationen liegen

| Instanz | Quelle (Workspace) | Original |
|---|---|---|
| **Sehprozess** (Reihenfolge, 12 Schritte, Schritt 7 in 7a und 7b) | `quellen/dokumente/11_wahrnehmung2.md`, Zeilen 99–173 (Aktivität 1, Kärtchenliste ab Zeile 107) | `11_Wiederholungsauftrag Wahrnehmung 2.md` |
| **Maslow** (Zuordnung, 8 Verhaltenskarten) | `quellen/dokumente/13_motivation1.md`, Zeilen 99–187 (Aktivität 1) | `13_Wiedernholungsauftrag Motivation 1.md` (Tippfehler im Dateinamen) |
| **Flussmodell** (Zuordnung, ca. 15 Post-its) | `quellen/dokumente/13_motivation1.md`, Zeilen 297–402 (Aktivität 3) | dito |

Das **Flussmodell-Bild fehlt** (`image1.png` ist nicht im Ordner). Nutze die Kategorien aus der Begriffsliste des Auftrags (Zeilen 330–400) als Behälter.

### Verbindlich einzuarbeiten

**Engine**
- **Bedienung:** Ziehen per Maus und Touch (Pointer Events), **zusätzlich** Tippen-und-Platzieren und volle **Tastaturbedienung** (Karte fokussieren, Pfeiltasten verschieben, Enter/Leertaste auswählen und ablegen). Kein reines HTML5-Drag-and-Drop (funktioniert auf Touch nicht).
- **Zurücksetzen und Mischen** jederzeit. Karten starten in zufälliger Reihenfolge (`?seed=`).
- **Daten statt Code:** Aufgabe als Datenobjekt (Titel, Aufgabentyp, Karten, Behälter, optional Schlüssel). Neue Aufgabe = neue Datendatei, ohne `engine.js` anzufassen. Beschreibe das im README mit Beispiel.
- **Ergebnis-Code und «Gruppe auswerten»** (siehe 0.4): Reihenfolge-Aufgabe zeigt pro Karte die Verteilung der gewählten Positionen, Zuordnungsaufgabe pro Karte die Verteilung auf die Behälter (Heatmap-Tabelle).
- **Bild- und Inhaltsrechte:** keine fremden Bilder. Schematische Grafiken selbst als SVG zeichnen.

**Reihenfolge-Aufgabe (Sehprozess)**
- Schlüssel: Reihenfolge laut Auftrag. **Prüfen** zeigt die Anzahl richtig platzierter Karten und markiert falsch platzierte, ohne die richtige Lösung zu verraten. Unbegrenzt wiederholbar. Die Lösung erscheint nur mit `?loesung=1` (für Fachpersonen).
- **Nur Titel auf den Karten** (z. B. «Hornhaut (Kornea)»), nicht die langen Beschreibungstexte. Grund: Die Beschreibungen im Auftrag enthalten fachliche Fehler (siehe unten). Das Datenfeld `beschreibung` bleibt leer und optional vorgesehen.
- **Mehrdeutigkeit:** Schritte 10 bis 12 («Sehrinde», «Merkmalserkennung», «Parallelwahrnehmung») sind nicht eindeutig sortierbar («Parallelwahrnehmung» ist eine Eigenschaft des ganzen Prozesses, keine Stufe). Die Engine unterstützt «Gruppen gleichwertiger Reihenfolge» (innerhalb einer Gruppe ist jede Reihenfolge richtig). Setze die Gruppe für 10–12 **nicht** von dir aus, sondern dokumentiere die Option und die Entscheidung im README als offene Frage. Standard: Reihenfolge wie im Auftrag.
- Optional («Kann»): eine einfache selbst gezeichnete Augenskizze (SVG) über der Aufgabe.

**Zuordnungsaufgabe (Maslow)**
- Behälter: die fünf Stufen der Bedürfnispyramide (Physiologisch, Sicherheit, Zugehörigkeit/Liebe, Wertschätzung, Selbstverwirklichung) plus **«passt auf keine Stufe»**. Mehrfachzuordnung erlaubt («manche passen auf mehrere Stufen»). **Kein Lösungsschlüssel** (der Auftrag will gerade zeigen, dass man «fast alles irgendwo reinquetschen kann»). Die Auswertung zeigt, wo die Gruppe uneins ist.
- Die 8 Verhaltenskarten wörtlich aus dem Auftrag.

**Zuordnungsaufgabe (Flussmodell)**
- Behälter: die Kategorien aus dem Auftrag (u. a. Rückversicherung, Metabolismus, Hygiene, Selbstbewahrung, Selbsterweiterung, Sex, Brutpflege). Mehrfachzuordnung erlaubt («gewisse Post-its passen bei mehreren Ästen»).
- Schlüssel: die im Auftrag unter den Kategorien aufgeführten Beispiele. «Prüfen» meldet, ob die gewählte Kategorie unter den im Auftrag genannten liegt, ohne alle Lösungen zu zeigen. Lösung nur mit `?loesung=1`.
- **Inkonsistenz im Auftrag** (nur dokumentieren): Der Skriptbezug (Zeile 299) nennt vier Ströme (Rückversicherung, Selbsterweiterung, Fürsorge, Selbsterhaltung), die Post-its haben sieben Kategorien.

### Fachliche Hinweise für das README (nicht ändern, nur melden)
Im Sehprozess-Auftrag (Zeilen 99–173): «Schritt 8→9: peripheres → zentrales Nervensystem» (Retina und Sehnerv gehören zum ZNS); die Kompression 130 Mio auf 1 Mio geschieht in der Retina; «Merkmalserkennung = Top-down» (Merkmalsdetektoren sind bottom-up); «Merkmalserkennung im Temporallappen» vs. Sehrinde; Pupillenreaktion als «Adaption» und «Akkommodation» vermischt; die Schritte «7a/7b» sind unsauber nummeriert; «Parallelwahrnehmung» ist keine Stufe.

### Randfälle für die Tests
Ziehen mit Maus, Touch (Playwright-Touch oder Pointer-Ereignisse), reine Tastatur; Karte auf sich selbst ablegen; schnelles Doppelziehen; Zurücksetzen; Prüfen bei leerer, voller und teilweise richtiger Anordnung; Gleichwertigkeitsgruppe (Test mit einem Beispielsatz); Mehrfachzuordnung hinzufügen und entfernen; Code-Rundreise und Gruppenansicht mit 4 Personen; 360-px-Viewport mit 12 Karten (Seite bleibt scrollbar, Ziehen löst keinen Seitenscroll aus); Seite ohne Daten gibt eine verständliche Fehlermeldung.

---

## P5: Schwellentest (Lückenerkennung) und Signalentdeckung

**Ordner:** `p5-psychophysik/` mit `index.html` (Übersicht), `schwelle.html` (Lückenerkennung) und `signalentdeckung.html` (SDT). Je Seite ein eigenes Skript, ohne gemeinsame JS-Datei.

### Ziel
Ersetzt den Padova-Hörtest (fremder Server, vorgeschaltete Datenabfrage, unklare Ergebnisanzeige) durch einen eigenen lokalen Test. Ergänzt eine Signalentdeckungs-Aufgabe, weil Sensitivität/Kriterium/ROC in Zielen und Vorbereitung des Auftrags stehen, aber in keiner Aktivität erlebbar sind.

### Wo die Informationen liegen

| Was | Datei (Workspace) | Original |
|---|---|---|
| Aktivität 1 (Material, Phasen, 2-down-1-up, Musterlösungen) | `quellen/dokumente/12_aufmerksamkeit_psychophysik.md`, Zeilen 93–238 | `12_Wiederholungsauftrag Aufmerksamkeit und Psychophysik.md` |
| Ziele und Begriffe zu SDT (Sensitivität/Kriterium, ROC, liberal/konservativ) | dito, Zeilen 7, 15, 19, 51, 53, 155, 259–261 | dito |
| Bisheriger Test | `https://psychoacoustics.dpg.psy.unipd.it/sito/demographicData.php?test=gap` (nicht laden, nur Referenz: Lückenerkennung in weissem Rauschen, adaptives Verfahren 2-down-1-up nach Levitt 1971, vorgeschaltete Demografie-Seite) | – |

### Verbindlich einzuarbeiten

**Schwellentest (`schwelle.html`)**
- **Aufgabe:** Zwei-Intervall-Wahl (2AFC): zwei kurze Rauschbursts nacheinander, in **einem** davon ist eine stille Lücke. Die Person gibt an, in welchem («1» oder «2»). Rauschen und Lücke werden mit der **Web Audio API** erzeugt (weisses Rauschen, Lücke sampling-genau, kurze Ein-/Ausblenden an den Lückenrändern gegen Knackgeräusche, Dauer der Rampen dokumentieren).
- **Adaptives Verfahren:** 2-down-1-up (nach zwei richtigen Antworten Lücke kürzer, nach einer falschen länger), Schrittweite logarithmisch. Start bei einer deutlich hörbaren Lücke. Abbruch nach festgelegter Zahl Umkehrpunkte. Schwelle = Mittel der letzten Umkehrpunkte. **Dieses Verfahren konvergiert bei ca. 70.7 % Treffern, nicht bei 50 %.** Die Seite sagt das so, ohne Lektion.
- **Ablauf:** Hinweis «Kopfhörer», Lautstärke-Einstellung mit Testton (ohne Anspruch auf Kalibrierung), 3 Übungsdurchgänge, Test, Ergebnis.
- **Ergebnis:** Schwelle in Millisekunden, Verlauf (Lückendauer über die Durchgänge, Umkehrpunkte markiert, selbst gezeichnetes Diagramm), Anzahl Durchgänge und Trefferquote. Ergebnis-Code und «Gruppe auswerten» (siehe 0.4: Tabelle der Schwellen und Gruppenmittel).
- **Audio nur nach Nutzerklick starten** (Autoplay-Regeln auf Handy). Umgang mit gesperrtem oder nicht unterstütztem Audio: verständliche Meldung statt stillem Fehler.
- **Datenschutz:** keine Abfrage von Alter, Geschlecht o. Ä. (Der Padova-Test verlangt das vorab.)

**Signalentdeckung (`signalentdeckung.html`)**
- **Aufgabe:** Ja/Nein-Detektion. Ein Rauschbild (Canvas, zufällige Helligkeit pro Pixel) wird kurz gezeigt. In der Hälfte der Durchgänge steckt ein schwaches, helles Signal (weicher Fleck) darin, in der anderen Hälfte nicht (**Catch-Trials**). Antwort «Ja, Signal» oder «Nein» (Knöpfe, Tasten J/N). Kurz sichtbar (z. B. 300 ms), danach Maske.
- **Zwei Blöcke mit verschiedener Auszahlungsmatrix**, in zufälliger Reihenfolge: liberal (verpasstes Signal kostet viel, Fehlalarm wenig) und konservativ (Fehlalarm kostet viel). Die Matrix steht **vor** dem Block sichtbar auf dem Bildschirm, mit laufendem Punktestand. Je Block 40 bis 60 Durchgänge, **gleiche Signalstärke in beiden Blöcken**.
- **Schwierigkeit** vor dem Start per Regler und kurzem Probelauf einstellbar (Ziel: Treffer etwa 65–85 %), danach fest.
- **Auswertung je Block:** Treffer, Verpasser, Fehlalarme, korrekte Ablehnungen, Trefferrate, Fehlalarmrate, **d′** und **Kriterium c** (mit Log-linear-Korrektur, falls eine Rate 0 oder 1 ist; Formel im README). **ROC-Diagramm** (Fehlalarmrate × Trefferrate) mit beiden Blöcken als Punkte, Diagonale, und der Isosensitivitätskurve des gemessenen d′ (gleiche Varianz). Die Seite benennt die Grössen neutral. Sie sagt nicht «du warst liberal», sondern zeigt die Zahlen und die Matrix, die gegolten hat.
- **Ergebnis-Code und «Gruppe auswerten»:** gemeinsames ROC-Diagramm aller Personen (liberale und konservative Punkte unterscheidbar), Mittelwerte von d′ und c je Block.
- Keine Daten werden gesendet.

**Gemeinsam**
- `index.html` mit zwei Kacheln (kurze Beschreibung, geschätzte Dauer).
- Keine erklärenden Texte über Begriffe, die die Diskussion vorwegnehmen.

### Fachliche Hinweise für das README (nicht ändern, nur melden)
Der Auftrag (Zeilen 93–238) spricht teils von «absoluter Schwelle», «Ton» und «Lautstärke», der Test misst jedoch die zeitliche Auflösung (kürzeste erkennbare Lücke). Die Musterlösung nennt eine «50 %-Schwelle», das Verfahren liefert ca. 70.7 %. Die Abgrenzung absolute Schwelle gegenüber Unterschiedsschwelle ist beim Lückentest nicht trivial (die Lückendauer ist ein Unterschied zu «keine Lücke»). Zeile 175: Weber-Argument mit den Münzpaaren inkonsistent (bei einem Bruch von 2 % liegen beide Paare weit darüber). Die Münzaufgabe selbst bleibt physisch und ist nicht Teil dieses Projekts.

### Prüfen (Pflicht)
- **Stimulus:** Test über `OfflineAudioContext` oder den Generator direkt (per Testhaken, im README erwähnt): Lückenlänge in Samples stimmt exakt, Pegel in der Lücke null, ausserhalb Rauschen mit erwartetem Pegel, Rampen vorhanden, kein Knacken (kein Sprung grösser als die Rampe erlaubt).
- **Adaptives Verfahren:** Simulation eines Hörers mit psychometrischer Funktion (z. B. echte Schwelle 4 ms) über mindestens 500 Läufe. Die Schätzung liegt im Mittel bei der Lückendauer mit ca. 70.7 % Treffern (Toleranz dokumentieren), Streuung berichten. Randfälle: Hörer nie richtig, Hörer immer richtig, Ratehörer (50 %), Abbruchbedingung greift.
- **SDT-Berechnung:** Simulation von Beobachtern mit bekanntem d′ und c (z. B. d′ = 1.5, c = −0.5 / 0 / 0.5) über viele Durchgänge. Geschätzte Werte nahe den wahren (Toleranz dokumentieren). Kantenfälle H = 0, H = 1, FA = 0, FA = 1.
- **UI:** kompletter Durchlauf beider Seiten per Skript mit simuliertem Hörer/Beobachter über einen Testhaken (Antworten werden vorgegeben), auf Desktop und Handy-Viewport mit Touch. Echtes Hören kann nicht getestet werden. Das steht im TESTBERICHT so.

---

## Anhang A: Vorschlag Struktur für GitHub Pages

```
repo-root/
  shared/base.css
  p1-motivation2/gofundme/index.html
  p1-motivation2/mere-exposure/index.html
  p2-emotion-spiel/index.html
  p3-hindsight/index.html
  p4-sortieren/{sehprozess,maslow,flussmodell}.html
  p5-psychophysik/{schwelle,signalentdeckung}.html
```

Nicht ins Repo: `.psd`, `.zip`, `bilder/Originale/`, `.DS_Store`, `quellen/`, `tests/` und `screenshots/` (optional).

## Anhang B: Bekannt, aber nicht Teil dieser fünf Projekte

Weitere HTML-Kandidaten aus der Analyse (Priming-Test, Videoseite, Rauschbilder-Experiment, Kartendecks, Farbwahrnehmung, Blinder Fleck, Tank-Simulator, VAE-Werkzeug, Quizze, Szenario-Karten). Die 20 Rauschbilder für das Muster-Experiment (Einführung 2, Aktivität 3) liegen unter `Material für die Aufträge/10. Einführung 2/10. noise_exercise_images_v3/` und werden später verwendet.
