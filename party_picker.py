import os
import json
import sys
from pathlib import Path
import numpy as np
import soundfile as sf
from tinytag import TinyTag
from PySide6.QtCore import Qt, QUrl, QThread, Signal, Slot, QTimer, QSettings
from PySide6.QtGui import (QColor, QDesktopServices, QIcon, QPainter, QPen,
                           QShortcut, QKeySequence, QPixmap)
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
    QHBoxLayout, QGridLayout, QPushButton, QLabel, QListWidget, QFileDialog, QMessageBox,
    QSplitter, QCheckBox, QSlider, QComboBox, QSpinBox)
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
from core import (natural_key, path_key, read_playlist, save_playlist,
                  save_text_playlist, text_entry, track_identity, preview_position, normalization_gain)


KO_FI_URL = 'https://ko-fi.com/murryb'

TEXTS = {
    'de': {
        'window_title': 'PARTYPICKER / Der Playlist-Generator',
        'subtitle': 'Der Playlist-Generator',
        'language': 'Sprache:',
        'new_playlist': 'Neue Playlist …', 'text_only': 'Nur TXT-Datei',
        'text_only_tip': 'Speichert eine reine Titelliste im Format Artist - Titel',
        'open_playlist': 'Playlist öffnen …', 'save_as': 'Speichern unter …',
        'open_folder': 'Musikordner öffnen …', 'recursive': 'Unterordner einbeziehen',
        'support': '🍺 Ein Bier für MurryB',
        'support_tip': 'Öffnet die Ko-fi-Unterstützerseite im Browser',
        'first_playlist': 'Zuerst eine Playlist anlegen oder öffnen.',
        'ready_listen': 'Bereit zum Durchhören',
        'wave_start': 'Ordner auswählen und loshören',
        'wave_loading': 'Waveform wird berechnet …',
        'wave_unavailable': 'Waveform nicht verfügbar',
        'wave_hint': 'Klick in die Waveform zum Springen',
        'previous': '⏮ Vorheriger', 'back_10': '−10 s', 'play': '▶ Play',
        'pause': '⏸ Pause', 'forward_10': '+10 s', 'add': '+ Playlist [Enter]',
        'next': 'Nächster ⏭', 'volume': 'Lautstärke',
        'auto_next': 'Am Titelende automatisch weiter',
        'folder_heading': 'ORDNER · Doppelklick zum Abspielen',
        'playlist_heading': 'PARTY-PLAYLIST · sofort gespeichert',
        'count': '{tracks} Titel im Ordner · {selected} ausgewählt',
        'remove': 'Aus Playlist entfernen',
        'shortcuts': 'Leertaste: Play/Pause   ·   ←/→: 10 Sekunden   ·   Strg+←/→: Titel wechseln   ·   A: aufnehmen   ·   Enter: aufnehmen & weiter',
        'ready': 'Bereit', 'playback_error': 'Wiedergabefehler: {error}',
        'not_saved': 'Nicht gespeichert. Die bisherige Playlist bleibt erhalten.\n{error}',
        'saved': 'Gespeichert: {path}', 'save_text_title': 'Titelliste speichern',
        'text_filter': 'Textdatei (*.txt)', 'save_playlist_title': 'Playlist speichern',
        'playlist_filter': 'M3U-Playlist (*.m3u);;M3U8-Playlist (*.m3u8)',
        'open_playlist_title': 'Playlist öffnen und weiterbearbeiten',
        'open_playlist_filter': 'Playlists (*.m3u *.m3u8)',
        'playlist_loaded_missing': 'Playlist geladen · {missing} nicht erreichbare Dateien',
        'playlist_loaded': 'Playlist geladen', 'playlist_location': 'Playlist: {path}',
        'already_added': 'Bereits aufgenommen – zum nächsten Titel wechseln',
        'add_tip': 'Titel speichern und zum nächsten Titel wechseln',
        'choose_folder': 'Bravo-Hits-Ordner auswählen',
        'searching': 'Suche FLAC- und MP3-Dateien …',
        'scan_skipped': 'Scan abgeschlossen · {count} nicht lesbare Ordner übersprungen',
        'no_files': 'Keine FLAC- oder MP3-Dateien in diesem Ordner gefunden.',
        'no_files_skipped': 'Keine Musikdateien gefunden · {count} nicht lesbare Ordner übersprungen',
        'saving': 'Playlist wird gespeichert …',
        'save_in_progress': 'Bitte kurz warten – die Playlist wird noch gespeichert.',
        'folder_finished': 'Ordner durchgehört. Wähle den nächsten Ordner.',
        'file_unavailable': 'Datei nicht erreichbar:\n{path}',
        'wave_error': 'Waveform: {error}',
        'local_paths_only': 'Diese App importiert lokale Dateipfade, keine Streaming-URLs.',
        'newline_unsupported': 'Zeilenumbruch im Dateinamen wird nicht unterstützt.',
    },
    'en': {
        'window_title': 'PARTYPICKER / The Playlist Generator',
        'subtitle': 'The Playlist Generator',
        'language': 'Language:',
        'new_playlist': 'New playlist …', 'text_only': 'TXT file only',
        'text_only_tip': 'Saves a plain track list in Artist - Title format',
        'open_playlist': 'Open playlist …', 'save_as': 'Save as …',
        'open_folder': 'Open music folder …', 'recursive': 'Include subfolders',
        'support': '🍺 Buy MurryB a beer',
        'support_tip': 'Opens the Ko-fi support page in your browser',
        'first_playlist': 'Create or open a playlist first.',
        'ready_listen': 'Ready to start listening',
        'wave_start': 'Select a folder and start listening',
        'wave_loading': 'Calculating waveform …',
        'wave_unavailable': 'Waveform unavailable',
        'wave_hint': 'Click the waveform to seek',
        'previous': '⏮ Previous', 'back_10': '−10 sec', 'play': '▶ Play',
        'pause': '⏸ Pause', 'forward_10': '+10 sec', 'add': '+ Playlist [Enter]',
        'next': 'Next ⏭', 'volume': 'Volume',
        'auto_next': 'Automatically continue at end of track',
        'folder_heading': 'FOLDER · Double-click to play',
        'playlist_heading': 'PARTY PLAYLIST · saved immediately',
        'count': '{tracks} tracks in folder · {selected} selected',
        'remove': 'Remove from playlist',
        'shortcuts': 'Space: Play/Pause   ·   ←/→: 10 seconds   ·   Ctrl+←/→: change track   ·   A: add   ·   Enter: add & continue',
        'ready': 'Ready', 'playback_error': 'Playback error: {error}',
        'not_saved': 'Not saved. The existing playlist has been preserved.\n{error}',
        'saved': 'Saved: {path}', 'save_text_title': 'Save track list',
        'text_filter': 'Text file (*.txt)', 'save_playlist_title': 'Save playlist',
        'playlist_filter': 'M3U playlist (*.m3u);;M3U8 playlist (*.m3u8)',
        'open_playlist_title': 'Open and edit playlist',
        'open_playlist_filter': 'Playlists (*.m3u *.m3u8)',
        'playlist_loaded_missing': 'Playlist loaded · {missing} unavailable files',
        'playlist_loaded': 'Playlist loaded', 'playlist_location': 'Playlist: {path}',
        'already_added': 'Already added – continue to the next track',
        'add_tip': 'Save track and continue to the next track',
        'choose_folder': 'Select Bravo Hits folder',
        'searching': 'Searching for FLAC and MP3 files …',
        'scan_skipped': 'Scan complete · {count} unreadable folders skipped',
        'no_files': 'No FLAC or MP3 files found in this folder.',
        'no_files_skipped': 'No music files found · {count} unreadable folders skipped',
        'saving': 'Saving playlist …',
        'save_in_progress': 'Please wait – the playlist is still being saved.',
        'folder_finished': 'Folder finished. Select the next folder.',
        'file_unavailable': 'File unavailable:\n{path}',
        'wave_error': 'Waveform: {error}',
        'local_paths_only': 'This app imports local file paths, not streaming URLs.',
        'newline_unsupported': 'Line breaks in file names are not supported.',
    },
}


