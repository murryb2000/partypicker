PARTYPICKER / Der Playlist-Generator
by MurryB · Version 2.1.5
====================================

KURZBESCHREIBUNG
----------------
PartyPicker hilft dabei, FLAC- und MP3-Musikordner schnell durchzuhören und passende
Titel für eine Party auszuwählen. Die Musikdateien werden nicht kopiert oder
verändert.


START
-----
1. PartyPicker.exe doppelklicken.
2. Beim ersten Start kann es etwas länger dauern, weil sich die EXE intern
   kurz entpackt.
3. Die App startet maximiert. Sie kann über die normalen Windows-Fensterknöpfe
   verkleinert oder geschlossen werden.


WICHTIGER WINDOWS-HINWEIS
-------------------------
Wegen der fehlenden digitalen Signatur kann Windows SmartScreen warnen.
Dann „Weitere Informationen“ und anschließend „Trotzdem ausführen“ wählen.

Die Datei sollte nur gestartet werden, wenn sie direkt von MurryB bzw. aus
einer vertrauenswürdigen Quelle stammt. Bei Unsicherheit die EXE vor dem Start
mit Windows-Sicherheit oder einem anderen aktuellen Virenscanner prüfen.


ERSTE SCHRITTE
--------------
1. „Neue Playlist …“ anklicken und Speicherort sowie Dateinamen festlegen.
2. „Musikordner öffnen …“ anklicken und den gewünschten Musikordner auswählen.
3. Der erste Titel startet automatisch.
4. Mit „+ Playlist [Enter]“ den laufenden Titel übernehmen und direkt zum
   nächsten Titel wechseln.
5. Jede Änderung wird sofort gespeichert.
6. Die Playlist scrollt nach jeder Aufnahme automatisch zum zuletzt
   hinzugefügten Titel und markiert ihn. Beim Öffnen einer vorhandenen
   M3U-Playlist wird ebenfalls deren letzter Eintrag angezeigt.


SPRACHE
-------
Oben rechts kann PartyPicker jederzeit zwischen „Deutsch“ und „English“
umgeschaltet werden. Die gesamte Bedienoberfläche wird sofort aktualisiert.
Die gewählte Sprache bleibt gespeichert und wird beim nächsten Start wieder
verwendet.


FREIWILLIGE UNTERSTÜTZUNG
-------------------------
Der Button „Ein Bier für MurryB“ beziehungsweise „Buy MurryB a beer“ öffnet
die Unterstützerseite https://ko-fi.com/murryb im normalen Webbrowser.
PartyPicker verarbeitet selbst keine Zahlungs- oder Zugangsdaten.


BEDIENUNG
---------
- Klick oder Ziehen in der Waveform: zu einer Stelle im Titel springen
- Leertaste: Play/Pause
- Pfeil links/rechts: 10 Sekunden zurück/vor
- Strg + Pfeil links/rechts: vorheriger/nächster Titel
- Enter oder Enter auf dem Ziffernblock: Titel zur Playlist hinzufügen und weiterschalten
- Doppelklick auf einen Titel: Titel abspielen
- Pfeile unter der Playlist: ausgewählten Eintrag verschieben
- „Aus Playlist entfernen“: ausgewählten Eintrag löschen
- „Unterordner einbeziehen“: durchsucht auch untergeordnete Musikordner
- Nicht lesbare Unterordner werden übersprungen und nach dem Scan gemeldet


M3U-PLAYLIST
------------
Standardmäßig erstellt PartyPicker eine M3U-Datei. Diese enthält Verweise auf
die ursprünglichen Musikdateien und kann zum Beispiel in VirtualDJ verwendet
werden. Die FLAC- und MP3-Dateien müssen an ihrem bisherigen Speicherort erreichbar
bleiben. Beim Verschieben auf einen anderen PC müssen die gespeicherten Pfade
ebenfalls stimmen.

Gemappte Windows-Laufwerke wie Z: bleiben beim Speichern in dieser Darstellung
erhalten. Speichern, TXT-Metadatenlesen und Dateistatus-Prüfungen laufen im
Hintergrund, damit die Bedienoberfläche auch bei langen Playlists oder einem NAS
reaktionsfähig bleibt.


TXT-TITELLISTE
--------------
Wird vor dem Anlegen „Nur TXT-Datei“ aktiviert, speichert PartyPicker eine
reine Textliste im Format:

Artist - Titel

Die Angaben stammen aus den FLAC- beziehungsweise MP3-Tags. Fehlen Tags, verwendet die App den
Dateinamen. Eine TXT-Datei enthält keine Musikpfade und kann deshalb nicht als
abspielbare Playlist in PartyPicker oder VirtualDJ importiert werden.


