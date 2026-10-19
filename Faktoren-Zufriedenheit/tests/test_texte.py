"""Kurztexte nach dem Wurf (spiel-texte.js): Vollstaendigkeit, Laenge, Saetze, verbotene Woerter, und vor allem
die RICHTUNG: Was ein Text ueber Energie, Zeit, Erfuellung, soziale Verbindungen, Lebensstil, Finanzen und Stimmung
behauptet, wird gegen die tatsaechlichen Aenderungen einer unabhaengigen Excel-Nachrechnung (Dezimal) geprueft.

Aufruf: python3 -I tests/test_texte.py   (schreibt tests/ergebnis_texte.md)

Vorgehen
  1. Statisch: 76 Texte (19 Episoden x 2 Optionen x Erfolg/Misserfolg) vorhanden, 1 bis 2 Saetze, Laenge begrenzt,
     keine verbotenen Woerter, Platzhalter nur {ZEIT} und {ENERGIE}.
  2. Behauptungen: Ein Woerterbuch (hier im Test, nicht auf der Seite) erkennt im fertig eingesetzten Text, welche
     Richtung zu welchem Attribut behauptet wird. Die erkannten Behauptungen muessen genau den Angaben im Feld
     «gefuehl» des Textes entsprechen (nichts Ungetaggtes, nichts Falsches).
  3. Dynamisch: Fuer jede der 38 Excel-Zeilen werden viele Zustaende (Zufall, Kanten, alle Wuerfe) durch die Seite
     (Rechenkern und Textwahl im Browser) und durch rechne_decimal() aus dem Excel gerechnet. Verglichen werden:
     Erfolg/Misserfolg, Vorzeichen aller Aenderungen gegen die Behauptungen, Stimmung (Erfolg: nie gesunken,
     Misserfolg: nie gestiegen), und die eingesetzten Platzhalter (mehr / weniger / gleich viel Zeit bzw. Energie).
"""
import os
import random
import re
import sys
from collections import Counter, defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from playwright.sync_api import sync_playwright

import excel_referenz as X
import hilfen as H
import referenz_spiel as R
from test_dateien import lade_texte, lade_daten

HIER = os.path.dirname(os.path.abspath(__file__))
E = H.Ergebnisse()
G = "-"

# ---- Woerterbuch: welche Formulierung behauptet welche Richtung (nur fuer den Test)
LEX = {
    ("erfuellung", "+"): [r"erfüllter", r"mehr Erfüllung", r"mehr Sinn", r"sinnvoller"],
    ("erfuellung", "-"): [r"weniger erfüllt", r"weniger Erfüllung", r"weniger Sinn", r"sinnlos", r"\bleer\b", r"unerfüllt"],
    ("soz", "+"): [r"verbundener", r"enger verbunden", r"mehr Kontakt", r"mehr Rückhalt", r"\bnäher\b"],
    ("soz", "-"): [r"weniger verbunden", r"distanzierter", r"weniger Kontakt", r"einsamer", r"weniger Rückhalt", r"isoliert"],
    ("lebensstil", "+"): [r"gesünder", r"geordneter", r"besser strukturiert", r"mehr Struktur", r"ruhigerer Alltag"],
    ("lebensstil", "-"): [r"ungesünder", r"aus dem Takt", r"ungeordneter", r"weniger Struktur", r"chaotischer"],
    ("finanzen", "+"): [r"mehr Geld", r"finanziell besser", r"finanziell abgesichert", r"mehr finanziellen Spielraum"],
    ("finanzen", "-"): [r"weniger Geld", r"finanziell knapper", r"finanziell enger", r"Geldsorgen", r"weniger finanziellen Spielraum"],
    ("zeit", "+"): [r"mehr Zeit"], ("zeit", "-"): [r"weniger Zeit"], ("zeit", "0"): [r"gleich viel Zeit"],
    ("energie", "+"): [r"mehr Energie"], ("energie", "-"): [r"weniger Energie"], ("energie", "0"): [r"gleich viel Energie"],
}
# Woerter, die ohne Platzhalter etwas ueber Energie oder Zeit behaupten wuerden (in festem Text nicht erlaubt)
ENERGIE_ZEIT_FEST = [r"Energie", r"erschöpf", r"müde", r"ausgelaugt", r"ausgepowert", r"kraftlos", r"energiegeladen", r"ausgeruht", r"\bKraft\b", r"Kräfte",
                     r"Schlafmangel", r"überlastet", r"Zeitdruck", r"zeitlich", r"Zeit knapp", r"keine Zeit", r"mehr Zeit", r"weniger Zeit", r"gleich viel Zeit"]
