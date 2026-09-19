PARTYPICKER / The Playlist Generator
by MurryB
====================================

OVERVIEW
--------
PartyPicker lets you quickly listen through folders containing FLAC and MP3
music and select suitable tracks for a party. Music files are never copied or
modified.


START
-----
1. Double-click PartyPicker.exe.
2. The first launch may take a little longer while the EXE briefly extracts
   its internal components.
3. The app starts maximized. Use the normal Windows buttons to resize or close
   it.


IMPORTANT WINDOWS NOTICE
------------------------
Because the EXE is not digitally signed, Windows SmartScreen may display a
warning. Select "More info" and then "Run anyway".

Only run the file when it came directly from MurryB or another trusted source.
If in doubt, scan it with Windows Security or another up-to-date virus scanner.


FIRST STEPS
-----------
1. Select "New playlist …" and choose a location and file name.
2. Select "Open music folder …" and choose the desired folder.
3. The first track starts automatically.
4. Use "+ Playlist [Enter]" to add the current track and immediately continue
   to the next one.
5. Every change is saved immediately.
6. The playlist automatically scrolls to and selects the most recently added
   track. The last entry is also shown after opening an existing M3U playlist.


LANGUAGE
--------
Use the selector in the upper-right corner to switch between Deutsch and
English at any time. The complete interface is updated immediately. Your
selection is saved and restored the next time PartyPicker starts.


CONTROLS
--------
- Click or drag in the waveform to seek within a track
- Space: Play/Pause
- Left/Right arrow: skip back/forward 10 seconds
- Ctrl + Left/Right arrow: previous/next track
- Enter or numeric keypad Enter: add the track to the playlist and continue
- Double-click a track to play it
- Arrow buttons below the playlist: move the selected entry
- "Remove from playlist": delete the selected entry
- "Include subfolders": also search nested music folders
- Unreadable subfolders are skipped and reported after the scan


PLAYLIST FORMATS
----------------
By default, PartyPicker creates an M3U playlist containing links to the
original music files. It can be used in applications such as VirtualDJ. The
FLAC and MP3 files must remain available at their original locations.

Mapped Windows drives such as Z: retain that representation when saved. Saving,
TXT metadata reading, and file availability checks run in the background so the
interface remains responsive with long playlists or NAS storage.

When "TXT file only" is selected before creating a playlist, PartyPicker saves
a plain-text list in this format:

Artist - Title

The information comes from the FLAC or MP3 tags. If no tags are available, the
file name is used. A TXT file contains no music paths and therefore cannot be
imported as a playable playlist in PartyPicker or VirtualDJ.


SUPPORT
-------
The "Buy MurryB a beer" button opens https://ko-fi.com/murryb in your default
web browser. PartyPicker itself never processes payment or login information.


DISTRIBUTION
------------
PartyPicker.exe is a self-contained single-file version. No additional files,
Python installation, or PartyPicker installation are required on the target
computer.

PartyPicker may be used free of charge for personal, non-commercial purposes
and redistributed free of charge as the complete, unmodified original package.
See LICENSE.txt for the complete terms and THIRD_PARTY_NOTICES.txt for notices
covering third-party components.


NOTICE
------
PartyPicker is a private utility by MurryB. Use it at your own risk.