WEITERGABE
----------
PartyPicker.exe ist eine eigenständige Ein-Datei-Version. Es müssen keine
weiteren Dateien mitgegeben und weder Python noch PartyPicker installiert
werden. Die EXE kann kopiert, vollständig heruntergeladen und direkt gestartet
werden.

Das PartyPicker-Symbol zeigt Kopfhörer, eine Waveform und ein Pluszeichen. Es
wird für die EXE sowie im Fenstertitel und in der Windows-Taskleiste verwendet.

PartyPicker darf für private, nicht kommerzielle Zwecke kostenlos genutzt und
als vollständiges, unverändertes Originalpaket kostenlos weitergegeben werden.
Die vollständigen Bedingungen stehen in LICENSE.txt; Hinweise zu verwendeten
Komponenten stehen in THIRD_PARTY_NOTICES.txt.


HINWEIS
-------
PartyPicker ist ein privates Hilfsprogramm von MurryB. Verwendung auf eigene
Verantwortung.

NEU AB VERSION 1.1.0
Tastaturbelegung unten auswählen: Strg+Pfeile, Pfeile, Hoch/Runter oder
Ziffernblock (Num Lock: 1 = -10 s, 2 = +10 s, 3 = nächster Titel, Strg+3 = vorheriger Titel).
Die Kurzanleitung zeigt die aktive Belegung. Die Auswahl wird gespeichert.
Beim Start: neue Playlist oder letzte Playlist fortsetzen. Beim ersten Start
dieser Version zunächst eine Playlist öffnen oder speichern.

NEU IN VERSION 1.1.1
Beim Fortsetzen kann „Letzten Musikordner ebenfalls öffnen“ angehakt werden.
Der zuletzt ausgewählte Ordner und die Einstellung für Unterordner werden
wiederhergestellt; nach dem Einlesen startet der erste Titel automatisch.
Wenn noch kein Musikordner gespeichert wurde, kann beim Fortsetzen über den
hellgrau hervorgehobenen Haken ein Ordner ausgewählt werden.
Neben dem Logo stehen PARTYPICKER, Der Playlist-Generator und by MurryB · Version 1.2.0
untereinander.

NEU IN VERSION 1.1.2
Beim Fortsetzen mit dem letzten Musikordner startet der zuletzt gespielte
Titel aus diesem Ordner. Fehlt er inzwischen, startet der erste Titel.


NEU IN VERSION 1.2.1
--------------------
- Beim Fortsetzen springt die Ordnerliste sichtbar zum zuletzt gespielten
  Titel und startet ihn von vorn.

NEU IN VERSION 1.2.0
--------------------
- Grau: noch nicht entschieden; Grün: in der aktuellen Playlist;
  Orange: manuell mit Vorheriger/Nächster bzw. Tastenkürzel übersprungen.
  Grün hat Vorrang. Markierungen bleiben gespeichert und lassen sich mit
  „Markierungen zurücksetzen“ für den geöffneten Ordner löschen.
- Gleicher Interpret und Titel in unterschiedlichen Dateien: Nachfrage vor
  der Aufnahme. Artist-/Titel-Tags werden bevorzugt; sonst ein eindeutiger
  Dateiname im Format Artist - Titel. Verschiedene Mix-Bezeichnungen bleiben
  eigenständig. Die Prüfung läuft im Hintergrund.
- „Vorhören ab“: Start bei 0–600 Sekunden, Standard 0. Bei kurzen Liedern
  bleiben mindestens 10 Sekunden oder das Lied beginnt am Anfang.
- „Rückgängig [Strg+Z]“: bis zu 20 erfolgreiche Playlist-Änderungen dieser
  Sitzung zurücknehmen. Das Ergebnis wird sofort gespeichert. Bei einem
  Speicherfehler bleiben Playlist und Verlauf erhalten.
- „Lautstärke angleichen“: standardmäßig aus, wirkt nach der Waveform-Analyse.
  RMS- und Spitzenpegel werden für die Abhörlautstärke genutzt. Keine Änderung
  der Musikdateien, keine LUFS-Normalisierung; sehr leise Titel werden durch
  den Lautstärkeregler begrenzt. Die Einstellung bleibt gespeichert.
- Bei fehlender Musikdatei oder Wiedergabefehler: „Erneut versuchen“ oder
  „Titel überspringen“. Die Dateiprüfung läuft im Hintergrund; ein nicht
  antwortendes NAS kann trotzdem längere Wartezeiten verursachen.

Playlist-Manager in Version 2.0.0

