# main.py

import ctypes
import sys
import customtkinter as ctk
from ui.UI import MainWindow

MUTEX_NAME = "Local\\RobotSequenceControlDataManagementSystemMutex"


def main():
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        try:
            ctypes.windll.user32.SetProcessDPIAware()
        except Exception:
            pass

    kernel32 = ctypes.windll.kernel32
    mutex = kernel32.CreateMutexW(None, False, MUTEX_NAME)
    last_error = kernel32.GetLastError()

    if last_error == 183:
        user32 = ctypes.windll.user32
        hwnd = user32.FindWindowW(None, "ロボットシーケンス制御データ管理システム")
        if hwnd:
            if user32.IsIconic(hwnd):
                user32.ShowWindow(hwnd, 9)
            user32.SetForegroundWindow(hwnd)
        sys.exit(0)

    ctk.set_appearance_mode("Light")
    ctk.set_default_color_theme("blue")

    app = MainWindow()
    app.mainloop()


if __name__ == "__main__":
    main()
