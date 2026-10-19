# Testbericht P5: Schwellentest und Signalentdeckung

Stand: Endlauf nach allen Korrekturen. Alle Tests: `python3 -I tests/<datei>.py` (Playwright für Python, Chromium; lokaler `http.server` und `file://`). Stand nach der Überarbeitung Signalentdeckung (kürzere Aufgabe, Fleck ausserhalb der Kreuzmitte, Code v2). Gesamt: 331 Prüfungen, 0 fehlgeschlagen (Test 04 mit --realtime 58, sonst 51).

**Wichtig vorab:** Echtes Hören und echte Wahrnehmung wurden nicht getestet. Kein Mensch hat die Töne gehört oder das Rauschbild gesehen. Getestet wurde, was Software prüfen kann: die erzeugten Zahlenwerte, die Rechnung, die Abläufe, die Oberfläche und die Konsole. Ob die Lücke bei einer bestimmten Hörer:in tatsächlich hörbar ist und ob der Regler im Rauschbild sinnvolle Schwierigkeiten ergibt, ist offen.

## Getestet

| Test | Gerät | Ergebnis |
|---|---|---|
| 01 Stimulus-Generator (`test_01_stimulus.py`): Lücke = genau round(ms·sr/1000) Nullwerte (min. 1) ausserhalb der Rampen, bei 44100 und 48000 Hz; Rampen 0,5 ms cos² und 10 ms Kante; Rauschen Gauss σ = 0,15 und unabhängig von der Lücke (gleicher Seed, gleiche Samples ausserhalb der Lücke); Lückenbeginn 120–220 ms; Pufferlänge 1550 ms; ein Puffer pro Durchgang; OfflineAudioContext-Rendering; keine Konsolenfehler | Desktop 1280×800, Chromium | 27 von 27 bestanden |
| 02 Adaptives Verfahren (`test_02_staircase.py`): Schrittregeln (×2 bis zur 2. Umkehr, dann ×1,25), 2-ab-1-auf, Grenzen 0,25–50 ms, 12 Umkehrungen, Schwelle = geometrisches Mittel der letzten 8, Abbruchbedingungen (Decke, Boden, 100 Durchgänge), Statuscodes. Unabhängige Python-Referenz: 1000 Läufe je Szenario in beiden Implementationen, 2500 Folgen Durchgang für Durchgang verglichen, Markov-Kette (Langzeitanteil richtig 0,706), 1000 Rate-Läufe | Desktop, Chromium + Python/numpy | 41 von 41 bestanden |
| 03 Rechnung SDT: wie zuvor, Stichprobe 20 + 20, Code v2, alte v1-Codes und v3 abgelehnt | Desktop, Chromium + scipy | 51 von 51 bestanden |
| 04 Oberfläche `schwelle.html` (`test_04_ui_schwelle.py`): Ablauf Einrichtung, Übung, Test, Ergebnis, Tastatur, Abbruch mit Bestätigung, Audio blockiert, Code erzeugen und wieder einlesen, Gruppenansicht, Diagramm, Layout ohne Querscroll, Tippflächen mindestens 44 px, Dunkelmodus; mit `--realtime` zusätzlich ein Lauf in Echtzeit mit echtem AudioContext (46 Antworten bis zum Ergebnis) | Desktop 1280×800, Handy 390×844 (Touch), 360×640, Tablet 768×1024 | 58 von 58 bestanden |
| 05 Oberfläche `signalentdeckung.html` (`test_05_ui_sdt.py`), angepasst auf 16 / 40 / 40 Durchgänge, Beispielort, Protokoll der Fleckorte, Ergebnistabelle ohne abgeschnittene Spalte: Probebild, Sperre des Reglers erst nach Probe, beide Blöcke mit Auszahlungsmatrix, Reihenfolge, Verwerfen unterbrochener Durchgänge, Ergebnistabelle, ROC-Diagramm, Kantenfälle, Code und Gruppenansicht, Layout, Dunkelmodus, Echtzeitlauf | Desktop 1280×800, Handy 390×844 (Touch), 360×640, Tablet 768×1024 | 66 von 66 bestanden |
| 06 Statisch und file:// (`test_06_static.py`): kein Eszett (`grep -rnP "\xC3\x9F"`), nur drei HTML-Seiten, keine gemeinsame JS-Datei, keine ES-Module, keine externen Anfragen, kein Speichern (localStorage, Cookies), keine Abfrage von Alter oder Geschlecht, AudioContext nur im Klick, Links der Übersicht, kompletter Durchlauf beider Seiten über `file://` | Desktop, `file://` und `http://127.0.0.1` | 31 von 31 bestanden (Code v2) |
| 07 Ort des Flecks (`test_07_position.py`): 600 Seeds x 48 Signal-Durchgänge = 28800 Positionen, nie in der Zone (kleinster Abstand 44.0 px, Zone 40), Ring, Randabstand, Gleichverteilung (Chi-Quadrat p 0.996, KS), gleiche Verteilung in Probelauf und Blöcken, gerenderte Bilder (Fleck dort, wo protokolliert, im Kreuzbereich höchstens 6 % der Amplitude), Rauschen und Maske in der Mitte unauffällig, Kreuzgeometrie, Beispielbilder | Desktop | 38 von 38 bestanden |
| 08 Dauer (`test_08_dauer.py`, mit `--full` Echtzeit): Aufgabe gemessen 231.7 s = 3.86 min (96 Durchgänge, 2.41 s je Durchgang), gesamt mit Lesezeiten 5.73 min; vorher 372 s | Desktop | 11 von 11 (--full; ohne 8 von 8) |
| 09 Präzision (`test_09_praezision.py`): Simulation 20000 Läufe je Zeile über computeSDT, Zahlen siehe README | Desktop | 12 von 12 bestanden |
| 10 Screenshots (`test_10_screenshots.py`) | Desktop, Handy | 5 von 5 bestanden |