KEY_PROFILES = {
    'ctrl': [('Left', -10000), ('Right', 10000)],
    'arrows': [('Ctrl+Left', -10000), ('Ctrl+Right', 10000)],
    'vertical': [('Left', -10000), ('Right', 10000)],
    'keypad': [('Left', -10000), ('Right', 10000)],
}
for language, additions in {
    'de': {'keyboard': 'Tastaturbelegung', 'profile_ctrl': 'Strg + rechts: nächster Song',
           'profile_arrows': 'Rechts: nächster Song', 'profile_vertical': 'Unten: nächster Song',
           'profile_keypad': 'Ziffernblock: 1 / 2 / 3', 'startup': 'Wie möchtest du starten?',
           'resume': 'Letzte Playlist fortsetzen', 'later': 'Später auswählen',
           'restore_folder': 'Letzten Musikordner ebenfalls öffnen',
           'choose_folder_on_resume': 'Musikordner beim Fortsetzen auswählen',
           'txt_changed': 'Die TXT-Liste wurde außerhalb der App geändert. Die gespeicherte Sitzung passt nicht mehr dazu.',
           'keys_common': 'Leertaste: Play/Pause · A: aufnehmen · Enter (auch Ziffernblock): aufnehmen & weiter',
           'keys_ctrl': '←/→: ±10 s · Strg+←/→: vorheriger/nächster Song',
           'keys_arrows': '←/→: vorheriger/nächster Song · Strg+←/→: ±10 s',
           'keys_vertical': '↑/↓: vorheriger/nächster Song · ←/→: ±10 s',
           'keys_keypad': 'Ziffernblock (Num Lock): 1: −10 s · 2: +10 s · 3: nächster Song · Strg+3: vorheriger Song'},
    'en': {'keyboard': 'Keyboard layout', 'profile_ctrl': 'Ctrl + right: next track',
           'profile_arrows': 'Right: next track', 'profile_vertical': 'Down: next track',
           'profile_keypad': 'Numeric keypad: 1 / 2 / 3', 'startup': 'How would you like to start?',
           'resume': 'Continue last playlist', 'later': 'Choose later',
           'restore_folder': 'Also open the last music folder',
           'choose_folder_on_resume': 'Choose a music folder when resuming',
           'txt_changed': 'The TXT list was changed outside the app. The saved session no longer matches it.',
           'keys_common': 'Space: Play/Pause · A: add · Enter (including keypad): add & continue',
           'keys_ctrl': 'Left/Right: ±10 s · Ctrl+Left/Right: previous/next track',
           'keys_arrows': 'Left/Right: previous/next track · Ctrl+Left/Right: ±10 s',
           'keys_vertical': 'Up/Down: previous/next track · Left/Right: ±10 s',
           'keys_keypad': 'Keypad (Num Lock): 1: −10 s · 2: +10 s · 3: next track · Ctrl+3: previous track'},
}.items():
    TEXTS[language].update(additions)


for language, additions in {'de': {'preview_start': 'Vorhören ab:', 'normalize': 'Lautstärke angleichen', 'normalize_tip': 'Gleicht die Abhörlautstärke anhand des mittleren Pegels an. Musikdateien bleiben unverändert. Sehr leise Titel sind durch den Lautstärkeregler begrenzt.', 'undo': 'Rückgängig [Strg+Z]', 'legend': 'Grau: gehört · Grün: aufgenommen · Orange: übersprungen', 'legend_tip': 'Nach 3 Sekunden Wiedergabe gilt ein Titel als gehört. Manuelles Weiter-/Zurückschalten markiert nicht aufgenommene Titel als übersprungen. Die Farben bleiben nach einem Neustart erhalten.', 'duplicate': 'Dieser Interpret und Titel ist bereits in der Playlist:\n{title}\n\nTrotzdem diese andere Datei aufnehmen?', 'add_anyway': 'Trotzdem aufnehmen', 'skip_duplicate': 'Nicht aufnehmen', 'checking_track': 'Prüfe Titel und Playlist …', 'retry': 'Erneut versuchen', 'skip_file': 'Titel überspringen', 'unavailable_detail': 'Der Titel konnte nicht geladen werden. Prüfe die Verbindung zum Laufwerk/NAS.\n\n{path}\n\n{error}', 'history_reset': 'Markierungen zurücksetzen', 'history_confirm': 'Markierungen für den aktuellen Ordner zurücksetzen? Aufgenommene Titel bleiben grün.', 'undo_done': 'Letzte Playlist-Änderung rückgängig gemacht'}, 'en': {'preview_start': 'Preview from:', 'normalize': 'Match listening volume', 'normalize_tip': 'Matches listening volume using average level. Music files are unchanged. Very quiet tracks are limited by the volume slider.', 'undo': 'Undo [Ctrl+Z]', 'legend': 'Grey: heard · Green: added · Orange: skipped', 'legend_tip': 'A track is heard after 3 seconds of playback. Manually moving to another track marks unselected tracks as skipped. Colours persist across restarts.', 'duplicate': 'This artist and title is already in your playlist:\n{title}\n\nAdd this different file anyway?', 'add_anyway': 'Add anyway', 'skip_duplicate': 'Do not add', 'checking_track': 'Checking track and playlist …', 'retry': 'Retry', 'skip_file': 'Skip track', 'unavailable_detail': 'The track could not be loaded. Check your drive/NAS connection.\n\n{path}\n\n{error}', 'history_reset': 'Reset markings', 'history_confirm': 'Reset markings for the current folder? Selected tracks remain green.', 'undo_done': 'Last playlist change undone'}}.items():
    TEXTS[language].update(additions)


def resource_path(name):
    """Resolve bundled assets both from source and a PyInstaller one-file EXE."""
    base = Path(getattr(sys, '_MEIPASS', Path(__file__).resolve().parent))
    return base / name


APP_VERSION = resource_path('VERSION').read_text(encoding='utf-8').strip()


class Scan(QThread):
    result = Signal(object, str, int)
    def __init__(self, root, recursive, parent):
        super().__init__(parent)
        self.root, self.recursive = root, recursive
    def run(self):
        try:
            files = []
            errors = []
            root_seen = False

            def skip(error):
                errors.append(error)

            for root, dirs, names in os.walk(self.root, onerror=skip):
                if self.isInterruptionRequested():
                    return
                if os.path.normcase(os.path.normpath(root)) == os.path.normcase(os.path.normpath(self.root)):
                    root_seen = True
                files.extend(
                    Path(root) / n for n in names
                    if Path(n).suffix.lower() in ('.flac', '.mp3')
                )
                if not self.recursive:
                    dirs.clear()
            if not root_seen and errors:
                self.result.emit([], str(errors[0]), 0)
                return
            self.result.emit(sorted(files, key=natural_key), '', len(errors))
        except Exception as exc:
            self.result.emit([], str(exc), 0)


