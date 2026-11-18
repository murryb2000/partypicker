# PARTYPICKER / Der Playlist-Generator

Lokale Desktop-App zum Durchhören von FLAC- und MP3-Sammlungen und Zusammenstellen einer Party-Playlist. Python mit PySide6 ermöglicht direkte Dateizugriffe und Speichern ohne Browser-Berechtigungsdialoge. Wiedergabe über Qt Multimedia; Waveform aus den echten Audiodaten über SoundFile. TinyTag liest Artist-, Titel- und vorhandene BPM-Metadaten. Keine Musik-Uploads.

## Neu in Version 2.1.1

- Behoben: Große Musikordner konnten beim Aufbau und Einfärben der Titelliste die Oberfläche lange blockieren. Der erste Listenaufbau erfolgt jetzt gesammelt; Farbüberblendungen gelten für sichtbare Zustandsänderungen.
- Zurückwechseln aus dem Playlist-Manager und Schließen warten nicht mehr auf blockierte Datei-Lesezugriffe, etwa auf einem NAS.
- Abgebrochene oder verspätete Leseergebnisse werden ignoriert. Metadaten werden gezielt aktualisiert und bereits gelesene Titel zwischengespeichert.
- Laufende Speichervorgänge werden vor dem Beenden abgeschlossen, ohne die Ereignisverarbeitung der Oberfläche zu blockieren. Bei einem Speicherfehler bleibt das Fenster zur Korrektur geöffnet.
- Zusätzliche Prüfungen mit 6.000 Titeln, blockierten Metadaten, Beenden des Prozesses und verzögertem beziehungsweise fehlgeschlagenem Speichern.

## Neu in Version 2.1.0

- Playlist-Manager: animiertes Aufnehmen und Verschieben von Titeln. Die ursprünglichen Zeilen werden leer, die Liste gleitet zusammen, und am Einfügepunkt öffnet sich Platz.
- Beim Loslassen blenden die eingefügten Titel ein. Abbrechen stellt die ursprüngliche Reihenfolge und Auswahl wieder her.
- Die Ziehvorschau ändert die Playlist-Datei nicht. Gespeichert wird erst die endgültige Reihenfolge beim Ablegen. Fehler beim Speichern stellen auch die Ansicht zurück.
- PartyPicker: sanfte Übergänge zwischen den Statusfarben, Ein-/Ausblenden der Playlist-Titel und Überblenden der Waveform beim Titelwechsel.
- Die Animationen blockieren weder Wiedergabe noch Speicherung; schnelle Änderungen können laufende Übergänge ersetzen.
- Bildschirmrand-Scrollen, zehn Pixel Stoppabstand, Rückgängig und der korrigierte Vorhör-Startpunkt aus 2.0 bleiben erhalten.

## Neu in Version 2.0.1

Automatisches Scrollen beim Ziehen beginnt ausschließlich durch Berühren des oberen oder unteren Bildschirmrands und stoppt ab zehn Pixeln Abstand. Die Grenzen des App-Fensters und der Listen lösen kein Scrollen mehr aus.

## Neu in Version 2.0.0

- Playlist-Manager im selben Fenster, erreichbar unten rechts im PartyPicker.
- Fortlaufende Playlist über zwei Spalten mit gemeinsamem Scrollbalken.
- Mehrfachauswahl, Drag-and-drop mit grüner Einfügelinie und Ziehvorschau mit drei Titeln plus Restanzahl.
- Automatisches Scrollen am Rand: 4, 8, 16, 28, 44 und maximal 60 Titel pro Sekunde, Stufenwechsel alle 1,5 Sekunden.
- Separate Buttons zum Verschieben der Auswahl und zum Springen der Ansicht an Listenanfang oder Listenende.
- Rückgängig per Button oder Strg+Z, auch im Manager; jede Änderung wird gespeichert.
- Vorhören im Manager per Leertaste, BPM aus vorhandenen Datei-Tags.
- Behoben: Der Vorhör-Startpunkt wird nach dem Laden angewendet und bestätigt; ein beim Wiedergabestart zurückgesetzter Sprung wird wiederholt.

