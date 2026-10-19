# P5: Schwellentest (Lückenerkennung) und Signalentdeckung

Zwei statische HTML5-Seiten für Allgemeine Psychologie 1 (HSLU), Aktivität 1 «Schwellen erleben» (Auftrag Aufmerksamkeit und Psychophysik). Sie ersetzen den Padova-Hörtest und machen Sensitivität, Kriterium und ROC erlebbar. Kein Build, keine Bibliotheken, keine Netzwerkanfragen, keine Cookies, kein Speicher. Es werden keine Daten (Alter, Geschlecht o. Ä.) abgefragt.

| Datei | Inhalt |
|---|---|
| `index.html` | Übersicht mit zwei Kacheln (Beschreibung, geschätzte Dauer, Link «Gruppe auswerten») |
| `schwelle.html` | Lückenerkennung, Web Audio, 2AFC, 2-down-1-up |
| `signalentdeckung.html` | Ja/Nein-Detektion im Rauschbild, zwei Blöcke mit Auszahlungsmatrix |
| `tests/`, `screenshots/` | Testskripte und Bilder (nicht fürs Repo nötig) |

Je Seite ein eigenes, inline eingebettetes klassisches Skript (keine Module, keine gemeinsame JS-Datei). Läuft über `file://` und `http://`. Einzige Abhängigkeit: `../shared/base.css` (relativ).

## Link-Struktur für GitHub Pages

```
repo-root/shared/base.css
repo-root/p5-psychophysik/index.html
repo-root/p5-psychophysik/schwelle.html            (Direktlink Gruppenansicht: schwelle.html#gruppe)
repo-root/p5-psychophysik/signalentdeckung.html    (Direktlink Gruppenansicht: signalentdeckung.html#gruppe)
```

`tests/` und `screenshots/` müssen nicht ins Repo.

## Bedienung für Teilnehmende

**Schwellentest.** Kopfhörer aufsetzen, mit «Testton abspielen» die Lautstärke einstellen (Rauschen wie im Test, keine Kalibrierung). «Weiter zur Übung»: 3 Übungsdurchgänge mit Rückmeldung und deutlich hörbarer Lücke (30, 25, 20 ms). Danach der Test ohne Rückmeldung. In jedem Durchgang kommen zwei Rauschbursts (Intervall 1 und 2), in einem steckt eine stille Lücke. Antwort per Knopf oder Taste 1 / 2. Der Test endet automatisch. Ergebnis: Schwelle in ms, Durchgänge, Trefferquote, Verlaufsdiagramm, Ergebnis-Code. Jeder Durchgang wird nur einmal abgespielt. Wird der Tab verlassen, wird der Durchgang verworfen und wiederholt.

**Signalentdeckung.** Beispielbilder ansehen (der Fleck erscheint nie in der Mitte, dort steht das Kreuz), Schwierigkeit mit dem Regler einstellen (Start 40), «Probelauf» (16 Durchgänge, Rückmeldung, Ziel 65 bis 85 % richtig). «Festlegen und weiter» ist erst nach einem Probelauf mit der aktuellen Reglerstellung möglich. Danach zwei Blöcke zu je 40 Durchgängen (20 mit Signal, 20 Catch-Trials, zufällige Reihenfolge), Blockreihenfolge zufällig. Vor jedem Block steht die Auszahlungsmatrix, sie bleibt mit dem Punktestand sichtbar. Ablauf je Durchgang: kleines Kreuz 400 ms, Reiz 300 ms, Maske 150 ms, Antwort («Ja, Signal» / «Nein», Tasten J / N), Rückmeldung 500 ms, keine Pause. Ergebnis je Block: Zählwerte, Raten, d′, c, Punkte, ROC-Diagramm, Ergebnis-Code.

**Gruppe auswerten (beide Seiten).** Codes einfügen, ein Code pro Zeile. Leerzeilen und doppelte Codes werden ignoriert, ungültige Zeilen (mit Zeilennummer und Grund: Prüfsumme, Format, Version, Code der anderen Seite) benannt. Schwelle: Tabelle und Gruppenmittel, Median, SD, Min/Max, Punktdiagramm. SDT: Tabelle d′ und c je Person und Block, Mittelwert und SD je Block, gemeinsames ROC (Einzelpunkte und Mittelpunkt je Block, unterscheidbar durch Form und Farbe).

