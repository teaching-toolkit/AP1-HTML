# P3: Forschungsbefunde einschätzen (Hindsight-Bias-Experiment, Einführung 2, Aktivität 1), Version 2

Statische HTML5-Seite für Studierende der Psychologie (HSLU, Allgemeine Psychologie 1). Sie ersetzt die Google Forms und die allocate.monster-Links durch **eine** Seite mit Zufallszuteilung im Browser. Reines HTML/CSS/JavaScript, kein Build, keine Bibliotheken, keine Netzwerkanfragen zur Laufzeit, keine Daten verlassen das Gerät.

**Überarbeitung vom 15.10.2026 nach Rückmeldung des Dozenten:** fünf statt neun Befunde, neuer Ablauf in zwei Teilen (zuerst alle Aussagen beurteilen, dann die Erklärungen einordnen), Plausibilitätsfrage statt «Offensichtlichkeit», Auflösung auf Knopfdruck, Ergebnis-Code v2.

> **Wichtig für die Weitergabe:** Diese README, der TESTBERICHT, `tests/` und die Screenshots verraten, welche Fassung die tatsächliche ist (Version A) und enthalten die Prüfnotizen. Sie gehören nicht ins öffentliche Repo. Siehe «Ausnahme zu Regel 0.2 Punkt 8».

## Dateien

| Datei | Inhalt |
|---|---|
| `index.html` | die ganze Seite (Ablauf, Zusammenfassung, Auflösung, Ergebnis-Code, «Gruppe auswerten»), CSS und JavaScript eingebettet |
| `befunde.js` | Daten der 5 Befunde (klassisches Skript, setzt `window.BEFUNDE`), erzeugt aus dem Auftrag, plus `quelle` und `vorbehalt` für die Auflösung |
| `../shared/base.css` | gemeinsames CSS, relativ eingebunden (nicht geändert) |
| `tests/` | Testskripte, `screenshots/` die wichtigsten Bilder, `TESTBERICHT.md` |

## Ablauf für Teilnehmende

1. **Start:** Startseite lesen («Plane etwa 6 bis 8 Minuten ein»), «Starten».
2. **Teil 1: Aussagen beurteilen.** Alle fünf Studienaussagen nacheinander, eine pro Bildschirm, Fortschrittsanzeige («Befund 3 von 5», «Teil 1 von 2»). Pro Aussage ein Freitextfeld mit der Frage «Wie würdest du diesen Befund erklären?» und dem sichtbaren Hinweis «**Stichworte genügen:** ein bis zwei Wörter oder ein kurzer Halbsatz reichen.» Das Feld darf leer bleiben (Zähler «0 Zeichen»). **«Zurück» ist in Teil 1 erlaubt** (Knopf und Browser-Zurück), die Texte bleiben erhalten, weil noch keine Erklärung gesehen wurde. Enter schickt ab (Umschalt + Enter gibt einen Zeilenumbruch).
3. **Übergang:** Der letzte Knopf heisst «Teil 1 abschliessen» mit dem Hinweis, dass Teil 1 danach nicht mehr änderbar ist. Auf dem Übergangsbildschirm «Teil 1 ist abgeschlossen» steht «Weiter zu Teil 2».
4. **Teil 2: Erklärungen einordnen.** Pro Befund werden die Studienaussage, die eigenen Stichworte aus Teil 1 und die zugeteilte Erklärung gezeigt. Frage: «**Wie plausibel wirkt diese Erklärung jetzt auf dich?**», Skala 1 bis 5 (1 = gar nicht plausibel, 5 = sehr plausibel). Bedienung per Tippen, Klicken, Tab und Pfeiltasten oder Zifferntasten 1 bis 5 (Enter geht weiter). Ohne Auswahl ist «Weiter» gesperrt.
5. **Kein Zurück ab Teil 2:** Es gibt keinen Weg zurück zu Teil 1, auch nicht mit dem Browser-Zurück (Seite bleibt stehen und zeigt den Hinweis «Zurück ist ab Teil 2 nicht mehr möglich»). Neuladen stellt den Stand wieder her (Teil 1 bleibt unerreichbar).
6. **Zusammenfassung «Deine fünf Berichte»:** pro Befund Titel, Studienaussage, deine Stichworte, deine Plausibilitätsbewertung (die Erklärung ist eingeklappt abrufbar), damit die Gruppe nebeneinander vergleichen kann. Darunter der **Ergebnis-Code** mit «Code kopieren» und die Karte **«Auflösung»** mit dem Hinweis, sie erst nach dem Vergleich in der Gruppe zu öffnen.
7. **Auflösung** (nur auf Klick auf «Auflösung anzeigen», verbergbar): pro Befund die Aussage, die tatsächlich gestimmt hat (mit Erklärung aus dem Auftrag), ob die eigene Version die tatsächliche oder die gegenteilige war, die eigene Bewertung, und wo vorhanden Quelle und Vorbehalt.

