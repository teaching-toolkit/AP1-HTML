/* befunde.js: Daten der fünf Forschungsbefunde (klassisches Skript, kein Modul).
   Erzeugt durch tests/extract_befunde.py aus dem Wiederholungsauftrag Einführung 2,
   Aktivität 1 (fünf von neun Befunden, Auswahl im Skript). Nicht von Hand ändern, sondern neu erzeugen.
   Pro Befund zwei Fassungen A und B mit je Studie und Erklärung.
   *wort* markiert ein hervorgehobenes Wort (wird kursiv angezeigt).
   quelle und vorbehalt werden nur in der Auflösung angezeigt (Knopf «Auflösung anzeigen»). */
window.BEFUNDE = [
  {
    nr: 1,
    titel: "Gesichtsattraktivität und Durchschnittlichkeit",
    A: {
      studie: "Computer-generierte Gesichter werden als *attraktiver* bewertet, je mehr Einzelgesichter zu ihrer Erstellung gemittelt wurden.",
      erklaerung: "Durchschnittliche Gesichter signalisieren genetische Gesundheit und Normalität. Extreme Merkmale könnten auf Mutationen hinweisen, daher bevorzugen wir evolutionär das \"Mittelmass\" als sicheren Partner."
    },
    B: {
      studie: "Computer-generierte Gesichter werden als *unattraktiver* bewertet, je mehr Einzelgesichter zu ihrer Erstellung gemittelt wurden.",
      erklaerung: "Attraktivität entsteht durch einzigartige, markante Merkmale. Durchschnittsgesichter wirken langweilig und austauschbar. Menschen bevorzugen charakteristische Züge, die Individualität und besondere Gene signalisieren."
    },
    quelle: "Langlois & Roggman (1990), Psychological Science, 1(2), 115–121.",
    vorbehalt: "Gemittelte Gesichter wirken attraktiv, sind aber nicht die attraktivsten: Die gemittelte Form besonders attraktiver Gesichter wurde dem Durchschnitt aller Gesichter vorgezogen (Perrett, May & Yoshikawa, 1994, Nature, 368, 239–242). Warum Durchschnittsgesichter attraktiv wirken, ist offen: Langlois und Roggman nennen evolutionäre und kognitive Gründe."
  },
  {
    nr: 2,
    titel: "Belohnung und Motivation",
    A: {
      studie: "Kinder, die für das Malen belohnt werden, malen später *weniger* gerne als Kinder ohne Belohnung.",
      erklaerung: "Externe Belohnungen untergraben die intrinsische Motivation. Kinder interpretieren die Belohnung als Signal, dass die Aktivität nicht von sich aus wertvoll ist (\"Wenn ich bezahlt werde, muss es langweilig sein\")."
    },
    B: {
      studie: "Kinder, die für das Malen belohnt werden, malen später *lieber* als Kinder ohne Belohnung.",
      erklaerung: "Belohnungen verstärken positive Assoziationen mit der Aktivität. Kinder verknüpfen das Malen mit angenehmen Erfahrungen und entwickeln dadurch eine stärkere Präferenz."
    },
    quelle: "Lepper, Greene & Nisbett (1973), Journal of Personality and Social Psychology, 28(1), 129–137; Metaanalyse: Deci, Koestner & Ryan (1999), Psychological Bulletin, 125(6), 627–668.",
    vorbehalt: "Der Effekt zeigt sich bei erwarteter, an die Tätigkeit geknüpfter Belohnung, nicht bei unerwarteter (Deci, Koestner & Ryan, 1999). Wie allgemein er gilt, ist umstritten (Cameron & Pierce, 1994, Review of Educational Research, 64(3), 363–423)."
  },
  {
    nr: 3,
    titel: "Anwesenheit anderer und Leistung",
    A: {
      studie: "Menschen lösen *komplexe* Aufgaben schlechter, wenn andere Personen zuschauen.",
      erklaerung: "Soziale Präsenz erhöht die Erregung, was bei schwierigen Aufgaben zu mehr Fehlern führt. Die dominante (oft falsche) Reaktion wird verstärkt, während durchdachte Lösungen schwieriger werden."
    },
    B: {
      studie: "Menschen lösen *komplexe* Aufgaben besser, wenn andere Personen zuschauen.",
      erklaerung: "Publikum motiviert zu Höchstleistungen - Menschen wollen sich von ihrer besten Seite zeigen. Die erhöhte Aufmerksamkeit und der Wettbewerbsdruck fördern Konzentration und Anstrengung."
    },
    quelle: "Zajonc (1965), Science, 149(3681), 269–274; Metaanalyse über 241 Studien: Bond & Titus (1983), Psychological Bulletin, 94(2), 265–292.",
    vorbehalt: "Eine vorregistrierte Replikation der bekannten Kakerlaken-Studie (Zajonc, Heingartner & Herman, 1969) fand keinen Unterschied zwischen einfacher und schwieriger Aufgabe: Das Publikum verlangsamte die Tiere bei beiden Aufgaben (Halfmann, Bredehöft & Häusser, 2020, Psychological Science, 31(3))."
  },
  {
    nr: 4,
    titel: "Aufmerksamkeit auf sich selbst",
    A: {
      studie: "Menschen überschätzen *drastisch*, wie sehr andere auf ihre Kleidung, ihr Verhalten oder ihre Fehler achten.",
      erklaerung: "\"Spotlight-Effekt\" - wir stehen im Zentrum unserer eigenen Aufmerksamkeit und projizieren das auf andere. Da wir jeden unserer Schritte bewusst erleben, nehmen wir fälschlich an, andere tun das auch."
    },
    B: {
      studie: "Menschen unterschätzen *drastisch*, wie sehr andere auf ihre Kleidung, ihr Verhalten oder ihre Fehler achten.",
      erklaerung: "Menschen sind so in ihre eigenen Gedanken vertieft, dass sie die natürliche menschliche Neugier unterschätzen. Tatsächlich beobachten und bewerten andere viel aufmerksamer, als wir annehmen."
    },
    quelle: "Gilovich, Medvec & Savitsky (2000), Journal of Personality and Social Psychology, 78(2), 211–222.",
    vorbehalt: ""
  },
  {
    nr: 5,
    titel: "Gruppengrösse und Hilfeverhalten",
    A: {
      studie: "Menschen helfen seltener in Notfällen, wenn *mehr* andere Personen anwesend sind.",
      erklaerung: "\"Verantwortungsdiffusion\" - jeder denkt, jemand anders wird schon helfen. Zusätzlich sorgt \"pluralistische Ignoranz\" dafür, dass die Passivität anderer als Signal interpretiert wird, dass kein Notfall vorliegt."
    },
    B: {
      studie: "Menschen helfen häufiger in Notfällen, wenn *mehr* andere Personen anwesend sind.",
      erklaerung: "Mehr Zeugen erhöhen den sozialen Druck zu helfen und das Risikogefühl bei Untätigkeit. Menschen orientieren sich an Gruppennormen - wenn alle hinschauen, muss Handeln erwartet werden."
    },
    quelle: "Darley & Latané (1968), Journal of Personality and Social Psychology, 8(4), 377–383; Metaanalyse: Fischer et al. (2011), Psychological Bulletin, 137(4), 517–537.",
    vorbehalt: "Die Metaanalyse findet den Effekt im Mittel (g = -0.35), aber abgeschwächt in gefährlichen Notfällen (Fischer et al., 2011). In Überwachungsvideos realer öffentlicher Konflikte (N = 219) griff in etwa 9 von 10 Fällen mindestens eine Person ein, und mit mehr Anwesenden stieg die Wahrscheinlichkeit dafür (Philpot et al., 2020, American Psychologist)."
  }
];
