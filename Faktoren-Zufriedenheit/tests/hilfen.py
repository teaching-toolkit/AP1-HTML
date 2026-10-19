"""Gemeinsame Hilfen fuer die Playwright-Tests (Server, Browser, Fehlersammlung, Klick mit Sperrzeit)."""
import functools
import http.server
import os
import socketserver
import threading

PROJEKT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WURZEL = os.path.dirname(PROJEKT)  # /home/claude/html-projekte (damit ../shared/base.css gefunden wird)
ORDNER = os.path.basename(PROJEKT)
SPERRE_MS = 300  # die Seite ignoriert Klicks in den ersten 250 ms nach einem Schritt (Schutz vor Doppeltipp)


class _Handler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a):
        pass


class Server:
    def __init__(self):
        handler = functools.partial(_Handler, directory=WURZEL)
        socketserver.TCPServer.allow_reuse_address = True
        self.httpd = socketserver.TCPServer(("127.0.0.1", 0), handler)
        self.port = self.httpd.server_address[1]
        self.thread = threading.Thread(target=self.httpd.serve_forever, daemon=True)
        self.thread.start()

    @property
    def url(self):
        return "http://127.0.0.1:%d/%s/index.html" % (self.port, ORDNER)

    @property
    def file_url(self):
        return "file://" + os.path.join(PROJEKT, "index.html")

    def stop(self):
        self.httpd.shutdown()
        self.httpd.server_close()


class Fehler:
    """Sammelt Konsolenfehler, pageerror, fehlgeschlagene und externe Anfragen."""

    def __init__(self, seite, name=""):
        self.liste = []
        self.anfragen = []
        self.name = name
        seite.on("console", lambda m: self.liste.append("console.%s: %s" % (m.type, m.text)) if m.type in ("error", "warning") else None)
        seite.on("pageerror", lambda e: self.liste.append("pageerror: %s" % e))
        seite.on("requestfailed", lambda r: self.liste.append("requestfailed: %s" % r.url))
        seite.on("request", self._anfrage)

    def _anfrage(self, r):
        self.anfragen.append(r.url)
        u = r.url
        if not (u.startswith("file://") or u.startswith("http://127.0.0.1") or u.startswith("data:") or u.startswith("blob:")):
            self.liste.append("externe Anfrage: " + u)


def warte(seite, ms=SPERRE_MS):
    seite.wait_for_timeout(ms)


def klick(seite, selektor, ms=SPERRE_MS):
    """Wartet die Sperrzeit der Seite ab und klickt dann (oder tippt auf Touch-Seiten)."""
    warte(seite, ms)
    seite.locator(selektor).first.click()


def tippe(seite, selektor, ms=SPERRE_MS):
    warte(seite, ms)
    seite.locator(selektor).first.tap()


class Ergebnisse:
    """Sammelt Testergebnisse als Tabelle (Test, Geraet, Ergebnis, Detail)."""

    def __init__(self):
        self.zeilen = []

    def pruefe(self, test, geraet, bedingung, detail=""):
        self.zeilen.append((test, geraet, "OK" if bedingung else "FEHLER", detail))
        print("%-7s %-62s %-12s %s" % ("OK" if bedingung else "FEHLER", test[:62], geraet, detail[:150]))
        return bedingung

    @property
    def fehler(self):
        return [z for z in self.zeilen if z[2] != "OK"]

    def speichern(self, pfad):
        with open(pfad, "w", encoding="utf-8") as f:
            f.write("| Test | Geraet | Ergebnis | Detail |\n|---|---|---|---|\n")
            for t, g, e, d in self.zeilen:
                f.write("| %s | %s | %s | %s |\n" % (t.replace("|", "/"), g, e, d.replace("|", "/").replace("\n", " ")))
            f.write("\nGesamt: %d Pruefungen, %d Fehler\n" % (len(self.zeilen), len(self.fehler)))