Vor der Auflösung sagt die Seite nirgends, dass es zwei Versionen gibt. Auf allen Bildschirmen der Teilnehmenden kommen die Wörter «Version», «Variante», «Fassung», «echt», «falsch», «gegenteilig» nicht vor (ausser in den wörtlichen Befundtexten). «hindsight» steht nur im Ergebnis-Code. Der Link «Gruppe auswerten» steht nur auf der Zusammenfassung, nicht mehr auf der Startseite.

## Bedienung für die Fachperson

- **Link an die Studierenden:** `…/p3-hindsight/` (ein einziger Link, keine Gruppen-Links nötig).
- **Zuteilung:** Pro Person und Befund zufällig echte (A) oder gegenteilige (B) Version. Bei «Starten» zieht die Seite zuerst, ob **2 oder 3** der 5 Befunde in Version A erscheinen (je 50 %), und dann zufällig welche (Fisher-Yates). Damit ist jedes der 20 möglichen Muster gleich wahrscheinlich (je 5 %), und jeder Befund zeigt mit 50 % Version A. Zufallsquelle: `crypto.getRandomValues` (nur für sehr alte Browser ohne diese Funktion Rückfall auf `Math.random`).
- **«Gruppe auswerten»:** Link unten auf der Zusammenfassung oder direkt `…/p3-hindsight/?gruppe=1` (für die Fachperson der bequemste Weg). Ein Ergebnis-Code pro Zeile einfügen, «Auswerten». Leerzeilen und doppelte Codes werden ignoriert, ungültige Zeilen werden mit Zeilennummer und Grund genannt, unvollständige Personen werden benannt, **Codes der früheren Seitenversion (v1, neun Befunde) werden mit eigenem Hinweis zurückgewiesen**. Angezeigt werden pro Befund Mittelwert der Plausibilität und Anzahl n für «Version A» und «Version B» getrennt, dazu die Zeile «Alle Befunde» (Mittel aller Bewertungen der jeweiligen Version, nicht Mittel der Personenmittel). Mittelwerte mit zwei Nachkommastellen.
- **Auflösung in «Gruppe auswerten»:** Der Knopf «Auflösung anzeigen» (unter den Ergebnissen) gibt die Zuordnung **A = echt, B = gegenteilig** frei (Spaltenköpfe «Version A (echt)» / «Version B (gegenteilig)») und zeigt die Auflösung pro Befund (tatsächliche Aussage, Erklärung, Quelle, Vorbehalt). Ohne Klick nennt die Auswertung nur neutral «Version A / Version B».
- **Vorzeitig beenden: gestrichen.** Die frühere Version erlaubte ab dem zweiten Befund ein vorzeitiges Ende mit Teilcode. Bei fünf Befunden (rund 4 bis 8 Minuten) ist das nicht mehr sinnvoll: Der Weg erhöht die Zahl der Zustände, und Teilcodes verwässern den A/B-Vergleich pro Befund. Zudem muss Teil 1 komplett sein, bevor in Teil 2 etwas bewertet werden kann. Das Codeformat kann `x` (nicht bewertet) weiterhin lesen, und die Gruppenansicht nennt solche Personen. Die Seite selbst erzeugt solche Codes nicht mehr (die Tests erzeugen sie über den Testhaken).

### URL-Parameter (Testparameter)

