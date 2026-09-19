# PARTYPICKER / Der Playlist-Generator

Lokale Desktop-App zum Durchhören von FLAC- und MP3-Sammlungen und Zusammenstellen einer Party-Playlist. Python mit PySide6 ermöglicht direkte Dateizugriffe und Speichern ohne Browser-Berechtigungsdialoge. Wiedergabe über Qt Multimedia; Waveform aus den echten Audiodaten über SoundFile. TinyTag liest ausschließlich Artist- und Title-Metadaten. Keine Musik-Uploads.

## Start

1. Python 3.12 oder neuer (64 Bit) von https://www.python.org/downloads/windows/ installieren, einschließlich Python Launcher.
2. Dieses ZIP vollständig entpacken.
3. `Starten.bat` doppelklicken. Beim ersten Start werden die benötigten Pakete aus dem Internet installiert. Danach arbeitet die App offline.
4. „Neue Playlist“ wählen und Speicherort festlegen – oder eine vorhandene M3U/M3U8 über „Playlist öffnen“ weiterbearbeiten.
5. „Musikordner öffnen“ wählen. Der erste FLAC- oder MP3-Titel startet automatisch. Unterordner sind optional eingeschlossen; Dateien sind natürlich nach Pfad/Dateiname sortiert (2 vor 10).

Optional kann unter „Neue Playlist …“ die standardmäßig deaktivierte Auswahl „Nur TXT-Datei“ gesetzt werden. Dann wird statt einer M3U eine Textdatei angelegt und nach jeder Änderung automatisch mit einer Zeile pro Titel im Format `Artist - Titel` gespeichert. Dafür werden die Artist- und Title-Tags der FLAC- beziehungsweise MP3-Dateien verwendet; fehlen sie, dient der Dateiname als Ersatz. Eine solche reine TXT-Titelliste enthält keine Dateipfade und kann deshalb nicht wieder zum Abspielen in PartyPicker oder VirtualDJ importiert werden.

## Bedienung

- Oben rechts lässt sich die gesamte Bedienoberfläche sofort zwischen Deutsch und Englisch umschalten. Die Auswahl wird gespeichert und beim nächsten Start wiederhergestellt.
- „🍺 Ein Bier für MurryB“ öffnet `https://ko-fi.com/murryb` im normalen Webbrowser. PartyPicker verarbeitet keine Zahlungs- oder Zugangsdaten.
- Waveform anklicken oder mit gedrückter Maustaste ziehen: im Lied springen. Berechnung läuft im Hintergrund.
- Play/Pause: Leertaste.
- Vorheriger/Nächster: Buttons oder Strg+Pfeil links/rechts.
- Zehn Sekunden zurück/vor: Buttons oder Pfeil links/rechts.
- A: laufenden Titel hinzufügen und sofort speichern (Tastenkürzel).
- „+ Playlist [Enter]“ / Enter: speichern und nächsten Titel starten. Das funktioniert mit der normalen Eingabetaste und mit Enter auf dem Ziffernblock. Der Button steht zwischen „+10 s“ und „Nächster“.
- Nach jeder neuen Aufnahme scrollt die Playlist automatisch zum zuletzt hinzugefügten Titel und markiert ihn. Dieses Verhalten gilt auch beim Öffnen einer vorhandenen M3U-Playlist.
- Bereits enthaltene Dateipfade werden nicht doppelt aufgenommen. Andere Dateien desselben Songs gelten als eigenständige Titel.
- Am Titelende automatisch zum nächsten Titel wechseln: abwählbar. Am Ordnerende stoppt die Wiedergabe.
- Ein neuer Musikordner ersetzt nur die Durchhörliste. Die Party-Playlist bleibt bestehen.
- Nicht lesbare Unterordner werden beim Scan übersprungen und anschließend gemeldet; bereits gefundene Titel bleiben nutzbar.
- Titel in beiden Listen per Doppelklick anhören. Vorschau aus der Playlist beeinflusst die aktuelle Ordnerposition nicht.
- Playlist-Titel auswählen, um sie zu entfernen oder mit ↑/↓ umzusortieren. Auch diese Änderungen werden sofort gespeichert.

## Playlists und VirtualDJ

M3U ist die Voreinstellung; M3U8 ist ebenfalls möglich. Beide werden als UTF-8-Text mit vollständigen lokalen Dateipfaden gespeichert. Die konkrete Unterstützung der Dateiendung .m3u8 wurde in VirtualDJ nicht verifiziert; verwende dort zunächst .m3u. Den gespeicherten Playlist-Ordner im VirtualDJ-Dateibrowser aufsuchen und die Playlist öffnen.

Es werden nur Verweise gespeichert, keine Musikdateien kopiert. Musik muss unter denselben Pfaden erreichbar bleiben, auch bei NAS-Laufwerken und externen Datenträgern. Auf einem anderen PC müssen diese Pfade ebenfalls passen. Gemappte Windows-Laufwerke wie `Z:` bleiben in dieser Darstellung erhalten und werden nicht absichtlich in UNC-Pfade umgewandelt. Fehlende Dateien werden beim Import markiert und bleiben in der Playlist erhalten. Import unterstützt lokale absolute und relative Pfade, keine Streaming-URLs. Beim Speichern werden vorhandene Kommentare/EXTINF-Zusatzinformationen nicht übernommen.

