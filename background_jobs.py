"""Read-only I/O jobs that cannot block navigation or interpreter shutdown.

Qt objects and slots remain on the GUI thread. Blocking filesystem calls run in
Python daemon threads, so cancelling never waits for an unavailable NAS. Writes
continue to use QThread and are allowed to finish before application exit.
"""
import threading
import traceback
from PySide6.QtCore import QObject, Signal


class ReadJob(QObject):
    finished = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._cancel = threading.Event()
        self._done = threading.Event()
        self._thread = None

    def start(self):
        if self._thread is not None:
            raise RuntimeError('Read job already started')
        self._thread = threading.Thread(target=self._execute, daemon=True, name=type(self).__name__)
        self._thread.start()

    def _execute(self):
        try:
            self.run()
        except RuntimeError:
            # The window can be destroyed while a cancelled OS read is blocked.
            if not self._cancel.is_set():
                traceback.print_exc()
        except Exception:
            traceback.print_exc()
        finally:
            self._done.set()
            try:
                self.finished.emit()
            except RuntimeError:
                pass  # GUI already closed; no QObject is kept alive by a QThread.

    def publish(self, name, *values):
        if self._cancel.is_set():
            return
        try:
            getattr(self, name).emit(*values)
        except RuntimeError:
            if not self._cancel.is_set():
                raise

    def isRunning(self):
        return self._thread is not None and not self._done.is_set()

    def requestInterruption(self):
        self._cancel.set()

    def isInterruptionRequested(self):
        return self._cancel.is_set()

    def wait(self, timeout=None):
        if self._thread is None:
            return True
        return self._done.wait(None if timeout is None else max(0, timeout) / 1000)
