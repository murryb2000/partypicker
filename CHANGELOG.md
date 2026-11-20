# Changelog

## 2.2.2 – 2026-11-20

- Statusfilter als Pulldown-Menü im Ordnerfenster: Keine, Ungehört, Übersprungen und Beides.
- Keine zeigt alle Titel; Beides zeigt ungehörte und übersprungene Titel. Aufgenommene Titel sind bei aktiven Filtern ausgeblendet.
- Auswahl bleibt nach Neustart erhalten und wird vollständig auf Deutsch/Englisch angezeigt.
- Manueller und automatischer Titelwechsel sowie Aufnehmen & weiter berücksichtigen den Filter. Wechseln des Filters unterbricht den aktuellen Song nicht.
- Keine Treffer beziehungsweise kein weiterer passender Titel: klarer Hinweis, kein Start eines ausgeblendeten Titels.
- Die vierte Zeile als Vorhörposition berücksichtigt nun drei vorherige sichtbare Titel.
- Sieben zusätzliche Tests einschließlich 6000 Titeln, Statusänderungen, Wiederaufnahme und gefilterter Navigation.

## 2.2.1 – 2026-11-20

- Playlist-Manager: „Markierte Titel entfernen“ für Einzel- und Mehrfachauswahl.
- Bestätigungsdialog ist standardmäßig aktiv. „Beim Entfernen nicht mehr nachfragen“ wird gespeichert und lässt sich wieder ausschalten.
- Entfernt ausschließlich Playlist-Einträge; die Musikdateien bleiben erhalten. Änderungen werden gespeichert, gesichert und lassen sich rückgängig machen.
- Laufendes Vorhören eines erfolgreich entfernten Eintrags wird beendet; fehlgeschlagenes Speichern erhält Einträge und Auswahl.

## 2.2 – 2026-11-19

- Gesamtdauer der Playlist in PartyPicker und im Playlist-Manager; der Manager zeigt zusätzlich die Dauer markierter Titel.
- Längen werden asynchron gelesen und zwischengespeichert. Offene beziehungsweise nicht erreichbare Titel sind ausdrücklich gekennzeichnet; ≥ zeigt eine unvollständige Summe.
- Vor dem Überschreiben werden bis zu drei bisherige Playlist-Stände direkt neben der Datei gesichert. Identische Inhalte erzeugen keine weitere Sicherung.
- Sicherungsnamen enthalten Datum/Uhrzeit (UTC) und eine eindeutige Kennung. Der gleiche Ordner erhält die Bedeutung relativer M3U-Pfade.
- Schlägt die Sicherung fehl, wird die bestehende Playlist nicht überschrieben. Die Musikdateien werden nicht kopiert.
- Acht zusätzliche Tests für Dauer, Auswahl, Sprache, blockierte Zugriffe, Sicherungsrotation, relative Pfade und Schreibfehler.

## 2.1.8 – 2026-11-19

### Robustheitskorrekturen ohne Versionsänderung

- Verspätetes Speichern nach „Aufnehmen & weiter“ überspringt keinen weiteren Titel, wenn zwischenzeitlich navigiert wurde.
- Waveform-Analyse liest höchstens 4096 Frames pro Block und erzeugt höchstens 1600 Punkte; manipulierte Längenangaben vergrößern den Puffer nicht.
- Playlist-Import einschließlich TXT-Sitzungsprüfung läuft im Hintergrund. Veraltete Ergebnisse werden verworfen; Fehler erhalten die bisherige Playlist.
- Maximal zwei gleichartige Lesejobs laufen parallel; nur der neueste wartende Auftrag bleibt erhalten.
- Mindestversion PySide6 6.12.0; Starten.bat aktualisiert ältere bestehende Umgebungen einmalig.
- Zusätzliche Regressionstests für verzögerte Speicherung, NAS-Import, Job-Begrenzung und manipulierte FLAC-Header.


- Farbüberblendungen im Vorhörfenster dauern jetzt 440 statt 220 Millisekunden und laufen damit halb so schnell. Timer-Intervall und Begrenzung auf sichtbare Titel bleiben erhalten.

## 2.1.7 – 2026-11-19

- Vorhörfenster: Der aktuelle Titel bleibt beim Titelwechsel in der vierten sichtbaren Zeile, mit drei vorherigen Titeln darüber. Am Ordneranfang und -ende wird die Position an die verfügbaren Einträge angepasst.
- Gilt auch beim Fortsetzen des letzten Musikordners sowie beim Vor- und Zurückspringen.

## 2.1.6 – 2026-11-19

- Vollbild-Steuerung oben links mit „Fensteransicht [F11]“ und „Beenden“, auch im Playlist-Manager.
- Buttons erscheinen nur im Vollbild; die Beschriftung folgt der Spracheinstellung.
- Beenden verwendet den bestehenden Ablauf zum sicheren Abschließen laufender Speichervorgänge.
- UI-Prüfung mit echten Button-Klicks in beiden Oberflächen, Sprachwechsel und Schließen.

## 2.1.5 – 2026-11-19

- Echter Vollbildmodus ist die Standardansicht beim Start; die zuletzt gewählte Ansicht wird gespeichert.
- F11 schaltet in beiden Oberflächen um, Esc verlässt das Vollbild.
- Esc während eines Ziehvorgangs bricht nur das Verschieben ab und lässt das Vollbild bestehen.
- Neue Prüfungen für Standardansicht, gespeicherte Auswahl, Tastenkürzel in beiden Oberflächen und Esc beim Ziehen.

## 2.1.4 – 2026-11-18

