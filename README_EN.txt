PARTYPICKER / The Playlist Generator
by MurryB · Version 2.1.5
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

NEW IN VERSION 1.1.0
Choose a keyboard layout at the bottom: Ctrl+arrows, arrows, Up/Down, or
numeric keypad (Num Lock: 1 = -10 s, 2 = +10 s, 3 = next track, Ctrl+3 = previous track).
The shortcut hints reflect your saved choice. On startup, create a new playlist
or continue the last one. On first use, open or save a playlist to enable resume.

NEW IN VERSION 1.1.1
When resuming, check "Also open the last music folder" to restore the most
recently selected folder and the subfolder setting. Its first track starts
automatically after the scan. If no folder has been saved yet, check "Choose a
music folder when resuming" to select one. The checkbox is highlighted in
light gray. The logo now has three stacked lines: PARTYPICKER, the subtitle,
and by MurryB.

NEW IN VERSION 1.1.2
When resuming with the last music folder, playback starts at the last track
played from that folder. If it is no longer available, the first track starts.


NEW IN VERSION 1.2.1
--------------------
- When resuming, the folder list scrolls to the last played track and starts
  it from the beginning.

NEW IN VERSION 1.2.0
--------------------
- Grey: undecided; Green: in the current playlist;
  Orange: manually skipped with Previous/Next or a keyboard shortcut.
  Green takes priority. Markings persist and can be cleared for the current
  folder using "Reset markings".
- Matching artist and title in different files: confirmation before adding.
  Artist/title tags are preferred, with an unambiguous Artist - Title filename
  as fallback. Different mix names remain distinct. Checks run in the background.
- "Preview from": start at 0–600 seconds, default 0. Short tracks keep at least
  10 seconds for auditioning or start from the beginning.
- "Undo [Ctrl+Z]": undo up to 20 successful playlist changes in this session.
  Every undo is saved immediately; failed saves preserve playlist and history.
- "Match listening volume": off by default, takes effect after waveform analysis.
  Uses RMS and peak levels to adjust listening volume. Music files are unchanged.
  This is not LUFS normalization; very quiet tracks are limited by the volume
  slider. This setting and the preview position persist across restarts.
- Missing file or playback error: "Retry" or "Skip track". File checks run in
  the background; an unresponsive NAS can still cause longer waits.

PLAYLIST MANAGER IN VERSION 2.0.0

The button at the lower right of the PartyPicker playback pane opens the manager in the same window. It uses the current playlist or opens an M3U/M3U8 file. The playlist continues from the left column into the right column; both share one scrollbar.

Use Ctrl-click or Ctrl with the left mouse button to select tracks, then drag the selection. A green insertion line shows the drop position. The drag preview shows three tracks plus the remaining count. Edge scrolling starts only on contact with the upper/lower screen edge and stops at a distance of at least ten pixels, resetting acceleration. Speed increases every 1.5 seconds: 4, 8, 16, 28, 44, then at most 60 tracks per second. Leaving the edge stops scrolling and resets acceleration.

Move to beginning/end changes track order. Go to beginning/end only moves the view. Undo or Ctrl+Z restores a previous edit. Every edit is saved immediately. Space toggles preview playback for one selected track. BPM is read from existing file tags; there is no automatic BPM analysis.

Fixed in 2.0.0: Preview from waits for loading and confirms the actual start position. Audio is briefly muted during seeking. Short-track handling is preserved.

ANIMATIONS IN VERSION 2.1.0
Dragging in the manager fades the selected rows out and slides the remaining tracks together. A preview gap opens at the intended insertion point. Dropping fades the tracks in and saves the final order. Cancelling restores the original order and selection. A failed save also restores the view.
In PartyPicker, status colours transition smoothly, playlist tracks fade in/out on add/remove, and the waveform crossfades on track changes. Short transitions do not delay actual list changes or playback.

FIXES IN VERSION 2.1.1
Large music folders are populated and coloured in a batch. Only visible subsequent status changes are animated. Navigation and closing do not wait for blocked file reads. Previously read metadata is cached.
If a playlist save is still running when closing, the interface remains responsive until it finishes. A save failure keeps the window open and displays the error.

COMPACT LAYOUT IN VERSION 2.1.5
Song titles stay on one line; long titles end with an ellipsis. File and playlist paths are shortened in the middle. Hover over the text to see the full title/path. Internal titles and file paths remain unchanged.
At smaller window heights or widths, PartyPicker uses compact spacing and controls automatically. The waveform keeps its full height. This helps with displays such as 2256 × 1504 at 200 percent Windows scaling.


Fixed screen-edge scrolling while dragging in the playlist manager on Windows: starts at the actual screen edge, accelerates with a stationary pointer, and stops at ten pixels distance. High display scaling is handled using Windows monitor pixels.



While dragging in the playlist manager, a small red no-entry sign indicates that tracks cannot be dropped outside the two playlist columns. The hand cursor returns over either column.


Fullscreen: PartyPicker starts in fullscreen by default, without the Windows title bar or taskbar. F11 toggles fullscreen and windowed mode; Esc leaves fullscreen. While dragging tracks, Esc only cancels the drag. The last chosen mode is remembered. Works in both interfaces.
