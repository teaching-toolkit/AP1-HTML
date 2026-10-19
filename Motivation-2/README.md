# P1 Motivation 2: GoFundMe-Simulation und Pfeil-Experiment (Mere Exposure)

Zwei statische HTML5-Seiten für Aktivität 1 «Ähnlichkeit, Altruismus und Mere Exposure Effect» (Allgemeine Psychologie 1, HSLU). Sie ersetzen die zwei Dateien, die bisher «per Mail» verschickt wurden. Kein Build, keine Bibliothek, kein CDN, keine Schrift von aussen, keine Netzwerkanfrage zur Laufzeit. Es verlässt nichts das Gerät. Es werden weder Cookies noch `localStorage` noch `sessionStorage` verwendet.

```
p1-motivation2/
  gofundme/index.html        + assets/ (6 JPEG, 640 px, 59-103 KB)
  mere-exposure/index.html   + assets/ (49 WebP, 325 px, je höchstens 29 KB)
  tests/  screenshots/  README.md  TESTBERICHT.md
```
Beide Seiten binden `../../shared/base.css` ein. Beim Ausliefern muss `shared/` neben `p1-motivation2/` liegen. Alle Pfade sind relativ, die Seiten laufen über `https://` (GitHub Pages) und über `file://`. `tests/` und `screenshots/` müssen nicht ins Repo.

Link-Struktur (GitHub Pages): `…/p1-motivation2/gofundme/` und `…/p1-motivation2/mere-exposure/`.

## Bedienung für Teilnehmende
Seite öffnen, durchklicken. Die Reihenfolge im Unterricht (zuerst die eine, dann die andere Seite, danach erst erklären) ist unverändert. Beide Seiten erklären nichts vorab.

**GoFundMe-Simulation.** Schritt 1: 500 CHF auf 6 Profile verteilen (Regler oder Knöpfe − / +, Schritte von 10; es muss nicht alles verteilt werden; mindestens ein Betrag grösser 0; über 500 gibt eine Warnung und sperrt «Weiter»; der Rest steht als «Nicht verteilt»). Schritt 2: Sympathie 1-10. Schritt 3: subjektive Ähnlichkeit 1-10. Schritt 4: Selbstangaben (Geschlecht, Politik 1-7, Wohnort, Extraversion 1-7, Erregungssuche 1-7). Danach die Auswertung (drei Streudiagramme, r, Tabellen «Deine Angaben je Profil» und «Profilmerkmale», Ergebnis-Code). Die Skalen haben bewusst keinen Vorgabewert (im Original war überall 5 bzw. 4 voreingestellt und zählte als Antwort). Die Zurück-Knöpfe und die Zurück-Taste des Browsers (auch Android) behalten die Eingaben.

**Pfeil-Experiment.** Teil 1 (120 s): Gesichter mit Pfeil darüber, Aufgabe «In welche Richtung zeigt der Pfeil?» mit zwei grossen Knöpfen links/rechts oder den Pfeiltasten. Teil 2: 10 Gesichter auf einer Skala 1-7 bewerten (Tippen, Zifferntasten 1-7, «Vorheriges Gesicht»). Danach «Auflösung» mit Mittelwerten, Differenz, allen 10 Bewertungen, Trefferquote der Pfeil-Aufgabe und Ergebnis-Code. Die Bilder werden beim Öffnen vorgeladen (Fortschrittsanzeige), «Experiment starten» ist erst danach aktiv.

## Gruppe auswerten (beide Seiten)
Am Ende steht ein **Ergebnis-Code** (mit Kopieren-Knopf). Auf der Startseite und der Auswertung gibt es «Gruppe auswerten» (auch direkt über `…/#gruppe`): ein Code pro Zeile einfügen, «Auswerten». Leerzeilen und Duplikate werden ignoriert, ungültige Zeilen mit Zeilennummer und Grund genannt (falsche Prüfsumme, andere Seite, andere Version, Werte ausser Bereich, kein Code). Codes enthalten nur Ergebnisse, keine Namen und keine Freitexte; sie enthalten eine zufällige 3-stellige Kennung, damit zwei Personen mit gleichen Antworten nicht als Duplikat gelten.
- GoFundMe: Tabelle r je Person, r «Alle Punkte» (Personen × 6 Profile), Mittel der r je Person, drei gemeinsame Streudiagramme (Person = Farbe × Form, Legende), Mittelwerte je Profil.
- Pfeil-Experiment: Gruppenmittel häufig/selten, mittlere Differenz, Anzahl Personen mit positiver / negativer / gleicher Differenz, Balkendiagramm der Differenzen, Tabelle je Person.

