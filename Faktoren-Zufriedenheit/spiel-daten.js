/* AUTOMATISCH ERZEUGT von tools/erzeuge_daten.py aus Excel und Word. Nicht von Hand abschreiben.
   Zum Aendern: Quelle anpassen und das Skript neu laufen lassen (oder hier gezielt editieren). */
var SPIEL_DATEN = {
 "meta": {
  "titel": "Glücksfaktoren-Spiel",
  "figur": "Alexandra",
  "quelleExcel": "gluecksfaktoren.xlsx, Blatt Tabelle1, Zeilen 3-46",
  "quelleWord": "gluecksfaktor_spiel.docx",
  "erzeugtMit": "tools/erzeuge_daten.py",
  "excelAuffaelligkeiten": [
   "Zellen Y3 und Y40 (Stimmung nach der Entscheidung) enthalten keine Formel. Die Seite rechnet dort wie in allen anderen 36 Zeilen M+AN."
  ]
 },
 "attribute": [
  {
   "key": "zeit",
   "name": "Zeit",
   "langname": "Zeit"
  },
  {
   "key": "energie",
   "name": "Energie",
   "langname": "Energie"
  },
  {
   "key": "soz",
   "name": "Soz. Verb.",
   "langname": "Soziale Verbindungen"
  },
  {
   "key": "erfuellung",
   "name": "Erfüllung",
   "langname": "Persönliche Erfüllung"
  },
  {
   "key": "lebensstil",
   "name": "Lebensstil",
   "langname": "Lebensstil-Qualität"
  },
  {
   "key": "finanzen",
   "name": "Finanzen",
   "langname": "Finanzen"
  }
 ],
 "konfig": {
  "_hinweis": "Zahlen und Formelparameter stammen aus gluecksfaktoren.xlsx (Tabelle1). Aenderungen hier wirken direkt auf das Spiel.",
  "start": {
   "zeit": 0,
   "energie": 0,
   "soz": 1,
   "erfuellung": 1,
   "lebensstil": 1,
   "finanzen": 1,
   "stimmung": 50
  },
  "gewichte": {
   "zeit": 0.25,
   "energie": 0.3,
   "soz": 0.2,
   "erfuellung": 0.55,
   "lebensstil": 0.45,
   "finanzen": 0.25
  },
  "saettigungExcel": {
   "zeit": [
    {
     "ueber": 2,
     "faktor": 2
    },
    {
     "ueber": 4,
     "faktor": 3
    }
   ],
   "energie": [
    {
     "ueber": 2,
     "faktor": 2
    },
    {
     "ueber": 4,
     "faktor": 3
    }
   ],
   "soz": null,
   "erfuellung": null,
   "lebensstil": null,
   "finanzen": [
    {
     "ueber": 2,
     "faktor": 2
    },
    {
     "ueber": 4,
     "faktor": 3
    }
   ]
  },
  "resultat": {
   "faktorSumme": 2,
   "stellen": 1,
   "minimum": 0
  },
  "stimmungsaenderung": {
   "faktor": 8,
   "teiler": 10,
   "stellen": 0
  },
  "energieAusStimmung": {
   "faktor": 8,
   "nullpunkt": 50,
   "teiler": 50,
   "stellen": 0,
   "durch": 2
  },
  "zeitAbzugFinanzen": {
   "finanzenUnter": -2,
   "abzug": 1
  },
  "schranken": {
   "aktiv": false,
   "attributMin": -10,
   "attributMax": 10,
   "stimmungMax": 100
  },
  "spielendeStimmungUnter": 0,
  "wuerfelSeiten": 20,
  "mikroVorschlag": {
   "zeitEnergieUnter": -5,
   "attributUnter": 0
  }
 },
 "blockNamen": {
  "1": "Studium & persönliche Grundlagen",
  "2": "Soziale Beziehungen",
  "3": "Lebensstil & Berufseinstieg",
  "4": "Unvorhersehbare Lebensereignisse (Krisen)"
 },
 "episoden": [
  {
   "id": "1",
   "block": 1,
   "titel": "Studienwahl",
   "vorlesen": "Alexandra war schon immer gut im Verstehen menschlicher Emotionen und hilft Freund*innen bei Problemen. Ihre Eltern drängen sie zu BWL wegen der Karriereaussichten. Sie muss sich heute entscheiden.",
   "beginn": {
    "zeit": 0,
    "energie": 0,
    "stimmung": 0
   },
   "optionen": {
    "A": {
     "label": "BWL studieren",
     "folge": "Alexandra folgt dem Elternwunsch und sichert sich einen Studienplatz in einem gefragten Fach. Wie gut kann sie sich in den ersten Wochen behaupten?",
     "wuerfeltitel": "Guter Studienstart trotz mangelnder Motivation",
     "weiter": "2A",
     "soll": 13,
     "aenderung": {
      "zeit": 1,
      "soz": 0,
      "erfuellung": -1,
      "lebensstil": 0,
      "finanzen": 1
     },
     "energieBasis": 0,
     "excelZeile": 3,
     "excelName": "Block 1 – Ep1 Studienwahl  A – BWL"
    },
    "B": {
     "label": "Psychologie studieren",
     "folge": "Alexandra wählt gegen den Elternwillen und muss beweisen, dass sie trotz unsicherer Zukunft erfolgreich sein kann.",
     "wuerfeltitel": "Guter Studienstart gegen Widerstand",
     "weiter": "2B",
     "soll": 16,
     "aenderung": {
      "zeit": -1,
      "soz": 0,
      "erfuellung": 1,
      "lebensstil": 0,
      "finanzen": -1
     },
     "energieBasis": -1,
     "excelZeile": 4,
     "excelName": "Block 1 – Ep1 Studienwahl  B – Psychologie"
    }
   },
   "glueck": [
    "C1: Arbeit mit Einsatz eigener Fähigkeiten (Primär)"
   ],
   "erkenntnis": [
    "Wichtige Erkenntnis: Sinnstiftende Arbeit (Teil von „Persönliche Erfüllung“)"
   ]
  },
  {
   "id": "2A",
   "block": 1,
   "titel": "Herausforderung im BWL-Studium",
   "vorlesen": "Nach einem Semester langweiliger BWL-Grundlagen bietet ein Professor ein anspruchsvolles Projekt über Unternehmensethik an. Es würde viel Extra-Arbeit bedeuten, aber endlich mal etwas Interessanteres als Buchführung.",
   "beginn": {
    "zeit": 0,
    "energie": 0,
    "stimmung": 0
   },
   "optionen": {
    "A": {
     "label": "Nur Pflicht-Minimum absolvieren",
     "folge": "Alexandra konzentriert sich auf sichere Noten und Freizeit. Schafft sie es, alle To-dos entspannt unter einen Hut zu bekommen?",
     "wuerfeltitel": "Entspannter Semesterabschluss mit soliden Noten",
     "weiter": "3",
     "soll": 11,
     "aenderung": {
      "zeit": 1,
      "soz": 0,
      "erfuellung": -0.5,
      "lebensstil": 0,
      "finanzen": 1
     },
     "energieBasis": 1,
     "excelZeile": 5,
     "excelName": "Block 1 – Ep2A BWL-Herausforderung A – Pflicht-Minimum"
    },
    "B": {
     "label": "Ethik-Projekt übernehmen",
     "folge": "Alexandra stürzt sich in das komplexe Projekt. Kann sie trotz Überforderung etwas Sinnvolles erschaffen?",
     "wuerfeltitel": "Erfolgreiches Projektmanagement trotz Stress",
     "weiter": "3",
     "soll": 17,
     "aenderung": {
      "zeit": -1,
      "soz": 0,
      "erfuellung": 1,
      "lebensstil": -1,
      "finanzen": 0
     },
     "energieBasis": -1,
     "excelZeile": 6,
     "excelName": "Block 1 – Ep2A BWL-Herausforderung B – Ethik-Projekt"
    }
   },
   "glueck": [
    "C2: Flow-Erleben bei angemessenen Herausforderungen (Primär)",
    "C1: Arbeit mit Einsatz eigener Fähigkeiten (Sekundär – Ethik passt besser zu Alexandra als Buchführung)"
   ],
   "erkenntnis": [
    "Wichtige Erkenntnis: Sinnstiftende Arbeit"
   ]
  },
  {
   "id": "2B",
   "block": 1,
   "titel": "Herausforderung im Psychologie-Studium",
   "vorlesen": "Alexandras Statistik-Professor bietet ihr die Chance, bei einem echten Forschungsprojekt mitzuarbeiten. Die Datenanalyse wäre kompliziert und zeitaufwändig, aber sie würde echte Wissenschaft machen.",
   "beginn": {
    "zeit": 0,
    "energie": 0,
    "stimmung": 0
   },
   "optionen": {
    "A": {
     "label": "Normale Kurse belegen",
     "folge": "Alexandra wählt den bewährten Weg und fokussiert sich auf Grundlagen. Gelingt ihr ein strukturierter Semesterablauf?",
     "wuerfeltitel": "Solide Grundausbildung ohne Überforderung",
     "weiter": "3",
     "soll": 12,
     "aenderung": {
      "zeit": 1,
      "soz": 0,
      "erfuellung": -0.5,
      "lebensstil": 0,
      "finanzen": 1
     },
     "energieBasis": 0,
     "excelZeile": 7,
     "excelName": "Block 1 – Ep2B Psycho-Herausforderung A – Normale Kurse"
    },
    "B": {
     "label": "Forschungsprojekt übernehmen",
     "folge": "Alexandra taucht in komplexe Datenanalyse ein. Kann sie trotz steiler Lernkurve einen wissenschaftlichen Beitrag leisten?",
     "wuerfeltitel": "Erfolgreiche Forschungsarbeit trotz hoher Anforderungen",
     "weiter": "3",
     "soll": 18,
     "aenderung": {
      "zeit": -1,
      "soz": 0,
      "erfuellung": 1,
      "lebensstil": -1,
      "finanzen": 0
     },
     "energieBasis": -1,
     "excelZeile": 8,
     "excelName": "Block 1 – Ep2B Psycho-Herausforderung B – Forschungsprojekt"
    }
   },
   "glueck": [
    "C2: Flow-Erleben bei angemessenen Herausforderungen (Primär)",
    "C1: Arbeit mit Einsatz eigener Fähigkeiten (Primär)",
    "G3: Setzen und Verfolgen von Zielen (Sekundär – wissenschaftliche Karriere)"
   ],
   "erkenntnis": []
  },
  {
   "id": "3",
   "block": 1,
   "titel": "Jahresrückblick & Zielsetzung",
   "vorlesen": "Nach einem Jahr Studium reflektiert Alexandra. Manche Kommiliton*innen sind bereits pessimistisch über ihre Zukunftsaussichten und beschweren sich ständig. Alexandra kann entweder konkrete Pläne für ihr weiteres Studium machen oder sich treiben lassen und die pessimistische Haltung übernehmen.",
   "beginn": {
    "zeit": 0,
    "energie": 0,
    "stimmung": 0
   },
   "optionen": {
    "A": {
     "label": "„Mal schauen, was passiert“ (pessimistische Haltung übernehmen)",
     "folge": "Alexandra lässt das Leben auf sich zukommen, übernimmt die negative Sichtweise ihrer Kommiliton*innen und vermeidet stressige Entscheidungen. Gelingt ihr ein entspanntes, sorgenfreies Jahr?",
     "wuerfeltitel": "Entspannter Alltag ohne grosse Sorgen",
     "weiter": "4",
     "soll": 10,
     "aenderung": {
      "zeit": 1,
      "soz": 0,
      "erfuellung": -1,
      "lebensstil": 0,
      "finanzen": 0
     },
     "energieBasis": 0,
     "excelZeile": 9,
     "excelName": "Block 1 – Ep3 Jahresrückblick A – Keine Pläne"
    },
    "B": {
     "label": "Klare 3-Jahres-Ziele definieren und optimistisch nach vorn schauen",
     "folge": "Alexandra erstellt einen detaillierten Plan für Studium, Praktika und Zukunft und entscheidet sich bewusst für eine optimistische, zukunftsorientierte Haltung. Kann sie realistische und motivierende Ziele setzen?",
     "wuerfeltitel": "Sinnvolle Zielsetzung ohne Selbstüberforderung",
     "weiter": "4",
     "soll": 15,
     "aenderung": {
      "zeit": -1,
      "soz": 0,
      "erfuellung": 1,
      "lebensstil": 1,
      "finanzen": 0
     },
     "energieBasis": 0,
     "excelZeile": 10,
     "excelName": "Block 1 – Ep3 Jahresrückblick B – 3-Jahres-Ziele"
    }
   },
   "glueck": [
    "G3: Setzen und Verfolgen von Zielen (Primär)",
    "A2: Optimistische vs. pessimistische Einstellung (Primär)"
   ],
   "erkenntnis": []
  },
  {
   "id": "4",
   "block": 2,
   "titel": "Neue Mitbewohnerin",
   "vorlesen": "Alexandra zieht in eine WG. Lisa wirkt nett, aber sehr schüchtern. Alexandra kann aktiv eine Freundschaft aufbauen oder höflich distanziert bleiben.",
   "beginn": {
    "zeit": 3,
    "energie": 3,
    "stimmung": 0
   },
   "optionen": {
    "A": {
     "label": "Höflich auf Distanz",
     "folge": "Alexandra bleibt freundlich, aber unverbindlich und konzentriert sich auf ihre eigenen Angelegenheiten. Gelingt ihr ein entspanntes WG-Leben ohne Komplikationen?",
     "wuerfeltitel": "Harmonisches WG-Leben ohne Stress",
     "weiter": "5A",
     "soll": 15,
     "aenderung": {
      "zeit": 1,
      "soz": -1,
      "erfuellung": 0,
      "lebensstil": 0,
      "finanzen": 1
     },
     "energieBasis": 1,
     "excelZeile": 13,
     "excelName": "Block 2 – Ep4 Neue Mitbewohnerin A – Höflich distanziert"
    },
    "B": {
     "label": "Aktiv Freundschaft aufbauen",
     "folge": "Alexandra investiert Zeit in gemeinsame Aktivitäten und Gespräche mit der schüchternen Lisa. Kann sie Vertrauen aufbauen und eine echte Freundschaft entwickeln?",
     "wuerfeltitel": "Aufbau einer tragfähigen Freundschaft",
     "weiter": "5B",
     "soll": 16,
     "aenderung": {
      "zeit": -1,
      "soz": 1,
      "erfuellung": 0.5,
      "lebensstil": 0,
      "finanzen": 0
     },
     "energieBasis": -1,
     "excelZeile": 14,
     "excelName": "Block 2 – Ep4 Neue Mitbewohnerin B – Freundschaft aufbauen"
    }
   },
   "glueck": [
    "B1: Enge Freundschaften (Primär)",
    "A3: Extraversion und Liebenswürdigkeit (Sekundär)"
   ],
   "erkenntnis": []
  },
  {
   "id": "5A",
   "block": 2,
   "titel": "Uni-Party",
   "vorlesen": "Auf einer Party plätschern Gespräche. Jemand erwähnt Angst vor der Zukunft. Alexandra kann tief nachfragen oder beim Smalltalk bleiben.",
   "beginn": {
    "zeit": 0,
    "energie": 0,
    "stimmung": 0
   },
   "optionen": {
    "A": {
     "label": "Smalltalk bleiben",
     "folge": "Alexandra hält die Gespräche oberflächlich und geniesst eine entspannte Party-Atmosphäre. Schafft sie es, sich gut zu amüsieren und Kontakte zu knüpfen?",
     "wuerfeltitel": "Unterhaltsame Party ohne tiefere Verbindungen",
     "weiter": "6",
     "soll": 16,
     "aenderung": {
      "zeit": 0,
      "soz": -0.5,
      "erfuellung": 0,
      "lebensstil": 0,
      "finanzen": 0
     },
     "energieBasis": 1,
     "excelZeile": 15,
     "excelName": "Block 2 – Ep5A Uni-Party A – Smalltalk bleiben"
    },
    "B": {
     "label": "Tiefes Gespräch führen",
     "folge": "Alexandra wendet sich der Person mit Zukunftsängsten zu und versucht ein ehrliches Gespräch. Kann sie echte Unterstützung bieten und dabei selbst etwas lernen?",
     "wuerfeltitel": "Bedeutsames Gespräch mit gegenseitigem Gewinn",
     "weiter": "6",
     "soll": 16,
     "aenderung": {
      "zeit": -1,
      "soz": 1,
      "erfuellung": 0,
      "lebensstil": 0,
      "finanzen": 0
     },
     "energieBasis": 0,
     "excelZeile": 16,
     "excelName": "Block 2 – Ep5A Uni-Party B – Tiefes Gespräch"
    }
   },
   "glueck": [
    "B3: Sinnvolle Gespräche statt Smalltalk (Primär)",
    "B1: Enge Freundschaften (Sekundär – potenzielle tiefere Verbindungen)"
   ],
   "erkenntnis": []
  },
  {
   "id": "5B",
   "block": 2,
   "titel": "Lisas Problem",
   "vorlesen": "Lisa ist überfordert und denkt über Abbruch nach. Alexandra kann kurz trösten oder sich Zeit für ein echtes Gespräch nehmen.",
   "beginn": {
    "zeit": 0,
    "energie": 0,
    "stimmung": 0
   },
   "optionen": {
    "A": {
     "label": "Kurz trösten, Thema wechseln",
     "folge": "Alexandra gibt schnelle Ermutigung und lenkt das Gespräch auf Leichteres. Gelingt es ihr, die Stimmung zu heben ohne sich zu tief zu verstricken?",
     "wuerfeltitel": "Oberflächliche Aufmunterung ohne Belastung",
     "weiter": "6",
     "soll": 13,
     "aenderung": {
      "zeit": 1,
      "soz": 0,
      "erfuellung": 0,
      "lebensstil": 0,
      "finanzen": 0
     },
     "energieBasis": 0,
     "excelZeile": 17,
     "excelName": "Block 2 – Ep5B Lisas Problem A – Kurz trösten"
    },
    "B": {
     "label": "Zeit nehmen & wirklich zuhören",
     "folge": "Alexandra setzt sich intensiv mit Lisas Problemen auseinander und versucht konstruktive Hilfe zu leisten. Kann sie echte Unterstützung bieten ohne selbst überlastet zu werden?",
     "wuerfeltitel": "Effektive Hilfe ohne Selbstüberforderung",
     "weiter": "6",
     "soll": 15,
     "aenderung": {
      "zeit": -1,
      "soz": 1,
      "erfuellung": 0,
      "lebensstil": 0,
      "finanzen": 0
     },
     "energieBasis": -1,
     "excelZeile": 18,
     "excelName": "Block 2 – Ep5B Lisas Problem B – Wirklich zuhören"
    }
   },
   "glueck": [
    "B4: Anderen Menschen helfen (Primär)",
    "B3: Sinnvolle Gespräche statt Smalltalk (Primär)",
    "B1: Enge Freundschaften (Sekundär – Freundschaft vertiefen)"
   ],
   "erkenntnis": []
  },
  {
   "id": "6",
   "block": 2,
   "titel": "Helfen oder Eigenzeit",
   "vorlesen": "Ein Kommilitone hat grosse Probleme in einem Fach, das Alexandra gut kann. Gleichzeitig ist ihre Woche voll.",
   "beginn": {
    "zeit": 0,
    "energie": 0,
    "stimmung": 0
   },
   "optionen": {
    "A": {
     "label": "Grenzen setzen („heute nicht, gern später“)",
     "folge": "Alexandra lehnt höflich ab und schützt ihre eigene Zeit für wichtige Aufgaben. Schafft sie es, ohne schlechtes Gewissen bei ihren Prioritäten zu bleiben?",
     "wuerfeltitel": "Gesunde Abgrenzung ohne Schuldgefühle",
     "weiter": "7",
     "soll": 13,
     "aenderung": {
      "zeit": 1,
      "soz": -1,
      "erfuellung": 0,
      "lebensstil": 1,
      "finanzen": 0
     },
     "energieBasis": 1,
     "excelZeile": 19,
     "excelName": "Block 2 – Ep6 Helfen oder Eigenzeit A – Grenzen setzen"
    },
    "B": {
     "label": "Nachhilfe geben (2 Std)",
     "folge": "Alexandra opfert ihre eigene Zeit, um dem Kommilitonen zu helfen. Kann sie effektive Nachhilfe geben und dabei auch persönlich davon profitieren?",
     "wuerfeltitel": "Hilfreiche Nachhilfe mit beiderseitigem Gewinn",
     "weiter": "7",
     "soll": 17,
     "aenderung": {
      "zeit": -1,
      "soz": 1,
      "erfuellung": 0.5,
      "lebensstil": -0.5,
      "finanzen": 1
     },
     "energieBasis": -1,
     "excelZeile": 20,
     "excelName": "Block 2 – Ep6 Helfen oder Eigenzeit B – Nachhilfe geben"
    }
   },
   "glueck": [
    "B4: Anderen Menschen helfen (Primär)",
    "E1: Kontrolle über die eigene Zeit (Option A – Grenzen setzen)",
    "D3: Zeit für Erneuerung (Option A – Eigenzeit schützen)"
   ],
   "erkenntnis": []
  },
  {
   "id": "7",
   "block": 3,
   "titel": "Der erste Job",
   "vorlesen": "Zwei Angebote: gut bezahlte Unternehmensberatung mit Standardaufgaben oder schlechter bezahlte Jugendberatung, wo Alexandra ihre psychologischen Stärken einsetzen kann.",
   "beginn": {
    "zeit": 3,
    "energie": 3,
    "stimmung": 0
   },
   "optionen": {
    "A": {
     "label": "Unternehmensberatung",
     "folge": "Alexandra wählt das lukrative Angebot und startet in einem prestigeträchtigen Umfeld. Kann sie sich trotz mangelnder inhaltlicher Begeisterung professionell etablieren?",
     "wuerfeltitel": "Erfolgreicher Berufseinstieg trotz fehlender Leidenschaft",
     "weiter": "8A",
     "soll": 18,
     "aenderung": {
      "zeit": 0,
      "soz": 0,
      "erfuellung": -1,
      "lebensstil": -1,
      "finanzen": 1
     },
     "energieBasis": -1,
     "excelZeile": 23,
     "excelName": "Block 3 – Ep7 Erster Job A – Unternehmensberatung"
    },
    "B": {
     "label": "Jugendberatung",
     "folge": "Alexandra folgt ihrer Berufung und nimmt das schlechter bezahlte, aber sinnstiftende Angebot an. Gelingt ihr der Einstieg in das herausfordernde soziale Arbeitsfeld?",
     "wuerfeltitel": "Erfolgreicher Start in sinnvoller, aber fordernder Arbeit",
     "weiter": "8B",
     "soll": 18,
     "aenderung": {
      "zeit": -1,
      "soz": 0,
      "erfuellung": 1,
      "lebensstil": -1,
      "finanzen": -1
     },
     "energieBasis": 0,
     "excelZeile": 24,
     "excelName": "Block 3 – Ep7 Erster Job B – Jugendberatung"
    }
   },
   "glueck": [
    "C1: Arbeit mit Einsatz eigener Fähigkeiten (Primär bei Option B)"
   ],
   "erkenntnis": [
    "Wichtige Erkenntnis: Sinnstiftende Arbeit vs. materieller Wohlstand",
    "Forschungserkenntnis: Geld trägt ab gewissem Niveau nicht mehr zu Glück bei"
   ]
  },
  {
   "id": "8A",
   "block": 3,
   "titel": "Überstundenkultur",
   "vorlesen": "In der Beratung gilt: bis 22 Uhr arbeiten, am Wochenende erreichbar, kaum Schlaf. Mitmachen oder Grenzen setzen?",
   "beginn": {
    "zeit": 0,
    "energie": 0,
    "stimmung": 0
   },
   "optionen": {
    "A": {
     "label": "Mitziehen („always on“)",
     "folge": "Alexandra passt sich der Hochleistungskultur an und arbeitet exzessive Stunden mit wenig Schlaf. Schafft sie es, trotz Stress gute Leistungen zu erbringen und anerkannt zu werden?",
     "wuerfeltitel": "Hohe Arbeitsleistung ohne Burnout",
     "weiter": "9",
     "soll": 16,
     "aenderung": {
      "zeit": -2,
      "soz": -1,
      "erfuellung": -1,
      "lebensstil": -1,
      "finanzen": 1
     },
     "energieBasis": -2,
     "excelZeile": 25,
     "excelName": "Block 3 – Ep8A Überstundenkultur A – Mitziehen"
    },
    "B": {
     "label": "Feste Arbeitszeiten, private Zeit und Schlaf schützen",
     "folge": "Alexandra setzt klare Grenzen für Arbeitszeiten und Schlafhygiene und riskiert damit Kritik von Vorgesetzten. Kann sie trotz weniger Präsenz durch Effizienz überzeugen?",
     "wuerfeltitel": "Professionelle Anerkennung trotz Work-Life-Balance",
     "weiter": "9",
     "soll": 18,
     "aenderung": {
      "zeit": 0,
      "soz": 0,
      "erfuellung": 0,
      "lebensstil": 1,
      "finanzen": 0
     },
     "energieBasis": 1,
     "excelZeile": 26,
     "excelName": "Block 3 – Ep8A Überstundenkultur B – Feste Arbeitszeiten"
    }
   },
   "glueck": [
    "E1: Kontrolle über die eigene Zeit (Primär)",
    "D1: Guter Schlaf (Sekundär)",
    "D3: Zeit für Erneuerung (Sekundär)"
   ],
   "erkenntnis": []
  },
  {
   "id": "8B",
   "block": 3,
   "titel": "Flexible Arbeitszeit",
   "vorlesen": "Die Jugendberatung erlaubt flexible Modelle. Feste Bürozeiten wählen oder eigenverantwortlich planen?",
   "beginn": {
    "zeit": 0,
    "energie": 0,
    "stimmung": 0
   },
   "optionen": {
    "A": {
     "label": "Feste Bürozeiten",
     "folge": "Alexandra wählt die Sicherheit fester Strukturen und regelmässiger Kollegenkontakte. Gelingt ihr ein ausgeglichener Arbeitsalltag mit gutem Teamanschluss?",
     "wuerfeltitel": "Strukturierter Alltag mit stabilen Arbeitsbeziehungen",
     "weiter": "9",
     "soll": 18,
     "aenderung": {
      "zeit": 0,
      "soz": 1,
      "erfuellung": -1,
      "lebensstil": -1,
      "finanzen": 0
     },
     "energieBasis": 0,
     "excelZeile": 27,
     "excelName": "Block 3 – Ep8B Flexible Arbeitszeit A – Feste Bürozeiten"
    },
    "B": {
     "label": "Eigenverantwortlich planen",
     "folge": "Alexandra übernimmt volle Verantwortung für ihre Arbeitsorganisation und muss Disziplin beweisen. Kann sie ihre Zeit effektiv strukturieren ohne externe Vorgaben?",
     "wuerfeltitel": "Erfolgreiche Selbstorganisation ohne Prokrastination",
     "weiter": "9",
     "soll": 18,
     "aenderung": {
      "zeit": -1,
      "soz": -1,
      "erfuellung": 1,
      "lebensstil": 1,
      "finanzen": 0
     },
     "energieBasis": 0,
     "excelZeile": 28,
     "excelName": "Block 3 – Ep8B Flexible Arbeitszeit B – Eigenverantwortlich"
    }
   },
   "glueck": [
    "E1: Kontrolle über die eigene Zeit (Primär bei beiden Optionen)"
   ],
   "erkenntnis": [
    "Wichtige Erkenntnis: Eigenverantwortung und Selbstorganisation"
   ]
  },
  {
   "id": "9",
   "block": 3,
   "titel": "Gehaltserhöhung vs. Reise",
   "vorlesen": "Alexandra bekommt eine Gehaltserhöhung. Kolleg:innen vergleichen ständig, wer was Neues gekauft hat – teure Kleidung, Autos, Gadgets. Alexandra könnte mithalten oder das Geld anders verwenden: für eine lang ersehnte Reise nach Island.",
   "beginn": {
    "zeit": 0,
    "energie": 0,
    "stimmung": 0
   },
   "optionen": {
    "A": {
     "label": "Statuskauf (mit Kolleg:innen mithalten)",
     "folge": "Alexandra investiert in teure Kleidung, Technik oder ein Auto, um mit ihren Kolleg:innen mitzuhalten und im sozialen Vergleich gut dazustehen. Kann sie dadurch ihr Standing im Beruf verbessern und sich selbstbewusster fühlen?",
     "wuerfeltitel": "Statusgewinn durch materielle Investitionen",
     "weiter": "10",
     "soll": 13,
     "aenderung": {
      "zeit": 0,
      "soz": 0,
      "erfuellung": 0,
      "lebensstil": -0.5,
      "finanzen": -1
     },
     "energieBasis": 0,
     "excelZeile": 29,
     "excelName": "Block 3 – Ep9 Gehaltserhöhung vs. Reise A – Statuskauf"
    },
    "B": {
     "label": "Erlebnisfokus (Reise planen/sparen)",
     "folge": "Alexandra verzichtet auf Statussymbole und den Vergleich mit anderen und plant stattdessen eine bedeutsame Reise oder Erfahrung. Gelingt es ihr, eine bereichernde und erholsame Zeit zu planen?",
     "wuerfeltitel": "Erfüllende Reiseerfahrung mit nachhaltiger Wirkung",
     "weiter": "10",
     "soll": 15,
     "aenderung": {
      "zeit": 0,
      "soz": 0,
      "erfuellung": 1,
      "lebensstil": 0,
      "finanzen": -1
     },
     "energieBasis": 1,
     "excelZeile": 30,
     "excelName": "Block 3 – Ep9 Gehaltserhöhung vs. Reise B – Erlebnisfokus"
    }
   },
   "glueck": [
    "G2: Investition in Erlebnisse statt materieller Besitz (Primär)",
    "E3: Positive vs. negative Vergleiche mit anderen (Primär)"
   ],
   "erkenntnis": [
    "Wichtige Erkenntnis: Hedonische Anpassung an materielle Güter"
   ]
  },
  {
   "id": "10",
   "block": 4,
   "titel": "Jobverlust-Krise",
   "vorlesen": "Der Arbeitgeber geht bankrott. Alexandra ist arbeitslos. Sie könnte jetzt in Panik verfallen und den Jobverlust als Katastrophe sehen – oder die Situation als Chance neu rahmen. Schnell irgendwas annehmen oder gezielt Traumjobs suchen?",
   "beginn": {
    "zeit": 1,
    "energie": 1,
    "stimmung": -5
   },
   "optionen": {
    "A": {
     "label": "Übergangsjob schnell annehmen (pessimistische Sicht: „Ich muss nehmen, was ich kriege“)",
     "folge": "Alexandra sieht die Situation als Notfall, nimmt das erste verfügbare Angebot, um schnell wieder Einkommen zu haben. Kann sie trotz Panik und Zeitdruck einen halbwegs passenden Job finden?",
     "wuerfeltitel": "Schnelle Jobfindung ohne grosse Abstriche",
     "weiter": "11A",
     "soll": 18,
     "aenderung": {
      "zeit": -1,
      "soz": 0,
      "erfuellung": -0.5,
      "lebensstil": 0,
      "finanzen": 1
     },
     "energieBasis": 0,
     "excelZeile": 33,
     "excelName": "Block 4 – Ep10 Jobverlust-Krise A – Übergang schnell"
    },
    "B": {
     "label": "Zeit nehmen für Traumjobsuche (optimistische Neurahmung: „Endlich die Chance für den richtigen Job“)",
     "folge": "Alexandra rahmt den Jobverlust als Gelegenheit um, riskiert eine längere arbeitslose Phase, bleibt aber zuversichtlich, um den wirklich passenden Job zu finden. Gelingt ihr eine zielgerichtete Suche ohne zu lange finanzielle Engpässe?",
     "wuerfeltitel": "Erfolgreiche Traumjobsuche trotz Risiko",
     "weiter": "11B",
     "soll": 19,
     "aenderung": {
      "zeit": -2,
      "soz": 0,
      "erfuellung": 1.5,
      "lebensstil": 0,
      "finanzen": -1
     },
     "energieBasis": -1,
     "excelZeile": 34,
     "excelName": "Block 4 – Ep10 Jobverlust-Krise B – Traumjobsuche"
    }
   },
   "glueck": [
    "A2: Optimistische vs. pessimistische Einstellung (Primär)",
    "C1: Arbeit mit Einsatz eigener Fähigkeiten (Sekundär bei Option B)"
   ],
   "erkenntnis": [
    "Wichtige Erkenntnis: Kognitive Neurahmung (Reframing)"
   ]
  },
  {
   "id": "11A",
   "block": 4,
   "titel": "Kompromiss-Job → Start-up-Angebot",
   "vorlesen": "Im Übergangsjob läuft es solide, doch nun lockt ein Start-up: mehr Sinn, mehr Risiko.",
   "beginn": {
    "zeit": 0,
    "energie": 0,
    "stimmung": 0
   },
   "optionen": {
    "A": {
     "label": "Sicheren Job behalten",
     "folge": "Alexandra bleibt bei der bewährten, stabilen Lösung und verzichtet auf das ungewisse Abenteuer. Kann sie sich mit dieser Entscheidung langfristig arrangieren?",
     "wuerfeltitel": "Zufriedenheit mit sicherem, aber mittelmässigem Job",
     "weiter": "12A1",
     "soll": 13,
     "aenderung": {
      "zeit": 0,
      "soz": 0,
      "erfuellung": -1,
      "lebensstil": 0,
      "finanzen": 1
     },
     "energieBasis": 1,
     "excelZeile": 35,
     "excelName": "Block 4 – Ep11A Start-up-Angebot A – Sicheren Job behalten"
    },
    "B": {
     "label": "Start-up-Risiko eingehen",
     "folge": "Alexandra wagt den Sprung ins Ungewisse und hofft auf ein erfüllendes Arbeitsumfeld. Kann sie sich im dynamischen Start-up-Umfeld beweisen?",
     "wuerfeltitel": "Erfolgreicher Übergang ins riskante, aber sinnvolle Start-up",
     "weiter": "12A2",
     "soll": 18,
     "aenderung": {
      "zeit": -1,
      "soz": 0,
      "erfuellung": 1,
      "lebensstil": 0,
      "finanzen": -1
     },
     "energieBasis": 0,
     "excelZeile": 36,
     "excelName": "Block 4 – Ep11A Start-up-Angebot B – Start-up-Risiko"
    }
   },
   "glueck": [
    "C1: Arbeit mit Einsatz eigener Fähigkeiten (bei Option B)"
   ],
   "erkenntnis": [
    "Wichtige Erkenntnis: Sicherheit vs. Sinnerfüllung, Risikobereitschaft"
   ]
  },
  {
   "id": "11B",
   "block": 4,
   "titel": "Lange Suche → Zwei Angebote",
   "vorlesen": "Zwei Angebote nach langer Suche: befristeter Traumjob oder unbefristeter solider Job.",
   "beginn": {
    "zeit": 0,
    "energie": 0,
    "stimmung": 0
   },
   "optionen": {
    "A": {
     "label": "Befristeter Traumjob",
     "folge": "Alexandra entscheidet sich für das inspirierende, aber unsichere Angebot. Kann sie in der begrenzten Zeit genug erreichen, um ihre Position zu festigen?",
     "wuerfeltitel": "Maximaler Nutzen aus der befristeten Traumposition",
     "weiter": "12B1",
     "soll": 17,
     "aenderung": {
      "zeit": -1,
      "soz": 0,
      "erfuellung": 1,
      "lebensstil": 0,
      "finanzen": 0
     },
     "energieBasis": 0,
     "excelZeile": 37,
     "excelName": "Block 4 – Ep11B Zwei Angebote A – Befristeter Traumjob"
    },
    "B": {
     "label": "Unbefristeter solider Job",
     "folge": "Alexandra wählt Sicherheit über Leidenschaft und nimmt das solide, langfristige Angebot an. Gelingt ihr ein entspannter Neustart ohne Reue?",
     "wuerfeltitel": "Erfolgreicher Neustart in sicherer Position",
     "weiter": "12B2",
     "soll": 14,
     "aenderung": {
      "zeit": 1,
      "soz": 0,
      "erfuellung": 0,
      "lebensstil": 0,
      "finanzen": 1
     },
     "energieBasis": 1,
     "excelZeile": 38,
     "excelName": "Block 4 – Ep11B Zwei Angebote B – Unbefristeter Job"
    }
   },
   "glueck": [
    "C1: Arbeit mit Einsatz eigener Fähigkeiten (bei Option A)"
   ],
   "erkenntnis": [
    "Wichtige Erkenntnis: Kurzfristige vs. langfristige Perspektive"
   ]
  },
  {
   "id": "12A1",
   "block": 4,
   "titel": "Gesundheitskrise im sicheren Job",
   "vorlesen": "Diagnose: chronische Krankheit. Der sichere, aber wenig sinnerfüllte Job bietet Versicherung; der Stress verschlimmert Symptome.",
   "beginn": {
    "zeit": 0,
    "energie": 0,
    "stimmung": -10
   },
   "optionen": {
    "A": {
     "label": "Job behalten & durchhalten (passiv erdulden)",
     "folge": "Alexandra kämpft sich passiv und resigniert aufgrund gesundheitlicher Probleme durch den belastenden Arbeitsalltag. Kann sie ihre Gesundheit stabilisieren ohne den Job zu verlieren?",
     "wuerfeltitel": "Gesundheitsmanagement trotz stressiger Arbeit",
     "weiter": null,
     "soll": 20,
     "aenderung": {
      "zeit": 0,
      "soz": 0,
      "erfuellung": 0,
      "lebensstil": -1,
      "finanzen": 0
     },
     "energieBasis": -2,
     "excelZeile": 39,
     "excelName": "Block 4 – Ep12A1 Gesundheitskrise sicher A – Job behalten"
    },
    "B": {
     "label": "Job aufgeben & Heilung priorisieren (aktiv handeln trotz Angst)",
     "folge": "Alexandra riskiert finanzielle Unsicherheit, entscheidet sich aber bewusst für aktives Handeln, um ihre Gesundheit in den Mittelpunkt zu stellen. Sie verhält sich dabei so zuversichtlich und proaktiv wie es ihr möglich ist. Gelingt ihr eine Genesung ohne existenzielle Sorgen?",
     "wuerfeltitel": "Erfolgreiche Gesundheitswiederherstellung trotz Jobverlust",
     "weiter": null,
     "soll": 17,
     "aenderung": {
      "zeit": 1,
      "soz": 0,
      "erfuellung": 1,
      "lebensstil": 1,
      "finanzen": -2
     },
     "energieBasis": 0,
     "excelZeile": 40,
     "excelName": "Block 4 – Ep12A1 Gesundheitskrise sicher B – Heilung priorisieren"
    }
   },
   "glueck": [
    "G1: Handeln als wäre man glücklich / bewusstes positives Verhalten (Primär bei Option B)",
    "E1: Kontrolle über eigenes Leben (Primär bei Option B)"
   ],
   "erkenntnis": [
    "Wichtige Erkenntnis: Aktives vs. passives Coping in Krisen"
   ]
  },
  {
   "id": "12A2",
   "block": 4,
   "titel": "Gesundheitskrise im Start-up",
   "vorlesen": "Die Krankheit trifft mitten im Start-up. Versicherung mager, Arbeit erfüllt.",
   "beginn": {
    "zeit": 0,
    "energie": 0,
    "stimmung": -10
   },
   "optionen": {
    "A": {
     "label": "Start-up verlassen, bessere Versorgung suchen (Sicherheit priorisieren)",
     "folge": "Alexandra opfert ihre Traumposition für bessere medizinische Absicherung. Kann sie schnell eine neue Stelle mit guter Krankenversicherung finden?",
     "wuerfeltitel": "Erfolgreiche Jobsuche trotz Gesundheitsprobleme",
     "weiter": null,
     "soll": 16,
     "aenderung": {
      "zeit": -1,
      "soz": 0,
      "erfuellung": 0,
      "lebensstil": 1,
      "finanzen": 1
     },
     "energieBasis": 0,
     "excelZeile": 41,
     "excelName": "Block 4 – Ep12A2 Gesundheitskrise Start-up A – Start-up verlassen"
    },
    "B": {
     "label": "Bleiben & kreative Lösungen finden (optimistisch und proaktiv handeln)",
     "folge": "Alexandra entscheidet sich bewusst für eine optimistische Haltung und versucht, sowohl ihre Gesundheit als auch ihre Traumposition zu retten, indem sie aktiv Lösungen entwickelt. Gelingt ihr ein kreativer Kompromiss zwischen Behandlung und Arbeit?",
     "wuerfeltitel": "Innovation bei Gesundheitsmanagement und Joberhalt",
     "weiter": null,
     "soll": 19,
     "aenderung": {
      "zeit": -1,
      "soz": 0,
      "erfuellung": 1,
      "lebensstil": 0,
      "finanzen": -1
     },
     "energieBasis": -1,
     "excelZeile": 42,
     "excelName": "Block 4 – Ep12A2 Gesundheitskrise Start-up B – Kreative Lösungen"
    }
   },
   "glueck": [
    "A2: Optimistische Einstellung (Primär bei Option B)",
    "G1: Handeln als wäre man glücklich / bewusstes positives Verhalten (Primär bei Option B)"
   ],
   "erkenntnis": [
    "Wichtige Erkenntnis: Kreativität und Problemlösungsfähigkeit in Krisen"
   ]
  },
  {
   "id": "12B1",
   "block": 4,
   "titel": "Beziehungskrise im Traumjob",
   "vorlesen": "Traumjob läuft, aber die langjährige Beziehung zerbricht. Vertrag endet bald. Alexandra ist am Boden zerstört.",
   "beginn": {
    "zeit": 0,
    "energie": 0,
    "stimmung": -10
   },
   "optionen": {
    "A": {
     "label": "In Arbeit flüchten (so tun als wäre man funktionsfähig)",
     "folge": "Alexandra stürzt sich vollständig in die Arbeit und versucht durch aktives, positives Arbeitsverhalten, um den emotionalen Schmerz zu verdrängen. Kann sie trotz innerer Turbulenzen Höchstleistungen erbringen?",
     "wuerfeltitel": "Professionelle Leistung trotz emotionaler Belastung",
     "weiter": null,
     "soll": 18,
     "aenderung": {
      "zeit": 0,
      "soz": 0,
      "erfuellung": 0,
      "lebensstil": -1,
      "finanzen": 0
     },
     "energieBasis": -2,
     "excelZeile": 43,
     "excelName": "Block 4 – Ep12B1 Beziehungskrise Traumjob A – In Arbeit flüchten"
    },
    "B": {
     "label": "Zeit für Trauer, dann neu aufbauen (Gefühle zulassen, dann bewusst positiv handeln)",
     "folge": "Alexandra nimmt sich bewusst Zeit für die Verarbeitung und wählt dann gezielt positive Aktivitäten für den Neuanfang. Gelingt ihr eine gesunde Bewältigung ohne Karriereeinbussen?",
     "wuerfeltitel": "Emotionale Verarbeitung mit anschliessendem Neustart",
     "weiter": null,
     "soll": 17,
     "aenderung": {
      "zeit": -2,
      "soz": 1,
      "erfuellung": 1,
      "lebensstil": 0,
      "finanzen": 0
     },
     "energieBasis": 0,
     "excelZeile": 44,
     "excelName": "Block 4 – Ep12B1 Beziehungskrise Traumjob B – Zeit für Trauer"
    }
   },
   "glueck": [
    "G1: Handeln als wäre man glücklich (beide Optionen auf unterschiedliche Weise)",
    "D3: Zeit für Erneuerung (Primär bei Option B)"
   ],
   "erkenntnis": [
    "Wichtige Erkenntnis: Emotionale Verarbeitung vs. Vermeidung"
   ]
  },
  {
   "id": "12B2",
   "block": 4,
   "titel": "Familienkrise im soliden Job",
   "vorlesen": "Die Mutter erkrankt und braucht Pflege. Der Job ist sicher, aber unflexibel. Alexandra fühlt sich zerrissen und schuldig.",
   "beginn": {
    "zeit": 0,
    "energie": 0,
    "stimmung": -10
   },
   "optionen": {
    "A": {
     "label": "Job priorisieren & professionelle Pflege organisieren (aktiv organisieren)",
     "folge": "Alexandra übernimmt trotz emotionaler Belastung aktiv die Organisation der externen Betreuung und hält an ihrer Karriere fest. Kann sie eine gute Pflegelösung finden ohne das Gefühl, die Familie im Stich zu lassen?",
     "wuerfeltitel": "Effektive Organisation externer Pflege",
     "weiter": null,
     "soll": 16,
     "aenderung": {
      "zeit": 0,
      "soz": 0,
      "erfuellung": 0,
      "lebensstil": 0,
      "finanzen": -1
     },
     "energieBasis": -1,
     "excelZeile": 45,
     "excelName": "Block 4 – Ep12B2 Familienkrise solider Job A – Job priorisieren"
    },
    "B": {
     "label": "Auszeit/Reduktion & selbst pflegen (Kontrolle durch persönliche Fürsorge)",
     "folge": "Alexandra reduziert ihre Arbeitszeit drastisch, um ihre Mutter persönlich zu pflegen und nimmt damit aktiv Kontrolle über die Situation. Kann sie die emotionale und physische Belastung der Pflege bewältigen ohne selbst zu erschöpfen?",
     "wuerfeltitel": "Erfolgreiche Familienpflege ohne eigene Überforderung",
     "weiter": null,
     "soll": 18,
     "aenderung": {
      "zeit": -2,
      "soz": 1,
      "erfuellung": 0,
      "lebensstil": -1,
      "finanzen": -1
     },
     "energieBasis": -1,
     "excelZeile": 46,
     "excelName": "Block 4 – Ep12B2 Familienkrise solider Job B – Selbst pflegen"
    }
   },
   "glueck": [
    "E1: Kontrolle über eigene Entscheidungen in Krisenzeiten (Primär)",
    "B4: Anderen Menschen helfen (Primär bei Option B)"
   ],
   "erkenntnis": [
    "Wichtige Erkenntnis: Vereinbarkeit von Arbeit und Familie, Pflegeverantwortung"
   ]
  }
 ],
 "mikroszenen": [
  {
   "id": "M1",
   "titel": "Schlafhygiene vs. Nachtaktivität",
   "vorlesen": "Alexandra merkt, dass sie oft bis spät in die Nacht wach bleibt und morgens müde ist. Sie könnte feste Schlafenszeiten einführen oder weitermachen wie bisher.",
   "optionen": {
    "A": {
     "label": "Weiter chaotisch schlafen",
     "deltas": {
      "zeit": 1,
      "energie": 1,
      "lebensstil": -1
     }
    },
    "B": {
     "label": "Feste Schlafenszeiten etablieren",
     "deltas": {
      "zeit": -1,
      "energie": 1,
      "lebensstil": 1
     }
    }
   },
   "glueck": [
    "D1 – Guter Schlaf"
   ]
  },
  {
   "id": "M2",
   "titel": "Gemeinschaft andocken",
   "vorlesen": "Chor/Unisport/Verein/Study-Group sucht Mitglieder. Zeit ist knapp.",
   "optionen": {
    "A": {
     "label": "Absagen",
     "deltas": {
      "zeit": 1,
      "energie": 1
     }
    },
    "B": {
     "label": "Mitmachen (1 Termin)",
     "deltas": {
      "zeit": -1,
      "soz": 1
     }
    }
   },
   "glueck": [
    "B1: Enge Freundschaften (Primär)",
    "A3: Extraversion und Liebenswürdigkeit (Sekundär)"
   ]
  },
  {
   "id": "M3",
   "titel": "Sport vs. Netflix-Marathon",
   "vorlesen": "Nach einem anstrengenden Tag lockt die Couch, aber Alexandra hatte sich Bewegung vorgenommen.",
   "optionen": {
    "A": {
     "label": "Entspannung wählen",
     "deltas": {
      "zeit": 1,
      "energie": 1
     }
    },
    "B": {
     "label": "Sport treiben",
     "deltas": {
      "zeit": -1,
      "energie": -1,
      "lebensstil": 1
     }
    }
   },
   "glueck": [
    "D2: Sport/Bewegung (Primär)",
    "C3: Aktiver Lebensstil (Sekundär)"
   ]
  },
  {
   "id": "M4",
   "titel": "Dankbarkeitstagebuch vs. Social Media",
   "vorlesen": "Vor dem Schlafen: das Handy lockt mit Notifications, aber Alexandra könnte auch reflektieren.",
   "optionen": {
    "A": {
     "label": "Social Media checken",
     "deltas": {
      "zeit": 0,
      "energie": 1
     }
    },
    "B": {
     "label": "5 Minuten Dankbarkeit notieren",
     "deltas": {
      "zeit": -1,
      "energie": 0,
      "erfuellung": 1
     }
    }
   },
   "glueck": [
    "E2: Dankbarkeit (Primär)",
    "D1: Guter Schlaf (Sekundär – durch bessere Abendroutine)"
   ]
  },
  {
   "id": "M5",
   "titel": "Freunde kontaktieren vs. Zeit für bewusste Erneuerung",
   "vorlesen": "Alexandra merkt, dass sie schon lange niemanden mehr angerufen hat, fühlt sich aber auch erschöpft und merkt, dass sie Zeit für sich selbst braucht. Kontakt aufnehmen oder bewusst einen Abend nur für Selbstfürsorge nehmen (Bad, Buch, früh schlafen)?",
   "optionen": {
    "A": {
     "label": "Bewusste Selbstfürsorge",
     "deltas": {
      "zeit": 1,
      "energie": 2,
      "lebensstil": 1
     }
    },
    "B": {
     "label": "Jemanden anrufen",
     "deltas": {
      "zeit": -1,
      "energie": 1,
      "soz": 1
     }
    }
   },
   "glueck": [
    "B1 – Enge Freundschaften (Option B)",
    "D3 – Zeit für Erneuerung und Alleinsein (Option A)"
   ]
  },
  {
   "id": "M6",
   "titel": "Skill entwickeln vs. passiv konsumieren",
   "vorlesen": "Abends Zeit für ein Online-Tutorial (Sprache/Instrument/Kochen) oder lieber entspannt Videos schauen?",
   "optionen": {
    "A": {
     "label": "Videos schauen",
     "deltas": {
      "zeit": 0,
      "energie": 1
     }
    },
    "B": {
     "label": "Aktiv lernen",
     "deltas": {
      "zeit": -1,
      "energie": -1,
      "erfuellung": 1
     }
    }
   },
   "glueck": [
    "C2: Flow-Erleben bei angemessenen Herausforderungen (Primär)",
    "C1: Arbeit/Hobbys mit Einsatz eigener Fähigkeiten (Sekundär)"
   ]
  },
  {
   "id": "M7",
   "titel": "Meal Prep vs. spontan entscheiden",
   "vorlesen": "Sonntag: Alexandra könnte Mahlzeiten für die Woche vorbereiten oder spontan entscheiden.",
   "optionen": {
    "A": {
     "label": "Spontan bleiben",
     "deltas": {
      "zeit": 2,
      "energie": 1,
      "finanzen": -1
     }
    },
    "B": {
     "label": "Meal Prep",
     "deltas": {
      "zeit": -2,
      "energie": -1,
      "lebensstil": 1,
      "finanzen": 1
     }
    }
   },
   "glueck": [
    "E1: Kontrolle über die eigene Zeit (Primär – Zeitgewinn in der Woche)",
    "D2: Gesunder Lebensstil (Sekundär – bessere Ernährung)"
   ]
  },
  {
   "id": "M8",
   "titel": "Ehrenamtlich helfen vs. Freizeit",
   "vorlesen": "Eine Organisation sucht Freiwillige für ein Wochenend-Projekt. Zeit ist knapp.",
   "optionen": {
    "A": {
     "label": "Freizeit schützen",
     "deltas": {
      "zeit": 2
     }
    },
    "B": {
     "label": "Helfen gehen",
     "deltas": {
      "zeit": -2,
      "energie": -1,
      "soz": 1,
      "erfuellung": 1
     }
    }
   },
   "glueck": []
  },
  {
   "id": "M9",
   "titel": "Aufräumen vs. Chaos akzeptieren",
   "vorlesen": "Die Wohnung ist unordentlich. Alexandra bemerkt, dass die Unordnung sie unbewusst stresst. Grossputz machen oder damit leben?",
   "optionen": {
    "A": {
     "label": "Chaos akzeptieren",
     "deltas": {
      "zeit": 1,
      "energie": 1
     }
    },
    "B": {
     "label": "Ordnung schaffen",
     "deltas": {
      "zeit": -2,
      "energie": -2,
      "lebensstil": 2
     }
    }
   },
   "glueck": [
    "E1 – Kontrolle über die eigene Zeit/Umgebung (Ordnung schafft Kontrollgefühl)"
   ]
  },
  {
   "id": "M10",
   "titel": "Meditation vs. Ablenkung",
   "vorlesen": "Alexandra fühlt sich gestresst. Kurz innehalten und meditieren oder sich ablenken?",
   "optionen": {
    "A": {
     "label": "Ablenkung suchen",
     "deltas": {
      "zeit": -1,
      "energie": 1
     }
    },
    "B": {
     "label": "10 Minuten meditieren",
     "deltas": {
      "zeit": -1,
      "energie": 1,
      "lebensstil": 1
     }
    }
   },
   "glueck": [
    "D3: Zeit für Erneuerung und Alleinsein (Primär)",
    "E1: Kontrolle über eigene mentale Zustände (Sekundär)"
   ]
  }
 ],
 "mikroZuordnung": [
  {
   "kriterium": "Zeit oder Energie kritisch niedrig (unter -5)",
   "szenen": [
    {
     "id": "M1",
     "hinweis": ""
    },
    {
     "id": "M3",
     "hinweis": "für Energie"
    },
    {
     "id": "M5",
     "hinweis": "für beides"
    },
    {
     "id": "M10",
     "hinweis": "für Regeneration"
    }
   ]
  },
  {
   "kriterium": "Soziale Verbindungen vernachlässigt",
   "szenen": [
    {
     "id": "M2",
     "hinweis": ""
    },
    {
     "id": "M5",
     "hinweis": ""
    }
   ]
  },
  {
   "kriterium": "Persönliche Erfüllung niedrig",
   "szenen": [
    {
     "id": "M4",
     "hinweis": ""
    },
    {
     "id": "M6",
     "hinweis": ""
    },
    {
     "id": "M8",
     "hinweis": ""
    }
   ]
  },
  {
   "kriterium": "Lebensstil-Qualität niedrig",
   "szenen": [
    {
     "id": "M7",
     "hinweis": ""
    },
    {
     "id": "M9",
     "hinweis": ""
    }
   ]
  }
 ]
};