class Save(QThread):
    result = Signal(object, object, object, str)
    def __init__(self, target, entries, text_cache, parent):
        super().__init__(parent)
        self.target = Path(target)
        self.entries = list(entries)
        self.text_cache = dict(text_cache)

    def run(self):
        updates = {}
        try:
            if self.target.suffix.lower() == '.txt':
                labels = dict(self.text_cache)
                for path in self.entries:
                    key = path_key(path)
                    if key not in labels:
                        labels[key] = text_entry(path)
                        updates[key] = labels[key]
                save_text_playlist(self.target, self.entries, labels)
            else:
                save_playlist(self.target, self.entries)
            self.result.emit(self.target, self.entries, updates, '')
        except Exception as exc:
            self.result.emit(self.target, self.entries, updates, str(exc))


class CheckFiles(QThread):
    result = Signal(object, object)
    def __init__(self, entries, parent):
        super().__init__(parent)
        self.entries = list(entries)

    def run(self):
        states = []
        for path in self.entries:
            if self.isInterruptionRequested():
                return
            states.append(path.is_file())
        self.result.emit(self.entries, states)



class Probe(QThread):
    result = Signal(int, object, object, str)
    def __init__(self, token, path, parent):
        super().__init__(parent)
        self.token, self.path = token, path
    def run(self):
        try:
            if not self.path.is_file():
                raise FileNotFoundError(str(self.path))
            identity = track_identity(self.path)
            self.result.emit(self.token, self.path, identity, '')
        except Exception as exc:
            self.result.emit(self.token, self.path, None, str(exc))


class Duplicates(QThread):
    result = Signal(object, object, object, bool, object)
    def __init__(self, path, entries, cache, advance, parent):
        super().__init__(parent)
        self.path, self.entries, self.cache, self.advance = path, list(entries), dict(cache), advance
    def run(self):
        updates, duplicate = {}, None
        for path in [self.path, *self.entries]:
            if self.isInterruptionRequested():
                return
            key = path_key(path)
            if key not in self.cache:
                self.cache[key] = track_identity(path)
                updates[key] = self.cache[key]
        identity = self.cache[path_key(self.path)]
        if identity:
            duplicate = next((p for p in self.entries if self.cache[path_key(p)] == identity), None)
        self.result.emit(self.path, self.entries, duplicate, self.advance, updates)


class Analyze(QThread):
    result = Signal(int, str, object, str, float, str)
    def __init__(self, token, path, parent):
        super().__init__(parent)
        self.token, self.path = token, path
    def run(self):
        try:
            square_sum, samples, peak = 0.0, 0, 0.0
            with sf.SoundFile(str(self.path)) as audio:
                block = max(1, int(np.ceil(len(audio) / 1600)))
                peaks = []
                for data in audio.blocks(blocksize=block, dtype='float32', always_2d=True):
                    if self.isInterruptionRequested():
                        return
                    block_peak = float(np.abs(data).max())
                    peaks.append(block_peak)
                    peak = max(peak, block_peak)
                    square_sum += float(np.sum(np.square(data, dtype=np.float64)))
                    samples += data.size
            title = self.path.stem
            try:
                tags = TinyTag.get(self.path)
                title = ' – '.join(filter(None, [tags.artist, tags.title])) or title
            except Exception:
                pass
            rms = (square_sum / samples) ** .5 if samples else 0
            self.result.emit(self.token, str(self.path), peaks, title, normalization_gain(rms, peak), '')
        except Exception as exc:
            self.result.emit(self.token, str(self.path), [], self.path.stem, 1.0, str(exc))


class Waveform(QWidget):
    seek = Signal(float)
    def __init__(self, message):
        super().__init__()
        self.peaks, self.fraction, self.message = [], 0, message
        self.setFixedHeight(128)
        self.setCursor(Qt.PointingHandCursor)
    def paintEvent(self, event):
        p = QPainter(self)
        p.fillRect(self.rect(), QColor('#101827'))
        w, h = self.width(), self.height()
        if not self.peaks:
            p.setPen(QColor('#a8b9cc'))
            p.drawText(self.rect(), Qt.AlignCenter, self.message)
        else:
            for x in range(w):
                start = int(x * len(self.peaks) / w)
                end = max(start + 1, int((x + 1) * len(self.peaks) / w))
                amplitude = max(self.peaks[start:end], default=0) * (h * .43)
                p.setPen(QColor('#36dab5' if x < self.fraction * w else '#577b9a'))
                p.drawLine(x, int(h / 2 - amplitude), x, int(h / 2 + amplitude))
        p.setPen(QPen(QColor('#ffffff'), 2))
        p.drawLine(int(self.fraction * w), 0, int(self.fraction * w), h)
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.seek.emit(max(0, min(1, event.position().x() / max(1, self.width()))))
    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.LeftButton:
            self.seek.emit(max(0, min(1, event.position().x() / max(1, self.width()))))


