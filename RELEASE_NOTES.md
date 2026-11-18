# PartyPicker 2.1.3

- Bildschirmrand-Scrollen beim Ziehen von Titeln im Playlist-Manager unter Windows korrigiert.
- Die Randprüfung verwendet Windows-Mausposition und Monitorgrenzen in derselben Pixelkoordinate, ohne Rundungsfehler bei 200 Prozent Skalierung.
- Ein Windows-Timer hält das Scrollen auch während des nativen Ziehvorgangs bei unbewegtem Mauszeiger aktiv.
- Beginn erst bei Berührung des oberen beziehungsweise unteren Bildschirmrands; Stopp ab zehn Pixeln Abstand. Die bisherige Beschleunigung bleibt erhalten.
- Regressionstest mit echtem Windows-Drag-and-drop bei 200 Prozent Skalierung: unten scrollen, neun Pixel Abstand, Stopp bei zehn Pixeln, oben scrollen und Timer-Aufräumen.

ZIP vollständig entpacken und PartyPicker.exe starten. Die EXE ist weiterhin nicht digital signiert.
