import os
import re
import tempfile
import shutil
import uuid
import math
from datetime import datetime, timezone
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


BACKUP_LIMIT = 3


def playlist_backups(path):
    """Return only this playlist's generated snapshots, oldest first."""
    path = Path(path)
    pattern = re.compile(re.escape(path.name) + r'\.backup-\d{8}T\d{12}-[0-9a-f]{8}' + re.escape(path.suffix) + r'$')
    return sorted((p for p in path.parent.iterdir() if pattern.fullmatch(p.name)), key=lambda p: p.name)


def _same_contents(first, second):
    try:
        with open(first, 'rb') as a, open(second, 'rb') as b:
            while True:
                chunk = a.read(65536)
                if chunk != b.read(65536):
                    return False
                if not chunk:
                    return True
    except FileNotFoundError:
        return False


def _backup_previous(path):
    # Same directory preserves relative music paths in imported M3U files.
    try:
        source = path.open('rb')
    except FileNotFoundError:
        return
    stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%f')
    backup = path.with_name(f'{path.name}.backup-{stamp}-{uuid.uuid4().hex[:8]}{path.suffix}')
    tmp = None
    try:
        with source:
            fd, tmp = tempfile.mkstemp(prefix='.playlist-backup-', suffix='.tmp', dir=path.parent)
            with os.fdopen(fd, 'wb') as out:
                shutil.copyfileobj(source, out, length=65536)
                out.flush()
                os.fsync(out.fileno())
        os.replace(tmp, backup)
        for old in playlist_backups(path)[:-BACKUP_LIMIT]:
            old.unlink()
    except OSError as exc:
        raise OSError(f'Backup: {exc}') from exc
    finally:
        if tmp is not None and os.path.exists(tmp):
            os.unlink(tmp)


def _write_lines(path, lines):
    """Replace atomically; a failed write retains the previous file."""
    path = Path(path)
    fd, tmp = tempfile.mkstemp(prefix='.' + path.name, suffix='.tmp', dir=path.parent)
    try:
        with os.fdopen(fd, 'w', encoding='utf-8', newline='\n') as out:
            out.write('\n'.join(lines) + '\n')
            out.flush()
            os.fsync(out.fileno())
        if _same_contents(path, tmp):
            return
        _backup_previous(path)
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


def track_duration(path):
    """Read duration off the GUI thread; None means unavailable/invalid."""
    try:
        value = float(TinyTag.get(path).duration)
        return value if math.isfinite(value) and value >= 0 else None
    except Exception:
        return None


def format_duration(seconds):
    seconds = max(0, int(seconds + .5))
    hours, seconds = divmod(seconds, 3600)
    minutes, seconds = divmod(seconds, 60)
    return f'{hours:02}:{minutes:02}:{seconds:02}'
