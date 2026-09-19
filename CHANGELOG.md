# Changelog

## 1.1.0

- Vier umschaltbare, gespeicherte Tastaturbelegungen mit passender Kurzanleitung.
- Startauswahl: neue Playlist oder letzte Playlist fortsetzen, einschließlich eigener TXT-Sitzungen.

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