class Window(QMainWindow):
    def __init__(self):
        super().__init__()
        self.settings = QSettings('MurryB', 'PartyPicker')
        self.lang = self.settings.value('language', 'de')
        if self.lang not in TEXTS:
            self.lang = 'de'
        self.setWindowTitle(self.t('window_title'))
        self.resize(1180, 780)
        self.tracks, self.selected, self.jobs = [], [], []
        self.selected_keys, self.text_cache, self.availability = set(), {}, {}
        self.index, self.playlist, self.analyzer = -1, None, None
        self.save_job, self.pending_save = None, None
        self.audio = QAudioOutput(self)
        self.user_volume, self.track_gain = .65, 1.0
        self.audio.setVolume(self.user_volume)
        self.play_token, self.pending_seek = 0, None
        self.duplicate_job = None
        self.identity_cache, self.undo_stack, self.source_rows = {}, [], {}
        self.error_pending = None
        self.listened_ms, self.last_position = 0, 0
        try:
            self.history = json.loads(self.settings.value('track_history', '{}'))
            if not isinstance(self.history, dict):
                self.history = {}
        except (TypeError, ValueError):
            self.history = {}
        self.history_dirty = False
        self.history_timer = QTimer(self)
        self.history_timer.setInterval(1500)
        self.history_timer.timeout.connect(self.flush_history)
        self.history_timer.start()
        self.player = QMediaPlayer(self)
        self.player.setAudioOutput(self.audio)
        self.player.positionChanged.connect(self.position)
        self.player.durationChanged.connect(self.duration_ready)
        self.player.seekableChanged.connect(lambda _: self.apply_preview_start())
        self.player.playbackStateChanged.connect(self.state)
        self.player.mediaStatusChanged.connect(self.media_status)
        self.player.errorOccurred.connect(self.playback_failed)
        root = QWidget()
        self.setCentralWidget(root)
        layout = QVBoxLayout(root)
        body = QSplitter(Qt.Horizontal)
        player_pane = QWidget()
        player_layout = QVBoxLayout(player_pane)
        player_layout.setContentsMargins(0, 0, 12, 0)
        body.addWidget(player_pane)
        head_row = QHBoxLayout()
        head_row.setSpacing(12)
        self.logo = QLabel()
        self.logo.setFixedSize(80, 80)
        self.logo.setAlignment(Qt.AlignCenter)
        logo_pixmap = QPixmap(str(resource_path('PartyPicker-icon.png')))
        scaled_logo = logo_pixmap.scaled(160, 160, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        scaled_logo.setDevicePixelRatio(2)
        self.logo.setPixmap(scaled_logo)
        self.logo.setAccessibleName('PartyPicker')
        head_row.addWidget(self.logo)
        branding = QVBoxLayout()
        branding.setSpacing(2)
        title_row = QHBoxLayout()
        title_row.setSpacing(8)
        self.head = QLabel('PARTYPICKER')
        self.head.setWordWrap(False)
        self.head.setStyleSheet('font-size:22px; font-weight:bold;')
        self.version_label = QLabel(f'Version {APP_VERSION}')
        self.version_label.setStyleSheet('font-size:10px; color:#8fa4b8;')
        title_row.addWidget(self.head)
        title_row.addWidget(self.version_label, 0, Qt.AlignBottom)
        title_row.addStretch()
        credit = QLabel('by MurryB')
        credit.setStyleSheet('font-size:11px; color:#8fa4b8;')
        self.subtitle = QLabel(self.t('subtitle'))
        self.subtitle.setStyleSheet('font-size:15px;')
        branding.addLayout(title_row)
        branding.addWidget(self.subtitle)
        branding.addWidget(credit)
        head_row.addLayout(branding, 1)
        self.language_label = QLabel(self.t('language'))
        head_row.addWidget(self.language_label)
        self.language_box = QComboBox()
        self.language_box.addItem('Deutsch', 'de')
        self.language_box.addItem('English', 'en')
        self.language_box.setCurrentIndex(0 if self.lang == 'de' else 1)
        self.language_box.currentIndexChanged.connect(self.change_language)
        head_row.addWidget(self.language_box)
        player_layout.addLayout(head_row)
        row = QHBoxLayout()
        new_options = QVBoxLayout()
        new_options.setSpacing(2)
        self.new_button = self.button(new_options, self.t('new_playlist'), self.new_playlist)
        self.text_only = QCheckBox(self.t('text_only'))
        self.text_only.setChecked(False)
        self.text_only.setToolTip(self.t('text_only_tip'))
        new_options.addWidget(self.text_only, 0, Qt.AlignHCenter)
        row.addLayout(new_options)
        self.open_playlist_button = self.button(row, self.t('open_playlist'), self.open_playlist)
        self.save_as_button = self.button(row, self.t('save_as'), self.save_as)
        toolbar_buttons = [self.open_playlist_button, self.save_as_button]
        folder_options = QVBoxLayout()
        folder_options.setSpacing(2)
        self.folder_button = self.button(folder_options, self.t('open_folder'), self.open_folder)
        self.recursive = QCheckBox(self.t('recursive'))
        self.recursive.setChecked(self.settings.value('last_music_recursive', True, type=bool))
        folder_options.addWidget(self.recursive, 0, Qt.AlignHCenter)
        row.addLayout(folder_options)
        for toolbar_button in [self.new_button, *toolbar_buttons]:
            row.setAlignment(toolbar_button, Qt.AlignTop)
        row.addStretch()
        player_layout.addLayout(row)
        self.location = QLabel(self.t('first_playlist'))
        self.location.setWordWrap(True)
        player_layout.addWidget(self.location)
        self.title = QLabel(self.t('ready_listen'))
        self.title.setStyleSheet('font-size:25px; font-weight:bold; padding-top:15px;')
        self.title.setWordWrap(True)
        player_layout.addWidget(self.title)
        self.file_label = QLabel('')
        self.file_label.setWordWrap(True)
        player_layout.addWidget(self.file_label)
        self.wave = Waveform(self.t('wave_start'))
        self.wave_message_key = 'wave_start'
        self.wave.seek.connect(self.seek)
        player_layout.addWidget(self.wave)
        self.clock = QLabel('0:00 / 0:00   ·   ' + self.t('wave_hint'))
        player_layout.addWidget(self.clock)
        controls = QHBoxLayout()
        self.previous_button = self.button(controls, self.t('previous'), lambda: self.step(-1))
        self.back_button = self.button(controls, self.t('back_10'), lambda: self.jump(-10000))
        self.play_button = self.button(controls, self.t('play'), self.toggle)
        self.forward_button = self.button(controls, self.t('forward_10'), lambda: self.jump(10000))
        self.add_button = self.button(controls, self.t('add'), lambda: self.add(True))
        self.add_button.setStyleSheet('background:#136b5c; font-weight:bold;')
        self.next_button = self.button(controls, self.t('next'), lambda: self.step(1))
        player_layout.addLayout(controls)
        options = QHBoxLayout()
        self.volume_label = QLabel(self.t('volume'))
        options.addWidget(self.volume_label)
        volume = QSlider(Qt.Horizontal)
        volume.setRange(0, 100)
        volume.setValue(65)
        volume.setMaximumWidth(130)
        volume.valueChanged.connect(self.volume_changed)
        options.addWidget(volume)
        options.addStretch()
        self.auto = QCheckBox(self.t('auto_next'))
        self.auto.setChecked(True)
        options.addWidget(self.auto)
        player_layout.addLayout(options)
        audition = QHBoxLayout()
        self.preview_label = QLabel(self.t('preview_start'))
        audition.addWidget(self.preview_label)
        self.preview_seconds = QSpinBox()
        self.preview_seconds.setRange(0, 600)
        self.preview_seconds.setSuffix(' s')
        self.preview_seconds.setValue(self.settings.value('preview_seconds', 0, type=int))
        self.preview_seconds.valueChanged.connect(lambda v: self.settings.setValue('preview_seconds', v))
        audition.addWidget(self.preview_seconds)
        self.normalize = QCheckBox(self.t('normalize'))
        self.normalize.setChecked(self.settings.value('normalize', False, type=bool))
        self.normalize.setToolTip(self.t('normalize_tip'))
        self.normalize.toggled.connect(self.normalization_changed)
        audition.addWidget(self.normalize)
        audition.addStretch()
        player_layout.addLayout(audition)
        player_layout.addStretch(1)
        sidebar = QWidget()
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(0, 0, 0, 0)
        splitter = QSplitter(Qt.Vertical)
        self.sources, self.picks = QListWidget(), QListWidget()
        self.sources.itemDoubleClicked.connect(lambda item: self.play_track(self.sources.row(item)))
        self.picks.itemDoubleClicked.connect(self.preview_pick)
        self.pane_labels = []
        for label, widget in [(self.t('folder_heading'), self.sources), (self.t('playlist_heading'), self.picks)]:
            pane = QWidget()
            box = QVBoxLayout(pane)
            pane_label = QLabel(label)
            self.pane_labels.append(pane_label)
            box.addWidget(pane_label)
            if widget is self.sources:
                self.legend = QLabel(self.t('legend'))
                self.legend.setStyleSheet('font-size:11px; color:#a9b7c6;')
                self.legend.setToolTip(self.t('legend_tip'))
                box.addWidget(self.legend)
                self.reset_history_button = QPushButton(self.t('history_reset'))
                self.reset_history_button.clicked.connect(self.reset_history)
                box.addWidget(self.reset_history_button)
            box.addWidget(widget)
            splitter.addWidget(pane)
        sidebar_layout.addWidget(splitter, 1)
        playlist_controls = QGridLayout()
        playlist_controls.setContentsMargins(9, 0, 9, 0)
        playlist_controls.setHorizontalSpacing(6)
        playlist_controls.setVerticalSpacing(6)
        playlist_controls.setColumnStretch(0, 1)
        self.count = QLabel(self.t('count', tracks=0, selected=0))
        playlist_controls.addWidget(self.count, 0, 0, Qt.AlignLeft | Qt.AlignTop)
        self.up_button = QPushButton('↑')
        self.up_button.clicked.connect(lambda checked=False: self.move_pick(-1))
        playlist_controls.addWidget(self.up_button, 0, 1)
        self.down_button = QPushButton('↓')
        self.down_button.clicked.connect(lambda checked=False: self.move_pick(1))
        playlist_controls.addWidget(self.down_button, 0, 2)
        self.remove_button = QPushButton(self.t('remove'))
        self.remove_button.clicked.connect(lambda checked=False: self.remove_pick())
        playlist_controls.addWidget(self.remove_button, 0, 3)
        self.support_button = QPushButton(self.t('support'))
        self.support_button.clicked.connect(lambda checked=False: self.open_support())
        self.support_button.setToolTip(self.t('support_tip'))
        self.support_button.setStyleSheet('background:#7a4a16; font-weight:bold;')
        playlist_controls.addWidget(self.support_button, 1, 3)
        self.undo_button = QPushButton(self.t('undo'))
        self.undo_button.clicked.connect(self.undo)
        self.undo_button.setEnabled(False)
        playlist_controls.addWidget(self.undo_button, 1, 0, 1, 3)
        sidebar_layout.addLayout(playlist_controls)
        body.addWidget(sidebar)
        body.setStretchFactor(0, 3)
        body.setStretchFactor(1, 2)
        body.setSizes([650, 500])
        layout.addWidget(body, 1)
        keyboard_row = QHBoxLayout()
        self.keyboard_label = QLabel(self.t('keyboard'))
        self.keyboard_box = QComboBox()
        for profile in KEY_PROFILES:
            self.keyboard_box.addItem(self.t('profile_' + profile), profile)
        saved_profile = self.settings.value('keyboard_profile', 'ctrl')
        self.keyboard_box.setCurrentIndex(max(0, self.keyboard_box.findData(saved_profile)))
        keyboard_row.addWidget(self.keyboard_label)
        keyboard_row.addWidget(self.keyboard_box)
        keyboard_row.addStretch()
        layout.addLayout(keyboard_row)
        self.shortcuts_label = QLabel()
        self.shortcuts_label.setWordWrap(True)
        layout.addWidget(self.shortcuts_label)
        self.keyboard_shortcuts = []
        self.keyboard_box.currentIndexChanged.connect(self.configure_keyboard)
        self.configure_keyboard()
        self.statusBar().showMessage(self.t('ready'))

    def t(self, key, **values):
        return TEXTS[self.lang][key].format(**values)

    def update_keyboard_hint(self):
        profile = self.keyboard_box.currentData()
        self.shortcuts_label.setText(self.t('keys_' + profile) + '\n' + self.t('keys_common'))

    def configure_keyboard(self):
        for shortcut in self.keyboard_shortcuts:
            shortcut.setEnabled(False)
            shortcut.deleteLater()
        self.keyboard_shortcuts.clear()
        profile = self.keyboard_box.currentData()
        self.settings.setValue('keyboard_profile', profile)
        bindings = [('Space', self.toggle), ('A', self.add), ('Ctrl+Z', self.undo),
                    ('Return', lambda: self.add(True)), ('Enter', lambda: self.add(True))]
        bindings += [(key, lambda offset=offset: self.jump(offset))
                     for key, offset in KEY_PROFILES[profile]]
        previous, next_key = ('Left', 'Right') if profile == 'arrows' else ('Ctrl+Left', 'Ctrl+Right')
        bindings += [(previous, lambda: self.step(-1)), (next_key, lambda: self.step(1))]
        if profile == 'vertical':
            bindings += [('Up', lambda: self.step(-1)), ('Down', lambda: self.step(1))]
        if profile == 'keypad':
            bindings += [(QKeySequence(Qt.KeypadModifier | Qt.Key_1), lambda: self.jump(-10000)),
                         (QKeySequence(Qt.KeypadModifier | Qt.Key_2), lambda: self.jump(10000)),
                         (QKeySequence(Qt.KeypadModifier | Qt.Key_3), lambda: self.step(1)),
                         ('Ctrl+3', lambda: self.step(-1)),
                         (QKeySequence(Qt.ControlModifier | Qt.KeypadModifier | Qt.Key_3),
                          lambda: self.step(-1))]
        for key, callback in bindings:
            shortcut = QShortcut(key if isinstance(key, QKeySequence) else QKeySequence(key), self)
            shortcut.setAutoRepeat(False)
            shortcut.activated.connect(callback)
            self.keyboard_shortcuts.append(shortcut)
        self.update_keyboard_hint()

    def remember_playlist(self):
        session = {'path': str(self.playlist), 'entries': [str(p) for p in self.selected],
                   'labels': self.text_cache if self.playlist.suffix.lower() == '.txt' else {}}
        self.settings.setValue('last_playlist_session', json.dumps(session))
        self.settings.sync()

    def startup_choice(self):
        try:
            session = json.loads(self.settings.value('last_playlist_session', '{}'))
        except (ValueError, TypeError):
            session = {}
        dialog = QMessageBox(self)
        dialog.setWindowTitle('PartyPicker')
        dialog.setText(self.t('startup'))
        new = dialog.addButton(self.t('new_playlist'), QMessageBox.ActionRole)
        resume = dialog.addButton(self.t('resume'), QMessageBox.ActionRole)
        resume.setEnabled(bool(session.get('path')))
        dialog.addButton(self.t('later'), QMessageBox.RejectRole)
        last_folder = self.settings.value('last_music_folder', '', type=str)
        restore_folder = QCheckBox(self.t('restore_folder' if last_folder else 'choose_folder_on_resume'))
        restore_folder.setEnabled(bool(session.get('path')))
        checkmark = resource_path('checkmark.png').as_posix()
        restore_folder.setStyleSheet(
            'QCheckBox::indicator { width:18px; height:18px; border:1px solid #8592a1; '
            'border-radius:3px; background:#d9dfe5; } '
            f'QCheckBox::indicator:checked {{ background:#218f7d; image:url("{checkmark}"); }}')
        dialog.setCheckBox(restore_folder)
        if session.get('path'):
            dialog.setInformativeText(session['path'])
        dialog.exec()
        if dialog.clickedButton() is new:
            self.new_playlist()
        elif dialog.clickedButton() is resume:
            if self.load_playlist(session['path'], session) and restore_folder.isChecked():
                if last_folder:
                    self.scan_folder(last_folder, resume_last_track=True)
                else:
                    self.open_folder(resume_last_track=True)

    def change_language(self):
        self.lang = self.language_box.currentData()
        self.settings.setValue('language', self.lang)
        self.retranslate_ui()

    def retranslate_ui(self):
        self.setWindowTitle(self.t('window_title'))
        self.subtitle.setText(self.t('subtitle'))
        self.language_label.setText(self.t('language'))
        self.support_button.setText(self.t('support'))
        self.support_button.setToolTip(self.t('support_tip'))
        self.new_button.setText(self.t('new_playlist'))
        self.text_only.setText(self.t('text_only'))
        self.text_only.setToolTip(self.t('text_only_tip'))
        self.open_playlist_button.setText(self.t('open_playlist'))
        self.save_as_button.setText(self.t('save_as'))
        self.folder_button.setText(self.t('open_folder'))
        self.recursive.setText(self.t('recursive'))
        self.previous_button.setText(self.t('previous'))
        self.back_button.setText(self.t('back_10'))
        self.forward_button.setText(self.t('forward_10'))
        self.add_button.setText(self.t('add'))
        self.next_button.setText(self.t('next'))
        self.volume_label.setText(self.t('volume'))
        self.auto.setText(self.t('auto_next'))
        self.pane_labels[0].setText(self.t('folder_heading'))
        self.pane_labels[1].setText(self.t('playlist_heading'))
        self.remove_button.setText(self.t('remove'))
        self.undo_button.setText(self.t('undo'))
        self.preview_label.setText(self.t('preview_start'))
        self.normalize.setText(self.t('normalize'))
        self.normalize.setToolTip(self.t('normalize_tip'))
        self.legend.setText(self.t('legend'))
        self.legend.setToolTip(self.t('legend_tip'))
        self.reset_history_button.setText(self.t('history_reset'))
        self.keyboard_label.setText(self.t('keyboard'))
        for index, profile in enumerate(KEY_PROFILES):
            self.keyboard_box.setItemText(index, self.t('profile_' + profile))
        self.update_keyboard_hint()
        playing = self.player.playbackState() == QMediaPlayer.PlayingState
        self.play_button.setText(self.t('pause') if playing else self.t('play'))
        if self.playlist is None:
            self.location.setText(self.t('first_playlist'))
        else:
            self.location.setText(self.t('playlist_location', path=self.playlist))
        if self.current_path() is None:
            self.title.setText(self.t('ready_listen'))
        if self.wave_message_key:
            self.wave.message = self.t(self.wave_message_key)
        self.position(self.player.position())
        self.refresh_count()
        self.update_add()
        self.wave.update()
        self.statusBar().showMessage(self.t('ready'))

    def open_support(self):
        QDesktopServices.openUrl(QUrl(KO_FI_URL))

    def button(self, row, text, callback):
        button = QPushButton(text)
        button.clicked.connect(lambda checked=False: callback())
        row.addWidget(button)
        return button

    def error(self, message):
        QMessageBox.warning(self, 'PartyPicker', str(message))

    def set_save_busy(self, busy):
        for widget in (self.new_button, self.open_playlist_button, self.save_as_button,
                       self.text_only, self.add_button, self.up_button,
                       self.down_button, self.remove_button, self.undo_button):
            widget.setEnabled(not busy)
        self.undo_button.setEnabled(not busy and bool(self.undo_stack))

    def commit(self, entries, target=None, ui_change=None, on_success=None, record_undo=True):
        target = target or self.playlist
        if target is None:
            return False
        if self.duplicate_job or (self.save_job and self.save_job.isRunning()):
            self.statusBar().showMessage(self.t('save_in_progress'))
            return False
        entries = list(entries)
        same_target = self.playlist is not None and path_key(target) == path_key(self.playlist)
        snapshot = list(self.selected) if same_target and entries != self.selected and record_undo else None
        self.pending_save = (ui_change, on_success, snapshot, same_target)
        self.save_job = Save(target, entries, self.text_cache, self)
        self.save_job.result.connect(self.saved)
        self.set_save_busy(True)
        self.statusBar().showMessage(self.t('saving'))
        self.launch(self.save_job)
        return True

    def saved(self, target, entries, cache_updates, error):
        ui_change, on_success, snapshot, same_target = self.pending_save or (None, None, None, True)
        self.pending_save = None
        self.save_job = None
        self.text_cache.update(cache_updates)
        self.set_save_busy(False)
        if error:
            self.error(self.t('not_saved', error=self.translate_core_error(error)))
            return
        if not same_target:
            self.undo_stack.clear()
        elif snapshot is not None:
            self.undo_stack.append(snapshot)
            self.undo_stack = self.undo_stack[-20:]
        self.playlist, self.selected = Path(target), list(entries)
        self.selected_keys = {path_key(path) for path in self.selected}
        self.apply_playlist_change(ui_change)
        self.update_source_colors()
        self.undo_button.setEnabled(bool(self.undo_stack))
        self.remember_playlist()
        self.statusBar().showMessage(self.t('saved', path=self.playlist))
        if on_success:
            on_success()

    def apply_playlist_change(self, change):
        if not change or change[0] == 'full':
            self.refresh()
            return
        action = change[0]
        if action == 'clear':
            self.picks.clear()
        elif action == 'append':
            self.add_pick_item(change[1])
            self.show_latest_pick()
        elif action == 'remove':
            self.picks.takeItem(change[1])
        elif action == 'move':
            row, target = change[1], change[2]
            item = self.picks.takeItem(row)
            self.picks.insertItem(target, item)
            self.picks.setCurrentRow(target)
        self.location.setText(self.t('playlist_location', path=self.playlist))
        self.refresh_count()
        self.update_add()

    def choose_target(self):
        if self.text_only.isChecked():
            current = self.playlist.with_suffix('.txt') if self.playlist else Path.home() / 'Party.txt'
            name, _ = QFileDialog.getSaveFileName(
                self, self.t('save_text_title'), str(current), self.t('text_filter'))
            if name and Path(name).suffix.lower() != '.txt':
                name += '.txt'
        else:
            current = self.playlist if self.playlist and self.playlist.suffix.lower() in ('.m3u', '.m3u8') else Path.home() / 'Party.m3u'
            name, _ = QFileDialog.getSaveFileName(
                self, self.t('save_playlist_title'), str(current), self.t('playlist_filter'))
            if name and Path(name).suffix.lower() not in ('.m3u', '.m3u8'):
                name += '.m3u'
        return Path(name) if name else None

    def new_playlist(self, on_success=None):
        target = self.choose_target()
        if target:
            self.commit([], target, ('clear',), on_success)

    def save_as(self):
        target = self.choose_target()
        if target:
            self.commit(self.selected, target, ('unchanged',))

    def open_playlist(self):
        name, _ = QFileDialog.getOpenFileName(
            self, self.t('open_playlist_title'), '', self.t('open_playlist_filter'))
        if not name:
            return
        self.load_playlist(name)

    def load_playlist(self, name, session=None):
        try:
            if Path(name).suffix.lower() == '.txt':
                session = session or {}
                entries = [Path(p) for p in session.get('entries', [])]
                labels = session.get('labels', {})
                expected = [labels[path_key(p)].replace('\r', ' ').replace('\n', ' ') for p in entries]
                if Path(name).read_text(encoding='utf-8-sig').splitlines() != (expected or ['']):
                    raise ValueError(self.t('txt_changed'))
                self.text_cache.update(labels)
            else:
                entries = read_playlist(name)
        except Exception as exc:
            self.error(self.translate_core_error(str(exc)))
            return False
        self.undo_stack.clear()
        self.undo_button.setEnabled(False)
        self.playlist, self.selected = Path(name), entries
        self.selected_keys = {path_key(path) for path in entries}
        self.text_only.setChecked(Path(name).suffix.lower() == '.txt')
        self.remember_playlist()
        self.refresh()
        self.show_latest_pick()
        self.statusBar().showMessage(self.t('playlist_loaded'))
        self.check_files(entries)
        return True

    def add_pick_item(self, path):
        missing = self.availability.get(path_key(path)) is False
        self.picks.addItem(('⚠ ' if missing else '') + path.stem)
        self.picks.item(self.picks.count() - 1).setToolTip(str(path))

    def refresh(self):
        self.picks.clear()
        for p in self.selected:
            self.add_pick_item(p)
        self.location.setText(self.t('playlist_location', path=self.playlist))
        self.refresh_count()
        self.update_add()
        self.update_source_colors()

    def check_files(self, entries):
        if not entries:
            return
        checker = CheckFiles(entries, self)
        checker.result.connect(self.files_checked)
        self.launch(checker)

    def files_checked(self, entries, states):
        if [path_key(p) for p in entries] != [path_key(p) for p in self.selected]:
            return
        for row, (path, available) in enumerate(zip(entries, states)):
            self.availability[path_key(path)] = available
            item = self.picks.item(row)
            if item:
                item.setText(('' if available else '⚠ ') + path.stem)
        missing = states.count(False)
        self.statusBar().showMessage(
            self.t('playlist_loaded_missing', missing=missing)
            if missing else self.t('playlist_loaded'))

    def refresh_count(self):
        self.count.setText(self.t('count', tracks=len(self.tracks), selected=len(self.selected)))

    def update_add(self):
        current = self.current_path()
        self.add_button.setToolTip(
            self.t('already_added')
            if current is not None and path_key(current) in self.selected_keys
            else self.t('add_tip'))

    def translate_core_error(self, message):
        replacements = {
            'Diese App importiert lokale Dateipfade, keine Streaming-URLs.': self.t('local_paths_only'),
            'Zeilenumbruch im Dateinamen wird nicht unterstützt.': self.t('newline_unsupported'),
        }
        return replacements.get(message, message)

    def show_latest_pick(self):
        """Select and reveal the most recently appended playlist entry."""
        if self.picks.count():
            last_row = self.picks.count() - 1
            self.picks.setCurrentRow(last_row)
            self.picks.scrollToItem(self.picks.item(last_row))

    def current_path(self):
        url = self.player.source()
        return Path(url.toLocalFile()) if url.isLocalFile() else None

    def launch(self, job):
        self.jobs.append(job)
        job.finished.connect(self.job_finished)
        job.start()

    @Slot()
    def job_finished(self):
        """Clear references on the GUI thread before deleting a finished worker."""
        job = self.sender()
        if self.analyzer is job:
            self.analyzer = None
        if self.duplicate_job is job:
            self.duplicate_job = None
            self.set_save_busy(self.save_job is not None)
        if self.save_job is job:
            self.save_job = None
        if job in self.jobs:
            self.jobs.remove(job)
        job.deleteLater()

    def open_folder(self, resume_last_track=False):
        if self.playlist is None:
            self.new_playlist(lambda: self.open_folder(resume_last_track))
            return
        folder = QFileDialog.getExistingDirectory(
            self, self.t('choose_folder'), self.settings.value('last_music_folder', '', type=str))
        if not folder:
            return
        self.scan_folder(folder, resume_last_track=resume_last_track)

    def scan_folder(self, folder, resume_last_track=False):
        last_track = self.settings.value('last_music_track', '', type=str) if resume_last_track else ''
        self.settings.setValue('last_music_folder', folder)
        self.settings.setValue('last_music_recursive', self.recursive.isChecked())
        self.settings.sync()
        self.folder_button.setEnabled(False)
        self.statusBar().showMessage(self.t('searching'))
        scan = Scan(folder, self.recursive.isChecked(), self)
        scan.result.connect(lambda files, error, skipped: self.scanned(files, error, skipped, last_track))
        self.launch(scan)

    def scanned(self, files, error, skipped, last_track=''):
        self.folder_button.setEnabled(True)
        if error:
            self.error(error)
            return
        if not files:
            self.statusBar().showMessage(
                self.t('no_files_skipped', count=skipped) if skipped else self.t('no_files'))
            return
        self.tracks = files
        self.source_rows = {path_key(p): i for i, p in enumerate(files)}
        self.sources.clear()
        for p in files:
            self.sources.addItem(p.parent.name + ' / ' + p.name)
            self.sources.item(self.sources.count()-1).setToolTip(str(p))
        self.update_source_colors()
        self.refresh_count()
        if skipped:
            self.statusBar().showMessage(self.t('scan_skipped', count=skipped))
        last_key = path_key(Path(last_track)) if last_track else None
        start_index = next((i for i, path in enumerate(files) if path_key(path) == last_key), 0)
        self.play_track(start_index)

    def play_track(self, index):
        if 0 <= index < len(self.tracks):
            self.index = index
            self.sources.setCurrentRow(index)
            self.play_path(self.tracks[index], folder_track=True)
        elif index >= len(self.tracks) and self.tracks:
            self.player.stop()
            self.statusBar().showMessage(self.t('folder_finished'))

    def play_path(self, path, folder_track=False):
        if self.analyzer and self.analyzer.isRunning():
            self.analyzer.requestInterruption()
        self.play_token += 1
        self.error_pending = None
        self.player.stop()
        self.player.setSource(QUrl())
        self.listened_ms, self.last_position = 0, 0
        self.pending_seek = None
        self.track_gain = 1.0
        self.apply_volume()
        self.title.setText(path.stem)
        self.file_label.setText(str(path))
        self.wave.peaks, self.wave.fraction = [], 0
        self.wave_message_key = 'wave_loading'
        self.wave.message = self.t(self.wave_message_key)
        self.wave.update()
        self.requested_path, self.requested_folder_track = Path(path), folder_track
        probe = Probe(self.play_token, Path(path), self)
        probe.result.connect(self.probed)
        self.launch(probe)
        self.update_add()

    @Slot(int, object, object, str)
    def probed(self, token, path, identity, error):
        if token != self.play_token:
            return
        if error:
            self.schedule_playback_error(token, path, error)
            return
        self.identity_cache[path_key(path)] = identity
        if self.requested_folder_track:
            self.settings.setValue('last_music_track', str(path))
        self.pending_seek = self.preview_seconds.value() * 1000
        self.player.setSource(QUrl.fromLocalFile(str(path)))
        self.player.play()
        self.analyzer = Analyze(token, path, self)
        self.analyzer.result.connect(self.analyzed)
        self.launch(self.analyzer)
        self.update_add()

    @Slot(int, str, object, str, float, str)
    def analyzed(self, token, path, peaks, title, gain, error):
        if token != self.play_token or str(self.current_path()) != path:
            return
        self.title.setText(title)
        self.track_gain = gain
        self.apply_volume()
        self.wave.peaks = peaks
        self.wave_message_key = 'wave_unavailable' if error else ''
        self.wave.message = self.t(self.wave_message_key) if self.wave_message_key else ''
        self.wave.update()
        if error:
            self.statusBar().showMessage(self.t('wave_error', error=error))

    def duration_ready(self, duration):
        self.apply_preview_start()
        self.position(self.player.position())

    def apply_preview_start(self):
        if self.pending_seek is not None and self.player.isSeekable() and self.player.duration() > 0:
            target = preview_position(self.pending_seek, self.player.duration())
            self.pending_seek = None
            self.last_position = target
            self.player.setPosition(target)

    def volume_changed(self, value):
        self.user_volume = value / 100
        self.apply_volume()

    def normalization_changed(self, enabled):
        self.settings.setValue('normalize', enabled)
        self.apply_volume()

    def apply_volume(self):
        enabled = hasattr(self, 'normalize') and self.normalize.isChecked()
        self.audio.setVolume(min(1.0, self.user_volume * (self.track_gain if enabled else 1.0)))

    def playback_failed(self, *args):
        path = self.current_path()
        if path:
            self.schedule_playback_error(self.play_token, path, self.player.errorString())

    def schedule_playback_error(self, token, path, error):
        if self.error_pending == token:
            return
        self.error_pending = token
        QTimer.singleShot(0, lambda: self.show_playback_error(token, path, error))

    def show_playback_error(self, token, path, error):
        if token != self.play_token or self.error_pending != token:
            return
        dialog = QMessageBox(self)
        dialog.setWindowTitle('PartyPicker')
        dialog.setText(self.t('unavailable_detail', path=path, error=error))
        retry = dialog.addButton(self.t('retry'), QMessageBox.AcceptRole)
        skip = dialog.addButton(self.t('skip_file'), QMessageBox.ActionRole)
        dialog.addButton('Abbrechen' if self.lang == 'de' else 'Cancel', QMessageBox.RejectRole)
        dialog.exec()
        if token != self.play_token:
            return
        if dialog.clickedButton() is retry:
            self.play_path(path, self.requested_folder_track)
        elif dialog.clickedButton() is skip:
            self.mark_history(path, 'skipped')
            if self.requested_folder_track:
                self.play_track(self.index + 1)

    def preview_pick(self, item):
        self.play_path(self.selected[self.picks.row(item)])

    def add(self, advance=False):
        path = self.current_path()
        if path is None:
            return
        if self.playlist is None:
            self.new_playlist(lambda: self.add(advance))
            return
        if self.duplicate_job or self.save_job:
            return
        if path_key(path) not in self.selected_keys:
            self.duplicate_job = Duplicates(path, self.selected, self.identity_cache, advance, self)
            self.duplicate_job.result.connect(self.duplicates_checked)
            self.set_save_busy(True)
            self.statusBar().showMessage(self.t('checking_track'))
            self.launch(self.duplicate_job)
        elif advance:
            self.step(1)

    @Slot(object, object, object, bool, object)
    def duplicates_checked(self, path, entries, duplicate, advance, updates):
        self.duplicate_job = None
        self.identity_cache.update(updates)
        self.set_save_busy(self.save_job is not None)
        if entries != self.selected or self.current_path() != path or self.save_job:
            return
        if duplicate:
            dialog = QMessageBox(self)
            dialog.setWindowTitle('PartyPicker')
            dialog.setText(self.t('duplicate', title=duplicate.stem))
            yes = dialog.addButton(self.t('add_anyway'), QMessageBox.AcceptRole)
            no = dialog.addButton(self.t('skip_duplicate'), QMessageBox.RejectRole)
            dialog.setDefaultButton(no)
            dialog.exec()
            if dialog.clickedButton() is not yes:
                if advance:
                    self.step(1)
                return
        if self.current_path() != path or entries != self.selected or self.save_job:
            return
        self.commit(self.selected + [path], ui_change=('append', path),
                    on_success=(lambda: self.step(1)) if advance else None)

    def undo(self):
        if not self.undo_stack or self.save_job or self.duplicate_job:
            return
        entries = list(self.undo_stack[-1])
        def done():
            self.undo_stack.pop()
            self.undo_button.setEnabled(bool(self.undo_stack))
            self.show_latest_pick()
            self.statusBar().showMessage(self.t('undo_done'))
        self.commit(entries, ui_change=('full',), on_success=done, record_undo=False)

    def mark_history(self, path, status):
        key = path_key(path)
        if self.history.get(key) != status:
            self.history[key] = status
            self.history_dirty = True
            self.update_source_colors(key)

    def flush_history(self):
        if self.history_dirty:
            self.settings.setValue('track_history', json.dumps(self.history))
            self.history_dirty = False

    def update_source_colors(self, only_key=None):
        rows = [self.source_rows[only_key]] if only_key in self.source_rows else ([] if only_key else range(len(self.tracks)))
        for row in rows:
            key = path_key(self.tracks[row])
            item = self.sources.item(row)
            if item:
                color = '#36dab5' if key in self.selected_keys else {
                    'heard': '#8c97a5', 'skipped': '#ffb454'}.get(self.history.get(key), '#e8eef5')
                item.setForeground(QColor(color))

    def reset_history(self):
        dialog = QMessageBox(self)
        dialog.setWindowTitle('PartyPicker')
        dialog.setText(self.t('history_confirm'))
        yes = dialog.addButton('Zurücksetzen' if self.lang == 'de' else 'Reset', QMessageBox.AcceptRole)
        no = dialog.addButton('Abbrechen' if self.lang == 'de' else 'Cancel', QMessageBox.RejectRole)
        dialog.setDefaultButton(no)
        dialog.exec()
        if dialog.clickedButton() is not yes:
            return
        for path in self.tracks:
            self.history.pop(path_key(path), None)
        self.history_dirty = True
        self.update_source_colors()
        self.flush_history()

    def remove_pick(self):
        row = self.picks.currentRow()
        if row >= 0:
            entries = list(self.selected)
            entries.pop(row)
            self.commit(entries, ui_change=('remove', row))

    def move_pick(self, delta):
        row = self.picks.currentRow()
        target = row + delta
        if row >= 0 and 0 <= target < len(self.selected):
            entries = list(self.selected)
            entries[row], entries[target] = entries[target], entries[row]
            self.commit(entries, ui_change=('move', row, target))

    def step(self, delta):
        path = self.current_path()
        if path and self.requested_folder_track and path_key(path) not in self.selected_keys:
            self.mark_history(path, 'skipped')
        self.play_track(self.index + delta)

    def toggle(self):
        if self.player.playbackState() == QMediaPlayer.PlayingState:
            self.player.pause()
        elif self.current_path():
            self.player.play()

    def seek(self, fraction):
        if self.player.isSeekable():
            self.last_position = int(fraction * self.player.duration())
            self.player.setPosition(self.last_position)

    def jump(self, delta):
        if self.player.isSeekable():
            self.last_position = max(0, min(self.player.duration(), self.player.position() + delta))
            self.player.setPosition(self.last_position)

    def state(self, state):
        self.play_button.setText(
            self.t('pause') if state == QMediaPlayer.PlayingState else self.t('play'))

    def position(self, value):
        elapsed = value - self.last_position
        self.last_position = value
        if self.player.playbackState() == QMediaPlayer.PlayingState and 0 < elapsed <= 2000:
            self.listened_ms += elapsed
            path = self.current_path()
            if self.listened_ms >= 3000 and path and getattr(self, 'requested_folder_track', False):
                self.mark_history(path, 'heard')
        duration = self.player.duration()
        def time(ms):
            seconds = ms // 1000
            return f'{seconds // 60}:{seconds % 60:02d}'
        self.clock.setText(f'{time(value)} / {time(duration)}   ·   {self.t("wave_hint")}')
        self.wave.fraction = value / duration if duration else 0
        self.wave.update()

    def media_status(self, status):
        if status == QMediaPlayer.EndOfMedia:
            path = self.current_path()
            if path and getattr(self, 'requested_folder_track', False):
                self.mark_history(path, 'heard')
        if status == QMediaPlayer.EndOfMedia and self.auto.isChecked():
            # Playlist previews do not unexpectedly jump into the folder queue.
            if (getattr(self, 'requested_folder_track', False) and
                    0 <= self.index < len(self.tracks) and self.current_path() == self.tracks[self.index]):
                token = self.play_token
                QTimer.singleShot(0, lambda: self.play_track(self.index + 1) if token == self.play_token else None)

    def closeEvent(self, event):
        self.flush_history()
        self.settings.sync()
        self.play_token += 1
        self.player.stop()
        for job in list(self.jobs):
            job.requestInterruption()
        for job in list(self.jobs):
            job.wait()
        event.accept()


def main():
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon(str(resource_path('PartyPicker.ico'))))
    app.setStyle('Fusion')
    app.setStyleSheet('''QWidget { background:#182333; color:#e8eef5; font-family:"Segoe UI"; font-size:13px; }
    QPushButton { background:#293d53; padding:10px; border:1px solid #425970; border-radius:6px; }
    QPushButton:hover { background:#385570; } QPushButton:disabled { color:#748395; }
    QListWidget { background:#101827; border:1px solid #304258; border-radius:6px; }
    QListWidget::item { padding:7px; } QListWidget::item:selected { background:#236e65; }
    QSlider::groove:horizontal { height:6px; background:#456078; }
    QSlider::handle:horizontal { background:#36dab5; width:14px; margin:-5px 0; border-radius:6px; }''')
    window = Window()
    window.showMaximized()
    QTimer.singleShot(0, window.startup_choice)
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