| Parameter | Wirkung |
|---|---|
| `?seed=abc` | reproduzierbare Zuteilung (und Kennung im Code). Für Tests und Proben. Mit Seed ist die Zuteilung **nicht** zufällig, im Unterricht nicht verwenden |
| `?neu=1` | verwirft einen gespeicherten Fortschritt in diesem Tab und beginnt neu |
| `?gruppe=1` | öffnet direkt «Gruppe auswerten» |

Parameter lassen sich kombinieren (`?seed=42&neu=1`).

### Neuladen, Neustart, Speicher

Der Fortschritt wird nur im `sessionStorage` des Tabs gehalten (Komfort, mit `try/catch`, Schlüssel `hsluP3ZustandV2`). Neuladen stellt den Stand wieder her (auch den begonnenen Text in Teil 1). Wer den Übergang oder Teil 2 erreicht hat, kommt auch nach Neuladen nicht mehr in Teil 1. Ein Speicherstand der früheren Seitenversion (v1) wird ignoriert. Ein neuer Tab oder ein privates Fenster beginnt neu mit **neuer** Zufallszuteilung. Ohne nutzbaren Speicher funktioniert die Seite vollständig, Neuladen startet dann aber von vorn. Es gibt absichtlich keinen sichtbaren «Neu starten»-Knopf, weil eine zweite Zuteilung die Versionen verraten würde. Die Auflösung ist nach Neuladen wieder verborgen.

## Ergebnis-Code (Format v2)

```
HSLU-hindsight-v2.<5 Datenzeichen><3 Zeichen Kennung><1 Prüfzeichen>
Beispiel: HSLU-hindsight-v2.37468zuj2
```

- **Datenzeichen** je Befund 1 bis 5: Ziffer 0 bis 9 = (Version A: 0, Version B: 5) + (Bewertung − 1); `x` = nicht bewertet. Beispiel `7` = Version B, Bewertung 3; `0` = Version A, Bewertung 1. **Befund 1 bis 5 meint die Seitenreihenfolge** (siehe Tabelle unten).
- **Kennung:** 3 Zeichen (0-9, a-z) zufällig, unterscheidet Personen mit gleichen Ergebnissen. Sie ist kein Name.
- **Prüfzeichen:** `(Σ Gewicht[i] · Wert[i]) mod 36` über die 8 Zeichen davor, Wert = Position in `0123456789abcdefghijklmnopqrstuvwxyz`, Gewichte `1 5 7 11 13 17 19 23` (alle teilerfremd zu 36). Erkennt jeden Einzelzeichen-Tippfehler (getestet: 18900 von 18900). Vertauschte Nachbarzeichen werden nicht immer erkannt (gemessen: etwa 6 % unerkannt).
- Gross-/Kleinschreibung beim Einlesen egal, Leerzeichen und unsichtbare Zeichen am Rand werden entfernt. Zwei Zeilen mit demselben Code gelten als Duplikat.
- **v1-Codes** (`HSLU-hindsight-v1.…`, neun Befunde) werden in «Gruppe auswerten» mit dem Hinweis «Code der früheren Seitenversion (v1, neun Befunde), wird nicht ausgewertet» zurückgewiesen.
- Keine Namen, keine Freitexte, keine Zeitangaben im Code.

## Auswahl der fünf Befunde (nicht öffentlich)

Kriterien in dieser Reihenfolge: (a) Version A fachlich tragfähig (gut repliziert oder Lehrbuchstandard, nicht aktuell stark umstritten), (b) die falsche Version B klingt mit ihrer Erklärung überzeugend, (c) neu für Studierende im 1. Semester (Sozialpsychologie-Grundlagen wie Konformität, Bystander-Effekt, Dissonanz, Einstellungen, Attribution wahrscheinlich bekannt), (d) inhaltlich abwechslungsreich.

Reihenfolge auf der Seite: 5, 3, 7, 9, 4 (Nummern im Auftrag). Der wahrscheinlich bekannteste Klassiker (Auftrag 4, Bystander) steht zuletzt, damit ein Erkennen die ersten vier Urteile nicht beeinflusst. Gleichartige Befunde («andere sind anwesend»: Auftrag 7 und 4) stehen nicht nebeneinander.

