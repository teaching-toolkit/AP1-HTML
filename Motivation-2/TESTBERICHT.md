# Testbericht P1 (GoFundMe-Simulation, Pfeil-Experiment)

Stand: 13.10.2026. Werkzeug: Playwright für Python, Chromium (headless). Jedes Testskript startet einen eigenen lokalen Server (`127.0.0.1`), prüft zusätzlich `file://` und wird mit `python3 -I tests/<datei>.py` gestartet. Letzter Lauf: alle vier Skripte grün.

| Skript | Prüfungen | Ergebnis |
|---|---|---|
| `tests/test_gofundme_ui.py` | 86 | 86 bestanden |
| `tests/test_gofundme_calc.py` | 34 | 34 bestanden |
| `tests/test_gofundme_layout.py` | 17 | 17 bestanden |
| `tests/test_mere_exposure.py` | 79 (dreimal wiederholt) | 79 bestanden |
| Summe | 216 | 216 bestanden |

## Was getestet wurde

| Test | Gerät | Ergebnis |
|---|---|---|
| Vollständiger Durchlauf bis Auswertung (Klick/Tipp) | Desktop 1280, Handy 360 und 390 (Touch), `file://` | bestanden |
| Kein Konsolenfehler, kein `pageerror`, keine fehlgeschlagene und keine externe Anfrage | alle Läufe beider Seiten | bestanden |
| Kein horizontaler Seitenüberlauf, alle Bildschirme | 360, 390, 768, 1280 px | bestanden |
| Klickflächen mindestens 44 × 44 px, alle Bildschirme (GoFundMe) | 360, 390, 768, 1280 px | bestanden (nach Korrektur, siehe unten) |
| Pfeil-Experiment: Knöpfe mindestens 44 px, Teil 1 ohne Scrollen | 360 × 640 hoch, 844 × 390 quer | bestanden |
| Reine Tastaturbedienung GoFundMe (Regler per Pfeil, Skalen per Pfeil/Leertaste, Enter) | Desktop | bestanden |
| Reine Tastaturbedienung Pfeil-Experiment (← →, Ziffern 1-7), Auto-Repeat zählt einmal | Desktop, `file://` | bestanden |
| Sichtbarer Fokus, Dunkelmodus (dunkler Hintergrund, Durchlauf ohne Überlauf) | Handy 390 | bestanden |
| Randfall GoFundMe: Wohnort zuletzt ohne Regler (Fehler `btn-show_results` im Original) | Desktop | bestanden, Auswertung wird frei |
| Nur ein Profil bedacht; alle 0 (Weiter gesperrt); Summe 600 (Warnung, gesperrt, Rest −100); Summe 500; Regler-Schritt 10; −/+ Knöpfe | Desktop | bestanden |
| Alle Spenden gleich: «nicht berechenbar» bei den drei r mit Spende, viertes r berechenbar | Desktop | bestanden |
| Zurück-Navigation (Knopf, Browser zurück/vor) behält Eingaben; Neu laden auf `#results` führt zum Start; `#gruppe` direkt und per Hash-Wechsel | Desktop | bestanden |
| Neustart setzt alles zurück (alle Spenden 0, keine Auswahl angekreuzt) | Desktop | bestanden (Fehler gefunden und behoben) |
| Eigenschaftsähnlichkeit: 30 Personen × 6 Profile = 180 Werte gegen unabhängige Python-Referenz (`Fraction`, Profildaten aus der Originaldatei gelesen) | Desktop | 0 Abweichungen |
| r: 4 Zusammenhänge × 30 Personen = 120 Werte gegen `numpy.corrcoef`, Toleranz 1e-9, davon 6 nicht berechenbare Fälle | Desktop | 0 Abweichungen |
| Ergebnis-Code der Seite = Python-Encoder (30 Personen, exakt inkl. Prüfsumme) | Desktop | 0 Abweichungen |
| Code-Rundreise: 6 von der Seite erzeugte Codes in «Gruppe auswerten» einlesen, Summe und r je Person gleich | Desktop | bestanden |
| Gruppe mit 40 Python-Codes: r je Person (120 Werte), r über 240 Punkte (3), Mittel der r (3), Profilmittel (24), 240 Punkte im Diagramm, Personen als 32 Farbe-Form-Kombinationen unterscheidbar (5 Personen: 5 verschiedene) | Desktop | bestanden |
| Gruppen-Randfälle: 3 gültige, 6 ungültige Zeilen mit Grund (Prüfsumme, andere Seite, andere Version, Summe über 500, keine Spende, kein Code), 1 Duplikat in anderer Schreibweise, Leerzeilen, nur ungültig, leer, HTML in Zeile (kein XSS) | Desktop | bestanden |
| Pfeil-Experiment `?dauer=5`: Teil 1 endet nach 4.5-8.5 s; 10 Bewertungen lückenlos und verschieden, 4 häufige + 6 seltene | Handy Touch 390/360, Desktop Maus, Tastatur, `file://` (je ein Lauf) | bestanden |
| Echter Lauf mit Standarddauer: Teil 1 endet nach 120.4 s (156 Antworten) | Handy 390 Touch, `file://` | bestanden (von Hand gestartetes Einzelskript, nicht im Testordner) |
| Mittel häufig/selten/Differenz, Trefferzahl und Code gegen Referenz | 5 Läufe | 0 Abweichungen |
| 200 Durchläufe: 4 verschiedene häufige Gesichter, nie [1,2,3,4], gleichmässig (χ² = 30.4, 48 Freiheitsgrade, p = 0.98, Häufigkeit je Gesicht 9-24, erwartet 16.3, alle 49 kamen vor) | Hook `pickFrequent` | bestanden |
| 40 Seitenladungen ohne Seed: verschiedene häufige Gesichter | Desktop | mehr als 30 verschiedene Kombinationen (Prüfschwelle) |
| Gewichtung über 4000 Darbietungen: Anteil häufiger Gesichter 44.2 % (Soll 47 %, Toleranz 3 %); Faktor je Gesicht 8.9 (Soll etwa 10, siehe README Hinweis 4) | Desktop | bestanden mit Dokumentation |
| Kein Gesicht direkt zweimal hintereinander (500 Durchgänge); Spiegelung 299/600, Pfeil links 298/600 | Desktop | bestanden |
| Doppeltippen in der Bewertung zählt einmal; «Vorheriges Gesicht» | Handy 390 | bestanden |
| Gruppenansicht Pfeil-Experiment: 4 gültige, 6 ungültige, 1 Duplikat; Gruppenmittel, Differenzen, Anzahl positiv/negativ, Differenz genau 0, 4 Balken | Handy 390 | bestanden |
| Dateigrössen: 49 Gesichter höchstens 29.7 KB (Summe 904 KB), 6 Profilbilder 59-103 KB | – | bestanden |
| Eszett-Prüfung `grep -rIP "\xC3\x9F"` über den Projektordner | – | leer |
| Keine `http(s)://`-Verweise ausser dem SVG-Namensraum `xmlns` | – | bestanden |
| Anrede «du», kein «Sie» im Pfeil-Experiment | Desktop | bestanden |

