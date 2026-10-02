import os
import re
import tempfile
from pathlib import Path
from tinytag import TinyTag


def natural_key(path):
    return [int(x) if x.isdecimal() else x.casefold() for x in re.split(r'(\d+)', str(path))]


def absolute_path(path):
    """Return an absolute path without resolving links or mapped drives."""
    return Path(os.path.abspath(os.path.normpath(os.fspath(path))))


def path_key(path):
    """Create a fast lexical comparison key while preserving the stored path."""
    return os.path.normcase(os.path.normpath(os.fspath(absolute_path(path))))


def read_playlist(path):
    path = Path(path)
    raw = path.read_bytes()
    try:
        text = raw.decode('utf-8-sig')
    except UnicodeDecodeError:
        text = raw.decode('cp1252')
    entries = []
    seen = set()
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        if '://' in line:
            raise ValueError('Diese App importiert lokale Dateipfade, keine Streaming-URLs.')
        p = Path(line)
        if not p.is_absolute():
            p = path.parent / p
        p = absolute_path(p)
        key = path_key(p)
        if key not in seen:
            entries.append(p)
            seen.add(key)
    return entries


def _write_lines(path, lines):
    """Replace atomically; a failed write retains the previous file."""
    path = Path(path)
    fd, tmp = tempfile.mkstemp(prefix='.' + path.name, suffix='.tmp', dir=path.parent)
    try:
        with os.fdopen(fd, 'w', encoding='utf-8', newline='\n') as out:
            out.write('\n'.join(lines) + '\n')
            out.flush()
            os.fsync(out.fileno())
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


def save_playlist(path, entries):
    """Save an M3U playlist containing absolute local file paths."""
    lines = ['#EXTM3U']
    for p in entries:
        value = str(absolute_path(p))
        if '\n' in value or '\r' in value:
            raise ValueError('Zeilenumbruch im Dateinamen wird nicht unterstützt.')
        lines.append(value)
    _write_lines(path, lines)


def text_entry(path):
    """Return Artist - Titel from FLAC/MP3 tags, with a filename fallback."""
    path = Path(path)
    try:
        tags = TinyTag.get(path)
        artist = (tags.artist or '').strip()
        title = (tags.title or '').strip()
        if artist and title:
            return f'{artist} - {title}'
        if title:
            return title
    except Exception:
        pass
    return path.stem


def save_text_playlist(path, entries, labels=None):
    """Save one human-readable Artist - Titel line per selected track."""
    labels = labels or {}
    lines = []
    for p in entries:
        key = path_key(p)
        value = labels[key] if key in labels else text_entry(p)
        lines.append(value.replace('\r', ' ').replace('\n', ' '))
    _write_lines(path, lines)


def track_identity(path):
    """Conservative artist/title identity; no network access beyond reading tags."""
    import unicodedata
    try:
        tags = TinyTag.get(path)
        artist, title = tags.artist, tags.title
    except Exception:
        artist = title = None
    if not artist or not title:
        # Only use a filename with an explicit artist/title separator.
        parts = Path(path).stem.split(' - ', 1)
        if len(parts) != 2:
            return None
        artist = re.sub(r'^(?:CD\d+[- .]*)?\d+[- .]*', '', parts[0], flags=re.I)
        title = parts[1]
    def normalize(value):
        return ' '.join(unicodedata.normalize('NFKC', value).casefold().split())
    return (normalize(artist), normalize(title)) if artist.strip() and title.strip() else None


def preview_position(requested_ms, duration_ms):
    """Keep at least ten seconds to audition, otherwise restart a short track."""
    return max(0, min(requested_ms, duration_ms - 10000)) if duration_ms > 10000 else 0


def normalization_gain(rms, peak):
    """RMS listening adjustment, max +6 dB; never deliberately raise peaks past 1."""
    if rms <= 1e-8 or peak <= 1e-8:
        return 1.0
    return max(0.0, min(2.0, 0.1 / rms, 0.98 / peak))
