# TESTBERICHT P3 (Forschungsbefunde / Hindsight-Bias-Experiment), überarbeitete Fassung mit 5 Befunden

Stand: 15.10.2026. Werkzeug: Playwright für Python, Chromium (Desktop 1280x800 mit Maus; Handy 390x844 und 360x740, Tablet 768x1024, jeweils mit Touch und `is_mobile`). Seiten über lokalen Server (`http://127.0.0.1`) **und** über `file://`. Alle Skripte laufen mit `python3 -I tests/<datei>.py`. Dieser Bericht verrät die Zuordnung A = echt und gehört nicht ins öffentliche Repo.

## Ergebnis in Zahlen

| Skript | Prüfungen | bestanden |
|---|---|---|
| `test_daten.py` | 23 | 23 |
| `test_logik.py` | 24 | 24 |
| `test_ui.py` | 164 | 164 |
| **Summe** | **211** | **211** |

Dazu zwei Zeitmessungen (`test_dauer.py`, siehe unten). Alle drei Skripte wurden am Ende nochmals vollständig ausgeführt. `shared/` und `quellen/` wurden nicht verändert (keine neueren Dateien als die Arbeitsstände von `p3-hindsight/`). Eine Suche nach dem Eszett im ganzen Projektordner ist leer (auch als Test in `test_daten.py`).

## Dauer eines Durchlaufs (Pflichtangabe)

Gemessen wird in Echtzeit mit einem **simulierten Nutzer** (Handy 390x844, Touch), von der Startseite (inklusive Lesezeit) bis zur Zusammenfassung. Das ist ein Modell, keine Messung mit Studierenden.

| Profil | Modellannahmen | Gesamt inkl. Startseite | Ab «Starten» | Teil 1 | Teil 2 |
|---|---|---|---|---|---|
| zügig | 250 Wörter/min, 15 s Nachdenken pro Befund, 5 Anschläge/s (23 Zeichen Stichworte), 3 s Überfliegen, 8 s Bewerten | **236 s = 3.9 min** | 211 s = 3.5 min | 114 s | 84 s |
| sorgfältig | 150 Wörter/min, 30 s Nachdenken, 3 Anschläge/s, 5 s Überfliegen, 15 s Bewerten | **426 s = 7.1 min** | 384 s = 6.4 min | 214 s | 148 s |

Gelesen werden 181 Wörter in Aussagen und Erklärungen, 105 auf der Startseite, 54 auf dem Übergang. Die Zielvorgabe von 6 bis 8 Minuten wird vom sorgfältigen Profil erreicht (7.1 min), vom zügigen unterschritten (3.9 min). Echte Studierende liegen vermutlich dazwischen oder darüber (Nachdenken, längere Stichworte, Ablenkung). Die Startseite sagt «Plane etwa 6 bis 8 Minuten ein»; das ist eine Annahme, die nach einer Probe mit Studierenden geprüft werden sollte.

## Tests im Einzelnen