**Ergebnis-Codes.** Nur ASCII, nur Ergebnisse, keine Namen. Eine zufällige 4-stellige Kennung (nicht aus Personendaten) verhindert, dass zwei gleiche Ergebnisse als Duplikat gelten. Prüfsumme: 3 Zeichen Basis 36, `h = 7; h = (h*31 + Zeichencode) mod 46656` über den Text vor der Prüfsumme.

- Schwelle: `HSLU-schwelle-v1.<id>.<status><schwelle in 0.01 ms>.<Durchgänge>.<richtig>.<chk>`, Status o = ok, c = Obergrenze, f = Untergrenze, m = Höchstzahl Durchgänge (Schwelle dann 0).
- SDT: `HSLU-sdt-v2.<id>.<lk|kl>.<Treffer>-<Verpasser>-<Fehlalarme>-<Korrekte Ablehnungen>.<dasselbe für den zweiten Block>.<chk>`. `lk` heisst: erster Block «Verpasser teuer». Die Zählwerte stehen immer zuerst für «Verpasser teuer», dann für «Fehlalarm teuer». **Version v2** (neu: Fleck ausserhalb der Mitte, 40 statt 50 Durchgänge je Block; Format sonst unverändert). Alte v1-Codes werden in «Gruppe auswerten» mit der Meldung «Version v1 ist veraltet … nicht mit v2 vergleichbar» abgelehnt.

## Parameter und Testhaken für Fachpersonen

URL: `?seed=<Zahl>` macht Rauschen, Zufallsreihenfolgen und Kennung reproduzierbar (beide Seiten), z. B. `schwelle.html?seed=42`. Mit gleichem Seed und gleichen Antworten entsteht derselbe Code. Direktlink `#gruppe` öffnet die Gruppenansicht.

Testhaken `window.__test` (vor dem Laden setzbar, z. B. mit Playwright `add_init_script`; ohne Eingriff inaktiv):

| Hook | Wirkung |
|---|---|
| `__test.instant = true` | alle Wartezeiten und die Audiowiedergabe entfallen, Oberfläche und Logik laufen sonst unverändert |
| `__test.listener = f(trial)` (Schwelle) | gibt die Antwort 1 oder 2 vor, `trial = {phase, n, level, gapMs, gapInterval, gapSamples, sr}` |
| `__test.observer = f(info)` (SDT) | gibt true («Ja») oder false vor, `info = {phase, block, i, signal, pos, amp, payoff}` |
| `__test.config = {…}` | überschreibt Konfigurationswerte (vor dem Laden) |
| `__test.order = ['konservativ','liberal']` (SDT) | erzwingt die Blockreihenfolge |
| `__test.seed`, `__test.log`, `__test.current`, `__test.lastResult`, `__test.state`, `__test.exposures` (SDT) | Seed, Protokoll aller Durchgänge, aktueller Durchgang, letztes Ergebnis, interner Zustand, gemessene Reizdauern |
| Schwelle: `generateBurst`, `generateTrial`, `buildEnvelope`, `renderOffline`, `Staircase`, `simulate(pcFn, seed, cfg)` | Stimulus-Generator (Samples), Wiedergabe über `OfflineAudioContext`, Treppenverfahren ohne Oberfläche |
| SDT: `qnorm`, `pnorm`, `computeSDT`, `makeStimulus`, `makeMask`, `makeSchedule`, `makePlan`, `makePositions`, `positionOk`, `sliderToAmp`, `groupSummary` | Rechenfunktionen und Generatoren |
| beide: `buildCode`, `parseCode`, `parseLines`, `checksum`, `CONFIG` | Code und Gruppenauswertung |

Die Haken geben über die Konsole Zugriff auf interne Daten (auch auf das Lückenintervall des aktuellen Durchgangs). Ein Schutz dagegen ist bei einer rein lokalen Seite nicht möglich und nicht nötig.

## Konfigurationswerte (Konstante `CONFIG` am Anfang des Skripts)

**Schwellentest**

