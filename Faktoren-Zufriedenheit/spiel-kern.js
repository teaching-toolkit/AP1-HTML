/* Glücksfaktoren-Spiel: Rechenkern
   Setzt die Formeln aus gluecksfaktoren.xlsx (Blatt Tabelle1) um. Kein Zugriff auf die Seite (DOM).
   Zahlen und Parameter stehen in spiel-daten.js (SPIEL_DATEN.konfig), nicht hier.

   Zuordnung Excel-Zelle -> Funktion (je Zeile r, Spalten wie im Excel):
     AA, AB, AF  beitragMitSaettigung()   =IF(G>2, w*2, IF(G>4, w*3, G*w))     (Zeit, Energie, Finanzen)
     AC, AD, AE  Beitrag linear           =w*Wert                              (Soz, Erfüllung, Lebensstil)
     Q           resultat                 =IF(ROUND(2*SUM(AA:AF)+O,1)<0, 0, ROUND(2*SUM(AA:AF)+O,1))
     AN          stimmungsaenderung       =ROUND(8*(Q-P)/(10),0)
     Y           stimmungNachher          =M+AN
     AI          energieAenderung         =AW+ROUND(8*(Y-50)/50,0)/2
     S           nachher.zeit             =IF(L<-2, G+AH-1, G+AH)    (L = Finanzen VOR der Entscheidung)
     T,U,V,W,X   nachher.*                =H+AI, I+AJ, J+AK, K+AL, L+AM
   Spalten G-M = Werte vor der Entscheidung, O = Würfel, P = Soll-Wert.

   Zusätzlich (ändert KEINE Rechenregel, siehe Abschnitt «Anzeige-Logik» unten): zufällige A/B-Zuordnung,
   Reihenfolge der Glücksfaktoren-Kandidaten, Kurztexte nach dem Wurf, Einordnung «langfristig/kurzfristig».
   Die Texte dazu stehen in spiel-texte.js (von Hand geschrieben), die Zahlen weiter in spiel-daten.js.

   Läuft im Browser (window.GLUECK_KERN) und unter Node (module.exports). */
