"""Sample pointer and monitor edges in the same physical Windows coordinates."""
import sys
from dataclasses import dataclass
from PySide6.QtGui import QCursor, QGuiApplication


@dataclass(frozen=True)
class EdgePosition:
    key: object
    y: int
    top: int
    bottom: int
    scale: float = 1.0


class WindowsDragAPI:
    def __init__(self):
        import ctypes
        from ctypes import wintypes
        self.ctypes, self.POINT = ctypes, wintypes.POINT
        class MonitorInfo(ctypes.Structure):
            _fields_ = [('cbSize', wintypes.DWORD), ('monitor', wintypes.RECT),
                        ('work', wintypes.RECT), ('flags', wintypes.DWORD)]
        self.MonitorInfo = MonitorInfo
        self.user32 = ctypes.WinDLL('user32', use_last_error=True)
        self.user32.GetCursorPos.argtypes = [ctypes.POINTER(wintypes.POINT)]
        self.user32.GetCursorPos.restype = wintypes.BOOL
        self.user32.MonitorFromPoint.argtypes = [wintypes.POINT, wintypes.DWORD]
        self.user32.MonitorFromPoint.restype = wintypes.HANDLE
        self.user32.GetMonitorInfoW.argtypes = [wintypes.HANDLE, ctypes.POINTER(MonitorInfo)]
        self.user32.GetMonitorInfoW.restype = wintypes.BOOL

    def position(self):
        point = self.POINT()
        if not self.user32.GetCursorPos(self.ctypes.byref(point)):
            return None
        monitor = self.user32.MonitorFromPoint(point, 0)  # No nearest-screen guess.
        if not monitor:
            return None
        info = self.MonitorInfo()
        info.cbSize = self.ctypes.sizeof(info)
        if not self.user32.GetMonitorInfoW(monitor, self.ctypes.byref(info)):
            return None
        rect = info.monitor  # Full screen, not the taskbar-reduced work area.
        return EdgePosition(('win32', monitor, rect.left, rect.top, rect.right, rect.bottom),
                            point.y, rect.top, rect.bottom - 1)


WINDOWS = WindowsDragAPI() if sys.platform == 'win32' else None


def edge_position():
    if WINDOWS is not None:
        return WINDOWS.position()
    cursor = QCursor.pos()
    screen = QGuiApplication.screenAt(cursor)
    if screen is None:
        return None
    rect = screen.geometry()
    key = (screen.name(), rect.x(), rect.y(), rect.width(), rect.height(), screen.devicePixelRatio())
    return EdgePosition(key, cursor.y(), rect.top(), rect.bottom(), screen.devicePixelRatio())

