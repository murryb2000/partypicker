import os
import sys
from pathlib import Path
import numpy as np
import soundfile as sf
from tinytag import TinyTag
from PySide6.QtCore import Qt, QUrl, QThread, Signal, QTimer, QSettings
from PySide6.QtGui import (QColor, QDesktopServices, QIcon, QPainter, QPen,
                           QShortcut, QKeySequence, QPixmap)
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
    QHBoxLayout, QGridLayout, QPushButton, QLabel, QListWidget, QFileDialog, QMessageBox,
    QSplitter, QCheckBox, QSlider, QComboBox)
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
from core import natural_key, read_playlist, save_playlist, save_text_playlist


KO_FI_URL = 'https://ko-fi.com/murryb'

TEXTS = {
    'de': {
        'window_title': 'PARTYPICKER / Der Playlist-Generator',
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
        'no_files': 'Keine FLAC- oder MP3-Dateien in diesem Ordner gefunden.',
        'folder_finished': 'Ordner durchgehört. Wähle den nächsten Ordner.',
        'file_unavailable': 'Datei nicht erreichbar:\n{path}',
        'wave_error': 'Waveform: {error}',
        'local_paths_only': 'Diese App importiert lokale Dateipfade, keine Streaming-URLs.',
        'newline_unsupported': 'Zeilenumbruch im Dateinamen wird nicht unterstützt.',
    },
    'en': {
        'window_title': 'PARTYPICKER / The Playlist Generator',
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
        'no_files': 'No FLAC or MP3 files found in this folder.',
        'folder_finished': 'Folder finished. Select the next folder.',
        'file_unavailable': 'File unavailable:\n{path}',
        'wave_error': 'Waveform: {error}',
        'local_paths_only': 'This app imports local file paths, not streaming URLs.',
        'newline_unsupported': 'Line breaks in file names are not supported.',
    },
}


def resource_path(name):
    """Resolve bundled assets both from source and a PyInstaller one-file EXE."""
    base = Path(getattr(sys, '_MEIPASS', Path(__file__).resolve().parent))
    return base / name


class Scan(QThread):
    result = Signal(object, str)
    def __init__(self, root, recursive, parent):
        super().__init__(parent)
        self.root, self.recursive = root, recursive
    def run(self):
        try:
            files = []
            def fail(error):
                raise error
            for root, dirs, names in os.walk(self.root, onerror=fail):
                if self.isInterruptionRequested():
                    return
                files.extend(
                    Path(root) / n for n in names
                    if Path(n).suffix.lower() in ('.flac', '.mp3')
                )
                if not self.recursive:
                    dirs.clear()
            self.result.emit(sorted(files, key=natural_key), '')
        except Exception as exc:
            self.result.emit([], str(exc))