| Seite | Auftrag | Titel | Entscheid | Begründung |
|---|---|---|---|---|
| 1 | 5 | Gesichtsattraktivität und Durchschnittlichkeit | **gewählt** | A: Langlois und Roggman (1990): Mit mehr gemittelten Gesichtern steigt die Attraktivität (geprüft). Robust, nicht umstritten. B klingt sehr überzeugend («Durchschnitt ist langweilig»). Im Studium wahrscheinlich noch nicht behandelt. Vorbehalt: Durchschnitt ist nicht das Attraktivste (Perrett et al. 1994). |
| 2 | 3 | Belohnung und Motivation | **gewählt, mit Vorbehalt** | A: Lepper, Greene und Nisbett (1973); Metaanalyse Deci, Koestner und Ryan (1999): erwartete, tätigkeitsgebundene Belohnung untergräbt freie Wahl (d = −0.36), unerwartete nicht (d = 0.01). Breite des Effekts umstritten (Cameron und Pierce 1994). Gemischte Lage, aber metaanalytisch gestützt. B (Verstärkung) klingt plausibel. Schwächste Stelle bei (a) unter den gewählten, mit Vorbehalt in der Auflösung. |
| 3 | 7 | Anwesenheit anderer und Leistung | **gewählt** | A: Zajonc (1965), Metaanalyse Bond und Titus (1983, 241 Studien). B («Publikum motiviert») sehr plausibel. Vorbehalt: Replikation der Kakerlaken-Studie zeigte das Muster nur teilweise (Halfmann et al. 2020). Möglich, dass Studierende es aus Gruppenpsychologie kennen. |
| 4 | 9 | Aufmerksamkeit auf sich selbst | **gewählt** | A: Spotlight-Effekt, Gilovich, Medvec und Savitsky (2000), Lehrbuchstandard (Quelle geprüft). B («andere beobachten uns aufmerksam») ist alltagspsychologisch plausibel. Offen: Ich fand keine grosse unabhängige Replikation. |
| 5 | 4 | Gruppengrösse und Hilfeverhalten | **gewählt, schwächste Wahl bei (c)** | A: Darley und Latané (1968), Metaanalyse Fischer et al. (2011, 105 Effektstärken, g = −0.35, in gefährlichen Notfällen schwächer), bei realen Konflikten gegenläufig (Philpot et al. 2020). Tragfähig, aber das Klassikerbeispiel, das Studierende mit Sozialpsychologie-Grundlagen sehr wahrscheinlich kennen (A-Erklärung nennt «Verantwortungsdiffusion»). Gewählt, weil sonst kein Befund mit tragfähigem A übrig blieb (siehe unten). Steht zuletzt. |
| – | 1 | Glück und Auflistungsaufgaben | verworfen | Leichtigkeit des Abrufens: grosse vorregistrierte Replikation ohne Effekt (laut Sekundärquelle Groncki et al. 2021, N = 659; Yeager et al. 2019), Metaanalyse nach Korrektur für Publikationsverzerrung deutlich kleiner. Die konkrete Studie «Glück, 10 gegenüber 3 Ereignisse» konnte ich nicht identifizieren. Verstösst gegen (a). |
| – | 2 | Wahlmöglichkeiten und Zufriedenheit | verworfen | Wahlüberfluss: Metaanalyse mit Effekt nahe null (Angabe des Dozenten, von mir nicht selbst geprüft). Verstösst gegen (a), obwohl B sehr überzeugend wäre. |
| – | 6 | Einkommen und Lebenszufriedenheit | verworfen | Kahneman und Deaton (2010) betrifft das emotionale Wohlbefinden, nicht die Lebenszufriedenheit; Killingsworth (2021) und die Zusammenarbeit von 2023 widersprechen dem Plateau für die meisten (Angabe des Dozenten, nicht selbst geprüft). Verstösst gegen (a). |
| – | 8 | Wiederholung und Präferenz | verworfen | Mere Exposure bei *unangenehmen* Geräuschen: Der Effekt ist laut Montoya et al. (2017) bei neutralen oder leicht positiven Reizen am grössten und hebt starke Ablehnung nicht verlässlich auf (nur aus einer Sekundärzusammenfassung, nicht im Original gelesen). Verstösst gegen (a). |

