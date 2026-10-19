/* Glücksfaktoren-Spiel: von Hand geschriebene Texte (klassisches Skript, setzt window.SPIEL_TEXTE).
   Diese Datei wird NICHT von tools/erzeuge_daten.py erzeugt. Zahlen und Regeln stehen in spiel-daten.js
   (aus Excel und Word). Hier stehen nur Texte und Einordnungen, keine Rechenregel.

   Aufbau pro Episode (Schlüssel = Episoden-ID wie in spiel-daten.js). «A» und «B» bedeuten hier immer die
   REGELOPTION (Excel-Zeile), nicht den Buchstaben, der den Teilnehmenden angezeigt wird. Die Anzeige
   vertauscht die Buchstaben pro Episode zufällig.

   ausrichtung       je Regeloption «langfristig» (Investition) oder «kurzfristig» (Optimierung).
                     Wird erst in der Abschlussansicht gezeigt, nie während des Spiels.
   unscharf          true, wenn die Zuordnung nicht eindeutig ist (Abschlussansicht markiert mit Stern).
   notiz             Begründung der Einordnung (nur für Fachpersonen, steht nicht auf der Seite).
   plausibel         Kandidaten, die plausibel klingen, aber in dieser Episode nicht zur Lösung gehören.
   unplausibel       Kandidaten, die klar absurd oder belanglos sind.
                     Die echten Glücksfaktoren stehen in spiel-daten.js (episoden[].glueck) und werden dort gelesen.
   ergebnis          Kurztext (1 bis 2 Sätze) je Regeloption und Ausgang: «erfolg» (Resultat grösser oder gleich
                     Soll-Wert) oder «misserfolg».
     text            Der Text. Die Platzhalter ZEIT und ENERGIE in geschweiften Klammern werden beim Anzeigen durch
                     «mehr Zeit», «weniger Energie», «gleich viel Zeit» usw. ersetzt, passend zur
                     tatsächlichen Änderung (Energie hängt von der Stimmung ab und ist daher nicht
                     vorab bekannt).
     gefuehl         Was der Text behauptet (für den automatischen Test): Für Zeit und Energie «dyn» (Platzhalter),
                     für Erfüllung, Soziale Verbindungen, Lebensstil und Finanzen «+» oder «-» (Vorzeichen der
                     Änderung), für die Stimmung «gut» (Erfolg: Stimmung sinkt nie) oder «schlecht»
                     (Misserfolg: Stimmung steigt nie).

   Die Ablenker sind Kandidaten ohne Behauptung. «Hier nicht entscheidend» heisst nur: gehört nicht zur Lösung
   dieser Episode im Spiel. Es ist keine Aussage über Glück im Allgemeinen. */
