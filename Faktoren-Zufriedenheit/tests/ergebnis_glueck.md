| Test | Geraet | Ergebnis | Detail |
|---|---|---|---|
| Vor dem Klick, alle 19 Episoden: 6 bis 8 gleich aufgebaute Eintraege (echte Faktoren + Ablenker), keine Markierung, kein Urteil, keine Erkenntnis, keine Codes im DOM | Desktop | OK | 19 Episoden;  |
| Konsole/Anfragen ohne Fehler (verdeckt) | Desktop | OK | [] |
| Nach «Loesung zeigen» (?ab=fest), alle 19 Episoden: echte Faktoren mit bestehendem Text (Option-Buchstaben der Anzeige angepasst), Ablenker als «Hier nicht entscheidend» / «Unplausibel», Erkenntnisse, keine Knoepfe mehr | Desktop | OK |  |
| Konsole/Anfragen ohne Fehler (Freigabe fest) | Desktop | OK | [] |
| Nach «Loesung zeigen» (?ab=tausch), alle 19 Episoden: echte Faktoren mit bestehendem Text (Option-Buchstaben der Anzeige angepasst), Ablenker als «Hier nicht entscheidend» / «Unplausibel», Erkenntnisse, keine Knoepfe mehr | Desktop | OK |  |
| Konsole/Anfragen ohne Fehler (Freigabe tausch) | Desktop | OK | [] |
| Reihenfolge der Eintraege variiert mit dem Seed (30 Seeds, Episode 5B: 30 verschiedene Reihenfolgen) | Desktop | OK |  |
| Gleicher Seed gleiche Reihenfolge (zwei Sitzungen) | Desktop | OK | ['Schuhgrösse von Lisa', 'Farbe der Tasse auf dem Tisch', 'Sinnvolle Gespräche statt Smalltalk'] |
| Position jedes Eintrags gleichverteilt (3000 Seeds, 7 Eintraege, Chi-Quadrat je Eintrag hoechstens 16.5, Grenze 22.5 bei 6 FG, p=0.001); jede Reihenfolge ist eine Permutation | Desktop | OK |  |
| Ohne Seed (crypto.getRandomValues): 12 Spiele geben 12 verschiedene Reihenfolgen | Desktop | OK |  |
| Antippen markiert: aria-pressed und Haken nur bei den 3 angetippten Eintraegen | Desktop | OK | [False, True, False, True, True, False, False] |
| Markierung liegt im Zustand (nur im Speicher), Phase bleibt «Werte danach» | Desktop | OK |  |
| Zweites Antippen nimmt die Markierung zurueck | Desktop | OK |  |
| Neuladen (sessionStorage): Phase, Markierungen und Reihenfolge bleiben | Desktop | OK | werte |
| Neuladen ohne Parameter: gleiche Episode, Phase, Reihenfolge und Markierungen wie vorher | Desktop | OK | werte [2, 5, 6] |
| Nach der Freigabe: Zaehlung «Von 3 markierten Eintraegen gehoeren 2 zur Loesung» und «markiert» an den 3 Zeilen | Desktop | OK | Von 3 markierten Einträgen gehören 2 zur Lösung. |
| Neuladen nach der Freigabe: Loesung bleibt sichtbar | Desktop | OK |  |
| Rueckgaengig nach der Freigabe: Liste wieder verdeckt, die 3 Markierungen sind noch da, kein Urteil im DOM | Desktop | OK |  |
| Naechste Episode: wieder verdeckt, keine Markierungen, Freigabe zurueckgesetzt | Desktop | OK | 6 |
| Tastatur: Tab, Leertaste und Enter markieren Eintraege (aria-pressed) | Desktop | OK | true true |
| Tastatur: «Loesung zeigen» per Tab und Enter; Fokus liegt danach auf der Ueberschrift der Karte | Desktop | OK | glueck-titel |
| Touch (390x844): Antippen markiert zwei Eintraege | Phone | OK |  |
| Touch: Eintraege mindestens 44 px hoch, kein horizontaler Scroll | Phone | OK | kleinster Eintrag 52 px |
| Touch: «Loesung zeigen» tippen gibt die Loesung frei | Phone | OK |  |
| Konsole/Anfragen ohne Fehler (Touch) | Phone | OK | [] |

Gesamt: 25 Pruefungen, 0 Fehler
