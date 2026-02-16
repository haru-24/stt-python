"""
設定ウィンドウ管理（薄いラッパー）
"""
import sys
import multiprocessing
from typing import Optional

from PyQt6.QtWidgets import QApplication


def _run_settings_window() -> None:
    """PyQt6ウィンドウを実行（別プロセス用）"""
    from ui.settings_window import SettingsDialog

    app = QApplication(sys.argv)
    dialog = SettingsDialog()
    dialog.exec()
    sys.exit()


class SettingsWindow:
    """設定ウィンドウ管理クラス"""

    def __init__(self) -> None:
        self._window_process: Optional[multiprocessing.Process] = None
        self._is_open: bool = False

    def show(self) -> None:
        """設定ウィンドウを表示（既に開いている場合は無視）"""
        if self._is_open and self._window_process and self._window_process.is_alive():
            print("[設定] ウィンドウは既に開いています")
            return

        self._is_open = True
        # 別プロセスでGUIを実行
        self._window_process = multiprocessing.Process(
            target=_run_settings_window, daemon=True
        )
        self._window_process.start()


# グローバルインスタンス
settings_window = SettingsWindow()
