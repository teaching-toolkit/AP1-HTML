# P2 Glücksfaktoren-Spiel (Emotion, Aktivität 2)

## Zweck

Die Gruppe entscheidet gemeinsam für Alexandra, eine Studentin, und würfelt nach jeder Entscheidung. Die Seite führt eine Fachperson und die Studierenden durch 12 Episoden pro Spiel (aus 19 Episoden in vier Blöcken mit Verzweigung, darunter vier Krisenepisoden), rechnet das Resultat nach der Logik des Excel `gluecksfaktoren.xlsx` und zeigt am Schluss den Verlauf der Stimmung. Die Seite interpretiert nichts: Es gibt keine Erklärung der pädagogischen Idee, keine Moderationshinweise und keine Literaturliste (diese bleiben bei der Fachperson).

Statische HTML5-Seite, keine Bibliothek, keine externen Anfragen, läuft auch von `file://`.

## Bedienung

### Teilnehmende (Handy, Tablet, Laptop)

Ein Bildschirm pro Schritt, grosse Knöpfe:

1. **Spiel starten.** Die Startwerte werden gezeigt (Zeit 0, Energie 0, Soziale Verbindungen 1, Erfüllung 1, Lebensstil 1, Finanzen 1, Stimmung 50).
2. **Entscheidung:** Vorlesetext, Option A und B je mit «Unmittelbare Folge». Welche Option als A und welche als B erscheint, ist pro Episode zufällig (siehe «A/B-Randomisierung»). Ob eine Option eher langfristig investiert oder kurzfristig optimiert, steht hier nirgends.
3. **Würfeln:** virtueller W20 (Knopf oder Taste W) oder der Wurf eines eigenen Würfels (Zahl 1 bis 20 eintippen).
4. **Ergebnis:** Wurf, Boost aus den Attributen (ein Balken je Attribut), Ergebnis gegenüber Soll-Wert, darunter ein Kurztext (1 bis 2 Sätze) dazu, was Alexandra erlebt und wie sie sich fühlt (Erfolg: Ergebnis grösser oder gleich Soll-Wert, sonst Misserfolg).
5. **Veränderungen:** Stimmung und alle Attribute, Vorher / Änderung / Nachher.
6. **Werte danach.** Hier steht zuerst eine **verdeckte Auswahlliste «Mögliche Glücksfaktoren»**: 6 bis 8 Einträge in zufälliger Reihenfolge, alle gleich dargestellt (echte Glücksfaktoren, plausible und absurde Ablenker). Die Gruppe bespricht, welche eine Rolle gespielt haben. Die Lösung zeigt erst die **Fachperson** mit dem Knopf «Lösung zeigen» (siehe unten).
7. **Weiter** zur nächsten Episode. Nach Episode 12 folgt die **Abschlussansicht**: Stimmungsverlauf als Grafik, gewählte Optionen je Episode, Endwerte.

**Rückgängig** macht beliebig viele Schritte rückgängig (Knopf oder Strg+Z), auch die Freigabe der Lösung. **Neues Spiel** fragt zur Sicherheit nach und zieht einen neuen Zufallsplan (A/B und Reihenfolge der Auswahlliste). Tasten: A / B wählt die **angezeigte** Option, W würfelt, Tab und Enter bedienen alles.

### Fachpersonen