| Wert | Standard | Bedeutung |
|---|---|---|
| Burst | 400 ms weisses Gauss-Rauschen, σ = 0.15 (Vollaussteuerung 1.0), 10 ms cos²-Ein-/Ausblenden an Anfang und Ende | gleich in beiden Intervallen |
| Ablauf Puffer | 150 ms Stille, Burst 1, 500 ms Pause, Burst 2, 100 ms Stille | ein einziger Puffer, ein Startzeitpunkt (kein Jitter zwischen den Bursts) |
| Lücke | Stille aus exakt `round(ms × Abtastrate / 1000)` Null-Samples (mindestens 1), Beginn zufällig 120 bis 220 ms nach Burst-Beginn | gleiche Rauschfolge mit und ohne Lücke bei gleichem Seed |
| Rampen | 0.5 ms cos² (`round(0.5 ms × Abtastrate)` Samples, mindestens 2), **ausserhalb** der Lücke: Ausblenden vor, Einblenden nach den Null-Samples | max. Hüllkurvenschritt `sin(π/(2R))`, 0.07 bei 44.1 kHz |
| Abtastrate | die des Geräts (`AudioContext.sampleRate`), Puffer in derselben Rate | keine Neuberechnung durch den Browser |
| Lautstärke | Regler 0 bis 100, `Gain = 0.8 × (v/100)²`, Start 40 | keine Kalibrierung |
| Start | 20 ms | deutlich hörbar |
| Grenzen | 0.25 bis 50 ms | |
| Verfahren | 2-down-1-up, Schrittfaktor 2 (logarithmisch) bis zum 2. Umkehrpunkt, danach 1.25 | gleiche Schritte rauf und runter (nötig für 70.7 %) |
| Abbruch | 12 Umkehrpunkte; Schwelle = geometrisches Mittel der letzten 8 | Mittel im Logarithmus, passend zu den logarithmischen Schritten |
| Weitere Abbruchgründe | 4 Fehler in Folge bei 50 ms (Status Obergrenze); 3 Abwärtsschritte in Folge bei 0.25 ms (Untergrenze); 100 Durchgänge (Höchstzahl) | in diesen Fällen «Schwelle nicht bestimmbar» |
| Randprüfung | liegen mindestens die Hälfte der gemittelten Umkehrpunkte an einer Grenze, gilt der Lauf als Ober- bzw. Untergrenze | |
| Übung | Lücke 30, 25, 20 ms, Rückmeldung | zählt nicht zum Test |

**Signalentdeckung**

| Wert | Standard |
|---|---|
| Durchgänge | 40 je Block (20 Signal, 20 Catch), Probelauf 16 (8 / 8) |
| Bild | 160 × 160 Pixel, per CSS bis 320 px vergrössert; Grauwert 128 + N(0, 28²) je Pixel; Signal: weicher Gauss-Fleck (σ = 14 px), additiv |
| Fleckort | nie in der Ausschlusszone (Radius 40 px um die Kreuzmitte = Bildmitte); Fleckmitte auf einem Ring 44 bis 52 px (Radius nach Fläche gleichverteilt), Winkel gleichmässig (Kreis in so viele Sektoren wie Signal-Durchgänge, je ein Zufallswinkel, gemischt); Randabstand mindestens 28 px (2 σ). Gleiche Regel im Probelauf, in beiden Blöcken und in den Beispielbildern |
| Kreuz | 10 × 10 px, Strichstärke 2, Grau 184 (heller als der Hintergrund, Kontrast +56 statt Schwarz), 400 ms statt 500 ms, nur in der Fixationsphase. Das «?» auf dem Bild entfällt (Antwortaufforderung steht als Text darunter) |
| Signalstärke | Regler 1 bis 100, Amplitude `16 × (0.5/16)^((v−1)/99)`, Start 40 (Amplitude 4.1), gleich in beiden Blöcken. Beispielbild Amplitude 40 |
| Zeiten | Fixation 400, Reiz 300 (gemessen 301.6 ms), Maske 150 (8-px-Blöcke), Rückmeldung 500, Pause 0 ms |
| Matrix «Verpasser teuer» | Treffer +1, Korrekte Ablehnung +1, Verpasser −4, Fehlalarm −1 |
| Matrix «Fehlalarm teuer» | Treffer +1, Korrekte Ablehnung +1, Verpasser −1, Fehlalarm −4 |
| Zielbereich Probelauf | 65 bis 85 % richtig (Hinweis, kein Zwang) |