| Test | Gerät | Ergebnis |
|---|---|---|
| `befunde.js` wird aus dem Auftrag per Skript erzeugt (Auftragsbefunde 5, 3, 7, 9, 4) und ist beim zweiten Erzeugen byte-identisch | – | bestanden |
| 5 Titel + 20 Texte (Studie/Erklärung, A/B) stimmen mit dem Auftrag überein: unabhängiger zweiter Parser, Teilstring-Suche im Roh-Markdown, Daten in Node und im Browser (file://) gleich; keine Umformung nötig | Node, Chromium | bestanden (Mutationstest: 3 absichtlich geänderte Texte werden erkannt) |
| Felder exakt `nr, titel, A, B, quelle, vorbehalt`; Quelle bei allen 5, Vorbehalt bei 4 (leer nur bei Befund 4) | – | bestanden |
| Die 4 verworfenen Befunde (Auftrag 1, 2, 6, 8) stehen weder in `index.html` noch in `befunde.js` | – | bestanden |
| Im Auftrag ist bei allen gewählten Befunden Version A mit «(ECHT)» gekennzeichnet | – | bestanden |
| Keine Wörter echt/falsch/real/fake in Schlüsseln, Bezeichnern, Kommentaren (Ausnahme: zwei Auflösungstexte); kein «Sie/Ihr/euch»; kein Eszett; keine http(s)-Verweise, keine Module, kein fetch; Gewicht 51.8 KB (index.html 45.4 KB, befunde.js 6.5 KB) | – | bestanden |
| Zuteilung, 1000 Simulationen mit `crypto.getRandomValues`: immer 2 oder 3 A bei 5 Befunden (1000/1000); 2 A: 507, 3 A: 493; A pro Befund 1..5: 506, 535, 483, 480, 489; 10 Paarhäufigkeiten gegen 0.20 unauffällig | Chromium | bestanden |
| Dasselbe mit Seeds sim0..sim999: 1000/1000 gültig; 2 A: 497, 3 A: 503 | Chromium | bestanden |
| 100000 Läufe: nur die 20 gültigen Muster, Gleichverteilung (chi2 = 16.7, p = 0.612, Minimum 4906, Maximum 5123, erwartet 5000); Anteil A pro Befund 0.499 bis 0.502 | Chromium | bestanden |
| Negativkontrolle: absichtlich verzerrter Zuteiler fällt durch (p = 2e-20) | Chromium | bestanden |
| Seed reproduzierbar (gleicher Seed gleiche Zuteilung, anderer Seed andere) | Chromium | bestanden |
| Ergebnis-Code v2: 500 Zufallscodes, Erzeugen und Lesen in JS gleich unabhängiger Python-Implementierung; alle 50 Kombinationen Befund x Version x Bewertung Rundreise; 18900 Einzelzeichen-Ersetzungen alle erkannt; Syntax-Grenzfälle (16), Grund wird genannt | Chromium | bestanden |
| Alter v1-Code wird abgelehnt mit Grund «Code der früheren Seitenversion (v1, neun Befunde), wird nicht ausgewertet» (Logik und Gruppenansicht, eigener Hinweis) | Chromium | bestanden |
| Gruppenstatistik: 80 Zufallsgruppen (0 bis 8 Personen, Duplikate, ungültige Zeilen, v1-Codes, Leerzeilen, unvollständige Personen), Zähler, n und Mittelwerte gleich Python | Chromium | bestanden |
| Vollständiger Durchlauf (Teil 1, Übergang, Teil 2), jeder Bildschirm gegen den Auftragstext geprüft, Code gültig und gleich dem Zustand | Desktop Klick, Handy 390x844 Touch, Desktop Tastatur, je http und file:// (6 Läufe) | bestanden |
| Auf allen 13 Bildschirmen vor der Auflösung kein Hinweis auf Versionen/echt/falsch; «hindsight» nur im Code; Anrede «du» | wie oben | bestanden |
| Kein Konsolenfehler, kein pageerror, keine externe oder fehlgeschlagene Anfrage; nur `index.html`, `base.css`, `befunde.js` geladen | wie oben | bestanden |
| Startseite: «Stichworte genügen», «6 bis 8 Minuten», Teil 1 und Teil 2; keine Rede von Google Forms, allocate.monster, neun Befunden, 10 bis 12 Minuten; kein Link «Gruppe auswerten» | Desktop | bestanden |
| Teil 1: Frage, sichtbarer Hinweis «Stichworte genügen», Fortschritt «Befund n von 5», keine Erklärung/Skala; leer erlaubt; Zähler; Zurück-Knopf ab Befund 2, Text bleibt erhalten; Browser-Zurück geht einen Befund zurück, bei Befund 1 Hinweis; Entwurf bleibt nach Neuladen | Desktop | bestanden |
| Übergang: erklärt Teil 2, kein Zurück, Browser-Zurück bleibt mit Hinweis | Desktop | bestanden |
| Teil 2 ohne Weg zurück: kein Zurück-Knopf, Browser-Zurück (3 Mal) bleibt auf Teil 2 mit Hinweis, Neuladen stellt denselben Befund mit gleicher Zuteilung wieder her, Teil 1 nicht erreichbar (http und file://) | Desktop | bestanden |
| Teil 2: Aussage, eigene Stichworte, Erklärung, Frage «Wie plausibel wirkt diese Erklärung jetzt auf dich?», Skalenenden; Weiter ohne Auswahl gesperrt (Knopf, Enter, Submit), nichts vorgewählt | Desktop | bestanden |
| Skala per Tab und Pfeiltasten, Ziffern 1 bis 5, Enter/Leertaste zum Weiter; Rahmenkontrast der Skala 5.9:1 hell, 7.2:1 dunkel (WCAG 1.4.11: 3:1) | Desktop, Handy | bestanden |
| «Vorzeitig beenden» gibt es nicht mehr (kein Knopf im ganzen Ablauf) | Desktop | bestanden |
| Zusammenfassung «Deine fünf Berichte», leere Stichworte als «(leer gelassen)», Code gültig, Neuladen zeigt dasselbe, Auflösung danach wieder verborgen | Desktop, Handy | bestanden |
| Auflösung nur nach Klick: vorher nichts davon im DOM (kein «tatsächlich», keine Quelle); nachher pro Befund tatsächliche Aussage (A) mit Erklärung, Quelle bei 5, Vorbehalt bei 4; «verbergen» blendet aus; eigene Version markiert | Desktop, Handy, alle 6 Läufe | bestanden |
| Layout: kein horizontaler Scroll, alle Klickflächen mindestens 44 px, kein Text läuft aus seinem Kasten (auch 200 Zeichen ohne Leerzeichen), Textkontrast mindestens AA, je 11 Bildschirme | 360, 390, 768, 1280 px; dazu dunkel 390 und 1280 | bestanden |
| Negativkontrollen der Layoutprüfung (20-px-Knopf, 900-px-Element, überlaufender Text, hellgrauer Text) werden erkannt | 360 px | bestanden |
| Randfälle: gleicher Seed stellt Fortschritt wieder her, anderer Seed/`?neu=1` beginnt neu, alter v1-Speicherstand wird ignoriert; ohne `sessionStorage` voller Durchlauf; fehlende `befunde.js` ergibt verständliche Meldung | Desktop | bestanden |
| Eingaben als Text, nie als HTML (Stichworte in Teil 2 und Zusammenfassung, ungültige Gruppenzeilen) | Handy | bestanden |
| Gruppenansicht vor Eingabe: kein Wort «Version», keine Tabelle; `?gruppe=1` öffnet sie direkt | Desktop | bestanden |
| Code-Rundreise: eigene Daten erscheinen unverändert in «Gruppe auswerten» (5 Befunde, richtige Version, gleiche Bewertung) | Desktop | bestanden |
| Gruppe aus 5 Personen (4 per UI: 2 Desktop/Maus, 2 Handy/Touch; 1 unvollständig mit 3 von 5 über den Testhaken) plus 2 ungültige Zeilen (Prüfzeichen, v1), 1 Duplikat, Leerzeilen: Chips, Meldungen mit Zeilennummer und Grund, unvollständige Person benannt, alle 5x2 Mittelwerte und n sowie Gesamtzeile (A: 2.33, n = 9; B: 3.64, n = 14) gleich unabhängiger Python-Rechnung | Desktop, Handy | bestanden |
| Gruppenansicht neutral («Version A / Version B»), bis «Auflösung anzeigen» geklickt wird; danach «Version A (echt)» / «Version B (gegenteilig)» plus Auflösungsliste, Zahlen unverändert; «verbergen» stellt Neutralität wieder her | Desktop | bestanden |
| Nur ungültige Zeilen, nur v1-Codes, nur Leerzeilen, derselbe Code 4 Mal (1 Person, 3 Duplikate) | Desktop | bestanden |
| «Code kopieren»: Zwischenablage gleich Code (http); Meldung über file:// (Rückfall) | Desktop | bestanden |

## Fehler beim Entwickeln und Testen (behoben)

1. Tippmarkierung (Tap-Highlight) auf der Skala und «Weiter» nicht volle Breite auf dem Handy: CSS und Klasse angepasst, Test bestätigt.
2. `.badge.good` erreichte nur 4.40:1 Kontrast: eigene `.marke`-Klassen mit ausreichendem Kontrast.
3. Gruppenansicht nannte vor der Eingabe schon «Version»: neutral formuliert, Test «kein Wort Version vor Eingabe».
4. Übergangsseite sagte «in Teil 2», obwohl man noch davor ist: «ab Teil 2».
5. Ein ganzseitiger Screenshot der Auflösung war unlesbar klein: Element-Screenshots.
6. Testfehler (nicht Seitenfehler): Mutationstest ersetzte ein Wort durch Text, der im Auftrag vorkommt (jetzt `mehr` zu `weniger`); `document.body.textContent` enthielt Skripttext (jetzt `#main`); falscher Prüfzeichen-String für den ungültigen Code; v1-Speicherschlüssel auch unter neuem Schlüssel.

## Nicht getestet (mit Grund)

- **Echte Studierende, echte Lesezeiten:** nicht möglich, Dauer nur simuliert (Modell oben).
- **Firefox, Safari, iOS, echte Handys:** nur Chromium mit Handy-Emulation verfügbar.
- **Screenreader** (NVDA, VoiceOver): nur Struktur, Fokus und Tastatur geprüft.
- **GitHub Pages selbst** (HTTPS, Gross-/Kleinschreibung der Pfade): lokal nicht prüfbar.
- **Einfügen aus der echten Zwischenablage** in «Gruppe auswerten»: Text wird per Skript eingesetzt.
- **Fachliche Quellenangaben:** Die Zitate wurden nur mit Websuche abgeglichen, nicht anhand der Originalartikel. Lepper, Greene & Nisbett (1973) und Zajonc, Heingartner & Herman (1969) stammen aus dem Fachwissen und sind nicht gesondert geprüft. Siehe README, Abschnitt «Fachliche Hinweise».
- Vertauschte Nachbarzeichen im Code werden zu etwa 6 % nicht erkannt (gemessen: 93 von 1500). Einzelzeichenfehler werden garantiert erkannt.

## Screenshots (`screenshots/`, JPEG, 25 Dateien)

Desktop: `desktop-1-start`, `desktop-2-teil1`, `desktop-2b-teil1-befund3`, `desktop-3-uebergang`, `desktop-4-teil2`, `desktop-5-zusammenfassung`, `desktop-6-aufloesung`, `desktop-7-gruppe`, `desktop-8-gruppe-aufloesung`, dunkel: `desktop-dunkel-4-teil2`, `-6-aufloesung`, `-7-gruppe`.
Handy (390x844): dieselben Zustände `handy-1` bis `handy-8`, dunkel: `handy-dunkel-1-start`, `-4-teil2`, `-6-aufloesung`, `-7-gruppe`.
Alle Zustände wurden mit dem Read-Werkzeug angesehen; die Bilder werden bei jedem Lauf von `test_ui.py` neu erzeugt.