* **Lösung zeigen.** Unter «Werte danach» sieht die Gruppe die verdeckte Liste. Der Knopf «Lösung zeigen» (am Ende der Liste) gibt die Lösung frei: Die echten Glücksfaktoren erscheinen mit dem Text aus dem Word (grün, «Glücksfaktor»), die Ablenker als «Hier nicht entscheidend» (plausibel, aber nicht Teil der Lösung dieser Episode im Spiel) oder «Unplausibel» (absurd). Darunter folgen die Erkenntnis-Zeilen aus dem Word. Danach ist die Liste nicht mehr verdeckt; **Rückgängig** deckt sie wieder zu. In der nächsten Episode ist die Liste wieder verdeckt.
* **Markieren (Entscheid).** Teilnehmende und Fachperson können Einträge durch Antippen markieren (Haken, wieder antippen nimmt zurück). Die Markierung ist rein lokal: sie liegt nur im Speicher dieses Tabs (bleibt beim Neuladen erhalten), wird nicht gesendet und erscheint nicht im Abschluss. Sie hat keinen eigenen Rückgängig-Schritt. Nach der Freigabe zeigt die Seite «Von n markierten Einträgen gehören m zur Lösung». Begründung: Die Besprechung in der Gruppe bleibt der Kern; die Markierung hilft, sich vor der Freigabe festzulegen, und kostet nichts.
* **Abschlussansicht.** Zusätzlich zu Verlauf, Optionen und Endwerten zeigt sie pro Episode die Ausrichtung der gewählten Option («langfristige Investition» oder «kurzfristige Optimierung», Stern bei nicht eindeutiger Einordnung) und eine Zählzeile (zum Beispiel «5 × langfristige Investition, 7 × kurzfristige Optimierung»). Das ist die Grundlage für die Nachbesprechung; vorher ist die Ausrichtung nirgends sichtbar.
* **Mikroszenen M1 bis M10** werden nie automatisch eingefügt. Unter «Werte danach» schlägt die Seite passende Szenen vor (Knopf), wenn Zeit oder Energie unter −5 liegen oder Soziale Verbindungen, Persönliche Erfüllung oder Lebensstil-Qualität unter 0 liegen (Zuordnung laut Word «Mikroszenen strategisch einsetzen»). «Mikroszene einschieben» zeigt alle zehn Szenen; jede Szene ist einmal pro Spiel möglich. Mikroszenen haben keinen Würfel und ändern die Stimmung nicht, nur die Attribute (feste Werte aus dem Word). Danach geht es regulär mit der nächsten geplanten Episode weiter.
* **Spielende:** Fällt die Stimmung unter 0 (nach einer Episode oder durch die Beginn-Änderung einer Episode), bietet die Seite beides an: direkt zur Abschlussansicht oder eine Rettungs-Mikroszene (M1, M3, M5, M10 hervorgehoben). Nach der Rettungs-Mikroszene geht es mit der nächsten Episode weiter, auch wenn die Stimmung noch unter 0 liegt.
* **Testparameter** in der Adresse (nur für Prüfung und Unterricht, ändern keine Regeln ausser `schranken`):

| Parameter | Wirkung |
|---|---|
| `?seed=abc` | Der virtuelle Würfel liefert eine reproduzierbare Folge (gleicher Wert, gleiche Würfe). Ohne `seed` wird `crypto.getRandomValues` benutzt (gleichverteilt). Mit `seed` wird kein Spielstand geladen. |
| `?schranken=1` | Schaltet die Schranken aus dem Word ein: Attribute begrenzt auf −10 bis +10, Stimmung höchstens 100. Standard ist aus, wie im Excel. Begrenzte Werte tragen den Hinweis «begrenzt». |
| `?neu=1` | Ignoriert einen gespeicherten Spielstand. |
| `?ab=fest` | Alte Zuordnung: A bleibt in jeder Episode die Excel-Option A, B die Option B. Nur für Vergleich und Prüfung. |
| `?ab=tausch` | Alle 19 Episoden vertauscht (A zeigt Excel-Option B). Nur für Prüfung. |
| (ohne `ab`) | Standard: pro Episode zufällig, ob die Buchstaben vertauscht sind. Ein unbekannter Wert wirkt wie der Standard. |

`?seed=` legt zusätzlich den Zufallsplan fest (A/B je Episode und Reihenfolge der Auswahllisten), unabhängig vom Würfelstrom: Die Würfelfolge zu einem Seed ist dieselbe wie vor dieser Überarbeitung. `?seed`, `?ab` und `?neu` laden keinen gespeicherten Spielstand.

* Der Spielstand wird in `sessionStorage` gehalten (nur dieser Tab; Neuladen stellt ihn wieder her). Ist der Speicher blockiert, läuft das Spiel trotzdem.
* Für automatische Tests gibt es `window.GLUECK` (`zustand()`, `undoTiefe()`, `springe(ep, werte)`, `setze(patch)`, `entsperren()`, dazu `kern`, `daten`, `texte`, `abModus`). Im Zustand steht `tausch[ep]` (1: Buchstaben vertauscht), `wahl` (Regeloption, Excel-Zeile) und `wahlAnz` (angezeigter Buchstabe). Die Seite ignoriert Klicks in den ersten 250 ms nach einem Schritt (Schutz vor Doppeltippen).