Codeformat (Version v1, alles Kleinbuchstaben und Ziffern, Prüfsumme `h = (h*31 + Zeichencode) mod 1296`, Start `h = 7`, 2 Zeichen Base36, über den Teil zwischen Version und Prüfsumme):
- `HSLU-gofundme-v1.<kennung:3>.<spenden:12>.<sympathie:6>.<ähnlichkeit:6>.<selbst:5>.<prüfsumme:2>`; Spenden je 2 Zeichen Base36 von Betrag/10; Skalen 1-10 als Base36-Zeichen (10 = `a`); Selbst = Geschlecht (m/f/n), Politik, Wohnort (u/s/r), Extraversion, Erregungssuche. **Die Reihenfolge der Profile ist Teil des Codes** (Alex, Mia, Jamie, Lukas, Sara, Thomas). Wer Profile ändert, erhöht die Version.
- `HSLU-mere-v1.<kennung:3>.<häufig:4>.<selten:6>.<durchgänge:3>.<treffer:3>.<prüfsumme:2>`; Bewertungen als Ziffern 1-7 in Bewertungsreihenfolge, Durchgänge und Treffer Base36.

## Parameter und Testhaken für Fachpersonen
| Seite | Parameter | Wirkung |
|---|---|---|
| Pfeil-Experiment | `?dauer=10` | Dauer von Teil 1 in Sekunden (1-600, Standard 120) |
| Pfeil-Experiment | `?seed=42` | reproduzierbarer Zufall (Gesichter, Reihenfolge, Pfeil, Spiegelung, Kennung) |
| beide | `#gruppe` | öffnet direkt «Gruppe auswerten» |

Testhaken im Pfeil-Experiment: `window.__mere` (`pickFrequent`, `mulberry32`, `getRun()`, `config`); wird von `tests/test_mere_exposure.py` genutzt und beeinflusst nichts.

## Inhalte ändern
- **GoFundMe:** Array `PROFILES` im Skript (Name, Alter, Ort, Post, Hashtags, Bild und die versteckten Merkmale `gender`, `politics`, `residence`, `extraversion`, `sensation`). `BUDGET = 500`, `STEP = 10`. Die Eigenschaftsähnlichkeit steht in `similarityPct` (ganzzahlig in Sechsteln gerechnet, Ergebnis identisch mit dem Original).
- **Pfeil-Experiment:** Konstanten oben im Skript: `N_FREQUENT = 4`, `N_RARE_RATED = 6`, `FREQUENT_WEIGHT = 10`, `DEFAULT_DURATION_S = 120`, `ONLY_SEEN_RARE`. Neue Bilder: `assets/1.webp` bis `49.webp` (325 px) ersetzen, bei anderer Anzahl `TOTAL_IMAGES` anpassen.

## Was gegenüber den Originalen geändert wurde
**GoFundMe:** Fehler `btn-show_results` behoben, eine Funktion `updateUi()` steuert alle «Weiter»-Knöpfe nach jeder Eingabe. Chart.js ersetzt durch eigene SVG-Diagramme (Achsen, Namen an den Punkten, Tabelle als Alternative). Einspaltig unter 700 px, Bilder `max-width: 100%`, 360 px getestet. Bilder: 1024 px / ca. 0.9 MB auf 640 px / 59-103 KB (Dateinamen gleich). Titel «GoFundMe-Simulation», durchgehend «du». Auswertung mit Tabelle «Profilmerkmale» und Erklärung der Berechnung; neutrale Deutung ohne Schwellenwörter, Hinweis «nur ein Diskussionsanstoss», «nicht berechenbar» bei konstanten Werten (der Text steht nur noch an der Stelle, wo es zutrifft). Budget wie verlangt. Skalen ohne Vorgabewert (siehe oben). Sticky-Anzeige «Nicht verteilt».
**Pfeil-Experiment:** Touch-Knöpfe zusätzlich zu den Pfeiltasten (Auto-Repeat der Taste wird ignoriert). Die 4 häufigen Gesichter werden pro Durchlauf zufällig aus 49 gezogen (Faktor 10, 6 seltene zur Bewertung, Bewertungsreihenfolge gemischt, kein Gesicht zweimal direkt hintereinander wie im Original). **Nebenaufgabe geändert:** statt «Blickrichtung des Gesichts» jetzt «Richtung des Pfeils», das Gesicht ist zufällig gespiegelt und für die Aufgabe irrelevant. Trefferquote wird erfasst und angezeigt. Bilder PNG 200 KB auf WebP höchstens 29 KB, Vorladen mit Fortschritt. Zwischenbildschirm vor Teil 2 (verhindert, dass ein letzter Tipp aus Teil 1 eine Bewertung auslöst). Text «Sie» auf «du»; die Auflösung nennt nur den Begriff und das Design, die Erklärung und die Interpretation («wäre ein Beispiel für…») sind entfernt, ebenso «der vorhin gezeigten Gesichter» (stimmt für seltene Gesichter nicht immer).

## Bekannte Grenzen
- Mit Pointer/Tippen am Handy kann man bei GoFundMe die Slider nur grob ziehen; die Knöpfe − / + und die Tastatur geben genaue Schritte.
- Zustand liegt nur im Speicher: Neu laden oder Tab schliessen verwirft die Eingaben (Ergebnis-Code vorher kopieren). Beim Pfeil-Experiment gibt es keinen Verlaufs-Schutz: die Zurück-Geste des Handys verlässt die Seite.
- Eine Person mit identischen Antworten und identischer Kennung zählt als Duplikat (Wahrscheinlichkeit sehr klein).
- `navigator.clipboard` ist nicht in jedem Kontext erlaubt; es gibt einen Ersatz (`execCommand`) und sonst den Hinweis, den Code von Hand zu markieren (Tipp auf den Code markiert ihn).
- WebP wird von allen aktuellen Browsern unterstützt (Safari ab 14).
- Wunsch an `shared/base.css`: keiner. Lokales CSS ergänzt `[hidden]`, Skalen-Knöpfe und Tabellen.