STIMMUNG_GUT = [r"(?<!un)zufrieden", r"erleichtert", r"\bstolz\b", r"\bfroh\b", r"zuversichtlich", r"gelassen", r"entspannt", r"gut gelaunt", r"glücklich", r"begeistert"]
STIMMUNG_SCHLECHT = [r"enttäuscht", r"frustriert", r"verunsichert", r"niedergeschlagen", r"bedrückt", r"ernüchtert", r"unzufrieden", r"genervt",
                     r"verzweifelt", r"überfordert", r"schuldig", r"traurig", r"besorgt", r"gestresst", r"gereizt", r"ängstlich"]
VERBOTEN = [r"langfristig", r"kurzfristig", r"Glücksfaktor", r"\bStudien?\b", r"Forschung(?!s(projekt|arbeit))", r"wissenschaft", r"Option", r"Ausrichtung", r"Investition", r"Optimierung", r"Prädiktor"]
ATTR_FEST = ["erfuellung", "soz", "lebensstil", "finanzen"]
ATTR_DYN = ["zeit", "energie"]
MAX_ZEICHEN = 270


def behauptungen(text):
    """Erkennt im fertigen Text (Platzhalter bereits eingesetzt) alle behaupteten Richtungen: Menge von (Attribut, Zeichen)."""
    out = set()
    for (attr, zeichen), muster in LEX.items():
        if any(re.search(m, text) for m in muster):
            out.add((attr, zeichen))
    return out


def saetze(text):
    return [x for x in re.split(r"(?<=[.!?])\s+", text.strip()) if x]


def stufe_ref(delta, name):
    """Unabhaengige Neuschreibung der Platzhalter-Regel: gleich viel / (deutlich|etwas) mehr oder weniger."""
    if delta == 0:
        return "gleich viel " + name
    m = abs(delta)
    vor = "deutlich " if m >= 2 else ("etwas " if m <= 0.5 else "")
    return vor + ("mehr " if delta > 0 else "weniger ") + name