class Analyze(QThread):
    result = Signal(str, object, str, str)
    def __init__(self, path, parent):
        super().__init__(parent)
        self.path = path
    def run(self):
        try:
            with sf.SoundFile(str(self.path)) as audio:
                block = max(1, int(np.ceil(len(audio) / 1600)))
                peaks = []
                for data in audio.blocks(blocksize=block, dtype='float32', always_2d=True):
                    if self.isInterruptionRequested():
                        return
                    peaks.append(float(np.abs(data).max()))
            title = self.path.stem
            try:
                tags = TinyTag.get(self.path)
                title = ' – '.join(filter(None, [tags.artist, tags.title])) or title
            except Exception:
                pass
            self.result.emit(str(self.path), peaks, title, '')
        except Exception as exc:
            self.result.emit(str(self.path), [], self.path.stem, str(exc))


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
        self.index, self.playlist, self.analyzer = -1, None, None
        self.audio = QAudioOutput(self)
        self.audio.setVolume(.65)
        self.player = QMediaPlayer(self)
        self.player.setAudioOutput(self.audio)
        self.player.positionChanged.connect(self.position)
        self.player.durationChanged.connect(lambda _: self.position(self.player.position()))
        self.player.playbackStateChanged.connect(self.state)
        self.player.mediaStatusChanged.connect(self.media_status)
        self.player.errorOccurred.connect(lambda *args: self.statusBar().showMessage(
            self.t('playback_error', error=self.player.errorString())))
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
        self.head = QLabel(self.t('window_title'))
        self.head.setWordWrap(False)
        self.head.setStyleSheet('font-size:22px; font-weight:bold;')
        credit = QLabel('by MurryB')
        credit.setStyleSheet('font-size:11px; color:#8fa4b8;')
        branding.addWidget(self.head)
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
        self.recursive.setChecked(True)
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
        volume.valueChanged.connect(lambda value: self.audio.setVolume(value / 100))
        options.addWidget(volume)
        options.addStretch()
        self.auto = QCheckBox(self.t('auto_next'))
        self.auto.setChecked(True)
        options.addWidget(self.auto)
        player_layout.addLayout(options)
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
        up_button = QPushButton('↑')
        up_button.clicked.connect(lambda checked=False: self.move_pick(-1))
        playlist_controls.addWidget(up_button, 0, 1)
        down_button = QPushButton('↓')
        down_button.clicked.connect(lambda checked=False: self.move_pick(1))
        playlist_controls.addWidget(down_button, 0, 2)
        self.remove_button = QPushButton(self.t('remove'))
        self.remove_button.clicked.connect(lambda checked=False: self.remove_pick())
        playlist_controls.addWidget(self.remove_button, 0, 3)
        self.support_button = QPushButton(self.t('support'))
        self.support_button.clicked.connect(lambda checked=False: self.open_support())
        self.support_button.setToolTip(self.t('support_tip'))
        self.support_button.setStyleSheet('background:#7a4a16; font-weight:bold;')
        playlist_controls.addWidget(self.support_button, 1, 3)
        sidebar_layout.addLayout(playlist_controls)
        body.addWidget(sidebar)
        body.setStretchFactor(0, 3)
        body.setStretchFactor(1, 2)
        body.setSizes([650, 500])
        layout.addWidget(body, 1)
        self.shortcuts_label = QLabel(self.t('shortcuts'))
        layout.addWidget(self.shortcuts_label)
        for key, callback in [('Space', self.toggle), ('Left', lambda: self.jump(-10000)), ('Right', lambda: self.jump(10000)), ('Ctrl+Left', lambda: self.step(-1)), ('Ctrl+Right', lambda: self.step(1)), ('A', self.add), ('Return', lambda: self.add(True))]:
            shortcut = QShortcut(QKeySequence(key), self)
            shortcut.activated.connect(callback)
        self.statusBar().showMessage(self.t('ready'))

    def t(self, key, **values):
        return TEXTS[self.lang][key].format(**values)

    def change_language(self):
        self.lang = self.language_box.currentData()
        self.settings.setValue('language', self.lang)
        self.retranslate_ui()

    def retranslate_ui(self):
        self.setWindowTitle(self.t('window_title'))
        self.head.setText(self.t('window_title'))
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
        self.shortcuts_label.setText(self.t('shortcuts'))
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

    def commit(self, entries, target=None):
        target = target or self.playlist
        if target is None:
            return False
        try:
            if Path(target).suffix.lower() == '.txt':
                save_text_playlist(target, entries)
            else:
                save_playlist(target, entries)
        except Exception as exc:
            self.error(self.t('not_saved', error=self.translate_core_error(str(exc))))
            return False
        self.playlist, self.selected = Path(target), list(entries)
        self.refresh()
        self.statusBar().showMessage(self.t('saved', path=self.playlist))
        return True

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

    def new_playlist(self):
        target = self.choose_target()
        if target:
            self.commit([], target)

    def save_as(self):
        target = self.choose_target()
        if target:
            self.commit(self.selected, target)

    def open_playlist(self):
        name, _ = QFileDialog.getOpenFileName(
            self, self.t('open_playlist_title'), '', self.t('open_playlist_filter'))
        if not name:
            return
        try:
            entries = read_playlist(name)
        except Exception as exc:
            self.error(self.translate_core_error(str(exc)))
            return
        self.playlist, self.selected = Path(name), entries
        self.text_only.setChecked(False)
        self.refresh()
        self.show_latest_pick()
        missing = sum(not p.is_file() for p in entries)
        self.statusBar().showMessage(
            self.t('playlist_loaded_missing', missing=missing)
            if missing else self.t('playlist_loaded'))

    def refresh(self):
        self.picks.clear()
        for p in self.selected:
            self.picks.addItem(('⚠ ' if not p.is_file() else '') + p.stem)
            self.picks.item(self.picks.count()-1).setToolTip(str(p))
        self.location.setText(self.t('playlist_location', path=self.playlist))
        self.refresh_count()
        self.update_add()

    def refresh_count(self):
        self.count.setText(self.t('count', tracks=len(self.tracks), selected=len(self.selected)))

    def update_add(self):
        current = self.current_path()
        self.add_button.setToolTip(
            self.t('already_added') if current in self.selected else self.t('add_tip'))

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
        job.finished.connect(lambda: self.jobs.remove(job) if job in self.jobs else None)
        job.start()

    def open_folder(self):
        if self.playlist is None:
            self.new_playlist()
            if self.playlist is None:
                return
        folder = QFileDialog.getExistingDirectory(self, self.t('choose_folder'))
        if not folder:
            return
        self.folder_button.setEnabled(False)
        self.statusBar().showMessage(self.t('searching'))
        scan = Scan(folder, self.recursive.isChecked(), self)
        scan.result.connect(self.scanned)
        self.launch(scan)

    def scanned(self, files, error):
        self.folder_button.setEnabled(True)
        if error:
            self.error(error)
            return
        if not files:
            self.statusBar().showMessage(self.t('no_files'))
            return
        self.tracks = files
        self.sources.clear()
        for p in files:
            self.sources.addItem(p.parent.name + ' / ' + p.name)
            self.sources.item(self.sources.count()-1).setToolTip(str(p))
        self.refresh()
        self.play_track(0)

    def play_track(self, index):
        if 0 <= index < len(self.tracks):
            self.index = index
            self.sources.setCurrentRow(index)
            self.play_path(self.tracks[index])
        elif index >= len(self.tracks) and self.tracks:
            self.statusBar().showMessage(self.t('folder_finished'))

    def play_path(self, path):
        if not path.is_file():
            self.error(self.t('file_unavailable', path=path))
            return
        if self.analyzer and self.analyzer.isRunning():
            self.analyzer.requestInterruption()
        self.player.stop()
        self.title.setText(path.stem)
        self.file_label.setText(str(path))
        self.wave.peaks, self.wave.fraction = [], 0
        self.wave_message_key = 'wave_loading'
        self.wave.message = self.t(self.wave_message_key)
        self.wave.update()
        self.player.setSource(QUrl.fromLocalFile(str(path)))
        self.player.play()
        self.analyzer = Analyze(path, self)
        self.analyzer.result.connect(self.analyzed)
        self.launch(self.analyzer)
        self.update_add()

    def analyzed(self, path, peaks, title, error):
        if str(self.current_path()) != path:
            return
        self.title.setText(title)
        self.wave.peaks = peaks
        self.wave_message_key = 'wave_unavailable' if error else ''
        self.wave.message = self.t(self.wave_message_key) if self.wave_message_key else ''
        self.wave.update()
        if error:
            self.statusBar().showMessage(self.t('wave_error', error=error))

    def preview_pick(self, item):
        self.play_path(self.selected[self.picks.row(item)])

    def add(self, advance=False):
        path = self.current_path()
        if path is None:
            return
        if self.playlist is None:
            self.new_playlist()
        if self.playlist is None:
            return
        if path not in self.selected:
            if not self.commit(self.selected + [path]):
                return
            self.show_latest_pick()
        if advance:
            self.step(1)

    def remove_pick(self):
        row = self.picks.currentRow()
        if row >= 0:
            entries = list(self.selected)
            entries.pop(row)
            self.commit(entries)

    def move_pick(self, delta):
        row = self.picks.currentRow()
        target = row + delta
        if row >= 0 and 0 <= target < len(self.selected):
            entries = list(self.selected)
            entries[row], entries[target] = entries[target], entries[row]
            if self.commit(entries):
                self.picks.setCurrentRow(target)

    def step(self, delta):
        self.play_track(self.index + delta)

    def toggle(self):
        if self.player.playbackState() == QMediaPlayer.PlayingState:
            self.player.pause()
        elif self.current_path():
            self.player.play()

    def seek(self, fraction):
        if self.player.isSeekable():
            self.player.setPosition(int(fraction * self.player.duration()))

    def jump(self, delta):
        if self.player.isSeekable():
            self.player.setPosition(max(0, min(self.player.duration(), self.player.position() + delta)))

    def state(self, state):
        self.play_button.setText(
            self.t('pause') if state == QMediaPlayer.PlayingState else self.t('play'))

    def position(self, value):
        duration = self.player.duration()
        def time(ms):
            seconds = ms // 1000
            return f'{seconds // 60}:{seconds % 60:02d}'
        self.clock.setText(f'{time(value)} / {time(duration)}   ·   {self.t("wave_hint")}')
        self.wave.fraction = value / duration if duration else 0
        self.wave.update()

    def media_status(self, status):
        if status == QMediaPlayer.EndOfMedia and self.auto.isChecked():
            # Playlist previews do not unexpectedly jump into the folder queue.
            if 0 <= self.index < len(self.tracks) and self.current_path() == self.tracks[self.index]:
                QTimer.singleShot(0, lambda: self.step(1))

    def closeEvent(self, event):
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
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