## A/B-Randomisierung und Ausrichtung

Jede Episode hat zwei Regeloptionen (im Excel Zeile A und B). Beim Start eines Spiels wird für alle 19 Episoden vorab gezogen, ob die Anzeige A und B vertauscht (`crypto.getRandomValues`, Ablehnungsverfahren ohne Modulo-Verzerrung; mit `?seed=` ein eigener, reproduzierbarer Strom). Dasselbe gilt für die Reihenfolge der Auswahlliste. Der Plan liegt im Spielstand; Rückgängig, Neuladen und Diagramm ändern ihn nicht. Intern ändert sich nichts: Gerechnet wird mit der **Regeloption** (`wahl`), die Verzweigung («Weiter bei») folgt der Regeloption, die Karten, die «Gewählt»-Zeile, die Taste A/B und die Optionsbuchstaben in den Glücksfaktoren-Texten («Primär bei Option B») folgen dem angezeigten Buchstaben. Mikroszenen (A/B aus dem Word) werden nicht vertauscht.

**Ausrichtung.** Pro Regeloption steht in `spiel-texte.js`, ob sie eher eine **langfristige Investition** oder eine **kurzfristige Optimierung** ist. Massstab ist das Prinzip aus dem Word: Option A spart oder sichert kurzfristig, Option B investiert (Beziehung, Erfüllung, Gesundheit, Planung). Das gilt in 18 von 19 Episoden. Ausnahmen und unklare Fälle (mit Stern in der Abschlussansicht, Begründung als `notiz` in `spiel-texte.js`):

| Episode | Einordnung |
|---|---|
| 11B | **Umgekehrt:** A (befristeter Traumjob) = langfristige Investition (Erfüllung), B (unbefristete Stelle) = kurzfristige Optimierung (Sicherheit). Unscharf, weil die Befristung auch die umgekehrte Lesart zulässt. |
| 6 | A (Grenzen setzen) schützt Zeit und Energie, investiert aber auch in Erholung. Einordnung kurzfristig, unscharf. |
| 8A | A (Mitziehen) spart keine Ressourcen, optimiert aber kurzfristig Leistung und Einkommen. Unscharf. |
| 8B | Beide Optionen enthalten Investitionen; Einordnung nach Aufwand (B verlangt mehr Disziplin). Unscharf. |
| 12A2, 12B2 | Krisenepisoden ohne klares Muster (A lässt sich als Investition in die Gesundheit lesen; beide Wege in 12B2 sind aktiv). Unscharf. |
| 12A1, 12B1 | Krisen, eindeutig (passiv erdulden gegen aktiv handeln; Flucht in die Arbeit gegen Verarbeiten). |

Die Einordnung ist meine Lesart der Optionen und des Word, nicht eine Angabe aus dem Excel. Bitte prüfen (offene Frage 9). Die Wörter «langfristig» und «kurzfristig» kommen auch in den Word-Texten von 11A (Option A, «langfristig arrangieren») und 11B (Option B, «langfristige Angebot») sowie in einer Erkenntnis in anderem Sinn vor; sie sind während des Spiels sichtbar und können die Einordnung von 11B verwischen.

**Regel 0.2.8 (Lösung nicht im Code).** Die Lösung der Auswahlliste (welche Einträge echte Glücksfaktoren sind) und die Ausrichtung stehen als Daten im öffentlichen Quelltext (`spiel-daten.js`, `spiel-texte.js`) und im Spielstand im Speicher des Tabs. Das ist eine bewusste Ausnahme: Die Seite ist statisch, es gibt keinen Server, der die Lösung zurückhalten könnte. Wer den Quelltext liest, kann die Lösung vorher finden. Im Seitenaufbau (DOM, Attribute, Bildschirmleser) ist sie vor der Freigabe nicht enthalten; ein Test prüft das.

## Inhalt ändern