**Begründung Ausschlusszone.** Radius 40 ≥ Kreuzarm 5 + angenommenes Verschmieren des Nachbilds 17 (ca. 0.5 Grad am Desktop, Annahme, nicht gemessen) + Halbwertsradius des Flecks 16.5 = 38.5. Der Ring beginnt bei 44 (4 px Reserve). Enger Ring, damit die Exzentrizität (55 bis 65 % der halben Bildkante) und damit die Entdeckbarkeit kaum vom Ort abhängt; mit Randabstand 2 σ passt der Ring ins 160-px-Bild. Der Ort unbekannt auf dem Ring macht die Aufgabe bei gleicher Amplitude schwerer (Idealbeobachter-Modell: d′ 1.6 statt 2.5 bei Reglerstellung 50), daher Startstellung 40. Kreuz zurückhaltender: kleiner, weniger Kontrast, kürzer, und heller als der Hintergrund, so dass ein Restnachbild dunkel wäre (entgegengesetzt zum hellen Fleck). Ob das Nachbild dadurch tatsächlich schwächer ist, wurde nicht an Menschen geprüft. Neutraler Hinweis in der Aufgabe: «Der Fleck kann an verschiedenen Stellen erscheinen, aber nie in der Mitte.» Das war nötig, damit niemand in der Mitte sucht.

**Begründung Durchgangszahl (Kompromiss).** 40 je Block ist die untere Grenze der ursprünglichen Vorgabe (40 bis 60). Simulation (Beobachter d′ = 1.5, 20000 Läufe): SD einer Einzelschätzung bei 20 + 20 Durchgängen d′ 0.46 bis 0.48, c 0.41 (halbe Verschiebung) bis 0.68 (volle Verschiebung). Korrektur wegen Rate 0 oder 1: 4 % der Blöcke (halbe Verschiebung) bzw. 16 % (volle), bei 20 je Block 22 % bzw. 41 %. Block-Unterschied pro Person (Delta c im Verhältnis zur Streuung): 1.9 bei halber Verschiebung, richtiges Vorzeichen bei 97 %; ohne wahren Unterschied zeigt Delta c > 0.3 bei 19 %. Eine Gruppe aus 5 Personen halbiert die Streuung des Mittels ungefähr (d′: 0.22 statt 0.49). Weniger Durchgänge (30 je Block) würden 0.8 Minuten sparen, aber die Korrekturhäufigkeit und die Streuung deutlich erhöhen. Einzelwerte sind Richtwerte, die Gruppe aussagekräftiger.

**Dauer (gemessen, Echtzeit, Antwortzeit 0.8 bis 1.2 s).** Vorher: reine Aufgabe 372 s = 6.2 min (gesamt ca. 8 min). Jetzt: reine Aufgabe 232 s = 3.9 min, gesamt 5.7 min (mit angenommenen Lesezeiten 112 s). Ein zweiter Probelauf verlängert auf ca. 6.8 min.

Die beiden Matrizen sind gespiegelt: Die Auszahlungsverhältnisse β = (V<sub>KA</sub> − V<sub>FA</sub>)/(V<sub>T</sub> − V<sub>V</sub>) betragen 0.4 bzw. 2.5. Die Seite nennt keinen «optimalen» Wert.

## Formeln

Ja = «Signal vorhanden». Trefferrate H = Treffer / (Treffer + Verpasser), Fehlalarmrate FA = Fehlalarme / (Fehlalarme + Korrekte Ablehnungen). z ist die Umkehrfunktion der Standardnormalverteilung (Algorithmus AS 241, Genauigkeit ca. 1e-15).

- d′ = z(H) − z(FA)
- c = −(z(H) + z(FA)) / 2 (positiv: weniger «Ja» als bei c = 0, negativ: mehr «Ja»; c = 0 liegt in der Mitte der beiden Verteilungen)
- Log-linear-Korrektur, nur wenn H oder FA gleich 0 oder 1 ist: **beide** Raten werden ersetzt durch H = (Treffer + 0.5) / (Signal-Durchgänge + 1) und FA = (Fehlalarme + 0.5) / (Catch-Durchgänge + 1). Betroffene Werte sind mit * markiert.
- Isosensitivitätskurve (gleiche Varianz): H = Φ(z(FA) + d′) mit dem Mittel der d′ beider Blöcke (Einzelseite) bzw. aller Personen und Blöcke (Gruppe). Die ROC-Punkte verwenden dieselben (ggf. korrigierten) Raten wie d′ und c.

## Wie man Inhalte ändert

