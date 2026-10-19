| Test | Geraet | Ergebnis | Detail |
|---|---|---|---|
| 19 Episoden in der verlangten Reihenfolge-Menge, 38 Optionen | - | OK | 19 Episoden |
| 10 Mikroszenen M1-M10 mit je zwei Optionen | - | OK |  |
| Word: 19 Episoden und 10 Mikroszenen unabhaengig gelesen | - | OK | 19 / 10 |
| Word gegen Daten: Titel, Vorlesen, 38 Optionen (Text, Folge, Wuerfeltitel), Weiter bei, Glücksfaktoren, Erkenntnis | - | OK |  |
| Word gegen Daten: Mikroszenen (Titel, Vorlesen, Optionen, Wertaenderungen A/B, Glücksfaktoren) | - | OK |  |
| Excel gegen Daten: Soll-Wert, 5 Aenderungen, Energie-Basis, Beginn-Aenderungen in allen 38 Zeilen | - | OK |  |
| Gewichte in der Konfiguration = Excel AP3:AU3 (Zeile 3, in allen Zeilen gleich) | - | OK | {'zeit': 0.25, 'energie': 0.3, 'soz': 0.2, 'erfuellung': 0.55, 'lebensstil': 0.45, 'finanzen': 0.25} |
| Krisenepisoden 12A1-12B2: Beginn Stimmung -10, Soll 16 bis 20 | - | OK |  |
| 4096 moegliche Wege, alle genau 12 Episoden lang, alle 19 Episoden erreichbar | - | OK | 4096 Wege |
| tools/erzeuge_daten.py erzeugt spiel-daten.js byte-identisch neu | - | OK |  |
| spiel-texte.js: Episoden = Episoden der erzeugten Daten, je Episode Ausrichtung, Ablenker und Ergebnistexte | - | OK | 19 Episoden |
| Ausrichtung: je Episode eine langfristige und eine kurzfristige Option (19 x), gleich der Referenztabelle; unscharfe Episoden ['11B', '12A2', '12B2', '6', '8A', '8B'] begruendet | - | OK |  |
| Ausrichtung: Ausnahme 11B (A langfristig, B kurzfristig) und sonst A kurzfristig, B langfristig | - | OK |  |
| Ablenker: 6 bis 8 Eintraege je Episode, mindestens 2 plausible und 2 unplausible, keine Doppelten, keine Behauptungen, keiner aehnelt einem echten Faktor | - | OK | Anzahl je Episode 7 bis 7; 43 plausible, 53 unplausible Ablenker |
| Ablenker: kein Ablenker kommt in zwei Episoden vor (kein Muster «immer wieder derselbe Ablenker») | - | OK | [] |
| Echte Faktoren: Kurzname (ohne Code und Klammerzusatz) aus den Daten, 3 bis 70 Zeichen | - | OK | 37 echte Faktoren in 19 Episoden |
| Hinweis: Glücksfaktoren mit Option-Buchstaben im Wort (werden bei vertauschten Buchstaben umgeschrieben) | - | OK | 12 Eintraege, Episoden ['10', '11A', '11B', '12A1', '12A2', '12B1', '12B2', '6', '7'] |
| Gesamtgroesse index.html + Daten + Texte + Kern unter 300 KB (ohne Bilder) | - | OK | 148 KB |
| Keine externen Adressen (http/https/CDN) im Code ausser Namespace | - | OK | ['http://www.w3.org/2000/svg">\';'] |
| Klassische Skripte: kein type=module, kein import/export, kein fetch/XMLHttpRequest | - | OK |  |
| Relative Pfade: shared/base.css, spiel-daten.js, spiel-texte.js, spiel-kern.js eingebunden | - | OK |  |
| lang="de", Viewport-Meta, kein Eszett in Quelltext und Daten | - | OK |  |
| Verbotener Inhalt nicht im Quelltext: «Pädagogische Kernidee» | - | OK |  |
| Verbotener Inhalt nicht im Quelltext: «Mini-Debriefing» | - | OK |  |
| Verbotener Inhalt nicht im Quelltext: «Wissenschaftliche Basis» | - | OK |  |

Gesamt: 25 Pruefungen, 0 Fehler