Alle Texte und Zahlen stehen in `spiel-daten.js` (klassisches Skript, setzt `window.SPIEL_DATEN`):

* `konfig`: Startwerte, Gewichte, Sättigung (`saettigungExcel`), Resultat (Faktor, Stellen, Minimum), Stimmungsänderung, Energie aus Stimmung, Zeitabzug bei Finanzen unter −2, Schranken, Spielende-Schwelle, Würfelseiten, Schwellen für Mikroszenen-Vorschläge.
* `episoden`: je Episode `id`, `block`, `titel`, `vorlesen`, `beginn` (Zeit, Energie, Stimmung), `optionen.A/B` mit `label`, `folge`, `wuerfeltitel`, `weiter` (nächste Episode oder `null`), `soll`, `aenderung`, `energieBasis`, Excel-Zeile; dazu `glueck` und `erkenntnis`.
* `mikroszenen`, `mikroZuordnung`.

Von Hand geschrieben ist dagegen **`spiel-texte.js`** (setzt `window.SPIEL_TEXTE`, JSON-kompatibel; der Generator berührt sie nicht, `tools/erzeuge_daten.py` und `spiel-daten.js` sind unverändert). Je Episode (Schlüssel = Episoden-ID, «A» und «B» = Regeloption): `ausrichtung`, `unscharf`, `notiz`, `plausibel` (2 bis 3 plausible Ablenker), `unplausibel` (2 bis 3 absurde Ablenker) und `ergebnis` mit `A`/`B` und `erfolg`/`misserfolg`, je `text` (1 bis 2 Sätze) und `gefuehl` (was der Text behauptet, für den Test). Dazu `ausrichtungNamen` und `urteilTexte`. In den Kurztexten werden die Platzhalter `{ZEIT}` und `{ENERGIE}` durch «mehr Zeit», «deutlich weniger Energie», «gleich viel Energie» usw. ersetzt, passend zur tatsächlichen Änderung: Die Energie-Änderung hängt von der Stimmung ab und ist vor dem Wurf nicht bekannt, die Zeit sinkt bei Finanzen unter −2 zusätzlich. Die echten Glücksfaktoren der Auswahlliste kommen aus `episoden[].glueck` (ohne Code und Klammerzusatz). Ablenker erscheinen nie in mehreren Episoden und behaupten nichts; «Hier nicht entscheidend» heisst nur «gehört in diesem Spiel nicht zur Lösung dieser Episode», nicht «hat mit Glück nichts zu tun». Eine Änderung der Texte prüft `tests/test_texte.py` (Vollständigkeit, Länge, Richtung gegen die Excel-Rechnung).

`spiel-daten.js` wird aus den Quellen erzeugt: `python3 tools/erzeuge_daten.py [xlsx] [docx]` liest Excel (alle Formeln und Konstanten, Zeilen 3 bis 46) und Word (python-docx) vollständig und bricht ab, wenn Formeln oder Reihenfolge von den Annahmen abweichen. Das Ergebnis ist reproduzierbar (Test vergleicht byte-identisch). Rechenregeln stehen in `spiel-kern.js` (Kopfkommentar: Excel-Zelle → Funktion).

## GitHub Pages

Der Ordner `p2-emotion-spiel/` muss zusammen mit dem Geschwisterordner `shared/` (Datei `base.css`) veröffentlicht werden:

```
<repo>/shared/base.css
<repo>/p2-emotion-spiel/index.html
<repo>/p2-emotion-spiel/spiel-daten.js
<repo>/p2-emotion-spiel/spiel-texte.js
<repo>/p2-emotion-spiel/spiel-kern.js
```

Link: `https://<konto>.github.io/<repo>/p2-emotion-spiel/index.html`. Alle Pfade sind relativ.

## Tests

Siehe `TESTBERICHT.md`. Aufruf (aus dem Projektordner): `python3 -I tests/pruefe_excel.py` (Excel-Abgleich mit LibreOffice, ca. 5 Minuten), `python3 -I tests/test_durchlauf.py`, `python3 -I tests/test_regeln.py`, `python3 -I tests/test_dateien.py`, `python3 -I tests/test_texte.py` (Ergebnistexte), `python3 -I tests/test_glueck.py` (Verdecken und Freigeben), `python3 -I tests/test_ab.py` (A/B-Randomisierung); Bilder: `python3 -I tests/mache_screenshots.py`. Voraussetzung: Playwright für Python mit Chromium, `openpyxl`, `python-docx`, LibreOffice (`soffice`).