Alle Zahlen stehen in `CONFIG` am Anfang des Skripts (Schwelle: Zeilen unter «Konfiguration», SDT ebenso). Auszahlungsmatrizen: `CONFIG.payoff` (SDT). Texte stehen direkt im HTML bzw. in den Funktionen `renderResult`, `renderProbe`, `STATUS_TEXT`. Die Tests lesen die Standardwerte und schlagen bei Änderung an (Testbericht anpassen).

## Bekannte Grenzen

- Echtes Hören und echte Wahrnehmung sind nicht getestet. Geräte, Kopfhörer, Bluetooth-Latenz und Betriebssystem-Mixer verändern den Ton in nicht prüfbarer Weise. Die Seite garantiert die Samples, nicht den Schall.
- iPhone: Der Stummschalter kann Web Audio stumm schalten. Die Seite weist im Hinweistext darauf hin. Nicht auf iOS getestet.
- Das Treppenverfahren liefert für einen Ratehörer (immer 50 %) in etwa einem Drittel der Läufe trotzdem eine «Schwelle» nahe der Obergrenze (Median 36 ms, 0.6 % der Läufe unter 10 ms), sonst «nicht bestimmbar». Ein einfaches Stabilitätskriterium trennt Ratehörer nicht von echten Hörern (siehe Testbericht), deshalb gibt es keines. Die angezeigte Trefferquote macht den Fall sichtbar.
- Die Reglerskala der Signalstärke ist nicht an Menschen kalibriert (Idealbeobachter-d′ ca. 2.5 bei der Reglermitte, Menschen liegen darunter). Der Probelauf mit Zielbereich fängt das ab.
- Pixelrauschen wird auf Bildschirmen mit Skalierung, Nachtmodus oder starkem Farbmanagement leicht verändert. Reizdauer folgt dem Bildraster (gemessen 300 ± 1 ms bei 60 Hz).
- Der Ergebnis-Code lässt sich von Hand manipulieren (Prüfsumme schützt nur gegen Tippfehler).
- Wunsch für `shared/base.css` (nicht geändert): `[hidden] { display: none !important; }`. Beide Seiten haben diese Regel lokal.

## Fachliche Hinweise zur Prüfung