**Warum ein Klassiker (Bystander) dabei ist:** Von den neun Befunden bleiben nach Kriterium (a) genau fünf übrig (3, 4, 5, 7, 9), wenn man die vier vom Dozenten angezweifelten Befunde (1, 2, 6, 8) ausschliesst. Kriterium (a) steht in der Reihenfolge vor (c). Befund 4 bleibt dabei der Kandidat, der Studierenden am ehesten verrät, dass sie hereingelegt werden. Alternative, falls der Dozent das nicht will: vier Befunde (5, 3, 7, 9), oder Befund 4 durch einen neuen Befund ersetzen, der nicht im Auftrag steht.

**Texte unverändert:** Alle Studien und Erklärungen (A und B) der fünf Befunde sind wörtlich aus dem Auftrag. Es wurde **nichts geändert** (kein eindeutiger sachlicher Fehler gefunden, der eine Version unhaltbar macht). Ungenauigkeiten sind als Vorbehalt in der Auflösung vermerkt (z. B. Befund 2: der Effekt gilt bei erwarteter Belohnung).

**Hinweis zum Aufbau der Texte:** Die A-Erklärungen enthalten oft Fachbegriffe («Spotlight-Effekt», «Verantwortungsdiffusion», «intrinsische Motivation», «dominante Reaktion»), die B-Erklärungen sind in Alltagssprache. Wer die Begriffe kennt, kann die echte Version daran erkennen. Das ist im Auftragstext angelegt und wurde nicht verändert.

## Ausnahme zu Regel 0.2 Punkt 8 (vom Dozenten gewollt)

Regel 0.2 Punkt 8 verbietet Lösungen auf der öffentlichen Seite. Die neue Auflösung ist **bewusst** Daten im Code: `befunde.js` enthält Version A (die tatsächliche Aussage), `quelle` und `vorbehalt`, `index.html` die Konstante `TATSAECHLICH = "A"` und zwei Texte der Gruppenauflösung. Wer den Quelltext öffnet, sieht beide Fassungen und kann erkennen, dass A die echte ist. Der Dozent nimmt das in Kauf (öffentliches Hosting, Dokumente im LMS). Die Oberfläche zeigt die Auflösung nur auf Klick. Der Inhalt der Auflösung wird erst beim Klick aufgebaut (vorher nicht im Seitentext).

## Inhalte ändern

- **Texte der Befunde:** stehen in `befunde.js`. Die Datei wird aus dem Auftrag erzeugt: `python3 -I tests/extract_befunde.py` (liest `../quellen/dokumente/10_einfuehrung2.md`, Aktivität 1; Auswahl und Reihenfolge in der Konstante `AUSWAHL`, Quellen und Vorbehalte in der Tabelle `META`). `python3 -I tests/test_daten.py` prüft danach, dass Seite und Auftrag wörtlich übereinstimmen. **Wird der Auftrag auf fünf Befunde umgeschrieben**, passen die Marker und Nummern im Skript nicht mehr: dann `befunde.js` von Hand pflegen und `test_daten.py` anpassen.
- **Datenstruktur** je Befund: `{ nr, titel, A: { studie, erklaerung }, B: { studie, erklaerung }, quelle, vorbehalt }`. A = tatsächliche Aussage gemäss Auftrag, B = gegenteilige Fassung. `*wort*` im Text wird als Kursivschrift angezeigt. `quelle` und `vorbehalt` erscheinen nur in der Auflösung, ein leeres Feld wird nicht angezeigt. Nur mit Inhalt füllen, der belegt ist.
- **Oberflächentexte** (Start, Fragen, Hinweise) stehen im JavaScript von `index.html`. Anrede überall «du».
- **Anzahl Befunde (5)** und die Regel «2 oder 3 Mal Version A» sind in `index.html` fest eingebaut (`ANZAHL`, `zuteilung()`, Code-Länge und Gewichte). Wer das ändert, muss auch den Code (Version v3) und die Tests anpassen.

## Link-Struktur für GitHub Pages

```
repo-root/
  shared/base.css
  p3-hindsight/index.html
  p3-hindsight/befunde.js
```