def statisch(T, D):
    ids = [e["id"] for e in D["episoden"]]
    E.pruefe("spiel-texte.js: genau die 19 Episoden der Daten", G, sorted(T["episoden"]) == sorted(ids), "%d" % len(T["episoden"]))
    slots = []
    for i in ids:
        for k in "AB":
            for art in ("erfolg", "misserfolg"):
                try:
                    sl = T["episoden"][i]["ergebnis"][k][art]
                    slots.append((i, k, art, sl))
                except KeyError:
                    slots.append((i, k, art, None))
    fehlt = [(i, k, a) for i, k, a, sl in slots if not sl or not sl.get("text") or not isinstance(sl.get("gefuehl"), dict)]
    E.pruefe("76 Ergebnistexte vorhanden (19 Episoden x Option A/B x Erfolg/Misserfolg)", G, len(slots) == 76 and not fehlt, "%d Texte, fehlt: %s" % (len(slots), fehlt[:3]))
    fehler = defaultdict(list)
    for i, k, art, sl in slots:
        if not sl:
            continue
        t = sl["text"]
        ID = "%s/%s/%s" % (i, k, art)
        # Platzhalter
        tok = re.findall(r"\{[^}]*\}", t)
        if any(x not in ("{ZEIT}", "{ENERGIE}") for x in tok):
            fehler["Platzhalter"].append(ID)
        gf = sl["gefuehl"]
        if set(gf) - set(ATTR_FEST + ATTR_DYN + ["stimmung"]) or "stimmung" not in gf:
            fehler["gefuehl-Schluessel"].append(ID)
        for a in ATTR_FEST:
            if a in gf and gf[a] not in ("+", "-"):
                fehler["gefuehl-Wert"].append(ID)
        for a in ATTR_DYN:
            if (a in gf) != (("{%s}" % a.upper()) in t) or (a in gf and gf[a] != "dyn"):
                fehler["Platzhalter-gegen-gefuehl"].append(ID)
        if gf.get("stimmung") != ("gut" if art == "erfolg" else "schlecht"):
            fehler["Stimmung-gegen-Ausgang"].append(ID)
        # laengster Fall einsetzen
        lang = t.replace("{ZEIT}", "deutlich weniger Zeit").replace("{ENERGIE}", "deutlich weniger Energie")
        n = len(saetze(lang))
        if not (1 <= n <= 2):
            fehler["Saetze"].append("%s (%d)" % (ID, n))
        if len(lang) > MAX_ZEICHEN or len(lang) < 60:
            fehler["Laenge"].append("%s (%d)" % (ID, len(lang)))
        if any(len(x) > 190 for x in saetze(lang)):
            fehler["Satzlaenge"].append(ID)
        if not lang.rstrip().endswith("."):
            fehler["Schlusspunkt"].append(ID)
        if any(re.search(v, lang, re.I) for v in VERBOTEN):
            fehler["verbotenes Wort"].append("%s: %s" % (ID, [v for v in VERBOTEN if re.search(v, lang, re.I)]))
        if chr(0xDF) in t:
            fehler["Eszett"].append(ID)
        # fester Text (ohne Platzhalter) darf nichts zu Energie/Zeit behaupten
        fest = t.replace("{ZEIT}", "").replace("{ENERGIE}", "")
        if any(re.search(w, fest) for w in ENERGIE_ZEIT_FEST):
            fehler["feste Aussage zu Energie/Zeit"].append("%s: %s" % (ID, [w for w in ENERGIE_ZEIT_FEST if re.search(w, fest)]))
        # Stimmungswoerter
        gut = any(re.search(w, t) for w in STIMMUNG_GUT)
        schlecht = any(re.search(w, t) for w in STIMMUNG_SCHLECHT)
        if art == "erfolg" and not (gut and not schlecht):
            fehler["Stimmungswort Erfolg"].append(ID)
        if art == "misserfolg" and not (schlecht and not gut):
            fehler["Stimmungswort Misserfolg"].append(ID)
        # Behauptungen gegen gefuehl (mit eingesetzten Platzhaltern, beliebige Stufe)
        for variante in ("mehr", "weniger", "gleich viel"):
            voll = t.replace("{ZEIT}", variante + " Zeit").replace("{ENERGIE}", variante + " Energie")
            erkannt = behauptungen(voll)
            erwartet = {(a, gf[a]) for a in ATTR_FEST if a in gf}
            erkannt_fest = {(a, z) for a, z in erkannt if a in ATTR_FEST}
            if erkannt_fest != erwartet:
                fehler["Behauptung gegen gefuehl"].append("%s: erkannt %s, angegeben %s" % (ID, sorted(erkannt_fest), sorted(erwartet)))
            erkannt_dyn = {a for a, z in erkannt if a in ATTR_DYN}
            if erkannt_dyn != {a for a in ATTR_DYN if a in gf}:
                fehler["Behauptung dyn"].append(ID)
            break  # die Fest-Behauptungen sind von der Variante unabhaengig, eine reicht
    for name, liste in fehler.items():
        E.pruefe("Texte statisch: %s" % name, G, False, "%d Treffer, z. B. %s" % (len(liste), liste[:3]))
    E.pruefe("Texte statisch: 1 bis 2 Saetze, Laenge 60 bis %d Zeichen, keine verbotenen Woerter, Platzhalter und Tags stimmig, Stimmungswort passt zum Ausgang, Behauptungen = Tags" % MAX_ZEICHEN, G, not fehler,
             "%d Texte geprueft" % len(slots))
    laengen = [len(t[3]["text"].replace("{ZEIT}", "deutlich weniger Zeit").replace("{ENERGIE}", "deutlich weniger Energie")) for t in slots if t[3]]
    E.pruefe("Texte statisch: alle verschieden, Erfolg und Misserfolg nie gleich", G,
             len({t[3]["text"] for t in slots}) == 76, "laengster Text %d Zeichen, mittlere Laenge %.0f" % (max(laengen), sum(laengen) / len(laengen)))
    return slots