class Spiel:
    """Bedient die Seite wie ein Nutzer (Maus oder Touch) und liest den Zustand ueber den Testhaken."""

    def __init__(self, seite, touch=False, schnell=False):
        self.s = seite
        self.touch = touch
        self.schnell = schnell  # True: Sperrzeit per Testhaken aufheben (nur fuer lange Serien)

    def z(self):
        return self.s.evaluate("window.GLUECK.zustand()")

    def phase(self):
        return self.s.evaluate("window.GLUECK.zustand().phase")

    def _aktion(self, sel):
        if self.schnell:
            self.s.evaluate("window.GLUECK.entsperren()")
        else:
            warte(self.s)
        loc = self.s.locator(sel).first
        if self.touch:
            loc.tap()
        else:
            loc.click()

    def start(self):
        self._aktion("[data-aktion=start]")

    def anzeige_fuer(self, regel, ep=None):
        """Angezeigter Buchstabe (A/B) fuer eine Regeloption in der aktuellen (oder gegebenen) Episode.
        Die Seite vertauscht die Buchstaben pro Episode zufaellig (Zustandsfeld «tausch»)."""
        z = self.z()
        tausch = z["tausch"][ep or z["ep"]]
        return {"A": "B", "B": "A"}[regel] if tausch else regel

    def waehle(self, opt):
        """Waehlt die REGELOPTION opt (Excel-Zeile A oder B): klickt den Knopf mit dem dazu angezeigten Buchstaben."""
        self._aktion("[data-aktion=waehle][data-wert=%s]" % self.anzeige_fuer(opt))

    def waehle_anzeige(self, buchstabe):
        """Waehlt den ANGEZEIGTEN Buchstaben (ohne Umrechnung)."""
        self._aktion("[data-aktion=waehle][data-wert=%s]" % buchstabe)

    def glueck_zeigen(self):
        self._aktion("[data-aktion=glueckZeigen]")

    def wurf_physisch(self, n):
        if self.schnell:
            self.s.evaluate("window.GLUECK.entsperren()")
        else:
            warte(self.s)
        self.s.fill("#wurf-eingabe", str(n))
        if self.touch:
            self.s.locator("#form-wurf button[type=submit]").tap()
        else:
            self.s.press("#wurf-eingabe", "Enter")

    def wurf_virtuell(self):
        self._aktion("[data-aktion=wuerfeln]")

    def zu_folgen(self):
        self._aktion("[data-aktion=zuFolgen]")

    def zu_werten(self):
        self._aktion("[data-aktion=zuWerten]")

    def weiter(self):
        self._aktion("[data-aktion=weiter]")

    def undo(self):
        self._aktion("#btn-undo")

    def episode(self, opt, wurf, bis="werte"):
        """Eine Episode bis zur Ansicht «Werte danach» spielen (Wurf physisch eingegeben)."""
        self.waehle(opt)
        self.wurf_physisch(wurf)
        self.zu_folgen()
        self.zu_werten()


class Tastatur(Spiel):
    """Nur Tastatur: Tab bis zum Ziel, Enter/Leertaste. Kein Mausklick."""

    def tab_bis(self, sel, max_tab=25):
        for _ in range(max_tab):
            if self.s.evaluate("(s) => document.activeElement && document.activeElement.matches(s)", sel):
                return
            self.s.keyboard.press("Tab")
        raise AssertionError("Tab erreicht %s nicht (Fokus: %s)" % (sel, self.s.evaluate("document.activeElement && document.activeElement.outerHTML.slice(0,80)")))

    def _aktion(self, sel):
        warte(self.s)
        self.tab_bis(sel)
        self.s.keyboard.press("Enter")

    def wurf_physisch(self, n):
        warte(self.s)
        self.tab_bis("#wurf-eingabe")
        self.s.keyboard.type(str(n))
        self.s.keyboard.press("Enter")


def kacheln(seite):
    """Liest die Kacheln (Stimmung + 6 Attribute) als Zahlen aus dem DOM."""
    roh = seite.evaluate("""() => Array.from(document.querySelectorAll('#app .kachel')).slice(0,7).map(k => [k.querySelector('.name').textContent.trim(), k.querySelector('.wert').childNodes[0].textContent.trim()])""")
    namen = {"Stimmung": "stimmung", "Zeit": "zeit", "Energie": "energie", "Soz. Verb.": "soz", "Erfüllung": "erfuellung", "Lebensstil": "lebensstil", "Finanzen": "finanzen"}
    return {namen[n]: float(t.replace("−", "-")) for n, t in roh}


def zahl(text):
    return float(text.replace("−", "-").replace("+", "").replace("±", "").strip("() "))