## Fachliche Hinweise zur Prüfung
1. **Bilder (KI-generiert).** Alle 6 Profilbilder und die 49 Gesichter sind KI-generiert (nicht verändert). Auf **«alex»** hängen Plakate mit politischen Parolen («NO BORDERS», «SOLIDARITY…», Faust, Friedenstaube): sie verstärken die politische Zuschreibung und sind ein zusätzlicher, nicht kontrollierter Reiz. Auf **«mia»** steht verzerrter Text auf dem Shirt (lesbar als «HEIMET»). Vorschlag: im Unterricht kurz erwähnen oder die Bilder später ersetzen.
2. **Nebenaufgabe (Mere Exposure).** Das Original verlangte die Blickrichtung des Gesichts. Bei den Fantasy-Porträts ist sie nicht eindeutig und wurde nie geprüft. Neu: Pfeilrichtung (eindeutig). Der Aufmerksamkeitsfokus liegt damit auf dem Pfeil statt auf dem Gesicht. Ob der Effekt dadurch anders ausfällt, ist offen; die Dokumentenaussage «selbst wenn sie bewusst auf etwas anderes achten» bleibt aber sinnvoll.
3. **Seltene Gesichter müssen nicht gesehen worden sein.** Wie im Original werden die 6 seltenen Gesichter der Bewertung zufällig aus den 45 seltenen gezogen, auch wenn sie in Teil 1 nie erschienen. Gemessen (je 60 Läufe): bei 60 / 100 / 150 Durchgängen waren 54 % / 72 % / 86 % der bewerteten seltenen Gesichter vorher mindestens einmal zu sehen. Ein realer Lauf (120 s, 700 ms pro Antwort) hatte 156 Durchgänge. Der Vergleich ist also «sehr oft gesehen» gegen «selten oder nie gesehen». Umschalter `ONLY_SEEN_RARE = true` zieht nur gezeigte Gesichter (die Seite zeigt je Bild «Anzahl Darbietungen» in der Auflösung).
4. **Faktor 10.** Wegen der Regel «kein Gesicht direkt zweimal hintereinander» (wie im Original) kommt ein häufiges Gesicht im Mittel etwa 9 mal so oft vor wie ein seltenes (gemessen 8.9 bei 4000 Durchgängen; Anteil häufiger Gesichter 44 % statt 47 %). Die Auflösung sagt «etwa zehnmal».
5. **Verrauscht.** 4 gegen 6 Bewertungen ergeben auf Personenebene oft das «falsche» Vorzeichen. Das Dokument (Musterlösung) formuliert vorsichtig («ev. höhere Sympathie»); die Gruppenansicht ist deshalb sinnvoll. Der Satz «Dieser alte Mechanismus funktioniert immer noch, auch bei Bruchteil-Sekunden-Expositionen» (Musterlösung) passt nicht zu diesem Experiment (Gesichter bis zur Antwort sichtbar, 120 s).
6. **Musterlösung GoFundMe** («Die Korrelation… zeigt sich in der Realität immer wieder», «Die Verteilung folgt systematisch der Ähnlichkeit»): mit 6 erfundenen Profilen und einer selbst gebauten Ähnlichkeitsformel ist das keine Replikation. Die Seite sagt das nicht, zeigt aber den Hinweis auf die Instabilität. Die Eigenschaftsähnlichkeit gewichtet alle fünf Merkmale gleich und ist ein Entscheid des Original-Codes, nicht empirisch begründet.
7. **Zwei Ähnlichkeiten.** «Subjektive Ähnlichkeit» (Frage «ähnlich/vertraut») mischt zwei Begriffe. Unverändert übernommen.
8. **Zeilen 55, 99 und 113 des Auftrags** nennen «beide Dateien»: im Dokument besser durch die zwei Links ersetzen.

## Offene Fragen an den Dozenten
- Soll der Ordnername `mere-exposure/` im Link stehen? Er verrät den Begriff vor der Durchführung (Seitentitel und Text sagen «Pfeil-Experiment»). Alternative: neutraler Ordner `pfeil/`.
- `ONLY_SEEN_RARE` (siehe Hinweis 3) und die Nebenaufgabe (Hinweis 2) bestätigen oder zurücknehmen.
- Geschlecht: gibt es eine Option «keine Angabe»? Aktuell Pflichtfeld wie im Original (Mann, Frau, Non-binär / Divers).
- Soll die Auflösung beim Pfeil-Experiment den Begriff «Mere-Exposure-Effekt» überhaupt nennen, oder erst die Fachperson?
- Alex- und Mia-Bild beibehalten (Hinweis 1)?
