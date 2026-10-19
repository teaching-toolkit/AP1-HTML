| Test | Geraet | Ergebnis | Detail |
|---|---|---|---|
| Virtueller W20 ohne Seed: nur 1..20, 1 und 20 kommen vor | Desktop | OK | Haeufigkeit 1: 971, 20: 964 |
| Virtueller W20: Gleichverteilung (Chi-Quadrat, 19 FG, Grenze 43.8 bei p=0.001) | Desktop | OK | chi2 = 16.7 aus 20000 Wuerfen |
| W20 mit ?seed=: Gleichverteilung | Desktop | OK | chi2 = 11.4 |
| ?seed= reproduzierbar (zwei Sitzungen, gleiche Wuerfe) | Desktop | OK | [17, 18, 3, 11, 9, 4, 17, 5] |
| ?seed= anderer Wert gibt andere Folge | Desktop | OK | [17, 18, 3, 11, 9, 4, 17, 5] gegen [17, 9, 13, 19, 15, 17, 2, 14] |
| Taste W wuerfelt (virtuell) | Desktop | OK | ergebnis |
| Eingabe '' wird abgelehnt (Hinweis sichtbar, kein Wurf) | Desktop | OK | wurf |
| Eingabe '0' wird abgelehnt (Hinweis sichtbar, kein Wurf) | Desktop | OK | wurf |
| Eingabe '21' wird abgelehnt (Hinweis sichtbar, kein Wurf) | Desktop | OK | wurf |
| Eingabe '3.5' wird abgelehnt (Hinweis sichtbar, kein Wurf) | Desktop | OK | wurf |
| Eingabe 'abc' wird abgelehnt (Hinweis sichtbar, kein Wurf) | Desktop | OK | wurf |
| Eingabe '1e1' wird abgelehnt (Hinweis sichtbar, kein Wurf) | Desktop | OK | wurf |
| Eingabe '-3' wird abgelehnt (Hinweis sichtbar, kein Wurf) | Desktop | OK | wurf |
| Eingabe '100' wird abgelehnt (Hinweis sichtbar, kein Wurf) | Desktop | OK | wurf |
| Eingabe '  ' wird abgelehnt (Hinweis sichtbar, kein Wurf) | Desktop | OK | wurf |
| Eingabe '7a' wird abgelehnt (Hinweis sichtbar, kein Wurf) | Desktop | OK | wurf |
| Eingabe '٣' wird abgelehnt (Hinweis sichtbar, kein Wurf) | Desktop | OK | wurf |
| Eingabe '1' wird als 1 uebernommen (eigener Wuerfel) | Desktop | OK | 1 |
| Eingabe '20' wird als 20 uebernommen (eigener Wuerfel) | Desktop | OK | 20 |
| Eingabe '07' wird als 7 uebernommen (eigener Wuerfel) | Desktop | OK | 7 |
| Eingabe ' 7 ' wird als 7 uebernommen (eigener Wuerfel) | Desktop | OK | 7 |
| Eingabe '13' wird als 13 uebernommen (eigener Wuerfel) | Desktop | OK | 13 |
| Konsole/Anfragen ohne Fehler (Eingabetest) | Desktop | OK | [] |
| Wurf 1, Ep 1 Option A, Normalwerte | Desktop | OK | Ep 1/A Wurf 1: Resultat 3.9, Stimmung 43.0 |
| Wurf 20, Ep 1 Option A, Normalwerte | Desktop | OK | Ep 1/A Wurf 20: Resultat 22.9, Stimmung 58.0 |
| Wurf 1, Ep 5B Option B, Normalwerte | Desktop | OK | Ep 5B/B Wurf 1: Resultat 3.9, Stimmung 41.0 |
| Wurf 20, Ep 5B Option B, Normalwerte | Desktop | OK | Ep 5B/B Wurf 20: Resultat 22.9, Stimmung 56.0 |
| Wurf 1, Ep 12A1 Option A, Normalwerte | Desktop | OK | Ep 12A1/A Wurf 1: Resultat 3.9, Stimmung 37.0 |
| Wurf 20, Ep 12A1 Option A, Normalwerte | Desktop | OK | Ep 12A1/A Wurf 20: Resultat 22.9, Stimmung 52.0 |
| Wurf 1, Ep 12B2 Option B, Normalwerte | Desktop | OK | Ep 12B2/B Wurf 1: Resultat 3.9, Stimmung 39.0 |
| Wurf 20, Ep 12B2 Option B, Normalwerte | Desktop | OK | Ep 12B2/B Wurf 20: Resultat 22.9, Stimmung 54.0 |
| Alle Attribute -10, Wurf 1: Resultat negativ wird 0 | Desktop | OK | Ep 3/A Wurf 1: Resultat 0.0, Stimmung 42.0 |
|   Resultat ist 0 und Hinweis «auf 0 gesetzt» sichtbar | Desktop | OK |  |
| Alle Attribute +10, Wurf 20 | Desktop | OK | Ep 3/B Wurf 20: Resultat 47.2, Stimmung 76.0 |
|   Saettigung: Resultat 20 + 2*(0.5+0.6+2+5.5+4.5+0.5) = 47.2 | Desktop | OK | 47.2 |
| Attribute -10 / +10 gemischt, Wurf 7 | Desktop | OK | Ep 9/A Wurf 7: Resultat 2.2, Stimmung 41.0 |
| Stimmung nach Episode genau 0: Spiel laeuft weiter | Desktop | OK | spielende=False, Weiter-Knopf=1 |
| Stimmung nach Episode genau -1: Spielende-Angebot | Desktop | OK | spielende=True, Weiter-Knopf=0 |
|   Spielende: beide Wege angeboten (Abschluss / Rettungs-Mikroszene) | Desktop | OK |  |
| Stimmung nach Episode genau 1: Spiel laeuft weiter | Desktop | OK | spielende=False, Weiter-Knopf=1 |
| Finanzen -2 (kein Zeitabzug) | Desktop | OK | Ep 9/B Wurf 12: Resultat 13.4, Stimmung 49.0 |
| Finanzen -3 (Zeit -1 zusaetzlich) | Desktop | OK | Ep 9/B Wurf 12: Resultat 12.9, Stimmung 48.0 |
|   Zeitabzug nur bei Finanzen -3 sichtbar und genau 1 | Desktop | OK |  |
| Zufallsserie ueber die Bedienoberflaeche, 76 Zustaende, alle 38 Zeilen (Dezimal-Referenz) | Desktop | OK | Abweichung bei exakten Haelften moeglich, siehe ergebnis_excel.txt |
| Konsole/Anfragen ohne Fehler (Rechenrand) | Desktop | OK | [] |
| Schranken aus (Standard): Soziale Verbindungen 10 + 1 -> 11 | Desktop | OK | angezeigt 11.0, Marker begrenzt=0 |
| Schranken aus: Erfuellung -10 + -1 -> -11 | Desktop | OK | -11.0 |
| Schranken aus: Stimmung 100 und starkes Ergebnis -> >100 | Desktop | OK | 106.0 |
| Konsole/Anfragen ohne Fehler (Schranken) | Desktop | OK | [] |
| Schranken an: Soziale Verbindungen 10 + 1 -> 10 | Desktop | OK | angezeigt 10.0, Marker begrenzt=1 |
| Schranken an: Erfuellung -10 + -1 -> -10 | Desktop | OK | -10.0 |
| Schranken an (max. 100): Stimmung 100 und starkes Ergebnis -> 100 | Desktop | OK | 100.0 |
| Konsole/Anfragen ohne Fehler (Schranken) | Desktop | OK | [] |
| Rueckgaengig am Anfang gesperrt | Desktop | OK |  |
| Undo-Tiefe nach 7 Schritten = 7 | Desktop | OK | 7 |
| 7x Rueckgaengig: jeder Zwischenzustand identisch zum gespeicherten | Desktop | OK |  |
| Danach wieder gesperrt, Startansicht | Desktop | OK | start |
| Nach Undo neu wuerfeln: neuer Wurf zaehlt | Desktop | OK |  |
| Strg+Z entspricht Rueckgaengig | Desktop | OK | wurf |
| 3x Rueckgaengig nach Mikroszene: wieder bei «Werte danach» mit Rechnung | Desktop | OK | werte |
| Stimmung unter 0 nach Wurf 1: Spielende-Ansicht | Desktop | OK |  |
|   Abschluss mit Hinweis «Stimmung unter 0», Diagramm da | Desktop | OK |  |
|   Rueckgaengig aus dem Abschluss zurueck zu «Werte danach» | Desktop | OK | werte |
| 10 Mikroszenen mit je zwei Optionen in den Daten | Desktop | OK |  |
| Mikroszenen-Vorschlag bei Zeit -8 | Desktop | OK | erwartet ['M1', 'M10', 'M3', 'M5'], angezeigt ['M1', 'M10', 'M3', 'M5'], Phase werte (nie automatisch) |
| Mikroszenen-Vorschlag bei Zeit -5.5 (nach Episode) | Desktop | OK | erwartet ['M1', 'M10', 'M3', 'M5'], angezeigt ['M1', 'M10', 'M3', 'M5'], Phase werte (nie automatisch) |
| Mikroszenen-Vorschlag bei Energie -9 | Desktop | OK | erwartet ['M1', 'M10', 'M3', 'M5'], angezeigt ['M1', 'M10', 'M3', 'M5'], Phase werte (nie automatisch) |
| Mikroszenen-Vorschlag bei Soz -3 | Desktop | OK | erwartet ['M2', 'M5'], angezeigt ['M2', 'M5'], Phase werte (nie automatisch) |
| Mikroszenen-Vorschlag bei Erfuellung -3 | Desktop | OK | erwartet ['M4', 'M6', 'M8'], angezeigt ['M4', 'M6', 'M8'], Phase werte (nie automatisch) |
| Mikroszenen-Vorschlag bei Lebensstil -4 | Desktop | OK | erwartet ['M7', 'M9'], angezeigt ['M7', 'M9'], Phase werte (nie automatisch) |
| Mikroszenen-Vorschlag bei Normalwerte | Desktop | OK | erwartet [], angezeigt [], Phase werte (nie automatisch) |
| Mikroszenen-Vorschlag bei Zeit/Energie hoch | Desktop | OK | erwartet [], angezeigt [], Phase werte (nie automatisch) |
| Schwelle zeit: Wert nach Episode -5.0 -> kein Vorschlag | Desktop | OK | Chips [] |
| Schwelle zeit: Wert nach Episode -5.5 -> mit Vorschlag | Desktop | OK | Chips ['M1', 'M10', 'M3', 'M5'] |
| Schwelle soz: Wert nach Episode 0.0 -> kein Vorschlag | Desktop | OK | Chips [] |
| Schwelle soz: Wert nach Episode -0.5 -> mit Vorschlag | Desktop | OK | Chips ['M2', 'M5'] |
| Schwelle erfuellung: Wert nach Episode 0.0 -> kein Vorschlag | Desktop | OK | Chips [] |
| Schwelle erfuellung: Wert nach Episode -0.5 -> mit Vorschlag | Desktop | OK | Chips ['M4', 'M6', 'M8'] |
| Schwelle lebensstil: Wert nach Episode 0.0 -> kein Vorschlag | Desktop | OK | Chips [] |
| Schwelle lebensstil: Wert nach Episode -0.5 -> mit Vorschlag | Desktop | OK | Chips ['M7', 'M9'] |
| Vorschlagsknopf startet Mikroszene M1 (Entscheidung A/B, kein Wuerfel) | Desktop | OK |  |
| Mikroszene M1 A: Deltas {'zeit': 1, 'energie': 1, 'lebensstil': -1} exakt angewendet, Stimmung unveraendert | Desktop | OK | {'stimmung': 47.0, 'zeit': -8.0, 'energie': 1.0, 'soz': 1.0, 'erfuellung': 2.0, 'lebensstil': 1.0, 'finanzen': 1.0} |
|   Glücksfaktoren erst nach der Entscheidung sichtbar | Desktop | OK |  |
| Danach regulaer Episode 4 mit Beginn-Aenderungen (+3 Zeit, +3 Energie) | Desktop | OK | Ep 4, Zeit -8.0 -> -5.0 |
| Liste zeigt alle 10 Mikroszenen, bereits gespielte (M1) gesperrt | Desktop | OK | 10 Knoepfe, 1 gesperrt |
| Alle 10 Mikroszenen x Option A/B: Wertaenderung = Deltas aus den Daten | Desktop | OK | 20 Kombinationen |
| Konsole/Anfragen ohne Fehler (Mikroszenen) | Desktop | OK | [] |
| Spielende nach Episode (Stimmung -7.0) | Desktop | OK |  |
| Rettungsauswahl: M1, M3, M5, M10 zuerst hervorgehoben | Desktop | OK | ['M1*', 'M3*', 'M5*', 'M10*', 'M2', 'M4', 'M6', 'M7', 'M8', 'M9'] |
| Nach Rettungs-Mikroszene geht es mit Episode 4 weiter (Beginn +3/+3, Stimmung bleibt unter 0, Entscheidung moeglich) | Desktop | OK | 4 / entscheidung, Stimmung -7 |
| Letzte Episode mit Stimmung unter 0: nur Abschlussansicht (keine Rettung moeglich, keine naechste Episode) | Desktop | OK |  |
| Stimmung nach Ep 11 = 10, Beginn Ep 12 (-10) ergibt 0 -> entscheidung | Desktop | OK | Phase entscheidung, Stimmung 0 |
| Stimmung nach Ep 11 = 9, Beginn Ep 12 (-10) ergibt -1 -> spielende | Desktop | OK | Phase spielende, Stimmung -1 |
|   Spielende zu Beginn: beide Wege angeboten | Desktop | OK |  |
|   Nach Rettung zurueck zur Entscheidung derselben Episode 12A1 | Desktop | OK | entscheidung |
| Neu laden: Spielstand (sessionStorage) wiederhergestellt inkl. Rueckgaengig-Tiefe | Desktop | OK | entscheidung |
| ?neu=1 beginnt ohne gespeicherten Stand | Desktop | OK | start |
| Speicher blockiert: Spiel laeuft trotzdem, keine Fehler in der Konsole | Phone | OK | [] |
| Neues Spiel: «Abbrechen» behaelt den Stand | Desktop | OK |  |
| Neues Spiel: «Ja» setzt zurueck | Desktop | OK |  |
| Sichtbarer Fokus bei Tab (Outline oder Schatten) | Desktop | OK | ['BUTTON', 'Neues Spiel', 'solid', 3, 'none'] |
| Tastenkuerzel B waehlt die Option, die als B angezeigt wird (Regeloption je nach Tausch) | Desktop | OK | Tausch Ep 1: 0, Regeloption B |
| Tastenkuerzel A waehlt die Option, die als A angezeigt wird | Desktop | OK | Regeloption A |
| Kein horizontaler Seitenscroll in allen 12 Ansichten | Phone 360x740 light | OK | [] |
| Alle Bedienelemente >= 44x44 px | Phone 360x740 light | OK | [] |
| Kein Element ragt ueber den Bildschirmrand | Phone 360x740 light | OK | [] |
| Kontrast Text AA (>= 4.5, gross >= 3) in allen Ansichten | Phone 360x740 light | OK | [] |
| Konsole/Anfragen ohne Fehler (Layout) | Phone 360x740 light | OK | [] |
| Kein horizontaler Seitenscroll in allen 12 Ansichten | Phone 360x740 dark | OK | [] |
| Alle Bedienelemente >= 44x44 px | Phone 360x740 dark | OK | [] |
| Kein Element ragt ueber den Bildschirmrand | Phone 360x740 dark | OK | [] |
| Kontrast Text AA (>= 4.5, gross >= 3) in allen Ansichten | Phone 360x740 dark | OK | [] |
| prefers-reduced-motion: keine laufenden Animationen/Uebergaenge | Phone 360x740 dark | OK | 0 Elemente |
| Konsole/Anfragen ohne Fehler (Layout) | Phone 360x740 dark | OK | [] |
| Kein horizontaler Seitenscroll in allen 12 Ansichten | Phone 390x844 light | OK | [] |
| Alle Bedienelemente >= 44x44 px | Phone 390x844 light | OK | [] |
| Kein Element ragt ueber den Bildschirmrand | Phone 390x844 light | OK | [] |
| Kontrast Text AA (>= 4.5, gross >= 3) in allen Ansichten | Phone 390x844 light | OK | [] |
| Konsole/Anfragen ohne Fehler (Layout) | Phone 390x844 light | OK | [] |
| Kein horizontaler Seitenscroll in allen 12 Ansichten | Phone 390x844 dark | OK | [] |
| Alle Bedienelemente >= 44x44 px | Phone 390x844 dark | OK | [] |
| Kein Element ragt ueber den Bildschirmrand | Phone 390x844 dark | OK | [] |
| Kontrast Text AA (>= 4.5, gross >= 3) in allen Ansichten | Phone 390x844 dark | OK | [] |
| prefers-reduced-motion: keine laufenden Animationen/Uebergaenge | Phone 390x844 dark | OK | 0 Elemente |
| Konsole/Anfragen ohne Fehler (Layout) | Phone 390x844 dark | OK | [] |
| Kein horizontaler Seitenscroll in allen 12 Ansichten | Tablet 768x1024 light | OK | [] |
| Alle Bedienelemente >= 44x44 px | Tablet 768x1024 light | OK | [] |
| Kein Element ragt ueber den Bildschirmrand | Tablet 768x1024 light | OK | [] |
| Kontrast Text AA (>= 4.5, gross >= 3) in allen Ansichten | Tablet 768x1024 light | OK | [] |
| Konsole/Anfragen ohne Fehler (Layout) | Tablet 768x1024 light | OK | [] |
| Kein horizontaler Seitenscroll in allen 12 Ansichten | Tablet 768x1024 dark | OK | [] |
| Alle Bedienelemente >= 44x44 px | Tablet 768x1024 dark | OK | [] |
| Kein Element ragt ueber den Bildschirmrand | Tablet 768x1024 dark | OK | [] |
| Kontrast Text AA (>= 4.5, gross >= 3) in allen Ansichten | Tablet 768x1024 dark | OK | [] |
| prefers-reduced-motion: keine laufenden Animationen/Uebergaenge | Tablet 768x1024 dark | OK | 0 Elemente |
| Konsole/Anfragen ohne Fehler (Layout) | Tablet 768x1024 dark | OK | [] |
| Kein horizontaler Seitenscroll in allen 12 Ansichten | Desktop 1280x800 light | OK | [] |
| Alle Bedienelemente >= 44x44 px | Desktop 1280x800 light | OK | [] |
| Kein Element ragt ueber den Bildschirmrand | Desktop 1280x800 light | OK | [] |
| Kontrast Text AA (>= 4.5, gross >= 3) in allen Ansichten | Desktop 1280x800 light | OK | [] |
| Konsole/Anfragen ohne Fehler (Layout) | Desktop 1280x800 light | OK | [] |
| Kein horizontaler Seitenscroll in allen 12 Ansichten | Desktop 1280x800 dark | OK | [] |
| Alle Bedienelemente >= 44x44 px | Desktop 1280x800 dark | OK | [] |
| Kein Element ragt ueber den Bildschirmrand | Desktop 1280x800 dark | OK | [] |
| Kontrast Text AA (>= 4.5, gross >= 3) in allen Ansichten | Desktop 1280x800 dark | OK | [] |
| prefers-reduced-motion: keine laufenden Animationen/Uebergaenge | Desktop 1280x800 dark | OK | 0 Elemente |
| Konsole/Anfragen ohne Fehler (Layout) | Desktop 1280x800 dark | OK | [] |

Gesamt: 147 Pruefungen, 0 Fehler
