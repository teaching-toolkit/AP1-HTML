| Test | Geraet | Ergebnis | Detail |
|---|---|---|---|
| A/B: Anteil vertauscht je Episode (2000 Seeds), alle 19 Episoden innerhalb 4 Sigma | Desktop | OK | kleinster Anteil 0.478, groesster 0.518 (n=2000) |
| A/B: Gesamtanteil vertauscht ca. 50 % (2000 Seeds) | Desktop | OK | 0.4981 |
| A/B: benachbarte Episoden unabhaengig (2000 Seeds): Anteil gleicher Paare ca. 50 % | Desktop | OK | 0.4939 |
| A/B: Muster der 19 Bits verschieden (Doppelte nur im Rahmen des Geburtstagsparadoxons) (2000 Seeds) | Desktop | OK | 1997 von 2000 (zufaellige Doppelte erwartet: 4) |
| A/B: Anteil vertauscht je Episode (4000 Spiele mit crypto.getRandomValues), alle 19 Episoden innerhalb 4 Sigma | Desktop | OK | kleinster Anteil 0.479, groesster 0.517 (n=4000) |
| A/B: Gesamtanteil vertauscht ca. 50 % (4000 Spiele mit crypto.getRandomValues) | Desktop | OK | 0.5001 |
| A/B: benachbarte Episoden unabhaengig (4000 Spiele mit crypto.getRandomValues): Anteil gleicher Paare ca. 50 % | Desktop | OK | 0.5034 |
| A/B: Muster der 19 Bits verschieden (Doppelte nur im Rahmen des Geburtstagsparadoxons) (4000 Spiele mit crypto.getRandomValues) | Desktop | OK | 3986 von 4000 (zufaellige Doppelte erwartet: 15) |
| A/B: Seite ohne Seed benutzt crypto.getRandomValues und nie Math.random (40 Ladevorgaenge) | Desktop | OK |  |
| A/B: 40 Spiele ohne Seed haben 40 verschiedene Muster, Anteil vertauscht ca. 50 % | Desktop | OK | 40 Muster, 393 von 760 vertauscht |
| A/B: Seite mit ?seed= benutzt weder crypto noch Math.random | Desktop | OK | [0, 0] |
| ?ab=fest: alle 19 Episoden unvertauscht, Modus «fest» | Desktop | OK | fest |
| ?ab=tausch: alle 19 Episoden vertauscht, Modus «tausch» | Desktop | OK | tausch |
| Standard: Modus «zufall», gemischt | Desktop | OK | 8 von 19 vertauscht |
| Unbekannter Wert bei ?ab= wirkt wie der Standard | Desktop | OK | zufall |
| ?seed= reproduzierbar: gleicher Seed, gleicher Plan (A/B und Reihenfolge) | Desktop | OK |  |
| Anderer Seed gibt anderen Plan | Desktop | OK |  |
| Reihenfolge der Kandidaten haengt nicht vom ab-Modus ab (gleicher Seed in allen drei Modi) | Desktop | OK |  |
| Plan zum Seed '7' stimmt mit unabhaengiger Python-Fassung ueberein (A/B und Reihenfolge, 19 Episoden) | Desktop | OK |  |
| Plan zum Seed '8' stimmt mit unabhaengiger Python-Fassung ueberein (A/B und Reihenfolge, 19 Episoden) | Desktop | OK |  |
| Plan zum Seed 'abc' stimmt mit unabhaengiger Python-Fassung ueberein (A/B und Reihenfolge, 19 Episoden) | Desktop | OK |  |
| Wuerfelfolge zu ?seed=5 ist in allen Modi gleich und entspricht FNV-1a/mulberry32 (unveraendert) | Desktop | OK | [5, 20, 13, 10, 16, 8] gegen [5, 20, 13, 10, 16, 8] |
| Zuordnung ueber die Oberflaeche, Modus fest: 38 Faelle (19 Episoden x A/B), Karte, Regeloption, Rechnung, Verzweigung, Protokoll | Desktop | OK | 38 Faelle, 0 mit vertauschten Buchstaben;  |
| Konsole/Anfragen ohne Fehler (Zuordnung fest) | Desktop | OK | [] |
| Zuordnung ueber die Oberflaeche, Modus tausch: 38 Faelle (19 Episoden x A/B), Karte, Regeloption, Rechnung, Verzweigung, Protokoll | Desktop | OK | 38 Faelle, 38 mit vertauschten Buchstaben;  |
| Konsole/Anfragen ohne Fehler (Zuordnung tausch) | Desktop | OK | [] |
| Zuordnung ueber die Oberflaeche, Modus zufall (Seed 11): 38 Faelle (19 Episoden x A/B), Karte, Regeloption, Rechnung, Verzweigung, Protokoll | Desktop | OK | 38 Faelle, 22 mit vertauschten Buchstaben;  |
| Konsole/Anfragen ohne Fehler (Zuordnung zufall (Seed 11)) | Desktop | OK | [] |
| Ausrichtung waehrend des Spiels nirgends sichtbar (zufall (Seed 21)): Text, Attribute, Ansage, alle Phasen von 12 Episoden | Desktop | OK |  |
| Plan (A/B und Reihenfolge) bleibt waehrend des ganzen Spiels unveraendert (zufall (Seed 21)) | Desktop | OK | [] |
| Abschluss erreicht, 12 Episoden im Protokoll (zufall (Seed 21)) | Desktop | OK | abschluss |
| Abschluss (zufall (Seed 21)): je Episode die richtige Ausrichtung (Wert und Anzeigetext) | Desktop | OK | ['kurzfristig', 'kurzfristig', 'kurzfristig', 'langfristig'] |
| Abschluss (zufall (Seed 21)): je Episode der angezeigte Buchstabe und der Name der Option | Desktop | OK | Option A · BWL studieren |
| Abschluss (zufall (Seed 21)): Zaehlzeile stimmt (5 x langfristig, 7 x kurzfristig, Summe 12) | Desktop | OK | Gewählte Ausrichtung: 5 × langfristige Investition, 7 × kurzfristige Optimierung. |
| Abschluss (zufall (Seed 21)): Hinweis zur Verteilung der Buchstaben passt zum Modus | Desktop | OK | Während des Spiels war die Ausrichtung nicht sichtbar, und die Buchstaben A und B waren pr |
| Abschluss (zufall (Seed 21)): Stern nur bei unscharfer Zuordnung | Desktop | OK |  |
| Konsole/Anfragen ohne Fehler (Sichtbarkeit zufall (Seed 21)) | Desktop | OK | [] |
| Ausrichtung waehrend des Spiels nirgends sichtbar (fest): Text, Attribute, Ansage, alle Phasen von 12 Episoden | Desktop | OK |  |
| Plan (A/B und Reihenfolge) bleibt waehrend des ganzen Spiels unveraendert (fest) | Desktop | OK | [] |
| Abschluss erreicht, 12 Episoden im Protokoll (fest) | Desktop | OK | abschluss |
| Abschluss (fest): je Episode die richtige Ausrichtung (Wert und Anzeigetext) | Desktop | OK | ['kurzfristig', 'langfristig', 'kurzfristig', 'langfristig'] |
| Abschluss (fest): je Episode der angezeigte Buchstabe und der Name der Option | Desktop | OK | Option A · BWL studieren |
| Abschluss (fest): Zaehlzeile stimmt (7 x langfristig, 5 x kurzfristig, Summe 12) | Desktop | OK | Gewählte Ausrichtung: 7 × langfristige Investition, 5 × kurzfristige Optimierung. |
| Abschluss (fest): Hinweis zur Verteilung der Buchstaben passt zum Modus | Desktop | OK | Während des Spiels war die Ausrichtung nicht sichtbar. * Bei dieser Episode ist die Einord |
| ?ab=fest: angezeigter Buchstabe = Regeloption in allen 12 Episoden (alte Zuordnung) | Desktop | OK |  |
| Abschluss (fest): Stern nur bei unscharfer Zuordnung | Desktop | OK |  |
| Konsole/Anfragen ohne Fehler (Sichtbarkeit fest) | Desktop | OK | [] |
| Rueckgaengig nach Wahl (Tausch): Phase, Wahl, Anzeigebuchstabe leer, Plan gleich, Karten unveraendert, danach andere Wahl richtig | Desktop | OK | True True True True |
| Rueckgaengig nach Wurf: wieder in «Wuerfeln», gleiche Wahl (Regeloption A, angezeigt B), Gewaehlt-Zeile stimmt | Desktop | OK | B · BWL studieren |
| Zweites Rueckgaengig: wieder Entscheidung, Plan gleich | Desktop | OK |  |
| Spiel mit Umwegen (Wahl, Wurf, Folgen, Rueckgaengig, ueber Episodengrenzen) endet im gleichen Zustand wie das gerade Spiel | Desktop | OK | abweichend: [] |
| Konsole/Anfragen ohne Fehler (Rueckgaengig) | Desktop | OK | [] |
| Neuladen (ohne Parameter) in 10 Phasen: Zustand, Anzeige und Plan unveraendert (Tausch) | Desktop | OK |  |
| Nach dem Neuladen: Wahl folgt weiter dem gespeicherten Plan | Desktop | OK |  |
| Rueckgaengig reicht ueber das Neuladen hinweg zurueck | Desktop | OK | mikro-folgen |
| Neues Spiel (mit Seed): zweiter Plan ist die Fortsetzung des Zufallsstroms (unabhaengige Python-Fassung) und anders als der erste | Desktop | OK |  |
| Neues Spiel (ohne Seed): neuer zufaelliger Plan (A/B und Reihenfolge) | Desktop | OK |  |
| Konsole/Anfragen ohne Fehler (Neuladen) | Desktop | OK | [] |
| Mikroszenen bleiben unvertauscht (A/B wie im Word) auch bei ?ab=tausch; Protokoll ohne Anzeigebuchstabe; Plan der Episoden unveraendert | Desktop | OK |  |
| Konsole/Anfragen ohne Fehler (Mikroszenen) | Desktop | OK | [] |
| Phone 390x844 Touch: 6 Episoden mit zufaelliger Zuordnung (1 vertauscht), Karte, Wahl, kein horizontaler Scroll | Phone | OK |  |
| Konsole/Anfragen ohne Fehler (Phone A/B) | Phone | OK | [] |

Gesamt: 62 Pruefungen, 0 Fehler