## Bekannte Grenzen

* Mikroszenen zeigen die Glücksfaktoren weiterhin direkt (ohne verdeckte Liste) und haben keine Kurztexte und keine zufällige A/B-Zuordnung. Das war nicht verlangt und ist eine Ausnahme.
* Die Ablenker und Kurztexte sind von Hand geschrieben und nicht vom Dozenten geprüft. Der Test prüft Richtung (Vorzeichen) und Form, nicht den Ton.
* Es gibt nur den Weg durch 12 Episoden. Mikroszenen verlängern das Spiel nicht über Episode 12 hinaus.
* Die Stimmung kann über 100 steigen und Attribute können über ±10 hinausgehen (so rechnet das Excel). Die Balken in der Anzeige enden bei 100 beziehungsweise ±10. Mit `?schranken=1` wird begrenzt.
* Die Grafik zeigt die Stimmung nach jeder Episode (Ring: Stimmung zu Beginn einer Episode, wenn die Beginn-Änderung sie verändert hat). Mikroszenen verändern die Stimmung nicht und erscheinen deshalb nur in der Liste.
* Bei exakten Rundungshälften (siehe unten) kann ein anderes Tabellenprogramm in sehr seltenen Fällen um 0.1 im Resultat abweichen.
* Getestet mit Chromium (Playwright). Safari und Firefox wurden nicht geprüft.

## Fachliche Hinweise zur Prüfung

1. **Sättigung der Faktoren Zeit, Energie, Finanzen.** Die Formel im Excel lautet `=IF(G>2, w*2, IF(G>4, w*3, G*w))`. Die zweite Stufe (über 4 ergibt das Dreifache) ist nie erreichbar, weil jeder Wert über 4 schon in die erste Bedingung (über 2) fällt. Folge: Der positive Beitrag dieser drei Faktoren ist bei 2·w gedeckelt (Zeit 0.5, Energie 0.6, Finanzen 0.5 vor dem Faktor 2), negative Werte wirken unbegrenzt linear, Soziale Verbindungen, Erfüllung und Lebensstil wirken immer linear. Die Seite setzt das genau so um und zeigt die Stufen als benannte Konfiguration (`konfig.saettigungExcel`). Wenn die Stufen gemeint waren (bis 2 linear, 2 bis 4 doppelt, über 4 dreifach), muss die Konfiguration dort geändert werden.
2. **Excel-Zellen Y3 und Y40 sind leer.** In den Zeilen «Ep1 A» und «Ep12A1 B» fehlt die Formel für die Stimmung nach der Entscheidung. Die leere Zelle zählt im Excel als 0, daher ergibt sich dort immer die Energie-Änderung AI = AW − 4 (in den anderen Zeilen AW + ROUND(8·(Y−50)/50, 0)/2). Die Seite rechnet in allen 38 Zeilen gleich (Y = M + AN). Vermutlich erklärt das den Energie-Basiswert −4 in einem älteren HTML.
3. **Resultat und Stimmung.** `Resultat = max(0, ROUND(2 · Summe der sechs Beiträge + Wurf, 1))`, `Stimmungsänderung = ROUND(8·(Resultat − Soll)/10, 0)`, `Energie-Änderung = Energie-Basis + ROUND(8·(Stimmung nachher − 50)/50, 0)/2`. Zeit sinkt zusätzlich um 1, wenn Finanzen vor der Entscheidung unter −2 liegen.
4. **Beginn-Änderungen** (Spalten C, D, E) gelten zu Beginn der Episode, bevor die Optionen sichtbar sind: Ep 4 und Ep 7 Zeit +3 und Energie +3, Ep 10 Zeit +1, Energie +1, Stimmung −5, Ep 12 (alle vier) Stimmung −10.
5. **Schranken:** Das Word nennt Attribute von −10 bis +10 und Stimmung 0 bis 100, das Excel hat keine Schranken. Standard: keine Schranken (Excel).
6. **Schwellen für Mikroszenen** «vernachlässigt» und «niedrig» nennt das Word nicht; angenommen wurde unter 0. Zeit und Energie «kritisch niedrig» ist im Word unter −5.
7. **Mikroszenen:** M8 hat im Word keine Glücksfaktoren (Feld leer, bleibt leer). In M10 hat Option A (Ablenkung suchen) Zeit −1 wie Option B, im Gegensatz zum Prinzip «A spart Ressourcen»; übernommen wie im Word.
8. **Zeilen mit «Forschungserkenntnis»** und «Wichtige Erkenntnis» erscheinen als zusätzliche Zeilen unter den Glücksfaktoren (nach der Entscheidung).
9. **Typografie:** Gerade Anführungszeichen im Word wurden in «„…“» umgewandelt, Vorlesetexte ohne Anführungszeichen bleiben so. Sonst unverändert (Schweizer Schreibweise des Word).
10. **Rundung bei exakten Hälften.** Etwa die Hälfte aller Zustände ergibt für `2·Summe + Wurf` einen Wert auf x.x5, weil alle Beiträge Vielfache von 0.05 sind. Excel und LibreOffice runden den 15-stellig gerundeten Gleitkommawert halb von null weg; die Seite macht dasselbe. Eine exakte Dezimalrechnung ergibt in 1 von 456 Zufallszuständen und 4 von 912 Hälftenfällen 0.1 mehr (nur bei Resultaten unter 1). Gegenüber LibreOffice mit der Summe als Addition (`AA+AB+…`) gibt es 0 Abweichungen, gegenüber LibreOffice mit `SUM()` 2 von 912 (andere Summationsreihenfolge). Microsoft Excel war nicht verfügbar; die Summationsreihenfolge von Excel ist deshalb eine Annahme.