var SPIEL_TEXTE = {
  "version": 1,
  "ausrichtungNamen": { "langfristig": "langfristige Investition", "kurzfristig": "kurzfristige Optimierung" },
  "urteilTexte": { "echt": "Glücksfaktor", "plausibel": "Hier nicht entscheidend", "unplausibel": "Unplausibel" },
  "episoden": {
    "1": {
      "ausrichtung": { "A": "kurzfristig", "B": "langfristig" }, "unscharf": false, "notiz": "",
      "plausibel": ["Ansehen des Studienfachs bei Bekannten", "Zustimmung der Eltern zur Studienwahl", "Entfernung der Hochschule zum Elternhaus"],
      "unplausibel": ["Sternzeichen der Dozierenden", "Farbe der Mensa-Tabletts", "Schuhgrösse der Mitstudierenden"],
      "ergebnis": {
        "A": {
          "erfolg": { "text": "Alexandra behauptet sich in den ersten Wochen im BWL-Studium und kommt gut mit. Sie ist zufrieden und finanziell besser gestellt, fühlt sich im Fach aber weniger erfüllt.", "gefuehl": { "stimmung": "gut", "finanzen": "+", "erfuellung": "-" } },
          "misserfolg": { "text": "Der Einstieg ins BWL-Studium holpert, und Alexandra hinkt den anderen hinterher. Sie ist frustriert und fühlt sich im Fach weniger erfüllt.", "gefuehl": { "stimmung": "schlecht", "erfuellung": "-" } }
        },
        "B": {
          "erfolg": { "text": "Alexandra setzt sich gegen die Skepsis der Eltern durch und findet im Psychologiestudium schnell Anschluss. Sie ist stolz, fühlt sich erfüllter und hat danach {ENERGIE}, ist aber finanziell knapper dran.", "gefuehl": { "stimmung": "gut", "erfuellung": "+", "energie": "dyn", "finanzen": "-" } },
          "misserfolg": { "text": "Gegen den Widerstand der Eltern kommt Alexandra im Psychologiestudium nur schwer in Gang. Sie ist verunsichert, fühlt sich aber im Fach erfüllter, hat danach {ENERGIE} und ist finanziell knapper dran.", "gefuehl": { "stimmung": "schlecht", "erfuellung": "+", "energie": "dyn", "finanzen": "-" } }
        }
      }
    },
    "2A": {
      "ausrichtung": { "A": "kurzfristig", "B": "langfristig" }, "unscharf": false, "notiz": "",
      "plausibel": ["Gute Noten im Semester", "Anerkennung durch den Professor"],
      "unplausibel": ["Farbe des Hörsaalteppichs", "Anfangsbuchstabe des Nachnamens", "Anzahl Treppenstufen im Uni-Gebäude"],
      "ergebnis": {
        "A": {
          "erfolg": { "text": "Alexandra erledigt das Pflichtprogramm und schliesst das Semester entspannt mit soliden Noten ab. Sie ist zufrieden, hat danach {ZEIT} und {ENERGIE}, fühlt sich aber weniger erfüllt.", "gefuehl": { "stimmung": "gut", "zeit": "dyn", "energie": "dyn", "erfuellung": "-" } },
          "misserfolg": { "text": "Das Pflicht-Minimum läuft holpriger als geplant, und die Noten bleiben durchschnittlich. Sie ist enttäuscht, hat danach {ZEIT} und fühlt sich weniger erfüllt.", "gefuehl": { "stimmung": "schlecht", "zeit": "dyn", "erfuellung": "-" } }
        },
        "B": {
          "erfolg": { "text": "Alexandra stemmt das anspruchsvolle Ethik-Projekt trotz Stress und liefert eine überzeugende Arbeit ab. Sie ist stolz und fühlt sich erfüllter, hat danach aber {ZEIT} und {ENERGIE}, und ihr Alltag gerät aus dem Takt.", "gefuehl": { "stimmung": "gut", "erfuellung": "+", "zeit": "dyn", "energie": "dyn", "lebensstil": "-" } },
          "misserfolg": { "text": "Das Ethik-Projekt wächst Alexandra über den Kopf, und die Arbeit bleibt unfertig. Sie ist frustriert, fühlt sich aber dennoch erfüllter, hat danach {ENERGIE}, und ihr Alltag gerät aus dem Takt.", "gefuehl": { "stimmung": "schlecht", "erfuellung": "+", "energie": "dyn", "lebensstil": "-" } }
        }
      }
    },
    "2B": {
      "ausrichtung": { "A": "kurzfristig", "B": "langfristig" }, "unscharf": false, "notiz": "",
      "plausibel": ["Ruf des Instituts", "Auszeichnung für die beste Prüfungsnote"],
      "unplausibel": ["Lieblingsfarbe des Statistik-Professors", "Geburtsmonat der Tutorin"],
      "ergebnis": {
        "A": {
          "erfolg": { "text": "Alexandra belegt die normalen Kurse und kommt strukturiert durchs Semester. Sie ist zufrieden, hat danach {ZEIT} und fühlt sich etwas weniger erfüllt.", "gefuehl": { "stimmung": "gut", "zeit": "dyn", "erfuellung": "-" } },
          "misserfolg": { "text": "Die Grundlagenkurse laufen zäh, und Alexandra verliert den Überblick über den Semesterablauf. Sie ist unzufrieden, hat danach {ZEIT} und fühlt sich weniger erfüllt.", "gefuehl": { "stimmung": "schlecht", "zeit": "dyn", "erfuellung": "-" } }
        },
        "B": {
          "erfolg": { "text": "Alexandra arbeitet sich in die Datenanalyse ein und trägt zum Forschungsprojekt bei. Sie ist stolz und fühlt sich erfüllter, hat danach aber {ZEIT} und {ENERGIE}, und ihr Alltag gerät aus dem Takt.", "gefuehl": { "stimmung": "gut", "erfuellung": "+", "zeit": "dyn", "energie": "dyn", "lebensstil": "-" } },
          "misserfolg": { "text": "Die Datenanalyse ist steiler als gedacht, und Alexandras Beitrag zum Forschungsprojekt bleibt klein. Sie ist verunsichert, fühlt sich aber erfüllter, hat danach {ENERGIE}, und ihr Alltag gerät aus dem Takt.", "gefuehl": { "stimmung": "schlecht", "erfuellung": "+", "energie": "dyn", "lebensstil": "-" } }
        }
      }
    },
    "3": {
      "ausrichtung": { "A": "kurzfristig", "B": "langfristig" }, "unscharf": false, "notiz": "",
      "plausibel": ["Noten des vergangenen Studienjahres", "Zahl der angebotenen Wahlfächer"],
      "unplausibel": ["Wetter am ersten Vorlesungstag", "Handymarke der Kommilitonen", "Haarlänge des Professors"],
      "ergebnis": {
        "A": {
          "erfolg": { "text": "Alexandra lässt das Jahr auf sich zukommen und geniesst einen sorgenfreien Alltag. Sie ist gelassen und hat danach {ZEIT}, fühlt sich aber weniger erfüllt.", "gefuehl": { "stimmung": "gut", "zeit": "dyn", "erfuellung": "-" } },
          "misserfolg": { "text": "Alexandra lässt sich treiben, doch die Sorgen der Kommilitonen stecken sie an, und der Alltag bleibt unruhig. Sie ist bedrückt, hat danach {ZEIT} und fühlt sich weniger erfüllt.", "gefuehl": { "stimmung": "schlecht", "zeit": "dyn", "erfuellung": "-" } }
        },
        "B": {
          "erfolg": { "text": "Alexandra setzt sich klare Ziele für die nächsten drei Jahre und plant Studium und Praktika realistisch. Sie ist zuversichtlich, fühlt sich erfüllter und hat danach {ZEIT}, und ihr Alltag wird geordneter.", "gefuehl": { "stimmung": "gut", "erfuellung": "+", "zeit": "dyn", "lebensstil": "+" } },
          "misserfolg": { "text": "Alexandras Plan wirkt überladen, und mit den Zielen kommt sie nicht richtig voran. Sie ist verunsichert, fühlt sich aber erfüllter und hat danach {ZEIT}, und ihr Alltag wird geordneter.", "gefuehl": { "stimmung": "schlecht", "erfuellung": "+", "zeit": "dyn", "lebensstil": "+" } }
        }
      }
    },
    "4": {
      "ausrichtung": { "A": "kurzfristig", "B": "langfristig" }, "unscharf": false, "notiz": "",
      "plausibel": ["Grosses vs. kleines eigenes Zimmer", "Lage der WG in der Stadt"],
      "unplausibel": ["Farbe der Wohnungstür", "Marke des Kühlschranks", "Hausnummer der WG"],
      "ergebnis": {
        "A": {
          "erfolg": { "text": "Alexandra bleibt freundlich auf Distanz, und das WG-Leben läuft ohne Komplikationen. Sie ist zufrieden, hat danach {ZEIT} und {ENERGIE}, fühlt sich aber weniger verbunden.", "gefuehl": { "stimmung": "gut", "zeit": "dyn", "energie": "dyn", "soz": "-" } },
          "misserfolg": { "text": "Trotz der Distanz kommt es in der WG zu kleinen Reibereien, und die Stimmung im Haus bleibt kühl. Sie ist genervt, hat danach {ZEIT} und fühlt sich weniger verbunden.", "gefuehl": { "stimmung": "schlecht", "zeit": "dyn", "soz": "-" } }
        },
        "B": {
          "erfolg": { "text": "Alexandra verbringt Zeit mit Lisa, und die beiden bauen Vertrauen zueinander auf. Sie ist froh, fühlt sich enger verbunden und etwas erfüllter, hat danach aber {ZEIT} und {ENERGIE}.", "gefuehl": { "stimmung": "gut", "soz": "+", "erfuellung": "+", "zeit": "dyn", "energie": "dyn" } },
          "misserfolg": { "text": "Lisa bleibt zurückhaltend, und aus den Annäherungsversuchen wird noch keine tragfähige Freundschaft. Alexandra ist ernüchtert, fühlt sich aber etwas verbundener und hat danach {ZEIT} und {ENERGIE}.", "gefuehl": { "stimmung": "schlecht", "soz": "+", "zeit": "dyn", "energie": "dyn" } }
        }
      }
    },
    "5A": {
      "ausrichtung": { "A": "kurzfristig", "B": "langfristig" }, "unscharf": false, "notiz": "",
      "plausibel": ["Lautstärke der Musik auf der Party", "Anzahl der Gäste"],
      "unplausibel": ["Sternzeichen der Gastgeberin", "Farbe der Partygirlanden", "Marke der Chips"],
      "ergebnis": {
        "A": {
          "erfolg": { "text": "Alexandra bleibt beim Smalltalk, geniesst die Party und knüpft ein paar lockere Kontakte. Sie ist gut gelaunt und hat danach {ENERGIE}, fühlt sich aber weniger verbunden.", "gefuehl": { "stimmung": "gut", "energie": "dyn", "soz": "-" } },
          "misserfolg": { "text": "Die Gespräche plätschern vor sich hin, und Alexandra langweilt sich auf der Party. Sie ist unzufrieden, fühlt sich weniger verbunden und hat danach {ENERGIE}.", "gefuehl": { "stimmung": "schlecht", "soz": "-", "energie": "dyn" } }
        },
        "B": {
          "erfolg": { "text": "Alexandra fragt nach, und es entsteht ein ehrliches Gespräch, das beiden etwas bringt. Sie ist erleichtert, fühlt sich enger verbunden und hat danach {ZEIT}.", "gefuehl": { "stimmung": "gut", "soz": "+", "zeit": "dyn" } },
          "misserfolg": { "text": "Alexandra fragt nach, doch das Gespräch gerät ins Stocken und bringt keine echte Unterstützung. Sie ist ernüchtert, fühlt sich aber enger verbunden und hat danach {ZEIT}.", "gefuehl": { "stimmung": "schlecht", "soz": "+", "zeit": "dyn" } }
        }
      }
    },
    "5B": {
      "ausrichtung": { "A": "kurzfristig", "B": "langfristig" }, "unscharf": false, "notiz": "",
      "plausibel": ["Ort des Gesprächs (Café oder Zimmer)", "Fachwissen über Studienabbrüche"],
      "unplausibel": ["Schuhgrösse von Lisa", "Farbe der Tasse auf dem Tisch"],
      "ergebnis": {
        "A": {
          "erfolg": { "text": "Alexandra muntert Lisa kurz auf, und die Stimmung im Gespräch hellt sich auf. Sie ist erleichtert und hat danach {ZEIT}.", "gefuehl": { "stimmung": "gut", "zeit": "dyn" } },
          "misserfolg": { "text": "Die kurze Ermutigung kommt bei Lisa nicht an, und ihr Problem bleibt im Raum stehen. Alexandra ist unzufrieden und hat danach {ZEIT}.", "gefuehl": { "stimmung": "schlecht", "zeit": "dyn" } }
        },
        "B": {
          "erfolg": { "text": "Alexandra nimmt sich Zeit und hört Lisa zu, und Lisa fasst wieder Mut. Sie ist froh und fühlt sich enger verbunden, hat danach aber {ZEIT} und {ENERGIE}.", "gefuehl": { "stimmung": "gut", "soz": "+", "zeit": "dyn", "energie": "dyn" } },
          "misserfolg": { "text": "Alexandra hört lange zu, doch Lisa bleibt unschlüssig, ob sie weitermacht. Sie ist bedrückt, fühlt sich aber enger verbunden und hat danach {ZEIT} und {ENERGIE}.", "gefuehl": { "stimmung": "schlecht", "soz": "+", "zeit": "dyn", "energie": "dyn" } }
        }
      }
    },
    "6": {
      "ausrichtung": { "A": "kurzfristig", "B": "langfristig" }, "unscharf": true,
      "notiz": "A (Grenzen setzen) schützt Zeit und Energie, ist aber auch eine Investition in Erholung (Lebensstil plus 1); zwei der drei Glücksfaktoren der Lösung gehören zu A. B investiert in Beziehung und Erfüllung.",
      "plausibel": ["Beliebtheit des Kommilitonen im Studiengang", "Schwierigkeitsgrad des Fachs"],
      "unplausibel": ["Haarfarbe des Kommilitonen", "Hausnummer der Bibliothek"],
      "ergebnis": {
        "A": {
          "erfolg": { "text": "Alexandra lehnt die Nachhilfe höflich ab und schützt ihre volle Woche. Sie ist gelassen, hat danach {ZEIT} und {ENERGIE}, und ihr Alltag wird geordneter, doch sie fühlt sich weniger verbunden.", "gefuehl": { "stimmung": "gut", "zeit": "dyn", "energie": "dyn", "lebensstil": "+", "soz": "-" } },
          "misserfolg": { "text": "Alexandra lehnt ab, bleibt aber mit schlechtem Gewissen zurück und grübelt über die Absage. Sie ist bedrückt, hat danach {ZEIT} und {ENERGIE}, ihr Alltag wird geordneter, doch sie fühlt sich weniger verbunden.", "gefuehl": { "stimmung": "schlecht", "zeit": "dyn", "energie": "dyn", "lebensstil": "+", "soz": "-" } }
        },
        "B": {
          "erfolg": { "text": "Alexandra gibt zwei Stunden Nachhilfe, und der Kommilitone versteht den Stoff danach deutlich besser. Sie ist stolz, fühlt sich enger verbunden und etwas erfüllter, hat danach aber {ZEIT} und {ENERGIE}.", "gefuehl": { "stimmung": "gut", "soz": "+", "erfuellung": "+", "zeit": "dyn", "energie": "dyn" } },
          "misserfolg": { "text": "Die Nachhilfe verläuft zäh, und der Kommilitone versteht den Stoff nur zum Teil. Alexandra ist ernüchtert, fühlt sich aber enger verbunden und etwas erfüllter, hat danach {ZEIT} und {ENERGIE}.", "gefuehl": { "stimmung": "schlecht", "soz": "+", "erfuellung": "+", "zeit": "dyn", "energie": "dyn" } }
        }
      }
    },
    "7": {
      "ausrichtung": { "A": "kurzfristig", "B": "langfristig" }, "unscharf": false, "notiz": "",
      "plausibel": ["Prestige des Arbeitgebers", "Lage des Büros", "Grösse des Betriebs"],
      "unplausibel": ["Sternzeichen der Chefin", "Farbe der Visitenkarte", "Marke des Bürostuhls"],
      "ergebnis": {
        "A": {
          "erfolg": { "text": "Alexandra startet in der Unternehmensberatung und etabliert sich professionell, auch ohne grosse Begeisterung. Sie ist zufrieden und finanziell besser gestellt, fühlt sich aber weniger erfüllt und hat danach {ENERGIE}.", "gefuehl": { "stimmung": "gut", "finanzen": "+", "erfuellung": "-", "energie": "dyn" } },
          "misserfolg": { "text": "Der Einstieg in die Beratung verläuft holprig, und die Standardaufgaben bringen Alexandra wenig Anerkennung. Sie ist frustriert, fühlt sich weniger erfüllt und hat danach {ENERGIE}.", "gefuehl": { "stimmung": "schlecht", "erfuellung": "-", "energie": "dyn" } }
        },
        "B": {
          "erfolg": { "text": "Alexandra findet sich in der Jugendberatung gut zurecht und kann ihre Stärken einsetzen. Sie ist stolz und fühlt sich erfüllter, hat danach aber {ZEIT} und ist finanziell knapper dran.", "gefuehl": { "stimmung": "gut", "erfuellung": "+", "zeit": "dyn", "finanzen": "-" } },
          "misserfolg": { "text": "Der Alltag in der Jugendberatung ist fordernd, und Alexandra hat anfangs Mühe, sich zurechtzufinden. Sie ist verunsichert, fühlt sich aber erfüllter, hat danach {ZEIT} und ist finanziell knapper dran.", "gefuehl": { "stimmung": "schlecht", "erfuellung": "+", "zeit": "dyn", "finanzen": "-" } }
        }
      }
    },
    "8A": {
      "ausrichtung": { "A": "kurzfristig", "B": "langfristig" }, "unscharf": true,
      "notiz": "A (Mitziehen) spart keine Ressourcen (Zeit minus 2, Energie-Basis minus 2), optimiert aber kurzfristig Leistung und Einkommen; B schützt Schlaf und private Zeit.",
      "plausibel": ["Lob der Vorgesetzten", "Ausstattung des Grossraumbüros"],
      "unplausibel": ["Lieblingszahl des Abteilungsleiters", "Schriftart auf dem Namensschild"],
      "ergebnis": {
        "A": {
          "erfolg": { "text": "Alexandra zieht bei der Überstundenkultur mit und wird für ihren Einsatz anerkannt. Sie ist stolz, hat danach aber {ZEIT} und {ENERGIE} und fühlt sich weniger verbunden.", "gefuehl": { "stimmung": "gut", "zeit": "dyn", "energie": "dyn", "soz": "-" } },
          "misserfolg": { "text": "Alexandra kann das Tempo nicht halten, und ihre Leistung bleibt hinter den Erwartungen zurück. Sie ist frustriert, hat danach {ZEIT} und {ENERGIE}, fühlt sich weniger erfüllt und weniger verbunden.", "gefuehl": { "stimmung": "schlecht", "zeit": "dyn", "energie": "dyn", "erfuellung": "-", "soz": "-" } }
        },
        "B": {
          "erfolg": { "text": "Alexandra hält feste Arbeitszeiten ein, schützt ihren Schlaf und überzeugt trotzdem durch Effizienz. Sie ist gelassen und hat danach {ENERGIE}, und ihr Alltag wird geordneter.", "gefuehl": { "stimmung": "gut", "energie": "dyn", "lebensstil": "+" } },
          "misserfolg": { "text": "Alexandra hält an ihren Arbeitszeiten fest, doch die Vorgesetzten reagieren mit Kritik auf ihre geringere Präsenz. Sie ist verunsichert und hat danach {ENERGIE}, ihr Alltag wird dennoch geordneter.", "gefuehl": { "stimmung": "schlecht", "energie": "dyn", "lebensstil": "+" } }
        }
      }
    },
    "8B": {
      "ausrichtung": { "A": "kurzfristig", "B": "langfristig" }, "unscharf": true,
      "notiz": "Beide Optionen enthalten Investitionen: A in Struktur und Teamkontakt (Soziale Verbindungen plus 1), B in Selbstorganisation und Erfüllung. Die Einordnung folgt dem Aufwand: B verlangt mehr Disziplin und Zeit.",
      "plausibel": ["Ausstattung der Büros", "Entfernung des Büros zum Bahnhof", "Auswahl in der Kantine"],
      "unplausibel": ["Farbe der Bürotür", "Hausnummer der Jugendberatung", "Sternzeichen der Teamleitung"],
      "ergebnis": {
        "A": {
          "erfolg": { "text": "Alexandra wählt feste Bürozeiten und findet in einem strukturierten Alltag guten Anschluss im Team. Sie ist zufrieden und fühlt sich verbundener, aber weniger erfüllt.", "gefuehl": { "stimmung": "gut", "soz": "+", "erfuellung": "-" } },
          "misserfolg": { "text": "Der Alltag mit festen Bürozeiten wird für Alexandra schnell eintönig, auch wenn sie ihre Kolleginnen öfter sieht. Sie ist frustriert und fühlt sich weniger erfüllt, aber verbundener.", "gefuehl": { "stimmung": "schlecht", "erfuellung": "-", "soz": "+" } }
        },
        "B": {
          "erfolg": { "text": "Alexandra plant ihre Arbeit selbst und hält ihre Ziele diszipliniert ein. Sie ist stolz, fühlt sich erfüllter und hat danach {ZEIT}, fühlt sich aber weniger verbunden.", "gefuehl": { "stimmung": "gut", "erfuellung": "+", "zeit": "dyn", "soz": "-" } },
          "misserfolg": { "text": "Ohne feste Vorgaben schiebt Alexandra Aufgaben auf, und ihre Planung gerät ins Rutschen. Sie ist unzufrieden, fühlt sich durch die Eigenverantwortung aber erfüllter und hat danach {ZEIT}.", "gefuehl": { "stimmung": "schlecht", "erfuellung": "+", "zeit": "dyn" } }
        }
      }
    },
    "9": {
      "ausrichtung": { "A": "kurzfristig", "B": "langfristig" }, "unscharf": false, "notiz": "",
      "plausibel": ["Wetter am Reiseziel", "Sprachkenntnisse für die Reise"],
      "unplausibel": ["Farbe des Autos des Nachbarn", "Schuhmarke der Kollegen", "Postleitzahl der Wohnung"],
      "ergebnis": {
        "A": {
          "erfolg": { "text": "Alexandra kauft teure Sachen, mit denen sie bei den Kolleginnen mithalten kann, und fällt positiv auf. Sie ist zufrieden, aber finanziell knapper dran.", "gefuehl": { "stimmung": "gut", "finanzen": "-" } },
          "misserfolg": { "text": "Alexandras Anschaffungen beeindrucken die Kolleginnen kaum, und der Vergleich geht weiter. Sie ist frustriert und finanziell knapper dran.", "gefuehl": { "stimmung": "schlecht", "finanzen": "-" } }
        },
        "B": {
          "erfolg": { "text": "Alexandra plant die Islandreise und freut sich auf eine bereichernde Zeit abseits des Vergleichs mit anderen. Sie ist zuversichtlich, fühlt sich erfüllter und hat danach {ENERGIE}, ist aber finanziell knapper dran.", "gefuehl": { "stimmung": "gut", "erfuellung": "+", "energie": "dyn", "finanzen": "-" } },
          "misserfolg": { "text": "Die Planung der Islandreise zieht sich hin, und einiges klappt nicht wie gedacht. Alexandra ist ernüchtert, fühlt sich aber erfüllter, hat danach {ENERGIE} und ist finanziell knapper dran.", "gefuehl": { "stimmung": "schlecht", "erfuellung": "+", "energie": "dyn", "finanzen": "-" } }
        }
      }
    },
    "10": {
      "ausrichtung": { "A": "kurzfristig", "B": "langfristig" }, "unscharf": false, "notiz": "",
      "plausibel": ["Ruf des früheren Arbeitgebers", "Bekanntheit der Branche"],
      "unplausibel": ["Farbe des Kündigungsschreibens", "Name des Pförtners", "Wochentag der Kündigung"],
      "ergebnis": {
        "A": {
          "erfolg": { "text": "Alexandra nimmt den erstbesten Übergangsjob an und hat schnell wieder ein Einkommen. Sie ist erleichtert und finanziell besser gestellt, fühlt sich aber weniger erfüllt und hat danach {ZEIT}.", "gefuehl": { "stimmung": "gut", "finanzen": "+", "erfuellung": "-", "zeit": "dyn" } },
          "misserfolg": { "text": "Der Übergangsjob passt schlecht, und Alexandra fühlt sich unter Wert verkauft. Sie ist frustriert, fühlt sich weniger erfüllt, ist aber finanziell besser gestellt und hat danach {ZEIT}.", "gefuehl": { "stimmung": "schlecht", "erfuellung": "-", "finanzen": "+", "zeit": "dyn" } }
        },
        "B": {
          "erfolg": { "text": "Alexandra rahmt den Jobverlust als Chance um und findet vielversprechende Stellen. Sie ist zuversichtlich und fühlt sich erfüllter, ist aber finanziell knapper dran und hat danach {ZEIT} und {ENERGIE}.", "gefuehl": { "stimmung": "gut", "erfuellung": "+", "finanzen": "-", "zeit": "dyn", "energie": "dyn" } },
          "misserfolg": { "text": "Die Suche nach dem Traumjob zieht sich hin, ohne dass sich eine passende Stelle zeigt. Alexandra ist verunsichert, fühlt sich aber erfüllter, ist finanziell knapper dran und hat danach {ZEIT} und {ENERGIE}.", "gefuehl": { "stimmung": "schlecht", "erfuellung": "+", "finanzen": "-", "zeit": "dyn", "energie": "dyn" } }
        }
      }
    },
    "11A": {
      "ausrichtung": { "A": "kurzfristig", "B": "langfristig" }, "unscharf": false, "notiz": "",
      "plausibel": ["Grösse des Start-ups", "Standort des Start-ups", "Bekanntheit des Start-ups"],
      "unplausibel": ["Farbe des Firmenlogos", "Marke der Kaffeemaschine", "Hausnummer des Büros"],
      "ergebnis": {
        "A": {
          "erfolg": { "text": "Alexandra bleibt im sicheren Job und arrangiert sich mit ihrer Entscheidung. Sie ist zufrieden und finanziell besser gestellt, fühlt sich aber weniger erfüllt und hat danach {ENERGIE}.", "gefuehl": { "stimmung": "gut", "finanzen": "+", "erfuellung": "-", "energie": "dyn" } },
          "misserfolg": { "text": "Alexandra bleibt im sicheren Job, doch der Gedanke an das verpasste Start-up lässt sie nicht los. Sie ist unzufrieden, fühlt sich weniger erfüllt, ist aber finanziell besser gestellt und hat danach {ENERGIE}.", "gefuehl": { "stimmung": "schlecht", "erfuellung": "-", "finanzen": "+", "energie": "dyn" } }
        },
        "B": {
          "erfolg": { "text": "Alexandra wagt den Sprung ins Start-up und beweist sich im dynamischen Umfeld. Sie ist stolz und fühlt sich erfüllter, ist aber finanziell knapper dran und hat danach {ZEIT}.", "gefuehl": { "stimmung": "gut", "erfuellung": "+", "finanzen": "-", "zeit": "dyn" } },
          "misserfolg": { "text": "Im Start-up läuft vieles ungeordnet, und Alexandra findet nur schwer ihren Platz. Sie ist verunsichert, fühlt sich aber erfüllter, ist finanziell knapper dran und hat danach {ZEIT}.", "gefuehl": { "stimmung": "schlecht", "erfuellung": "+", "finanzen": "-", "zeit": "dyn" } }
        }
      }
    },
    "11B": {
      "ausrichtung": { "A": "langfristig", "B": "kurzfristig" }, "unscharf": true,
      "notiz": "Ausnahme: Die Reihenfolge ist umgekehrt. A (befristeter Traumjob) investiert in Erfüllung, B (unbefristete Stelle) setzt auf Sicherheit. Weil A befristet ist, lässt die Erkenntnis «kurzfristige vs. langfristige Perspektive» auch die umgekehrte Lesart zu.",
      "plausibel": ["Ruf der Firma", "Dienstort der Stelle", "Arbeitsweg zum Büro"],
      "unplausibel": ["Sternzeichen der Personalerin", "Farbe des Arbeitsvertrags", "Marke des Kugelschreibers"],
      "ergebnis": {
        "A": {
          "erfolg": { "text": "Alexandra nimmt den befristeten Traumjob an und holt in der kurzen Zeit viel heraus. Sie ist stolz und fühlt sich erfüllter, hat danach aber {ZEIT}.", "gefuehl": { "stimmung": "gut", "erfuellung": "+", "zeit": "dyn" } },
          "misserfolg": { "text": "Im befristeten Traumjob kommt Alexandra nur langsam voran, und die Befristung setzt sie unter Druck. Sie ist verunsichert, fühlt sich aber erfüllter und hat danach {ZEIT}.", "gefuehl": { "stimmung": "schlecht", "erfuellung": "+", "zeit": "dyn" } }
        },
        "B": {
          "erfolg": { "text": "Alexandra nimmt die unbefristete Stelle an und startet entspannt in den Neustart. Sie ist erleichtert und finanziell besser gestellt, hat danach {ZEIT} und {ENERGIE}.", "gefuehl": { "stimmung": "gut", "finanzen": "+", "zeit": "dyn", "energie": "dyn" } },
          "misserfolg": { "text": "Der Neustart im soliden Job verläuft zäh, und Alexandra bereut ihre Entscheidung ein wenig. Sie ist unzufrieden, aber finanziell besser gestellt und hat danach {ZEIT} und {ENERGIE}.", "gefuehl": { "stimmung": "schlecht", "finanzen": "+", "zeit": "dyn", "energie": "dyn" } }
        }
      }
    },
    "12A1": {
      "ausrichtung": { "A": "kurzfristig", "B": "langfristig" }, "unscharf": false,
      "notiz": "Krisenepisode: Die Optionen unterscheiden sich im Umgang mit der Krise (passiv erdulden gegen aktiv handeln). B investiert in Gesundheit, A sichert kurzfristig den Job.",
      "plausibel": ["Ruf der behandelnden Klinik", "Jahreszeit der Diagnose"],
      "unplausibel": ["Farbe der Wartezimmerwand", "Sternzeichen der Hausärztin", "Länge des Arztbriefs"],
      "ergebnis": {
        "A": {
          "erfolg": { "text": "Alexandra hält im Job durch und bekommt ihre Beschwerden unter Kontrolle. Sie ist erleichtert, hat danach aber {ENERGIE}, und ihr Alltag gerät aus dem Takt.", "gefuehl": { "stimmung": "gut", "energie": "dyn", "lebensstil": "-" } },
          "misserfolg": { "text": "Alexandra erduldet den Arbeitsalltag, doch die Beschwerden nehmen zu. Sie ist niedergeschlagen, hat danach {ENERGIE}, und ihr Alltag gerät aus dem Takt.", "gefuehl": { "stimmung": "schlecht", "energie": "dyn", "lebensstil": "-" } }
        },
        "B": {
          "erfolg": { "text": "Alexandra gibt den Job auf, stellt ihre Gesundheit in den Mittelpunkt und erholt sich Schritt für Schritt. Sie ist erleichtert, hat danach {ZEIT}, fühlt sich erfüllter, und ihr Alltag wird gesünder, doch sie ist finanziell knapper dran.", "gefuehl": { "stimmung": "gut", "zeit": "dyn", "erfuellung": "+", "lebensstil": "+", "finanzen": "-" } },
          "misserfolg": { "text": "Alexandra gibt den Job auf, doch die Genesung kommt nur langsam voran, und die Geldsorgen wachsen. Sie ist bedrückt, hat danach {ZEIT}, fühlt sich aber erfüllter, und ihr Alltag wird gesünder.", "gefuehl": { "stimmung": "schlecht", "zeit": "dyn", "erfuellung": "+", "lebensstil": "+", "finanzen": "-" } }
        }
      }
    },
    "12A2": {
      "ausrichtung": { "A": "kurzfristig", "B": "langfristig" }, "unscharf": true,
      "notiz": "Krisenepisode, nicht eindeutig: A (Start-up verlassen, Sicherheit) lässt sich auch als Investition in die Gesundheit lesen; B (bleiben, kreative Lösungen) investiert in Erfüllung und Sinn.",
      "plausibel": ["Alter des Start-ups", "Länge des Arbeitswegs"],
      "unplausibel": ["Lieblingsfarbe der Ärztin", "Handymarke des Teams", "Hausnummer der Praxis"],
      "ergebnis": {
        "A": {
          "erfolg": { "text": "Alexandra verlässt das Start-up und findet schnell eine Stelle mit guter Krankenversicherung. Sie ist erleichtert und finanziell besser gestellt, hat danach {ZEIT}, und ihr Alltag wird geordneter.", "gefuehl": { "stimmung": "gut", "finanzen": "+", "zeit": "dyn", "lebensstil": "+" } },
          "misserfolg": { "text": "Alexandra verlässt das Start-up, doch eine passende Stelle mit guter Versicherung findet sie vorerst nicht. Sie ist bedrückt und hat danach {ZEIT}.", "gefuehl": { "stimmung": "schlecht", "zeit": "dyn" } }
        },
        "B": {
          "erfolg": { "text": "Alexandra bleibt im Start-up und findet kreative Lösungen für Behandlung und Arbeit. Sie ist zuversichtlich und fühlt sich erfüllter, ist aber finanziell knapper dran und hat danach {ZEIT} und {ENERGIE}.", "gefuehl": { "stimmung": "gut", "erfuellung": "+", "finanzen": "-", "zeit": "dyn", "energie": "dyn" } },
          "misserfolg": { "text": "Alexandra bleibt im Start-up, doch ein Kompromiss zwischen Behandlung und Arbeit gelingt nicht richtig. Sie ist bedrückt, fühlt sich aber erfüllter und hat danach {ZEIT} und {ENERGIE}.", "gefuehl": { "stimmung": "schlecht", "erfuellung": "+", "zeit": "dyn", "energie": "dyn" } }
        }
      }
    },
    "12B1": {
      "ausrichtung": { "A": "kurzfristig", "B": "langfristig" }, "unscharf": false,
      "notiz": "Krisenepisode: A flüchtet in die Arbeit (Vermeidung), B verarbeitet und baut neu auf.",
      "plausibel": ["Meinung der Kolleginnen zur Trennung", "Länge des Vertrags im Traumjob"],
      "unplausibel": ["Schuhgrösse des Ex-Partners", "Wochentag der Trennung", "Farbe des gemeinsamen Sofas"],
      "ergebnis": {
        "A": {
          "erfolg": { "text": "Alexandra stürzt sich in die Arbeit und liefert trotz des Beziehungsendes Höchstleistung. Sie ist stolz, hat danach aber {ENERGIE}, und ihr Alltag gerät aus dem Takt.", "gefuehl": { "stimmung": "gut", "energie": "dyn", "lebensstil": "-" } },
          "misserfolg": { "text": "Alexandra flüchtet in die Arbeit, doch die Konzentration fehlt, und der Schmerz bleibt. Sie ist niedergeschlagen, hat danach {ENERGIE}, und ihr Alltag gerät aus dem Takt.", "gefuehl": { "stimmung": "schlecht", "energie": "dyn", "lebensstil": "-" } }
        },
        "B": {
          "erfolg": { "text": "Alexandra nimmt sich Zeit für die Trauer und beginnt dann, ihr Leben bewusst neu aufzubauen. Sie ist erleichtert, fühlt sich verbundener und erfüllter und hat danach {ZEIT}.", "gefuehl": { "stimmung": "gut", "soz": "+", "erfuellung": "+", "zeit": "dyn" } },
          "misserfolg": { "text": "Alexandra nimmt sich Zeit für die Trauer, doch der Neuanfang kommt nur schleppend in Gang. Sie ist bedrückt, fühlt sich aber verbundener und erfüllter und hat danach {ZEIT}.", "gefuehl": { "stimmung": "schlecht", "soz": "+", "erfuellung": "+", "zeit": "dyn" } }
        }
      }
    },
    "12B2": {
      "ausrichtung": { "A": "kurzfristig", "B": "langfristig" }, "unscharf": true,
      "notiz": "Krisenepisode, nicht eindeutig: Beide Optionen sind aktive Wege (Organisation gegen persönliche Fürsorge). Die Einordnung folgt dem Einsatz: A sichert Job und Einkommen, B investiert in Beziehung zur Mutter.",
      "plausibel": ["Name des Pflegedienstes", "Entfernung zum Wohnort der Mutter"],
      "unplausibel": ["Lieblingsfarbe der Pflegefachperson", "Hausnummer der Klinik", "Postleitzahl der Mutter"],
      "ergebnis": {
        "A": {
          "erfolg": { "text": "Alexandra organisiert eine gute professionelle Pflege für ihre Mutter und bleibt in ihrem Job. Sie ist erleichtert, aber finanziell knapper dran und hat danach {ENERGIE}.", "gefuehl": { "stimmung": "gut", "finanzen": "-", "energie": "dyn" } },
          "misserfolg": { "text": "Die organisierte Pflege funktioniert nicht richtig, und Alexandra fühlt sich schuldig, weil sie ihre Mutter nicht selbst betreut. Sie ist niedergeschlagen, finanziell knapper dran und hat danach {ENERGIE}.", "gefuehl": { "stimmung": "schlecht", "finanzen": "-", "energie": "dyn" } }
        },
        "B": {
          "erfolg": { "text": "Alexandra reduziert ihre Arbeit und schafft es, die Pflege ihrer Mutter gut zu organisieren. Sie ist erleichtert und fühlt sich verbundener, hat danach aber {ZEIT} und {ENERGIE} und ist finanziell knapper dran.", "gefuehl": { "stimmung": "gut", "soz": "+", "zeit": "dyn", "energie": "dyn", "finanzen": "-" } },
          "misserfolg": { "text": "Die Pflege ihrer Mutter wächst Alexandra über den Kopf, und sie kommt kaum noch zu anderem. Sie ist verzweifelt, fühlt sich aber verbundener, hat danach {ZEIT} und {ENERGIE} und ist finanziell knapper dran.", "gefuehl": { "stimmung": "schlecht", "soz": "+", "zeit": "dyn", "energie": "dyn", "finanzen": "-" } }
        }
      }
    }
  }
};
