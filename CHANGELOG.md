# Changelog

## 1.2.0 – 2026-10-02

- Alle Checkbox-Kästchen verwenden das Blaugrau der noch nicht abgespielten Waveform, auch im Startdialog; gesetzte Haken bleiben weiß sichtbar.
- Ordnerliste mit gespeicherten Farben: gehörte Titel grau, aufgenommene grün, manuell übersprungene orange. Markierungen lassen sich pro geöffnetem Ordner zurücksetzen.
- Hintergrundprüfung auf gleiche Artist-/Titel-Metadaten; bei einer anderen Datei desselben Songs kann die Aufnahme bestätigt oder abgelehnt werden.
- Einstellbare Startposition fürs Vorhören (0 bis 600 Sekunden, Standard 0). Kurze Titel behalten mindestens zehn Sekunden Restlaufzeit oder starten am Anfang.
- Rückgängig-Button und Strg+Z für die letzten 20 erfolgreichen Playlist-Änderungen der Sitzung, einschließlich Aufnahme, Entfernung und Reihenfolge. Jede Rücknahme wird automatisch gespeichert.
- Optionale Lautstärkeangleichung beim Vorhören anhand von RMS und Spitzenpegeln, ohne Änderungen an Musikdateien.
- Dateiprüfung vor der Wiedergabe im Hintergrund; bei fehlenden Dateien oder Wiedergabefehlern stehen Erneut versuchen und Titel überspringen zur Verfügung.
- Verspätete Analyse- und Prüf-Ergebnisse beeinflussen keine inzwischen gestarteten Titel. Automatisierte Regressionstests für die neuen Funktionen.

## 1.1.2 – 2026-10-02

- Beim Fortsetzen mit dem letzten Musikordner beginnt die Wiedergabe beim zuletzt gespielten Titel aus diesem Ordner.
- Ist dieser Titel nicht mehr vorhanden, startet der erste verfügbare Titel.

## 1.1.1 – 2026-10-01

- Der Titelbereich zeigt PARTYPICKER, den Untertitel und „by MurryB“ untereinander neben dem Logo.
- Beim Fortsetzen lässt sich der letzte Musikordner optional öffnen; die Unterordner-Einstellung wird übernommen und der erste Titel startet automatisch.
- Bei bestehenden Installationen ohne gespeicherten Musikordner kann direkt beim Fortsetzen einer ausgewählt werden.
- Der Haken im Startdialog ist durch einen hellgrauen Hintergrund besser erkennbar.

## 1.1.0

- Vier umschaltbare, gespeicherte Tastaturbelegungen mit passender Kurzanleitung.
- Startauswahl: neue Playlist oder letzte Playlist fortsetzen, einschließlich eigener TXT-Sitzungen.
- Im Ziffernblock-Profil wechselt Strg+3 zum vorherigen Titel.
- Die Versionsnummer wird klein neben dem Programmtitel angezeigt.

## 1.0.4 – 2026-09-19

- Titelwechsel nach abgeschlossener Waveform-Analyse repariert: Referenzen auf fertige Threads werden im GUI-Thread vor `deleteLater()` entfernt.
- Ein verspätet beendeter Analyse-Thread löscht nicht die Referenz auf eine bereits gestartete neue Analyse.

## 1.0.3 – 2026-09-19

- Die natürliche Sortierung behandelt nur noch dezimale Ziffern als Zahlen und bleibt bei ungewöhnlichen Unicode-Zeichen robust.
- Beendete Scan-, Speicher-, Prüf- und Waveform-Threads werden mit `deleteLater()` freigegeben.

## 1.0.2 – 2026-09-19

- Nicht lesbare Unterordner werden beim Musikscan übersprungen, ohne bereits gefundene Titel zu verwerfen.
- Playlist-Speicherung, `fsync` und das Lesen von TXT-Metadaten laufen außerhalb des GUI-Threads.
- Gelesene Artist-/Titel-Metadaten werden während der Sitzung zwischengespeichert.
- Die Playlist-Anzeige wird nach Änderungen nur noch gezielt aktualisiert; Dateistatus-Prüfungen laufen im Hintergrund.
- M3U-Pfade behalten ihre Laufwerksdarstellung; `Path.resolve()` wird beim Import und Speichern nicht mehr verwendet.
- Die Duplikatprüfung verwendet einen separaten, schnellen und unter Windows nicht zwischen Groß-/Kleinschreibung unterscheidenden Vergleichsschlüssel.

## 1.0.1 – 2026-09-18

- Enter auf dem Ziffernblock führt jetzt ebenfalls „+ Playlist und weiter“ aus.

## 1.0.0 – 2026-09-18

- Erste öffentliche Version von PartyPicker.
- FLAC- und MP3-Wiedergabe mit anklickbarer Waveform.
- Automatisch gespeicherte M3U/M3U8-Playlists und optionale TXT-Titellisten.
- Deutsche und englische Oberfläche.
- TinyTag ersetzt Mutagen zum Lesen von Artist- und Title-Tags.
- Windows-Ein-Datei-Build mit eingebettetem PartyPicker-Symbol.