- Neues rotes Einfahrt-verboten-Schild am Mauszeiger außerhalb der beiden Ablageflächen im Playlist-Manager.
- Die Hand erscheint beim Zurückkehren in eine Playlist-Spalte; nach Ende oder Abbruch wird der normale Mauszeiger wiederhergestellt.

## 2.1.3 – 2026-11-18

- Rand-Scrollen im Playlist-Manager auf Windows-Monitorpixel umgestellt.
- Interne Ziehvorgänge umgehen die blockierende Windows-OLE-Schleife; Scrollen und Beschleunigung funktionieren auch ohne weitere Mausbewegung.
- Start ausschließlich am Bildschirmrand, Stopp ab zehn Pixeln Abstand; Monitorwechsel setzt den Randzustand zurück.
- Neuer Windows-Integrationstest mit internem Ziehvorgang und 200 Prozent Skalierung.

## 2.1.2 – 2026-11-18

- Songtitel belegen genau eine Zeile und werden bei Bedarf am Ende mit „…“ gekürzt.
- Musikdateipfad und Playlist-Pfad belegen je eine Zeile und werden in der Mitte gekürzt. Der Dateiname am Ende bleibt erkennbar.
- Der vollständige Titel beziehungsweise Pfad erscheint beim Darüberfahren mit der Maus und bleibt intern unverändert.
- Bei geringer Fensterhöhe oder -breite verwendet die PartyPicker-Oberfläche kleinere Abstände und kompaktere Bedienelemente. Die Waveform bleibt vollständig mit 128 logischen Pixeln Höhe sichtbar.
- Layout geprüft mit langen Texten, Deutsch/Englisch, 1128 × 752 sowie 1128 × 680 und 200 Prozent Qt-Skalierung.

## 2.1.1 – 2026-11-18

- Behoben: Große Musikordner konnten beim Aufbau und Einfärben der Titelliste die Oberfläche lange blockieren. Der erste Listenaufbau erfolgt jetzt gesammelt; Farbüberblendungen gelten für sichtbare Zustandsänderungen.
- Zurückwechseln aus dem Playlist-Manager und Schließen warten nicht mehr auf blockierte Datei-Lesezugriffe, etwa auf einem NAS.
- Abgebrochene oder verspätete Leseergebnisse werden ignoriert. Metadaten werden gezielt aktualisiert und bereits gelesene Titel zwischengespeichert.
- Laufende Speichervorgänge werden vor dem Beenden abgeschlossen, ohne die Ereignisverarbeitung der Oberfläche zu blockieren. Bei einem Speicherfehler bleibt das Fenster zur Korrektur geöffnet.
- Zusätzliche Prüfungen mit 6.000 Titeln, blockierten Metadaten, Beenden des Prozesses und verzögertem beziehungsweise fehlgeschlagenem Speichern.

## 2.1.0 – 2026-11-18

- Playlist-Manager: animiertes Aufnehmen und Verschieben von Titeln. Die ursprünglichen Zeilen werden leer, die Liste gleitet zusammen, und am Einfügepunkt öffnet sich Platz.
- Beim Loslassen blenden die eingefügten Titel ein. Abbrechen stellt die ursprüngliche Reihenfolge und Auswahl wieder her.
- Die Ziehvorschau ändert die Playlist-Datei nicht. Gespeichert wird erst die endgültige Reihenfolge beim Ablegen. Fehler beim Speichern stellen auch die Ansicht zurück.
- PartyPicker: sanfte Übergänge zwischen den Statusfarben, Ein-/Ausblenden der Playlist-Titel und Überblenden der Waveform beim Titelwechsel.
- Die Animationen blockieren weder Wiedergabe noch Speicherung; schnelle Änderungen können laufende Übergänge ersetzen.
- Bildschirmrand-Scrollen, zehn Pixel Stoppabstand, Rückgängig und der korrigierte Vorhör-Startpunkt aus 2.0 bleiben erhalten.

## 2.0.1 – 2026-11-18

- Korrigiert: Automatisches Scrollen beim Ziehen startet erst bei Berührung des tatsächlichen oberen oder unteren Bildschirmrands.
- Das Scrollen stoppt bei mindestens zehn Pixeln Abstand; die Beschleunigung wird dabei zurückgesetzt.
- Fensterränder und Listenränder lösen kein Scrollen mehr aus. Mehrere Monitore und Bildschirmskalierung werden berücksichtigt.
- Die Geschwindigkeitskurve aus Version 2.0 bleibt erhalten.

## 2.0.0 – 2026-11-18

- Playlist-Manager im selben Fenster, erreichbar unten rechts im PartyPicker.
- Fortlaufende Playlist über zwei Spalten mit gemeinsamem Scrollbalken.
- Mehrfachauswahl, Drag-and-drop mit grüner Einfügelinie und Ziehvorschau mit drei Titeln plus Restanzahl.
- Automatisches Scrollen am Rand: 4, 8, 16, 28, 44 und maximal 60 Titel pro Sekunde, Stufenwechsel alle 1,5 Sekunden.
- Separate Buttons zum Verschieben der Auswahl und zum Springen der Ansicht an Listenanfang oder Listenende.
- Rückgängig per Button oder Strg+Z, auch im Manager; jede Änderung wird gespeichert.
- Vorhören im Manager per Leertaste, BPM aus vorhandenen Datei-Tags.
- Behoben: Der Vorhör-Startpunkt wird nach dem Laden angewendet und bestätigt; ein beim Wiedergabestart zurückgesetzter Sprung wird wiederholt.

## 1.2.1 – 2026-10-14

- Beim Fortsetzen wird der zuletzt gespielte Titel im erneut geöffneten Musikordner sichtbar markiert und abgespielt, auch wenn er weit unten in einer langen Liste steht.

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