## Neu in Version 1.2.1

- Beim Fortsetzen springt die Ordnerliste sichtbar zum zuletzt gespielten Titel und startet ihn von vorn.

## Neu in Version 1.2.0

- Ordnerliste mit gespeicherten Farben: noch nicht entschiedene Titel grau, aufgenommene grün, nicht aufgenommene und übersprungene Titel orange. Markierungen lassen sich pro geöffnetem Ordner zurücksetzen.
- Hintergrundprüfung auf gleiche Artist-/Titel-Metadaten; bei einer anderen Datei desselben Songs kann die Aufnahme bestätigt oder abgelehnt werden.
- Einstellbare Startposition fürs Vorhören (0 bis 600 Sekunden, Standard 0). Kurze Titel behalten mindestens zehn Sekunden Restlaufzeit oder starten am Anfang.
- Rückgängig-Button und Strg+Z für die letzten 20 erfolgreichen Playlist-Änderungen der Sitzung, einschließlich Aufnahme, Entfernung und Reihenfolge. Jede Rücknahme wird automatisch gespeichert.
- Optionale Lautstärkeangleichung beim Vorhören anhand von RMS und Spitzenpegeln, ohne Änderungen an Musikdateien.
- Dateiprüfung vor der Wiedergabe im Hintergrund; bei fehlenden Dateien oder Wiedergabefehlern stehen Erneut versuchen und Titel überspringen zur Verfügung.
- Verspätete Analyse- und Prüf-Ergebnisse beeinflussen keine inzwischen gestarteten Titel. Automatisierte Regressionstests für die neuen Funktionen.

Noch nicht entschiedene Titel bleiben grau. Manuelles Wechseln mit Vorheriger/Nächster, Tastenkürzeln oder das natürliche Titelende markiert nicht aufgenommene Titel orange. Aufgenommene Titel sind grün und haben Vorrang. Ein Doppelklick auf einen anderen Titel erhält den vorherigen Status. Grün richtet sich immer nach der aktuell geöffneten Playlist und hat Vorrang. Die Hörmarkierungen werden lokal gespeichert, „Markierungen zurücksetzen“ entfernt sie für den geöffneten Ordner.

Die Vorhörposition und Lautstärkeoption bleiben gespeichert. Lautstärkeangleichung ist standardmäßig aus. Die Angleichung wird nach Abschluss der Waveform-Analyse wirksam, verwendet den mittleren Pegel (RMS, Ziel ungefähr −20 dBFS) und begrenzt die Anhebung auf maximal +6 dB sowie verfügbare Lautstärke und Spitzenpegel. Sie ist keine EBU-R128/LUFS-Normalisierung; sehr leise Titel können durch den Regler nicht beliebig verstärkt werden.

Duplikate werden anhand von Artist und Title erkannt, mit vereinheitlichter Groß-/Kleinschreibung, Unicode und Leerzeichen. Ohne vollständige Tags wird nur ein eindeutiger Dateiname mit „Artist - Titel“ verwendet. Unterschiedliche Mix-Bezeichnungen werden nicht entfernt; identische Tags bei unterschiedlichen Versionen können trotzdem eine Nachfrage auslösen. Die Prüfung läuft im Hintergrund und ihre Ergebnisse werden während der Sitzung zwischengespeichert.

Rückgängig betrifft die Playlist, nicht die aktuelle Abspielposition. Bei fehlgeschlagener Speicherung bleiben Playlist und Rückgängig-Verlauf erhalten. Beim Öffnen einer anderen Playlist beginnt ein neuer Verlauf. Ein wirklich nicht antwortendes NAS kann Hintergrundzugriffe länger verzögern; es gibt keine garantierte Netzwerk-Zeitüberschreitung.

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
- Bereits enthaltene Dateipfade werden nicht doppelt aufgenommen. Andere Dateien mit demselben Interpret und Titel lösen eine Duplikat-Nachfrage aus.
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
- Ziffernblock mit Num Lock: 1 = −10 Sekunden, 2 = +10 Sekunden, 3 = nächster Titel; Strg+3 = vorheriger Titel.