Jede Änderung wird außerhalb des GUI-Threads zunächst vollständig in eine temporäre Datei neben der Playlist geschrieben, mit `fsync` bestätigt und dann wird die Playlist ersetzt. Bei Schreibfehlern erscheint eine Meldung; „+ Playlist [Enter]“ springt dann nicht weiter. Artist-/Titel-Tags für TXT-Listen werden während der Sitzung zwischengespeichert. Dateistatus-Prüfungen und langsame Metadatenzugriffe blockieren dadurch nicht mehr die Oberfläche. Nicht gleichzeitig dieselbe Playlist mit einem anderen Programm bearbeiten.

## Optional: einzelne Windows-EXE erstellen

Nach dem ersten erfolgreichen Start kann `EXE_erstellen.bat` auf Windows eine eigenständige Ein-Datei-Version bauen. Ergebnis: `dist/PartyPicker.exe`. Diese eine Datei kann weitergegeben und direkt gestartet werden; Python muss auf dem Ziel-PC nicht installiert sein. Es liegt in diesem Paket noch keine vorgebaute Windows-EXE bei.

Die Ein-Datei-EXE ist größer und kann beim ersten Start einige Sekunden benötigen, weil ihre Bestandteile vorübergehend entpackt werden. Windows SmartScreen kann bei einer nicht digital signierten privaten App zunächst eine Warnung anzeigen. Dann „Weitere Informationen“ und „Trotzdem ausführen“ wählen. Manche Virenscanner prüfen selbst erstellte, nicht signierte PyInstaller-Dateien besonders streng.

## Prüfung und Grenzen

Playlist-Import/-Export, Fehlererhalt beim Speichern, FLAC-/MP3-Waveform und Oberfläche wurden automatisiert in einer Linux-Testumgebung geprüft. Tatsächliche Audioausgabe auf Windows, Windows-EXE-Erstellung und Import in VirtualDJ müssen auf dem Ziel-PC geprüft werden. Auf sehr langsamen Netzlaufwerken können Scan und Waveform länger dauern.

Technische Quellen: https://doc.qt.io/qtforpython-6/PySide6/QtMultimedia/QMediaPlayer.html, https://python-soundfile.readthedocs.io/ und https://pypi.org/project/tinytag/

Die Hinweise und Lizenzen der verwendeten Komponenten stehen in `THIRD_PARTY_NOTICES.txt`. Mutagen wird nicht verwendet.

PartyPicker selbst wird unter der `PartyPicker Freeware License 1.0` in `LICENSE.txt` veröffentlicht: kostenlose private Nutzung und unveränderte, kostenlose Weitergabe sind erlaubt; veränderte oder verkaufte Ausgaben benötigen die vorherige Erlaubnis des Urhebers.

## Oberfläche aktualisiert

Die Waveform ist von 170 auf 128 Pixel Höhe reduziert (rund 25 %). Ordnerliste und Party-Playlist stehen rechts untereinander; die Trennlinien lassen sich verschieben.

„Musikordner öffnen …“ steht direkt neben „Speichern unter …“, gefolgt von „Unterordner einbeziehen“. Die beiden Listenfenster rechts erhalten standardmäßig mehr Breite; die Aufteilung lässt sich weiterhin über die senkrechte Trennlinie verändern.

Die Option „Unterordner einbeziehen“ steht nun direkt unter „Musikordner öffnen …“. Die rechte Listenspalte beginnt dadurch bereits unter der Überschrift und nutzt den gewonnenen Platz vollständig für mehr Höhe.

Alle vier oberen Schaltflächen sind an derselben Oberkante ausgerichtet. Die rechte Listenspalte beginnt auf derselben Höhe wie die App-Überschrift.

Die App startet maximiert und nutzt die verfügbare Bildschirmfläche; Taskleiste und normale Fensterknöpfe bleiben sichtbar.

Das PartyPicker-Symbol mit Kopfhörer, Waveform und Pluszeichen wird beim Erstellen in die EXE eingebettet und außerdem als Fenster- und Taskleistensymbol verwendet. Falls Windows nach einem Neubau noch das alte Symbol zeigt, handelt es sich meist um den Windows-Icon-Cache; ein neuer Dateiname oder ein Neustart des Windows-Explorers aktualisiert die Anzeige.

Zum Aktualisieren: App schließen, ZIP entpacken und die enthaltenen Dateien in den bisherigen PartyPicker-Ordner kopieren/ersetzen. Die vorhandene .venv kann bleiben. Anschließend Starten.bat öffnen. Bei Nutzung einer selbst erstellten EXE danach EXE_erstellen.bat erneut ausführen.

## Tastaturprofile und Startauswahl

Unter den Listen lässt sich die Tastaturbelegung auswählen. Die Auswahl bleibt nach dem Neustart erhalten.

- Strg+Pfeile: Titel wechseln; Pfeile: ±10 Sekunden.
- Pfeile: Titel wechseln; Strg+Pfeile: ±10 Sekunden.
- Hoch/Runter: vorheriger/nächster Titel; Links/Rechts: ±10 Sekunden.
- Ziffernblock mit Num Lock: 1 = −10 Sekunden, 2 = +10 Sekunden, 3 = nächster Titel.

Leertaste, A und beide Enter-Tasten behalten ihre Funktion. Beim Start kann eine neue Playlist angelegt oder die letzte fortgesetzt werden. Beim ersten Start dieser Version ist Fortsetzen erst verfügbar, nachdem eine Playlist geöffnet oder gespeichert wurde. Eigene TXT-Sitzungen werden anhand zusätzlich gespeicherter Musikpfade fortgesetzt; extern veränderte TXT-Listen werden dabei nicht überschrieben.
