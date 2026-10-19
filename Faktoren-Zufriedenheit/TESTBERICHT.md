# Testbericht P2 Glücksfaktoren-Spiel

Stand: 15.10.2026 (nach der Überarbeitung: verdeckte Glücksfaktoren, Kurztexte, zufällige A/B-Zuordnung). Alle Tests laufen mit `python3 -I tests/<datei>.py` (siehe README). Rohergebnisse: `tests/ergebnis_excel.txt`, `ergebnis_durchlauf.md`, `ergebnis_regeln.md`, `ergebnis_dateien.md`. Geräte sind mit Playwright (Chromium) nachgebildet, keine echten Geräte.

## Ergebnis in Kürze

* Excel-Abgleich: 456 Zufallszustände (alle 38 Zeilen, je 12), 912 exakte Rundungshälften, 228 Zustände über die Bedienoberfläche. Abweichung gegen die Neuberechnung des Original-Excel (LibreOffice) 0 bei 7296 beziehungsweise 14592 verglichenen Werten (grösste Differenz 8.9e-16); Details und die zwei Ausnahmen unten.
* 5 vollständige Durchläufe (Maus, Touch, nur Tastatur; http und file://), 60 Episoden, jede Zahl gegen eine unabhängige Dezimal-Referenz aus dem Excel: 0 Abweichungen.
* 146 Regel- und Randfall-Prüfungen, 18 Datenprüfungen: 0 Fehler. Konsole, pageerror und externe Anfragen: in allen Läufen keine.

## Überarbeitung (neu)

Rechenlogik, Gewichte, Formeln, Würfel unverändert; Excel-Abgleich nach der Überarbeitung wiederholt: 0 Abweichungen (Teil C bedient die Seite mit der jeweils angezeigten Buchstabenzuordnung). Neue Tests, alle 0 Fehler:

| Datei | Prüft | Ergebnis |
|---|---|---|
| `test_texte.py` (8) | 76 Kurztexte vorhanden, 1 bis 2 Sätze, Länge, Richtung (Erfüllung, Soziales, Lebensstil, Finanzen, Zeit, Energie, Stimmung) gegen die Dezimal-Referenz in 13 756 Zuständen über alle 38 Excel-Zeilen | OK |
| `test_glueck.py` (25) | Liste 6 bis 8 Einträge, gleich aufgebaut, Lösung vor dem Klick nicht im DOM; Freigabe nur per Knopf; Reihenfolge seed-reproduzierbar und gleichverteilt (3000 Seeds); Markieren, Neuladen, Rückgängig, Tastatur, Touch 390x844 | OK |
| `test_ab.py` (62) | Anteil vertauscht je Episode ca. 50 % (2000 Seeds, 4000 crypto-Spiele); Plan gegen unabhängige Python-Fassung; Würfelfolge zu `?seed` unverändert; 38 Fälle x 3 Modi über die Oberfläche (Karte, Regeloption, Rechnung, Verzweigung, Protokoll); Ausrichtung während des Spiels unsichtbar, im Abschluss sichtbar; Rückgängig, Neuladen in 10 Phasen, Neues Spiel, Mikroszenen, Handy | OK |
| `test_durchlauf.py` | 5 vollständige Durchläufe (Desktop, Handy, file, nur Tastatur), 4 bis 9 Episoden je Lauf mit vertauschten Buchstaben | 0 Fehler |
| `test_regeln.py` | 147 Prüfungen; dabei Kontrastfehler der Beschriftung «Glücksfaktor» (4.40) gefunden und behoben | 0 Fehler |
| `test_dateien.py` | inkl. `spiel-texte.js` (Ablenker, Ausrichtung, kein Eszett); Generator weiter byte-identisch | 0 Fehler |

Empfindlichkeit: 12 Fehler in Kopien eingebaut (Text umgekehrt, Wahl ohne Abbildung, Verzweigung nach Anzeigebuchstabe, Karten nicht getauscht, Lösung im DOM, Ausrichtung sichtbar, Plan bei Rückgängig neu gezogen, Math.random statt crypto, keine Mischung, verzerrtes A/B-Bit, falsche Ausrichtung, Tatsachenbehauptung im Ablenker): alle von den Tests gemeldet.

Neue Bilder (mit Read geprüft, `tests/mache_screenshots.py`): `*-entscheidung`, `*-ergebnis` (mit Kurztext), `*-werte-verdeckt`, `*-werte-frei`, `*-abschluss` (mit Ausrichtung), Desktop und Handy. Ältere Bilder aus früheren Läufen (360 px, Tablet, dunkel) wurden entfernt.

## Excel-Abgleich (`tests/pruefe_excel.py`, `excel_referenz.py`)

Vorgehen: Das Original-Excel wird mit zufälligen Eingaben (G bis M, Würfel O; Kanten wie ±10, 2, 4, −2, Stimmung 0 bis 100, Würfel 1 und 20) in allen 38 Zeilen gefüllt, mit LibreOffice neu berechnet (Formeln unverändert) und mit der Seite verglichen. Gelesen werden Q, S bis Y, AA bis AF, AI, AN. Zusätzlich rechnet `rechne_decimal()` jede Zeile Zelle für Zelle in exakter Dezimalarithmetik nach. Die Parameter (Soll, Änderungen, Gewichte) liest die Referenz direkt aus dem Excel, nicht aus `spiel-daten.js`.

| Test | Gerät | Ergebnis |
|---|---|---|
| A: Rechenkern im Browser gegen LibreOffice, 456 Zustände, 7296 Werte (repariertes Y3/Y40) | Chromium, http und file:// | 0 Abweichungen |
| A: gegen Original-Excel ohne Reparatur (Zeilen 3 und 40 ohne Y, T, AI) | Chromium, http | 0 Abweichungen (7224 Werte) |
| A: gegen Excel mit Summe als Addition | Chromium, http | 0 Abweichungen |
| A: gegen exakte Dezimalrechnung | Chromium, http | 1 Abweichung: Zeile 18, Resultat 0.9 statt 1.0 (exakte Hälfte, Gleitkomma entscheidet) |
| B: 912 Hälftenfälle gegen LibreOffice mit `SUM()` | Chromium | 2 Abweichungen um 0.1 (Zeile 41: 0.1 gegen 0, Zeile 8: 0.5 gegen 0.6), beide Resultate unter 1 |
| B: dieselben 912 gegen Excel mit Summe als Addition | Chromium | 0 Abweichungen |
| B: gegen Dezimalrechnung | Chromium | 4 Abweichungen um 0.1 (Hälften unter 1) |
| C: 228 Zustände über die Bedienoberfläche (Seite bedient, Zahlen aus dem DOM gelesen: Resultat, Stimmung, Werte danach) | Desktop 1280x800 | 0 Abweichungen, 3876 Zahlen |
| Zeilen 3 und 40 (Y fehlt): Original ergibt AI = AW − 4 | LibreOffice | 24 von 24 Zuständen, Befund dokumentiert |

Einordnung: Excel und LibreOffice runden den auf 15 Stellen gerundeten Wert (`xlRound` in `spiel-kern.js`). Die Hälfte aller Zustände sind exakte Hälften, weil alle Beiträge Vielfache von 0.05 sind. Das Ergebnis hängt dort von der Summationsreihenfolge ab; LibreOffice summiert `SUM()` anders als links nach rechts. Microsoft Excel stand nicht zur Verfügung (siehe «Nicht getestet»).

## Vollständige Durchläufe (`tests/test_durchlauf.py`)

Je Episode: Titel, Fortschritt, Werte nach der Beginn-Änderung, Wurf, Resultat, Soll, Wirkung je Attribut, Stimmung, «Nachher» je Attribut und die Kacheln unter «Werte danach» gegen die Referenz; Verzweigung gegen die Tabelle aus dem Word; Abschluss (Diagramm, 12 Zeilen Verlauf, Endwerte, kein horizontaler Scroll).

| Test | Gerät | Ergebnis |
|---|---|---|
| R1 BWL, Berater, Krise 12A1; Mikroszenen M2 und M7 aus der Liste eingeschoben | Desktop 1280x800, Maus, http | OK |
| R2 Psychologie, Jugend, Krise 12A2; M4 eingeschoben; abwechselnd virtueller Wurf | Phone 390x844, Touch, http | OK |
| R3 Psychologie, Berater, Krise 12B1 | Desktop, Maus, file:// | OK |
| R4 BWL, Jugend, Krise 12B2 | Phone 390x844, Touch, file:// | OK |
| R5 Psychologie, Berater, Krise 12B2, nur Tab/Enter/Tastatur, ohne Maus | Desktop | OK |

Damit sind beide Studienwege, beide Jobwege und alle vier Krisen gespielt; Mikroszenen mit anschliessender regulärer Fortsetzung in R1 und R2.

## Regel- und Randfälle (`tests/test_regeln.py`, 146 Prüfungen)

| Test | Gerät | Ergebnis |
|---|---|---|
| Virtueller W20: nur 1 bis 20, 1 und 20 treten auf, Chi-Quadrat 12.1 (Grenze 43.8) bei 20 000 Würfen; mit Seed 11.4 | Desktop | OK |
| `?seed=`: gleiche Folge in zwei Sitzungen, anderer Seed andere Folge; Taste W würfelt | Desktop | OK |
| Eigener Würfel: Ablehnung von «», 0, 21, 3.5, abc, 1e1, −3, 100, Leerzeichen, 7a, arabische Ziffer; Annahme von 1, 20, 07, « 7 », 13 | Desktop | OK |
| Wurf 1 und Wurf 20 in vier Zeilen (Ep 1, 5B, 12A1, 12B2) gegen Referenz | Desktop | OK |
| Alle Attribute −10 und Wurf 1: Resultat negativ wird 0, Hinweis sichtbar | Desktop | OK |
| Alle Attribute +10, Wurf 20: Resultat 47.2 (Sättigung) | Desktop | OK |
| Stimmung nach der Episode genau 0 und 1 (läuft weiter), genau −1 (Spielende-Angebot mit beiden Wegen) | Desktop | OK |
| Finanzen −2 (kein Zeitabzug) und −3 (Zeit −1) | Desktop | OK |
| 76 Zufallszustände über alle 38 Zeilen über die Oberfläche gegen die Referenz | Desktop | OK |
| Schranken aus (Standard): Soz 10+1 = 11, Erfüllung −10−1 = −11, Stimmung 106; mit `?schranken=1`: 10, −10, 100 und Hinweis «begrenzt» | Desktop | OK |
| Rückgängig: 7 Schritte vor und 7 zurück, jeder Zwischenzustand identisch; am Anfang gesperrt; Strg+Z; über Mikroszene; aus dem Abschluss | Desktop | OK |
| Mikroszenen-Vorschlag bei Zeit, Energie, Soz, Erfüllung, Lebensstil und Normalwerten; Schwellen exakt (−5 und −5.5, 0 und −0.5); nie automatisch | Desktop | OK |
| Mikroszene einschieben: Deltas exakt, Stimmung unverändert, danach Episode 4 mit Beginn +3/+3; gespielte Szene gesperrt; alle 10 Szenen mit Option A und B gegen die Daten | Desktop | OK |
| Spielende nach Episode und zu Beginn von Ep 12 (Stimmung 10 gibt 0, läuft; 9 gibt −1, Spielende); beide Wege; Rettungsauswahl M1, M3, M5, M10 zuerst; letzte Episode ohne Rettung | Desktop | OK |
| Neu laden stellt Spielstand und Rückgängig-Tiefe wieder her; `?neu=1`; `sessionStorage` und `localStorage` blockiert; Neues Spiel mit Rückfrage | Desktop, Phone 390 | OK |
| Sichtbarer Fokus (Outline 3 px); Tasten A und B | Desktop | OK |
| 11 Ansichten je Gerät und Farbschema: kein horizontaler Scroll, Bedienelemente mindestens 44x44 px, nichts über dem Rand, Textkontrast AA (4.5, gross 3) gemessen aus den berechneten Farben | 360x740, 390x844, Tablet 768x1024, Desktop 1280x800; hell und dunkel | OK |
| `prefers-reduced-motion`: keine Animationen oder Übergänge | alle vier Grössen | OK |

Empfindlichkeitsprüfung der Tests: In vier Kopien des Projekts wurde je ein Fehler eingebaut (Zeitabzug 2 statt 1, Sättigung ab 3, Mikroszenen-Schwelle −4, Spielende bei Stimmung ≤ 0). `test_regeln.py` meldete in jedem Fall mindestens eine fehlgeschlagene Prüfung.

## Daten (`tests/test_dateien.py`, 18 Prüfungen)

19 Episoden und 38 Optionen, 10 Mikroszenen; das Word wird unabhängig neu gelesen und mit den Daten verglichen (Titel, Vorlesetexte, Optionen, Unmittelbare Folge, Würfeltitel, «Weiter bei», Glücksfaktoren, Erkenntnisse, Mikroszenen mit Wertänderungen); Excel-Konstanten (Soll, Änderungen, Energie-Basis, Beginn-Änderungen, Gewichte) gegen die Daten; 4096 mögliche Wege, alle genau 12 Episoden lang; Generator erzeugt `spiel-daten.js` byte-identisch; Gesamtgrösse 100 KB; keine externen Adressen; kein ES-Modul, kein fetch; relative Pfade; `lang="de"`; kein Eszett (auch `grep -rInP "\xC3\x9F"` über den Ordner ist leer); keine «Pädagogische Kernidee», kein «Mini-Debriefing», keine «Wissenschaftliche Basis». Ergebnis: 0 Fehler.

## Gefundene und behobene Fehler

1. Die Rückfrage «Neues Spiel» war immer sichtbar (`display:flex` überschrieb `hidden`). Behoben mit `[hidden]{display:none!important}`.
2. Beschriftung «GEWÄHLTB · …» ohne Abstand. Behoben (Etikett als Block).
3. Gerade Anführungszeichen im Word kamen unverändert durch. Generator wandelt Paare in «„…“» um.
4. Eine Summe nach Kahan (zum Angleichen an LibreOffice) wurde ausprobiert und verworfen: LibreOffice summiert weder naiv noch nach Kahan; die sequentielle Variante gleicht 0 Abweichungen aus.
5. Rettungspfad: Nach «Rettungs-Mikroszene» zeigte die nächste Episode sofort wieder das Spielende (Stimmung bleibt unter 0). Behoben: Die Fachperson führt das Spiel nach der Rettung fort (`betreteEpisode(id, trotzdem)`).
6. Diagramm: Der letzte Stimmungswert war am rechten Rand abgeschnitten. Behoben (Beschriftung rechtsbündig, Kontur).
7. Kopfzeile auf 360 px: «Neues Spiel» brach um und der Titel stiess an die Knöpfe. Behoben (kleinere Schrift und Polster; unter 340 px umbrechende Kopfzeile).
8. Testwerkzeuge: LibreOffice-Ausgabeordner fehlte; Gliederung des Word-Parsers (Blockzeilen, Doppelpunkt oder Gedankenstrich im Episodentitel). Betrifft nur Tests.

## Nicht getestet

* Microsoft Excel selbst (nicht verfügbar). Stellvertreter ist LibreOffice; die Summationsreihenfolge von Excel ist eine Annahme (README, Hinweis 10).
* Echte Geräte, Safari, Firefox, Bildschirmleser, Druckansicht. Handy und Tablet sind Emulationen (Viewport, Touch, mobiles Profil) in Chromium.
* Veröffentlichung auf GitHub Pages: nur lokaler Server und `file://` geprüft; die relative Einbindung `../shared/base.css` hängt vom gemeinsamen Repository-Aufbau ab.
* Wiederholte Durchläufe mit zufälligen virtuellen Würfen über sehr viele Spiele (nur R2 mit zufälligen Würfen, plus 20 000 Würfe auf Gleichverteilung).

## Screenshots (`screenshots/`, mit Read angesehen)

Je Desktop (1280 px, `desktop-*`) und Handy (390 px, Touch, `phone-*`): `entscheidung`, `wurf`, `ergebnis` (mit Kurztext), `werte-verdeckt` (Auswahlliste, zwei Einträge markiert), `werte-frei` (Lösung freigegeben), `mikro-wahl`, `abschluss` (mit Ausrichtung). Lange Ansichten sind bei vergrössertem Fenster aufgenommen, damit die Aktionsleiste unten sitzt wie im Spiel.

## Zuordnung Excel-Zelle zu Funktion

Datei `spiel-kern.js` (Kopfkommentar), Zeile r des Excel:

| Excel | Formel | Funktion / Feld |
|---|---|---|
| AA, AB, AF (Zeit, Energie, Finanzen) | `=IF(G>2, w*2, IF(G>4, w*3, G*w))` | `beitragMitSaettigung()` mit `konfig.saettigungExcel` |
| AC, AD, AE (Soz, Erfüllung, Lebensstil) | `=w*Wert` | `beitragMitSaettigung()` ohne Stufen |
| Q Resultat | `=IF(ROUND(2*SUM(AA:AF)+O,1)<0, 0, ROUND(…,1))` | `rechne().resultat` (Summe sequentiell, `xlRound`) |
| AN | `=ROUND(8*(Q-P)/10, 0)` | `rechne().stimmungsaenderung` |
| Y | `=M+AN` | `rechne().stimmungNachher` (Y3 und Y40 im Excel leer) |
| AI | `=AW+ROUND(8*(Y-50)/50,0)/2` | `rechne().energieAenderung` |
| S | `=IF(L<-2, G+AH-1, G+AH)` | `rechne().nachher.zeit`, `zeitAbzug` |
| T bis X | `=H+AI`, `I+AJ`, `J+AK`, `K+AL`, `L+AM` | `rechne().nachher` |
| G bis M, O, P | Werte vor der Entscheidung, Würfel, Soll | `vorher`, `wurf`, `optionen.X.soll` |
| C, D, E | Änderungen zu Beginn | `beginn()` und `episoden[].beginn` |
| AH, AJ bis AM, AW | Änderungen und Energie-Basis je Option | `optionen.X.aenderung`, `energieBasis` |
| AP bis AU | Gewichte | `konfig.gewichte` |