Kennzahlen der Simulation des adaptiven Verfahrens (Beobachter mit psychometrischer Funktion): Der Mittelwert der geschätzten Schwellen liegt bei 0,935 bis 1,072 des Sollwerts für 70,7 % richtig; das arithmetische Mittel statt des geometrischen wäre rund 3 bis 4 % höher. Ein reiner Rater (immer 50 % richtig) erhält in rund 31 % der Läufe trotzdem eine Schwelle (siehe nicht Gelöstes).

## Gefundene und behobene Fehler

| # | Fehler | Behebung |
|---|---|---|
| 1 | Gruppenansicht: Eine Zeile mit mehreren unbrauchbaren Teilen erzeugte mehrere Fehlermeldungen statt einer (`parseLines`, beide Seiten) | Pro Zeile höchstens eine Meldung; Test 03 prüft es |
| 2 | Diagramm der Treppenkurve war zu schmal, weil es gezeichnet wurde, solange die Ansicht noch verborgen war | Ansicht zuerst anzeigen, dann zeichnen |
| 3 | Schwelle-Beschriftung am rechten Rand des Diagramms bei 360 px Breite abgeschnitten | Rechter Rand 58 px |
| 4 | `schwelle.html`: Abbrechen ohne Bestätigung | Zweistufig (erst scharf stellen, dann bestätigen), wie bei `signalentdeckung.html` |
| 5 | Tippflächen unter 44 px (Schaltflächen, Details-Pfeil) | Mindesthöhe 44 px |
| 6 | Gruppentabelle der Signalentdeckung bei 390 px rechts abgeschnitten | Spalten gekürzt, Tabelle passt ohne Querscroll |
| 7 | Auszahlungsmatrix: Probebild und Regler konnten nach der Sperre noch verändert werden | Sperre erst nach Probe beim aktuellen Reglerstand, danach fest |
| 9 | Ergebnistabelle Signalentdeckung auf 390 px: zweite Blockspalte abgeschnitten | Kopfzeilen zweizeilig, feste Spaltenbreiten |
| 8 | Fehler in der Testkonstruktion (nicht in den Seiten): zu langsame Übertragung grosser Arrays (jetzt Base64 Float32); falsche Erwartung zur Symmetrie; konstantes Orakel bei der Tastaturprüfung (jetzt psychometrische Funktion) | Tests angepasst |