## Offene Fragen an den Dozenten

1. Soll die Sättigung so bleiben, dass positive Werte von Zeit, Energie und Finanzen ab 2 nicht mehr zählen (Deckel bei 2·w), oder waren drei Stufen gemeint (bis 2 linear, über 2 doppelt, über 4 dreifach)?
2. Fehlt in Y3 und Y40 die Formel nur aus Versehen? Die Seite nimmt «ja» an.
3. Sollen die Schranken (Attribute ±10, Stimmung höchstens 100) gelten? Ohne Schranken erreichen starke Verläufe Stimmung über 100 (im Test bis 121).
4. Ab welchem Wert gelten Soziale Verbindungen, Erfüllung und Lebensstil als «vernachlässigt/niedrig»? (Angenommen: unter 0.)
5. Soll eine Rettungs-Mikroszene die Stimmung anheben? Heute ändert sie nur die Attribute, die Stimmung bleibt unter 0, und die Fachperson entscheidet nach jeder Episode neu über das Spielende.
6. M10: Soll Option A Zeit −1 haben (wie im Word) oder 0 beziehungsweise +1?
7. M8: Gehören Glücksfaktoren zur Szene (im Word leer)?
8. Die Moderationsanleitung (Einleitung einer Mikroszene, Zeitplan, Checkliste) ist bewusst nicht auf der Seite. Soll sie als einklappbare Karte für die Fachperson hinzukommen?

9. Stimmt meine Einordnung der Optionen in «langfristige Investition» und «kurzfristige Optimierung» (Tabelle oben), besonders 11B (umgekehrt), 6, 8A, 8B, 12A2 und 12B2?
10. Sollen die Mikroszenen ebenfalls eine verdeckte Liste, Kurztexte und eine zufällige A/B-Zuordnung bekommen?
11. Die tote Verzweigungsformel im Excel (Sättigung, Hinweis 1) bleibt bewusst unverändert; diese Überarbeitung ändert keine Zahl, Gewichte oder Formel.

## Unterschiede zum älteren HTML

Die Rechenlogik stammt vollständig aus dem Excel und nicht aus dem alten HTML. Nicht übernommen: Schranken als Standard (nur per Parameter), der Energie-Basiswert −4 (siehe Hinweis 2) sowie jede Interpretation und Erklärung.