`index.html` bindet `../shared/base.css` relativ ein, daher muss `shared/` neben `p3-hindsight/` im Repo liegen. Studierende erhalten `https://<konto>.github.io/<repo>/p3-hindsight/`. Nicht ins öffentliche Repo gehören `tests/`, `screenshots/`, `README.md`, `TESTBERICHT.md`.

## Technische Eckdaten

- `lang="de"`, echte `<button>`, sichtbarer Fokus, Hell/Dunkel über `prefers-color-scheme`, `prefers-reduced-motion` (aus `base.css`). Klickflächen mindestens 44 px, ab 360 px Breite ohne horizontales Scrollen.
- Nach jedem Schritt wird der Fokus auf die Überschrift des neuen Bildschirms gesetzt (Tastatur und Screenreader).
- Eingaben der Nutzenden gelangen nie als HTML in die Seite (nur `textContent`).
- Gewicht: `index.html` etwa 45 KB, `befunde.js` etwa 6.5 KB.
- Testhaken: `window.P3` mit den reinen Funktionen `zuteilung`, `seededRng`, `cryptoRng`, `codeErzeugen`, `codeLesen`, `auswerten` und `zustand()` (Lesezugriff auf den Ablaufzustand). Die Tests nutzen ihn, die Bedienung nicht.

## Wunsch an `shared/base.css` (nicht geändert)

Die Rahmenfarbe `--border` der Eingabefelder und Knöpfe hat zum Hintergrund nur etwa 1.4:1 Kontrast (WCAG 1.4.11 verlangt 3:1 für Bedienelemente). Auf dieser Seite sind die Skalenknöpfe lokal dunkler gerahmt (`--muted`, 5.9:1). Für Textfelder gilt weiter `base.css`. Die Farbe `.badge.good` aus `base.css` erreicht auf ihrem Hintergrund nur 4.4:1 (AA verlangt 4.5:1); die Auflösung nutzt daher lokal eine eigene Markierung.

## Tests

Alle mit `python3 -I tests/<datei>.py` (Playwright für Python, Chromium). Ergebnisse siehe `TESTBERICHT.md`.

