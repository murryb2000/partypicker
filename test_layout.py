import os
os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
import unittest
from PySide6.QtCore import QPoint, QRect, Qt
from PySide6.QtWidgets import QStyle, QStyleOptionButton, QWidget
import test_party_picker as fixture
from party_picker import application_style

APP = fixture.APP


class CompactLayoutTests(unittest.TestCase):
    def setUp(self):
        self.old_style = APP.styleSheet()
        APP.setStyleSheet(application_style())
        fixture.PartyPickerTests.setUp(self)

    def tearDown(self):
        fixture.PartyPickerTests.tearDown(self)
        APP.setStyleSheet(self.old_style)
        APP.processEvents()

    def test_long_text_does_not_increase_height_or_hide_waveform(self):
        title = 'Artist featuring Guests – ' + ('Very long song title remix edition ' * 60)
        path = 'Z:\\Music\\' + ('Very long directory\\' * 60) + 'Party Song.flac'
        playlist = 'Playlist: C:\\Users\\Frank\\' + ('Very long directory\\' * 50) + 'Party.m3u'
        self.w.resize(1128, 680)
        self.w.show(); APP.processEvents()
        heights = [label.height() for label in (self.w.title, self.w.file_label, self.w.location)]
        self.w.title.setText(title)
        self.w.file_label.setText(path)
        self.w.location.setText(playlist)
        APP.processEvents()
        self.assertEqual([label.height() for label in (self.w.title, self.w.file_label, self.w.location)], heights)
        self.assertLessEqual(self.w.width(), 1128, sorted(
            [(w.metaObject().className(), getattr(w, 'text', lambda: '')()[:80],
              w.minimumSizeHint().width(), w.minimumWidth(), w.width())
             for w in self.w.findChildren(QWidget) if w.minimumSizeHint().width() > 600],
            key=lambda row: row[2], reverse=True))
        self.assertLessEqual(self.w.height(), 680)
        for label, original in [(self.w.title, title), (self.w.file_label, path), (self.w.location, playlist)]:
            self.assertEqual(label.text(), original)
            self.assertEqual(label.toolTip(), original)
            self.assertIn('…', label.displayed_text())
            self.assertLessEqual(label.fontMetrics().horizontalAdvance(label.displayed_text()), label.contentsRect().width() + 1)
        self.assertTrue(self.w.title.displayed_text().endswith('…'))
        self.assertTrue(self.w.file_label.displayed_text().endswith('Party Song.flac'))
        self.assertTrue(self.w.location.displayed_text().endswith('Party.m3u'))
        self.assertEqual(self.w.wave.height(), 128)
        option = QStyleOptionButton()
        self.w.text_only.initStyleOption(option)
        indicator = self.w.text_only.style().subElementRect(QStyle.SE_CheckBoxIndicator, option, self.w.text_only)
        image = self.w.text_only.grab().toImage()
        ratio = image.devicePixelRatio()
        self.assertEqual(image.pixelColor(int(indicator.center().x()*ratio), int(indicator.center().y()*ratio)).name(), '#577b9a')
        for widget in (self.w.title, self.w.file_label, self.w.wave, self.w.previous_button,
                       self.w.play_button, self.w.next_button, self.w.add_button):
            rect = QRect(widget.mapTo(self.w, QPoint()), widget.size())
            self.assertTrue(self.w.rect().contains(rect), (widget, rect))
            self.assertEqual(widget.visibleRegion().boundingRect().size(), widget.size())

    def test_compact_switch_and_both_languages(self):
        for lang in ('de', 'en'):
            self.w.language_box.setCurrentIndex(0 if lang == 'de' else 1)
            self.w.resize(1440, 900); self.w.show(); APP.processEvents()
            self.assertFalse(self.w.compact_mode)
            self.assertEqual(self.w.logo.height(), 80)
            self.w.resize(1128, 752); APP.processEvents()
            self.assertTrue(self.w.compact_mode)
            self.assertEqual(self.w.logo.height(), 64)
            self.assertEqual(self.w.wave.height(), 128)
            self.assertLessEqual(self.w.width(), 1128, sorted(
            [(w.metaObject().className(), getattr(w, 'text', lambda: '')()[:80],
              w.minimumSizeHint().width(), w.minimumWidth(), w.width())
             for w in self.w.findChildren(QWidget) if w.minimumSizeHint().width() > 600],
            key=lambda row: row[2], reverse=True))
            self.assertLessEqual(self.w.height(), 752)

    def test_full_text_is_preserved_and_rendering_is_single_line(self):
        value = 'Artist & Guests <Live>\n' + 'Long Title ' * 100
        self.w.title.setText(value)
        self.w.resize(1128, 752); self.w.show(); APP.processEvents()
        self.assertEqual(self.w.title.text(), value)
        self.assertEqual(self.w.title.toolTip(), value)
        self.assertEqual(self.w.title.textFormat(), Qt.PlainText)
        self.assertNotIn('\n', self.w.title.displayed_text())
        self.assertEqual(self.w.title.contentsRect().height(), self.w.title.fontMetrics().height())

    def test_layout_with_real_two_hundred_percent_qt_scaling(self):
        import subprocess
        import sys
        from pathlib import Path
        script = r'''
import tempfile
from unittest.mock import patch
from PySide6.QtCore import QSettings
from PySide6.QtWidgets import QApplication
from party_picker import Window, application_style
app = QApplication([]); app.setStyle('Fusion'); app.setStyleSheet(application_style())
with tempfile.TemporaryDirectory() as tmp:
    with patch('party_picker.QSettings', lambda *_: QSettings(tmp+'/settings.ini', QSettings.IniFormat)):
        window = Window()
        window.title.setText('Very long title ' * 500)
        window.file_label.setText('Z:/Music/' + 'Long Folder/' * 100 + 'Song.flac')
        window.location.setText('Playlist: C:/' + 'Long Folder/' * 100 + 'Party.m3u')
        window.resize(1128, 680); window.show(); app.processEvents()
        assert window.devicePixelRatioF() >= 1.99
        assert window.width() <= 1128 and window.height() <= 680
        for widget in (window.wave, window.next_button, window.add_button):
            assert widget.visibleRegion().boundingRect().size() == widget.size()
        assert window.wave.height() == 128
        assert window.title.displayed_text().endswith('\u2026')
        window.close(); app.processEvents()
'''
        env = dict(os.environ, QT_QPA_PLATFORM='offscreen', QT_SCALE_FACTOR='2')
        result = subprocess.run([sys.executable, '-c', script], cwd=Path(__file__).parent,
                                env=env, capture_output=True, text=True, timeout=15)
        self.assertEqual(result.returncode, 0, result.stderr)