Der Button unten rechts im linken PartyPicker-Bereich öffnet den Manager im selben Fenster. Die aktuelle Playlist wird übernommen; alternativ kann eine M3U-/M3U8-Datei geladen werden. Links beginnt die Liste, rechts wird sie fortgeführt. Ein gemeinsamer Scrollbalken bewegt beide Spalten.

Titel mit Strg auswählen oder mit Strg und gedrückter linker Maustaste überstreichen. Die Auswahl anschließend ziehen; die grüne Linie markiert die Einfügestelle. Die Ziehvorschau zeigt die ersten drei Titel und bei Bedarf +Restanzahl. Nach Berührung des oberen/unteren Bildschirmrands scrollt die Liste automatisch. Ab zehn Pixeln Abstand stoppt sie und setzt die Beschleunigung zurück. Geschwindigkeit: alle 1,5 Sekunden steigt die Geschwindigkeit auf 4, 8, 16, 28, 44 und maximal 60 Titel pro Sekunde. Beim Verlassen des Randbereichs endet das Scrollen und die Beschleunigung wird zurückgesetzt.

„An den Anfang“/„Ans Ende“ verschiebt ausgewählte Titel. „Zum Listenanfang“/„Zum Listenende“ bewegt nur die Ansicht. „Rückgängig“/Strg+Z nimmt eine Änderung zurück. Änderungen werden sofort gespeichert. Mit genau einem ausgewählten Titel schaltet die Leertaste zwischen Wiedergabe und Pause um. BPM wird aus vorhandenen Tags gelesen; es wird keine automatische BPM-Analyse durchgeführt.

Korrektur in 2.0.0: „Vorhören ab“ wartet auf das Laden und bestätigt den tatsächlichen Startpunkt. Während des Sprungs bleibt der Ton kurz stumm. Die Behandlung kurzer Titel bleibt erhalten.

ANIMATIONEN IN VERSION 2.1.0
Beim Ziehen im Manager werden die ausgewählten Zeilen ausgeblendet und die übrigen Titel gleiten zusammen. Am anvisierten Einfügepunkt öffnet sich eine Vorschau-Lücke. Beim Ablegen blenden die Titel dort ein; erst dann wird gespeichert. Abbrechen stellt Reihenfolge und Auswahl wieder her. Ein Speicherfehler stellt auch die Vorschau zurück.
In PartyPicker überblenden die Statusfarben, Titel blenden beim Aufnehmen/Entfernen ein oder aus, und die Waveform überblendet beim Titelwechsel. Die kurzen Übergänge verzögern weder die tatsächliche Listenänderung noch die Wiedergabe.

KORREKTUREN IN VERSION 2.1.1
Große Musikordner werden gesammelt aufgebaut und eingefärbt. Nur sichtbare spätere Farbwechsel werden animiert. Navigation und Schließen warten nicht auf blockierte Lesezugriffe. Bereits gelesene Metadaten werden zwischengespeichert.
Falls beim Schließen noch eine Playlist gespeichert wird, bleibt die Oberfläche während des Abschlusses ansprechbar. Bei einem Speicherfehler bleibt das Fenster geöffnet und zeigt den Fehler an.

KOMPAKTE ANSICHT IN VERSION 2.1.5
Der Songtitel bleibt einzeilig; zu lange Titel enden mit „…“. Datei- und Playlist-Pfad werden in der Mitte gekürzt. Der vollständige Text ist beim Darüberfahren mit der Maus abrufbar. Interne Titel und Dateipfade bleiben vollständig erhalten.
Bei geringer Fensterhöhe oder -breite verwendet PartyPicker automatisch kleinere Abstände und kompaktere Bedienelemente. Die Waveform behält ihre volle Höhe. Dies hilft beispielsweise bei 2256 × 1504 und 200 Prozent Windows-Skalierung.


Beim Ziehen im Playlist-Manager ist das Bildschirmrand-Scrollen unter Windows korrigiert: Start am echten Bildschirmrand, Beschleunigung auch bei unbewegter Maus, Stopp ab zehn Pixeln Abstand. Hohe Skalierung wird berücksichtigt.



Beim Ziehen im Playlist-Manager zeigt ein rotes Einfahrt-verboten-Schild außerhalb der beiden Playlist-Spalten an, dass dort nicht abgelegt werden kann. Innerhalb der Spalten erscheint wieder die Hand.


Vollbild: PartyPicker startet standardmäßig ohne Windows-Titelleiste und Taskleiste. F11 schaltet zwischen Vollbild und Fensteransicht um; Esc verlässt das Vollbild. Beim Ziehen von Titeln bricht Esc nur den Ziehvorgang ab. Die zuletzt gewählte Ansicht wird gespeichert. Gilt für beide Oberflächen.