## Nicht getestet, mit Grund

- **Echtes Hören.** Kein Mensch war beteiligt. Ob eine Lücke von 0,25 bis 50 ms bei dieser Lautstärke und mit dem jeweiligen Kopfhörer wahrnehmbar ist, ist offen. Die Lücke wurde nur als Zahlenwert im Puffer nachgewiesen.
- **Echte Wahrnehmung beim Rauschbild.** Der Reglerbereich (Amplitude 16 bis 0,5) ist an der Simulation und dem Aussehen der Screenshots orientiert, nicht an menschlichen Beobachtern. Eine Kalibrierung fehlt.
- **Kopfhörerwiedergabe, Lautstärke, Latenz echter Geräte.** Chromium im Testsystem hat kein Tonausgabegerät; der Echtzeitlauf prüft den Ablauf, nicht den Klang. Das genaue Timing der Darbietung (Rauschbild 300 ms) wurde nur über requestAnimationFrame-Zeitstempel im headless Chromium geprüft, nicht mit Hardware.
- **Safari, iOS, Firefox, echte Android-Geräte.** Nur Chromium wurde ausgeführt; Handy- und Tablet-Prüfungen sind Emulation (Viewport, Touch). Das Entsperren des AudioContext auf iOS ist eingebaut, aber ungetestet.
- **Zeitverhalten bei langsamen Geräten** (verworfene Durchgänge, Hintergrund-Tab) nur simuliert, nicht auf schwacher Hardware.
- **Eingabehilfen** (Screenreader): nicht geprüft.
- **Fachliche Wahl der Parameter** (Lückendefinition, 4:1-Auszahlung, Bedeutung von „Treffer 65–85 %“): nicht entschieden, siehe README, „Offene Fragen an den Dozenten“.

Zusätzlich nicht getestet: ob das Nachbild des neuen Kreuzes tatsächlich schwächer ist, ob der Fleck auf dem Ring für Menschen bei Reglerstellung 40 und Beispielamplitude 40 passend sichtbar ist (nur Pixelrechnung und Idealbeobachter-Modell). Die Auszahlung der Kriteriumsverschiebung (optimal/halb) ist eine Modellannahme.

## Nicht gelöst, nur dokumentiert

- Ein Rater erhält in rund 31 % der Läufe eine Schwelle, weil das Verfahren keine Zuverlässigkeitsprüfung hat. Eine Stabilitätsprüfung wurde erwogen, in der Simulation trennte sie Rater und Hörer nicht ausreichend; deshalb nicht eingebaut.
- Das Verfahren ist leicht verzerrt (siehe Kennzahlen oben).

## Screenshots (Ordner `screenshots/`)

`schwelle_setup_handy.png`, `schwelle_audio_blockiert.png`, `schwelle_ergebnis_desktop.png`, `schwelle_ergebnis_handy.png`, `schwelle_gruppe_desktop.png`, `sdt_setup_desktop.png`, `sdt_matrix_desktop.png`, `sdt_block_handy.png`, `sdt_ergebnis_desktop.png`, `sdt_ergebnis_handy.png`, `sdt_beispiel_desktop.png`, `sdt_beispiel_handy.png`, `sdt_fixation_desktop.png`, `sdt_fixation_handy.png`, `sdt_reiz_signal.png`, `sdt_ausschlusszone.png`, `sdt_gruppe_handy.png`, `sdt_kantenfall_immer_ja.png`.
Beim erneuten Ausführen der Tests können weitere Bilder in diesen Ordner geschrieben werden.