Leertaste, A und beide Enter-Tasten behalten ihre Funktion. Beim Start kann eine neue Playlist angelegt oder die letzte fortgesetzt werden. Beim ersten Start dieser Version ist Fortsetzen erst verfügbar, nachdem eine Playlist geöffnet oder gespeichert wurde. Eigene TXT-Sitzungen werden anhand zusätzlich gespeicherter Musikpfade fortgesetzt; extern veränderte TXT-Listen werden dabei nicht überschrieben.

Ab Version 1.1.1 kann beim Fortsetzen der zuletzt gewählte Musikordner zusätzlich geöffnet werden. Die gespeicherte Unterordner-Einstellung wird übernommen. Ab Version 1.1.2 startet nach dem Scan der zuletzt gespielte Titel aus dem Ordner; ist er nicht mehr vorhanden, beginnt die Wiedergabe beim ersten Titel. Wurde noch kein Musikordner gespeichert, lässt sich über den hellgrau hervorgehobenen Haken beim Fortsetzen ein Ordner auswählen. Im Kopfbereich stehen neben dem Logo PARTYPICKER, der lokalisierte Untertitel und „by MurryB“ untereinander.

## Playlist-Manager in Version 2.0.0

Der Button unten rechts im linken PartyPicker-Bereich öffnet den Manager im selben Fenster. Die aktuelle Playlist wird übernommen; alternativ kann eine M3U-/M3U8-Datei geladen werden. Links beginnt die Liste, rechts wird sie fortgeführt. Ein gemeinsamer Scrollbalken bewegt beide Spalten.

Titel mit Strg auswählen oder mit Strg und gedrückter linker Maustaste überstreichen. Die Auswahl anschließend ziehen; die grüne Linie markiert die Einfügestelle. Die Ziehvorschau zeigt die ersten drei Titel und bei Bedarf +Restanzahl. Nach Berührung des oberen/unteren Bildschirmrands scrollt die Liste automatisch. Ab zehn Pixeln Abstand stoppt sie und setzt die Beschleunigung zurück. Geschwindigkeit: alle 1,5 Sekunden steigt die Geschwindigkeit auf 4, 8, 16, 28, 44 und maximal 60 Titel pro Sekunde. Beim Verlassen des Randbereichs endet das Scrollen und die Beschleunigung wird zurückgesetzt.

„An den Anfang“/„Ans Ende“ verschiebt ausgewählte Titel. „Zum Listenanfang“/„Zum Listenende“ bewegt nur die Ansicht. „Rückgängig“/Strg+Z nimmt eine Änderung zurück. Änderungen werden sofort gespeichert. Mit genau einem ausgewählten Titel schaltet die Leertaste zwischen Wiedergabe und Pause um. BPM wird aus vorhandenen Tags gelesen; es wird keine automatische BPM-Analyse durchgeführt.

Korrektur in 2.0.0: „Vorhören ab“ wartet auf das Laden und bestätigt den tatsächlichen Startpunkt. Während des Sprungs bleibt der Ton kurz stumm. Die Behandlung kurzer Titel bleibt erhalten.

## Animationen
Beim Ziehen im Manager werden die ausgewählten Zeilen ausgeblendet und die übrigen Titel gleiten zusammen. Am anvisierten Einfügepunkt öffnet sich eine Vorschau-Lücke. Beim Ablegen blenden die Titel dort ein; erst dann wird gespeichert. Abbrechen stellt Reihenfolge und Auswahl wieder her. Ein Speicherfehler stellt auch die Vorschau zurück.
In PartyPicker überblenden die Statusfarben, Titel blenden beim Aufnehmen/Entfernen ein oder aus, und die Waveform überblendet beim Titelwechsel. Die kurzen Übergänge verzögern weder die tatsächliche Listenänderung noch die Wiedergabe.
