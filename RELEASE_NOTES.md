# PartyPicker 2.1.3

- Bildschirmrand-Scrollen beim Ziehen von Titeln im Playlist-Manager unter Windows korrigiert.
- Die Randprüfung verwendet Windows-Mausposition und Monitorgrenzen in derselben Pixelkoordinate, ohne Rundungsfehler bei 200 Prozent Skalierung.
- Der Manager verarbeitet interne Ziehvorgänge in der normalen App-Ereignisschleife, damit Windows das Rand-Scrollen nicht blockiert.
- Beginn erst bei Berührung des oberen beziehungsweise unteren Bildschirmrands; Stopp ab zehn Pixeln Abstand. Die bisherige Beschleunigung bleibt erhalten.
- Regressionstest mit internem Windows-Ziehvorgang bei 200 Prozent Skalierung: unten scrollen, neun Pixel Abstand, Stopp bei zehn Pixeln, oben scrollen und Aufräumen nach dem Ziehen.

ZIP vollständig entpacken und PartyPicker.exe starten. Die EXE ist weiterhin nicht digital signiert.