1. **Absolute Schwelle, «Ton», «Lautstärke».** Der Auftrag (Zeilen 99 bis 111, 127 bis 131, 145 bis 151) spricht von «absoluter Schwelle», «Ton» und «Lautstärke». Der Test misst die kürzeste erkennbare Lücke, also eine zeitliche Auflösung. Die Seite verwendet nur «Lücke», «Rauschen», «Schwelle». Vorschlag: Auftrag anpassen («Lückenerkennungsschwelle»), Begriffe wie in der Quelle belassen, wenn gewünscht.
2. **Absolute Schwelle gegenüber Unterschiedsschwelle.** Die Abgrenzung ist hier nicht trivial: Die Lückendauer ist zugleich ein Unterschied zu «keine Lücke» (Diskrimination) und ein Reiz, der erkannt wird (Detektion). Die Musterlösung (Zeilen 145 bis 147, 157 bis 159) ordnet den Test der absoluten Schwelle zu. Vorschlag: im Lösungsschlüssel begründen oder offen als Diskussion belassen.
3. **«50 %-Schwelle» (Zeilen 131, 151).** Das Verfahren liefert ca. 70.7 % richtige Antworten (Simulation: Langlauf 0.706 bis 0.707). Bei einer Zwei-Intervall-Wahl bedeutet 50 % richtig Raten. Mit Rateskorrektur (P − 0.5)/0.5 entspricht 70.7 % einem Wert von 0.41, und die «50-%-Schwelle» im Sinn des Auftrags läge bei 75 % richtig. Die Seite sagt «Die Schwelle gehört zu 70.7 % richtigen Antworten, nicht 50 %» und rechnet keine 50-%-Schwelle aus. Vorschlag: Satz im Auftrag («Davon kann man die 50 % Schwelle bestimmen») streichen oder erläutern, dass dafür die psychometrische Funktion nötig wäre.
4. **Weber-Argument Zeile 175.** 5 gegen 6 Münzen (20 %) und 10 gegen 11 (ca. 9 %) liegen beide weit über k = 2 % für Gewicht. Das Argument «näher an der Schwelle» ist damit nicht schlüssig. Die Münzaufgabe ist nicht Teil dieses Projekts. Vorschlag: Paare mit Brüchen um 2 bis 4 % wählen (z. B. 50 gegen 51 Münzen, falls verfügbar, bzw. andere Gewichte).
5. **Definition der Lückendauer.** Hier: Dauer der Null-Samples, die Rampen liegen davor und danach. Die Dauer zwischen den Halbamplitudenpunkten ist um die Rampendauer länger (+0.5 ms), die gesamte Einsenkung um 1 ms. Andere Konventionen sind möglich. Die Schwellenwerte sind daher nicht ohne Weiteres mit Werten aus Literatur oder dem Padova-Test vergleichbar. Vorschlag: Konvention festlegen, dann Rampe oder Definition anpassen. Es werden keine Normwerte genannt.
6. **Mittelung der Umkehrpunkte.** Geometrisches Mittel der letzten 8 von 12. Das arithmetische Mittel liegt im Mittel 3 bis 4 % höher (Simulation: Verhältnis zur Lückendauer bei 70.7 % im Mittel 1.00 gegenüber 0.96 bis 0.97). Beide liegen für übliche psychometrische Funktionen innerhalb von ±12 % (flache Funktion bis +7 %, geometrisch bzw. +13 % arithmetisch).
7. **«Treffer 65 bis 85 %» im Probelauf (Vorgabe für das SDT-Projekt).** Gedeutet als Anteil richtiger Antworten (Treffer + Korrekte Ablehnungen) / Durchgänge. Falls die Trefferrate (nur Signal-Durchgänge) gemeint ist, muss `renderProbe` angepasst werden.
8. **Log-linear-Korrektur nur bei Extremwerten.** Wie vorgegeben (nur wenn H oder FA gleich 0 oder 1). Es entsteht ein kleiner Sprung gegenüber unkorrigierten Nachbarwerten. Hautus (1995) empfiehlt die Korrektur immer; hier nicht umgesetzt, da nicht in der Vorgabe. Vorschlag: Dozent entscheidet.
9. **Neutrale Blockbenennung.** Die Seite nennt die Blöcke «Verpasser teuer» und «Fehlalarm teuer» (Eigenschaft der Matrix) und sagt nie «liberal» oder «konservativ». Im Auftrag (Zeilen 155, 261) heisst es «niedriges Kriterium» für «ja, gehört, wenn unsicher». Diese Aussage ist mit c als Abstand zur Mitte (hier c negativ = liberal) vereinbar, nicht mit jeder Konvention. Nur melden.
10. **Kleine Stichproben.** Mit 20 + 20 Durchgängen streut d′ (SD ca. 0.5) und c (SD 0.4 bis 0.7) deutlich, siehe oben. Die Gruppenansicht ist wichtiger als Einzelwerte. Die angenommene Verschiebung des Kriteriums (optimal bzw. halb) ist eine Modellannahme, keine Messung.
11. **Fleckort und Nachbild.** Annahmen (Verschmieren 17 px, Wirkung von hellem, kleinem Kreuz) sind nicht an Menschen geprüft. Der Fleck liegt immer auf einem Ring, die Aufgabe ist damit auf diesen Bereich zugeschnitten. Die Anisotropie des Gesichtsfelds (z. B. oben/unten) ist nicht ausgeglichen, nur gleichmässig über Winkel verteilt.
12. **Beispielbild** hat Amplitude 40, also mehr als die leichteste Reglerstellung (16). Die Reglerskala ist weiterhin nicht an Menschen kalibriert.

## Offene Fragen an den Dozenten

- Soll die Lückendauer als Stille (jetzt) oder zwischen Halbamplitudenpunkten definiert werden (Hinweis 5)? Gibt es Vergleichswerte?
- Soll ein Ratehörer-Schutz (z. B. Mindest-Trefferquote) ergänzt werden? Das würde auch echte Hörer gelegentlich ausschliessen.
- Durchgangszahl 40 je Block und 16 im Probelauf so lassen (siehe Begründung) oder auf 50 erhöhen (Dauer ca. 4.6 min Aufgabe)?
- Auszahlungsverhältnis 4 : 1 beibehalten oder stärker/schwächer?
- Anzeige «70.7 %» im Ergebnis so belassen (Hinweis 3)?
- Soll der Probelauf zwingend sein (jetzt ja) und der Zielbereich 65 bis 85 % richtig bedeuten (Hinweis 7)?
- Soll die Gruppenauswertung zusätzlich Reihenfolgeeffekte (Block 1 gegenüber Block 2) darstellen? Die Reihenfolge steht im Code.