**Beobachtung zu den seltenen Gesichtern** (je 60 Läufe, Zufallsauswahl wie die Seite): bei 60 / 100 / 150 Durchgängen waren 54 % / 72 % / 86 % der bewerteten seltenen Gesichter vorher mindestens einmal gezeigt worden.

## Gefundene und behobene Fehler
1. «Nochmal starten» (GoFundMe) liess Geschlecht und Wohnort angekreuzt, obwohl der Zustand leer war: «Auswertung anzeigen» blieb gesperrt. Gefunden vom Rechentest, behoben (Radios werden zurückgesetzt), durch Layouttest abgesichert.
2. Die 10er-Skala (Sympathie, Ähnlichkeit) hatte auf Desktop und Tablet nur 33-43 px breite Felder. Jetzt 5 × 2 Felder (bei 561-699 px einzeilig).
3. Der Ergebnis-Code-Kasten war 39.6 px hoch (Tipp-Ziel); jetzt mindestens 44 px.
4. Direktaufruf von `#gruppe` in einer bereits geöffneten Seite zeigte nichts: `hashchange` wird jetzt behandelt.
5. Beim Zeichnen lagen Punktbeschriftungen auf dem unteren Diagrammrand; Beschriftungen bleiben jetzt im Diagramm.
6. In der gestapelten Tabelle (Handy) stand das Farbsymbol getrennt vom Personennamen; leere Zellen erzeugten leere Zeilen. Beides behoben.
7. Testskripte: zwei Wettlauf-Fehler im Test selbst (Taste nach Ende von Teil 1, Variable `t0` überschrieben) behoben. Keine Fehler der Seite.

## Nicht getestet
- **Echte Geräte** (iOS Safari, Android Chrome, Firefox). Getestet ist Chromium mit Touch-Emulation. Echte Fingerführung bei den Reglern, die Zurück-Geste von iOS und die Bildschirmtastatur sind nicht geprüft.
- **Zwischenablage-Knopf** mit echter Erlaubnis; geprüft ist nur, dass er ohne Fehler läuft (Ersatzweg `execCommand`/manuelle Auswahl).
- **Screenreader**; geprüft sind nur Semantik (Radiogruppen, Beschriftungen, `role="img"` mit Text) und Tastatur.
- **Kontrast** nicht messtechnisch; es werden die Farben aus `shared/base.css` verwendet.
- **Wirkung der geänderten Nebenaufgabe** auf den Mere-Exposure-Effekt (fachlich, siehe README).
- **Ablaufzeit mit Studierenden**: Durchlaufdauer GoFundMe nicht gemessen.

## Screenshots (screenshots/, JPEG, klein)
`gofundme_handy360_2b_budget_warnung.jpg`, `gofundme_handy360_3_sympathie.jpg`, `gofundme_handy360_4_selbst.jpg`, `gofundme_handy360_5_auswertung.jpg`, `gofundme_handy360_6_gruppe.jpg`, `gofundme_desktop_2_budget.jpg`, `gofundme_desktop_5_auswertung.jpg`, `gofundme_dunkel_5_auswertung.jpg`, `mere_handy390_1_teil1.jpg`, `mere_handy390_1b_teil2.jpg`, `mere_handy390_1c_bewertung.jpg`, `mere_handy390_2_aufloesung.jpg`, `mere_handy390_3_gruppe.jpg`, `mere_handy_quer_teil1.jpg`. Alle wurden angesehen; die behobenen Layoutfehler stehen oben.