def dynamisch(b, srv, T, D):
    params = X.lies_zeilenparameter()
    zeilen = R.zeilen_nach_episode()  # (ep, opt) -> {"zeile": r, ...}
    rng = random.Random(20261014)
    faelle = []
    for (ep, opt), info in sorted(zeilen.items()):
        r = info["zeile"]
        zustaende = []
        for _ in range(300):
            zustaende.append(X.zufallszustand(rng))
        # Kanten: alles +10 / alles -10 mit Wuerfel 20 / 1 und alle Wuerfe bei Normalwerten und bei Randstimmung
        for wurf in range(1, 21):
            for stim in (50, 5, 95):
                zustaende.append({"zeit": 0, "energie": 0, "soz": 1, "erfuellung": 1, "lebensstil": 1, "finanzen": 1, "stimmung": stim, "wurf": wurf})
        zustaende.append({"zeit": 10, "energie": 10, "soz": 10, "erfuellung": 10, "lebensstil": 10, "finanzen": 10, "stimmung": 100, "wurf": 20})
        zustaende.append({"zeit": -10, "energie": -10, "soz": -10, "erfuellung": -10, "lebensstil": -10, "finanzen": -10, "stimmung": 0, "wurf": 1})
        for z in zustaende:
            faelle.append((ep, opt, r, {k: (int(v) if float(v) == int(v) else float(v)) for k, v in z.items()}))
    p = b.new_context(viewport={"width": 1280, "height": 800}).new_page()
    f = H.Fehler(p)
    p.goto(srv.url + "?seed=1")
    p.wait_for_selector("[data-aktion=start]")
    args = [{"ep": ep, "opt": opt, "z": z} for ep, opt, r, z in faelle]
    seite = p.evaluate("""(args) => args.map(a => {
        const K = window.GLUECK.kern;
        const vor = {zeit:a.z.zeit, energie:a.z.energie, soz:a.z.soz, erfuellung:a.z.erfuellung, lebensstil:a.z.lebensstil, finanzen:a.z.finanzen, stimmung:a.z.stimmung};
        const r = K.rechne(a.ep, a.opt, vor, a.z.wurf);
        const t = K.ergebnisText(a.ep, a.opt, r);
        return {art: t.art, text: t.text, gefuehl: t.gefuehl};
    })""", args)
    fehler = defaultdict(list)
    zaehler = Counter()
    n_pruef = 0
    energie_abweichung = Counter()  # Energie-Vorzeichen gegen Vorzeichen der Basis (nur zur Information)
    for (ep, opt, r, z), s in zip(faelle, seite):
        ref = X.rechne_decimal(params[r], z)
        P = params[r]["P"]
        art_ref = "erfolg" if ref["resultat"] >= P else "misserfolg"
        ID = "%s/%s Zeile %d %s" % (ep, opt, r, z)
        zaehler[(ep, opt, art_ref)] += 1
        n_pruef += 1
        if s["art"] != art_ref:
            fehler["Ausgang"].append(ID)
            continue
        slot = T["episoden"][ep]["ergebnis"][opt][art_ref]
        if s["gefuehl"] != slot["gefuehl"]:
            fehler["gefuehl-Weitergabe"].append(ID)
        d = {
            "zeit": ref["nachher_zeit"] - X.D(z["zeit"]), "energie": ref["energie_aenderung"],
            "soz": ref["nachher_soz"] - X.D(z["soz"]), "erfuellung": ref["nachher_erfuellung"] - X.D(z["erfuellung"]),
            "lebensstil": ref["nachher_lebensstil"] - X.D(z["lebensstil"]), "finanzen": ref["nachher_finanzen"] - X.D(z["finanzen"]),
        }
        an = ref["stimmung_aenderung"]
        # Stimmung: Erfolg nie gesunken, Misserfolg nie gestiegen
        if (art_ref == "erfolg" and an < 0) or (art_ref == "misserfolg" and an > 0):
            fehler["Stimmung"].append(ID)
        # erkannte Behauptungen gegen echte Vorzeichen
        for attr, zeichen in behauptungen(s["text"]):
            echt = d[attr]
            ist = "+" if echt > 0 else ("-" if echt < 0 else "0")
            if zeichen != ist:
                fehler["Richtung " + attr].append("%s: Text sagt %s, Aenderung %s | %s" % (ID, zeichen, echt, s["text"][:60]))
        # Platzhalter exakt wie die unabhaengige Regel
        for a, name in (("zeit", "Zeit"), ("energie", "Energie")):
            if a in slot["gefuehl"]:
                erwartet = stufe_ref(d[a], name)
                if erwartet not in s["text"]:
                    fehler["Platzhalter " + a].append("%s: erwartet «%s» in «%s»" % (ID, erwartet, s["text"][-70:]))
        if "{" in s["text"]:
            fehler["Platzhalter offen"].append(ID)
        eb = params[r]["AW"]
        if eb != 0 and d["energie"] != 0 and (d["energie"] > 0) != (eb > 0):
            energie_abweichung[(ep, opt)] += 1
    for name, liste in fehler.items():
        E.pruefe("Texte dynamisch: %s" % name, G, False, "%d Treffer, z. B. %s" % (len(liste), liste[:2]))
    E.pruefe("Texte dynamisch: %d Zustaende ueber alle 38 Excel-Zeilen: Ausgang, Richtung aller Behauptungen, Stimmung, Platzhalter stimmen mit der Dezimal-Nachrechnung" % n_pruef, G, not fehler, "0 Abweichungen" if not fehler else "")
    schwach = [(k, v) for k, v in zaehler.items() if v < 5]
    alle = {(ep, opt, art) for (ep, opt) in zeilen for art in ("erfolg", "misserfolg")}
    E.pruefe("Texte dynamisch: jeder der 76 Texte kommt in mindestens 5 Zustaenden vor", G, set(zaehler) >= alle and not schwach,
             "kleinste Anzahl %d, fehlend %s" % (min(zaehler.values()), sorted(alle - set(zaehler))[:4]))
    n_abw = sum(energie_abweichung.values())
    E.pruefe("Hinweis: Energie-Aenderung hat in einzelnen Zustaenden anderes Vorzeichen als die Basis (Platzhalter faengt das ab)", G, True,
             "%d Faelle in %d Optionen; ohne Platzhalter waeren die Texte dort falsch" % (n_abw, len(energie_abweichung)))
    E.pruefe("Konsole/Anfragen ohne Fehler (Texte)", G, not f.liste, str(f.liste[:2]))
    p.close()


def main():
    D = lade_daten()
    T = lade_texte()
    srv = H.Server()
    slots = statisch(T, D)
    with sync_playwright() as pw:
        b = pw.chromium.launch()
        dynamisch(b, srv, T, D)
        b.close()
    srv.stop()
    E.speichern(os.path.join(HIER, "ergebnis_texte.md"))
    print("Pruefungen:", len(E.zeilen), "Fehler:", len(E.fehler))
    return 1 if E.fehler else 0


if __name__ == "__main__":
    sys.exit(main())
