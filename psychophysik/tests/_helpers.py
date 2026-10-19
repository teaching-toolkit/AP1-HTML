"""Gemeinsame Hilfen für die Testskripte (Start: python3 -I tests/<datei>.py).

Kein Test ändert Dateien ausserhalb von tests/ und screenshots/.
"""
import contextlib
import functools
import http.server
import os
import socketserver
import sys
import threading

HERE = os.path.dirname(os.path.abspath(__file__))
PROJECT = os.path.dirname(HERE)                      # .../p5-psychophysik
ROOT = os.path.dirname(PROJECT)                      # .../html-projekte (enthält shared/)
SHOTS = os.path.join(PROJECT, "screenshots")
FILE_URL = "file://" + PROJECT


class _Quiet(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a, **k):
        pass


@contextlib.contextmanager
def serve():
    """Lokaler Server auf einem freien Port, Wurzel = html-projekte (damit ../shared/base.css stimmt)."""
    handler = functools.partial(_Quiet, directory=ROOT)
    socketserver.TCPServer.allow_reuse_address = True
    httpd = socketserver.ThreadingTCPServer(("127.0.0.1", 0), handler)
    port = httpd.server_address[1]
    t = threading.Thread(target=httpd.serve_forever, daemon=True)
    t.start()
    try:
        yield "http://127.0.0.1:%d/p5-psychophysik" % port
    finally:
        httpd.shutdown()
        httpd.server_close()


class Checker:
    def __init__(self, title):
        self.title = title
        self.n = 0
        self.failed = []
        print("=== %s ===" % title)

    def check(self, label, ok, detail=""):
        self.n += 1
        tag = "PASS" if ok else "FAIL"
        print("%s  %s%s" % (tag, label, ("  [" + str(detail) + "]") if detail != "" else ""))
        if not ok:
            self.failed.append(label)
        return ok

    def info(self, text):
        print("INFO  " + text)

    def finish(self):
        print("--- %s: %d Prüfungen, %d fehlgeschlagen ---" % (self.title, self.n, len(self.failed)))
        for f in self.failed:
            print("   FAIL: " + f)
        sys.exit(1 if self.failed else 0)


def attach_collectors(page, errors, external):
    """Sammelt Konsolenfehler, pageerror, fehlgeschlagene und externe Anfragen."""
    def on_console(m):
        if m.type == "error":
            errors.append("console.error: " + m.text)

    def on_request(r):
        u = r.url
        if not (u.startswith("file://") or u.startswith("http://127.0.0.1") or u.startswith("data:") or u.startswith("blob:")):
            external.append(u)

    page.on("console", on_console)
    page.on("pageerror", lambda e: errors.append("pageerror: " + str(e)))
    page.on("requestfailed", lambda r: errors.append("requestfailed: " + r.url))
    page.on("request", on_request)


MULBERRY_JS = """
function mulberry32(a){return function(){a|=0;a=a+0x6D2B79F5|0;var t=Math.imul(a^a>>>15,1|a);t=t+Math.imul(t^t>>>7,61|t)^t;return((t^t>>>14)>>>0)/4294967296;};}
"""


def checksum(s):
    """Unabhängige Python-Umsetzung der Prüfsumme (3 Zeichen, Basis 36)."""
    h = 7
    for ch in s:
        h = (h * 31 + ord(ch)) % 46656
    digits = "0123456789abcdefghijklmnopqrstuvwxyz"
    t = ""
    while h:
        t = digits[h % 36] + t
        h //= 36
    return t.rjust(3, "0")