| Datei | Zweck |
|---|---|
| `extract_befunde.py` | erzeugt `befunde.js` aus dem Auftrag (Auswahl der fünf Befunde, Quellen, Vorbehalte) |
| `test_daten.py` | Daten gegen den Auftrag (zweiter Parser und Teilstring-Suche, Mutationstest), Auswahl, verworfene Befunde nicht in der Seite, neutrale Namen, Eszett, externe Verweise |
| `test_logik.py` | Zuteilung (1000 und 100000 Simulationen), Ergebnis-Code v2, v1 abgelehnt, Gruppenstatistik gegen Python-Referenz |
| `test_ui.py` | Durchläufe (Klick, Touch, Tastatur; http und file://), Randfälle, Auflösung, Layout, Kontrast, Screenshots |
| `test_dauer.py` | Dauer eines simulierten Durchlaufs in Echtzeit (`zuegig` oder `sorgfaeltig`) |
| `common.py` | gemeinsame Hilfen und die unabhängige Python-Referenz |

## Bekannte Grenzen

- **Keine Geheimhaltung im Quelltext.** Siehe «Ausnahme zu Regel 0.2 Punkt 8».
- **Mehrfaches Ausfüllen** (neuer Tab) ergibt eine neue Zuteilung und wird nicht verhindert.
- **Browser-Zurück:** In Teil 1 geht es einen Befund zurück, ab dem Übergang bleibt die Seite stehen (Hinweis). Wer den Ablauf verlassen will, schliesst den Tab. Auf der Zusammenfassung ist Zurück frei, braucht aber wegen der Verlaufseinträge mehrere Klicks.
- **Ohne `sessionStorage`** (z. B. gesperrte Website-Daten) geht ein Neuladen mitten im Ablauf verloren.
- **Kopieren** nutzt `navigator.clipboard`, mit Rückfall auf `execCommand`. Misslingt beides, erscheint die Anweisung, den Code von Hand zu markieren.
- **Kleine Gruppen:** Mit wenigen Personen beruhen die Mittelwerte pro Befund und Version auf wenigen Einzelwerten (n steht daneben). Keine Signifikanztests, keine Effektgrössen.
- **Browser:** getestet nur in Chromium (Desktop- und Handy-Emulation). Firefox und Safari (iOS) nicht getestet.
- **Zeit:** Die gemessene Dauer stammt von einem simulierten Nutzer (siehe TESTBERICHT), nicht von Studierenden.

## Fachliche Hinweise zur Prüfung

Stand der Prüfung: 15.10.2026, mit Websuche. **Geprüft** (Seite abgerufen, Inhalt gelesen): Langlois und Roggman 1990 (Zusammenfassung), Perrett, May und Yoshikawa 1994 (Zusammenfassung und Zitat), Deci, Koestner und Ryan 1999 (Zusammenfassung, Effektgrössen), Fischer et al. 2011 (Zusammenfassung und Zitat), Philpot et al. (Zusammenfassung; online 2019, Heft 2020 aus meinem Wissen), Halfmann, Bredehöft und Häusser 2020 (Zusammenfassung, Zitat), Gilovich, Medvec und Savitsky 2000 (Zitat, PMID 10707330), Bond und Titus 1983 (nur Zitat, 241 Studien, ohne Abstract). **Nur aus Sekundärquellen oder aus meinem Wissen, nicht am Original geprüft:** Seiten und Hefte von Lepper et al. 1973, Zajonc 1965, Darley und Latané 1968, Cameron und Pierce 1994; die Aussagen zu Cameron und Pierce, Groncki et al. 2021, Yeager et al. 2019 und Montoya et al. 2017 (Websummaries); Effektgrössen von Bond und Titus (deshalb nicht in der Seite). Der Dozent sollte die Quellenangaben vor der Veröffentlichung gegenlesen.

| Befund (Seite) | Bedenken | Vorschlag |
|---|---|---|
| **2** Belohnung und Motivation (Auftrag 3) | Die Aussage nennt nicht, dass der Effekt bei *erwarteter*, tätigkeitsgebundener Belohnung auftritt. Die Verallgemeinerung ist umstritten (Cameron und Pierce vs. Deci et al.). | Vorbehalt steht in der Auflösung. In der Nachbesprechung erwähnen. |
| **3** Anwesenheit anderer (Auftrag 7) | Die tierexperimentelle Grundlage (Kakerlaken) zeigte in der vorregistrierten Replikation keinen Unterschied einfach/komplex. Effektgrössen beim Menschen konnte ich nicht belegen. | Vorbehalt steht in der Auflösung. Quelle für Effektgrössen beim Menschen ergänzen. |
| **4** Spotlight (Auftrag 9) | Keine grosse unabhängige Replikation gefunden (nicht heisst nicht vorhanden). Die oft genannten Zahlen (rund die Hälfte gegenüber rund einem Viertel) stammen aus Sekundärquellen und stehen nicht auf der Seite. | `vorbehalt` leer. Bei Bedarf Belege ergänzen. |
| **5** Gruppengrösse und Hilfeverhalten (Auftrag 4) | Allgemeine Aussage; in gefährlichen Notfällen und realen Konflikten abgeschwächt oder gegenläufig. Zudem für Studierende wahrscheinlich bekannt. | Vorbehalt steht in der Auflösung. |
| **1** Gesichtsattraktivität (Auftrag 5) | Die A-Erklärung («Mutationen», «sicherer Partner») ist nur eine von mehreren Erklärungen (auch kognitiv: Prototypen). Gemittelte Gesichter sind nicht die attraktivsten. | Vorbehalt steht in der Auflösung. |
| Verworfen: Auftrag 1, 2, 6, 8 | siehe Tabelle «Auswahl» | Falls im Auftragsdokument beibehalten, dort mit Vorbehalt versehen oder ersetzen. |

Weitere Hinweise zum Text (keine fachlichen Änderungen, nur gemeldet):

- **Bindestrich als Gedankenstrich** («Verantwortungsdiffusion" - jeder…», «Publikum motiviert zu Höchstleistungen - Menschen…») und gerade Anführungszeichen: wörtlich übernommen, nicht typografisch angepasst.
- **«ihr/ihre»** in den Studientexten meint die 3. Person («ihre Kleidung»), keine Anrede. Nicht auf «du» umgestellt. Nur Fragen und Oberfläche sind in «du».
- **Fragetexte** («Wie würdest du diesen Befund erklären?», «Wie plausibel wirkt diese Erklärung jetzt auf dich?») sind neu gemäss Rückmeldung des Dozenten. Die frühere Frage «Wie offensichtlich findest du diesen Befund jetzt, da du die Erklärung kennst?» entfällt.
- **Schreibung «Gruppengrösse», «Mittelmass»:** wörtlich aus dem Auftrag («ss» statt Eszett).

## Offene Fragen an den Dozenten

1. **Befund 5 (Bystander, Auftrag 4)** ist der Klassiker, den Studierende wahrscheinlich kennen. Behalten, durch einen anderen Befund ersetzen (müsste neu belegt werden) oder nur mit vier Befunden arbeiten?
2. **Befund 2 (Belohnung, Auftrag 3)**: Die Aussage gilt nur bei erwarteter Belohnung. Auftragstext so lassen, oder die Aussage um «erwartet» ergänzen?
3. **Dauer:** Die Startseite sagt «etwa 6 bis 8 Minuten». Der simulierte zügige Durchlauf dauerte 3.9 Minuten, der sorgfältige 7.1 Minuten (inklusive Startseite; Modell, siehe TESTBERICHT). Nach einer Probe mit Studierenden anpassen.
4. **Quellenangaben** in `quelle`/`vorbehalt` gegenlesen (siehe «Fachliche Hinweise»). Sollen sie überhaupt in der Auflösung stehen?
5. **Zuordnung A/B im Code:** A ist immer die tatsächliche Aussage. Wer im Quelltext liest, erkennt es. Mit der Ausnahme zu 0.2.8 vereinbar, oder soll die Ablage pro Befund zufällig vertauscht werden (dann braucht die Fachperson eine private Zuordnungsliste)?
6. **Zuteilung:** Jede Kombination mit 2 oder 3 Mal Version A ist zulässig (20 Muster, gleich wahrscheinlich). Gewollt oder nur eine feste Auswahl von Mustern?
7. **«Gruppe auswerten»** ist nur noch auf der Zusammenfassung verlinkt (und über `?gruppe=1`), damit niemand vor dem Durchlauf zur Auflösung gelangt. Einverstanden?
8. **Vorzeitig beenden** wurde gestrichen (siehe oben). Einverstanden?
9. **Auflösung auf der Zusammenfassung:** Sie ist für jede Person jederzeit per Klick erreichbar (nur mit Hinweis geschützt). Soll sie nur in der Fachpersonen-Ansicht (`?gruppe=1`) erscheinen?

## Änderungsliste für das Auftragsdokument (Aktivität 1)

- Ablauf: zwei Teile statt je Befund zwei Seiten. Teil 1 «Aussagen beurteilen» (alle 5 Aussagen, Stichworte genügen, Zurück erlaubt), Teil 2 «Erklärungen einordnen» (Erklärung, Plausibilität 1 bis 5, kein Zurück).
- Anzahl Befunde: 5 statt 9 (Auftrag 5, 3, 7, 9, 4 in dieser Reihenfolge).
- Zuteilung im Browser: pro Person und Befund zufällig Version A (echt) oder B (gegenteilig), 2 oder 3 Mal A bei 5 Befunden. Entfällt: 9 Google Forms, allocate.monster (Master- und Gruppen-Links), Beispielkombinationen, «10 bis 12 Minuten».
- Fragen im Wortlaut: «Wie würdest du diesen Befund erklären?» (Hinweis: Stichworte genügen: ein bis zwei Wörter oder ein kurzer Halbsatz) und «Wie plausibel wirkt diese Erklärung jetzt auf dich?» (1 = gar nicht plausibel, 5 = sehr plausibel).
- Auflösung: Knopf «Auflösung anzeigen» auf der Zusammenfassung und in «Gruppe auswerten», erst nach dem Gruppenvergleich öffnen.
- Ergebnis-Code v2 (`HSLU-hindsight-v2.…`), v1-Codes werden nicht ausgewertet. Parameter `?seed`, `?neu=1`, `?gruppe=1`. Dauer etwa 6 bis 8 Minuten.