(function (global) {
  "use strict";

  var KEYS = ["zeit", "energie", "soz", "erfuellung", "lebensstil", "finanzen"]; /* Reihenfolge der Spalten AA..AF */

  /* Excel-ROUND: Rundung "halb weg von null" auf Basis der 15 gültigen Dezimalstellen,
     die Excel/LibreOffice intern verwenden. Verhindert, dass Gleitkomma-Rauschen
     (z. B. 13.349999999999998 statt 13.35) bei exakten Hälften falsch rundet. */
  function xlRound(x, stellen) {
    if (!isFinite(x)) return x;
    var f = Math.pow(10, stellen);
    var vorzeichen = x < 0 ? -1 : 1;
    var a = Number((Math.abs(x) * f).toPrecision(15));
    var r = Math.floor(a + 0.5);
    return (vorzeichen * r) / f + 0;
  }

  function kopie(o) { return JSON.parse(JSON.stringify(o)); }

  /* Beitrag eines Attributs zum Resultat. Stufen werden in der Reihenfolge der verschachtelten
     IF des Excels geprüft; die erste zutreffende gewinnt. */
  function beitragMitSaettigung(wert, gewicht, stufen) {
    if (stufen) {
      for (var i = 0; i < stufen.length; i++) {
        if (wert > stufen[i].ueber) return gewicht * stufen[i].faktor;
      }
    }
    return wert * gewicht;
  }

  /* ---- Zufall --------------------------------------------------------------------------- */
  function hashSeed(s) { /* FNV-1a, 32 Bit */
    var h = 2166136261;
    s = String(s);
    for (var i = 0; i < s.length; i++) {
      h ^= s.charCodeAt(i);
      h = Math.imul(h, 16777619);
    }
    return h >>> 0;
  }
  function mulberry32(a) {
    return function () {
      a |= 0; a = (a + 0x6D2B79F5) | 0;
      var t = Math.imul(a ^ (a >>> 15), 1 | a);
      t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
      return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
    };
  }
  /* Liefert eine Funktion, die bei jedem Aufruf einen Wurf 1..seiten liefert.
     Mit seed reproduzierbar, sonst crypto.getRandomValues (gleichverteilt, ohne Modulo-Verzerrung). */
  function neuerWuerfel(seiten, seed) {
    if (seed !== undefined && seed !== null && seed !== "") {
      var rnd = mulberry32(hashSeed(seed));
      return function () { return Math.floor(rnd() * seiten) + 1; };
    }
    var c = global.crypto || (typeof require === "function" ? require("crypto").webcrypto : null);
    if (c && c.getRandomValues) {
      var grenze = Math.floor(4294967296 / seiten) * seiten;
      return function () {
        var buf = new Uint32Array(1);
        do { c.getRandomValues(buf); } while (buf[0] >= grenze);
        return (buf[0] % seiten) + 1;
      };
    }
    return function () { return Math.floor(Math.random() * seiten) + 1; };
  }

  /* Zufall für die Anzeige (A/B-Zuordnung, Reihenfolge der Kandidaten). Getrennt vom Würfel, damit die
     Würfelfolge zu einem ?seed= unverändert bleibt. Mit seed reproduzierbar, sonst crypto.getRandomValues. */
  function neuerZufall(seed, salz) {
    var ganz;
    if (seed !== undefined && seed !== null && seed !== "") {
      var rnd = mulberry32(hashSeed(String(seed) + "|" + salz));
      ganz = function (n) { return Math.floor(rnd() * n); };
    } else {
      var c = global.crypto || (typeof require === "function" ? require("crypto").webcrypto : null);
      if (c && c.getRandomValues) {
        ganz = function (n) {
          var grenze = Math.floor(4294967296 / n) * n, buf = new Uint32Array(1);
          do { c.getRandomValues(buf); } while (buf[0] >= grenze);
          return buf[0] % n;
        };
      } else {
        ganz = function (n) { return Math.floor(Math.random() * n); };
      }
    }
    return {
      ganz: ganz,
      mische: function (liste) { /* Fisher-Yates, liefert eine neue Liste */
        var a = liste.slice();
        for (var i = a.length - 1; i > 0; i--) {
          var j = ganz(i + 1), t = a[i]; a[i] = a[j]; a[j] = t;
        }
        return a;
      }
    };
  }

  /* Kurzname eines Glücksfaktors aus dem Wort der Daten: ohne Code («C1:») und ohne Klammerzusatz («(Primär)»). */
  function kurzname(t) {
    return String(t).replace(/^[A-G]\d\s*[:\u2013\u2212-]\s*/, "").replace(/\s*\([^)]*\)\s*$/, "").trim();
  }

  /* Text für Zeit oder Energie passend zur tatsächlichen Änderung (für die Platzhalter in den Kurztexten). */
  function stufeText(delta, name) {
    var d = Math.abs(delta) < 1e-9 ? 0 : delta;
    if (d === 0) return "gleich viel " + name;
    var m = Math.abs(d);
    var vor = m >= 2 ? "deutlich " : (m <= 0.5 ? "etwas " : "");
    return vor + (d > 0 ? "mehr " : "weniger ") + name;
  }

  /* Im Text der Glücksfaktoren stehen Buchstaben der Regeloptionen («Primär bei Option B»). Angezeigt wird der
     Buchstabe, den die Teilnehmenden in dieser Episode sehen. */
  function optionenImText(t, tausch) {
    return String(t).replace(/Option ([AB])\b/g, function (m, x) { return "Option " + (tausch ? (x === "A" ? "B" : "A") : x); });
  }

  function tauscheBuchstabe(b) { return b === "A" ? "B" : (b === "B" ? "A" : b); }

  /* ---- Kern ------------------------------------------------------------------------------ */
  function erzeuge(daten, optionen) {
    optionen = optionen || {};
    var K = kopie(daten.konfig);
    if (typeof optionen.schranken === "boolean") K.schranken.aktiv = optionen.schranken;

    var episoden = {};
    daten.episoden.forEach(function (e) { episoden[e.id] = e; });
    var mikroszenen = {};
    daten.mikroszenen.forEach(function (m) { mikroszenen[m.id] = m; });

    function episode(id) { return episoden[id]; }
    function mikro(id) { return mikroszenen[id]; }
    function option(epId, optKey) { return episoden[epId].optionen[optKey]; }

    function startWerte() { return kopie(K.start); }

    /* Schranken laut Word (Attribute -10..+10, Stimmung höchstens 100). Standard: aus (= Excel). */
    function begrenze(werte) {
      var w = kopie(werte);
      if (!K.schranken.aktiv) return w;
      KEYS.forEach(function (k) {
        w[k] = Math.max(K.schranken.attributMin, Math.min(K.schranken.attributMax, w[k]));
      });
      w.stimmung = Math.min(K.schranken.stimmungMax, w.stimmung);
      return w;
    }

    /* Spalten C, D, E des Excels: Änderungen zu Beginn der Episode. */
    function beginn(werte, epId) {
      var b = episoden[epId].beginn;
      var w = kopie(werte);
      w.zeit += b.zeit;
      w.energie += b.energie;
      w.stimmung += b.stimmung;
      return begrenze(w);
    }

    /* Eine Entscheidung. vorher = Spalten G..M, wurf = Spalte O. Gibt alle Zwischenwerte zurück. */
    function rechne(epId, optKey, vorher, wurf) {
      var o = option(epId, optKey);
      var G = K.gewichte;
      var beitraege = {};
      KEYS.forEach(function (k) {
        beitraege[k] = beitragMitSaettigung(vorher[k], G[k], K.saettigungExcel[k]);
      });
      /* Spalte AA..AF der Reihe nach addieren (wie die Summe im Excel, sequenziell in doppelter Genauigkeit). */
      var summe = 0;
      KEYS.forEach(function (k) { summe += beitraege[k]; });
      var boost = K.resultat.faktorSumme * summe;
      var roh = boost + wurf;
      var gerundet = xlRound(roh, K.resultat.stellen);
      var begrenztAufNull = gerundet < K.resultat.minimum;
      var resultat = begrenztAufNull ? K.resultat.minimum : gerundet;

      var sa = K.stimmungsaenderung;
      var dStimmung = xlRound(sa.faktor * (resultat - o.soll) / sa.teiler, sa.stellen);
      var stimmungNachher = vorher.stimmung + dStimmung;

      var es = K.energieAusStimmung;
      var energieAusStimmung = xlRound(es.faktor * (stimmungNachher - es.nullpunkt) / es.teiler, es.stellen) / es.durch;
      var energieAenderung = o.energieBasis + energieAusStimmung;

      var zeitAbzug = vorher.finanzen < K.zeitAbzugFinanzen.finanzenUnter ? K.zeitAbzugFinanzen.abzug : 0;
      var aenderung = {
        zeit: o.aenderung.zeit - zeitAbzug,
        energie: energieAenderung,
        soz: o.aenderung.soz,
        erfuellung: o.aenderung.erfuellung,
        lebensstil: o.aenderung.lebensstil,
        finanzen: o.aenderung.finanzen
      };
      var nachher = {};
      KEYS.forEach(function (k) { nachher[k] = vorher[k] + aenderung[k]; });
      nachher.stimmung = stimmungNachher;
      var wirkung = {};
      KEYS.forEach(function (k) { wirkung[k] = K.resultat.faktorSumme * beitraege[k]; });

      var uebernommen = begrenze(nachher);
      var begrenztListe = [];
      KEYS.concat(["stimmung"]).forEach(function (k) { if (uebernommen[k] !== nachher[k]) begrenztListe.push(k); });

      return {
        epId: epId, option: optKey, wurf: wurf,
        vorher: kopie(vorher),
        beitraege: beitraege, wirkung: wirkung, summe: summe, boost: boost,
        resultatRoh: roh, resultat: resultat, resultatAufNullGesetzt: begrenztAufNull,
        soll: o.soll, differenz: resultat - o.soll,
        stimmungsaenderung: dStimmung, stimmungNachher: stimmungNachher,
        energieBasis: o.energieBasis, energieAusStimmung: energieAusStimmung, energieAenderung: energieAenderung,
        zeitAbzug: zeitAbzug, aenderung: aenderung,
        nachher: nachher,
        uebernommen: uebernommen, begrenzt: begrenztListe,
        spielende: stimmungNachher < K.spielendeStimmungUnter
      };
    }

    /* Mikroszene: feste Änderungen aus dem Word, ohne Würfel, ohne Stimmung. */
    function mikroAnwenden(werte, mikroId, optKey) {
      var d = mikroszenen[mikroId].optionen[optKey].deltas;
      var w = kopie(werte);
      KEYS.forEach(function (k) { if (typeof d[k] === "number") w[k] += d[k]; });
      return { vorher: kopie(werte), deltas: kopie(d), nachher: w, uebernommen: begrenze(w) };
    }

    /* Vorschläge laut Word «Mikroszenen strategisch einsetzen». Gibt Reihenfolge und Gründe zurück. */
    function mikroVorschlag(werte) {
      var z = daten.mikroZuordnung;
      var treffer = [];
      var gruende = {};
      function add(kriteriumIndex, grund) {
        z[kriteriumIndex].szenen.forEach(function (s) {
          if (!gruende[s.id]) { gruende[s.id] = []; treffer.push(s.id); }
          if (gruende[s.id].indexOf(grund) < 0) gruende[s.id].push(grund);
        });
      }
      var v = K.mikroVorschlag;
      if (werte.zeit < v.zeitEnergieUnter) add(0, "zeit");
      if (werte.energie < v.zeitEnergieUnter) add(0, "energie");
      if (werte.soz < v.attributUnter) add(1, "soz");
      if (werte.erfuellung < v.attributUnter) add(2, "erfuellung");
      if (werte.lebensstil < v.attributUnter) add(3, "lebensstil");
      treffer.sort(function (a, b) { return parseInt(a.slice(1), 10) - parseInt(b.slice(1), 10); });
      return { ids: treffer, gruende: gruende };
    }

    /* Rettungs-Mikroszenen: die Szenen, die das Word für kritisch niedrige Zeit/Energie nennt. */
    function rettungsszenen() {
      return daten.mikroZuordnung[0].szenen.map(function (s) { return s.id; });
    }

    function naechste(epId, optKey) { return episoden[epId].optionen[optKey].weiter; }

    /* ======== Anzeige-Logik (keine Rechenregel; Texte aus spiel-texte.js) ======== */
    var texte = optionen.texte || null;
    function textEp(epId) { return texte && texte.episoden && texte.episoden[epId]; }

    /* Einordnung einer Regeloption: «langfristig» oder «kurzfristig» (nur für die Abschlussansicht). */
    function ausrichtung(epId, optKey) {
      var t = textEp(epId);
      if (!t) return null;
      return { wert: t.ausrichtung[optKey], unscharf: !!t.unscharf, notiz: t.notiz || "" };
    }

    /* Alle Kandidaten einer Episode: zuerst die echten Glücksfaktoren (aus den Daten), dann die Ablenker.
       Die Nummer in dieser Liste ist nur intern; angezeigt wird in der Reihenfolge von plan.ordnung. */
    function kandidaten(epId) {
      var e = episoden[epId], t = textEp(epId), liste = [];
      e.glueck.forEach(function (g, i) { liste.push({ art: "echt", name: kurzname(g), voll: g, ref: i }); });
      if (t) {
        (t.plausibel || []).forEach(function (n) { liste.push({ art: "plausibel", name: n }); });
        (t.unplausibel || []).forEach(function (n) { liste.push({ art: "unplausibel", name: n }); });
      }
      return liste;
    }

    /* Plan für ein ganzes Spiel: pro Episode, ob die Buchstaben vertauscht sind, und die Reihenfolge der
       Kandidaten. modus: «zufall» (Standard), «fest» (A bleibt A) oder «tausch» (alle vertauscht, nur für Tests). */
    function neuerPlan(zufall, modus) {
      var plan = { tausch: {}, ordnung: {} };
      daten.episoden.forEach(function (e) {
        var bit = zufall.ganz(2); /* immer ziehen, damit die Folge nicht vom Modus abhängt */
        plan.tausch[e.id] = modus === "fest" ? 0 : (modus === "tausch" ? 1 : bit);
        var n = kandidaten(e.id).length, idx = [];
        for (var i = 0; i < n; i++) idx.push(i);
        plan.ordnung[e.id] = zufall.mische(idx);
      });
      return plan;
    }

    /* Anzeigebuchstabe -> Regeloption und zurück (Tausch ist symmetrisch). */
    function anzeigeZuRegel(tausch, buchstabe) { return tausch ? tauscheBuchstabe(buchstabe) : buchstabe; }
    function regelZuAnzeige(tausch, regel) { return tausch ? tauscheBuchstabe(regel) : regel; }

    /* Kurztext nach dem Wurf. rech = Ergebnis von rechne(). Erfolg: Resultat grösser oder gleich Soll-Wert. */
    function ergebnisText(epId, optKey, rech) {
      var t = textEp(epId);
      if (!t) return null;
      var art = rech.differenz >= 0 ? "erfolg" : "misserfolg";
      var slot = t.ergebnis[optKey][art];
      var text = slot.text
        .split("{ZEIT}").join(stufeText(rech.aenderung.zeit, "Zeit"))
        .split("{ENERGIE}").join(stufeText(rech.aenderung.energie, "Energie"));
      return { art: art, text: text, gefuehl: slot.gefuehl };
    }

    /* Alle möglichen Wege (Folgen von Episoden-IDs mit Optionen). */
    function alleWege() {
      var wege = [];
      (function gehe(id, pfad) {
        ["A", "B"].forEach(function (k) {
          var p = pfad.concat([id + k]);
          var n = naechste(id, k);
          if (n === null) wege.push(p); else gehe(n, p);
        });
      })(daten.episoden[0].id, []);
      return wege;
    }

    return {
      K: K, KEYS: KEYS, daten: daten,
      episode: episode, option: option, mikro: mikro,
      startWerte: startWerte, begrenze: begrenze, beginn: beginn,
      rechne: rechne, mikroAnwenden: mikroAnwenden, mikroVorschlag: mikroVorschlag, rettungsszenen: rettungsszenen,
      naechste: naechste, alleWege: alleWege,
      texte: texte, ausrichtung: ausrichtung, kandidaten: kandidaten, neuerPlan: neuerPlan,
      anzeigeZuRegel: anzeigeZuRegel, regelZuAnzeige: regelZuAnzeige, ergebnisText: ergebnisText
    };
  }

  var api = { erzeuge: erzeuge, xlRound: xlRound, neuerWuerfel: neuerWuerfel, beitragMitSaettigung: beitragMitSaettigung, KEYS: KEYS,
    neuerZufall: neuerZufall, kurzname: kurzname, stufeText: stufeText, optionenImText: optionenImText };
  if (typeof module !== "undefined" && module.exports) module.exports = api;
  global.GLUECK_KERN = api;
})(typeof window !== "undefined" ? window : globalThis);
