"""
Mac用 Push-to-Talk 音声入力ツール
==================================
右Commandキーを押している間だけ録音し、離すとWhisperで文字起こしして
アクティブなウィンドウ（ターミナル、Claude Code等）にテキスト入力する。

セットアップ:
    pip install faster-whisper sounddevice numpy pynput rumps pyobjc-framework-Cocoa pydantic

macOSの設定:
    システム設定 → プライバシーとセキュリティ → アクセシビリティ
    → ターミナル（またはPythonの実行環境）を許可

使い方:
    python main.py
    → メニューバーに🥷🏻アイコンが表示される
    → 右Commandキーを押しながら話す → 離すとテキスト入力
"""

import time

from app.config import config
from app.whisper import WhisperTranscriber
from app.gemini import GeminiCorrector
from app.engine import VoiceInputEngine

# rumpsのインポート試行
try:
    import rumps

    class VoiceInputApp(rumps.App):
        """メニューバーUI"""
        _status_item: rumps.MenuItem

        def __init__(self) -> None:
            super().__init__("🥷🏻", quit_button="終了")
            self._status_item = rumps.MenuItem("待機中...")
            self.menu = [
                self._status_item,
                None,
                rumps.MenuItem("モデル: " + config.whisper_model),
            ]

        def set_recording(self) -> None:
            self.title = "🗣️"
            self._status_item.title = "🗣️ 録音中..."

        def set_processing(self) -> None:
            self.title = "👨🏻‍💻"
            self._status_item.title = "👨🏻‍💻 変換中..."

        def set_idle(self) -> None:
            self.title = "🥷🏻"
            self._status_item.title = "待機中..."

        def set_error(self, msg: str) -> None:
            self.title = "⚠️"
            self._status_item.title = f"⚠️ {msg}"

    HAS_RUMPS = True
except ImportError:
    HAS_RUMPS = False
    VoiceInputApp = None  # type: ignore
    print("rumps未インストール。メニューバーUIなしで動作します。")


def main() -> None:
    """メイン関数"""
    whisper = WhisperTranscriber()
    whisper.load()
    gemini = GeminiCorrector()

    if HAS_RUMPS:
        app = VoiceInputApp()
        engine = VoiceInputEngine(whisper, gemini, app=app)
        engine.start_keyboard_listener()
        app.run()
    else:
        engine = VoiceInputEngine(whisper, gemini)
        engine.start_keyboard_listener()

        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            pass

if __name__ == "__main__":
    main()
