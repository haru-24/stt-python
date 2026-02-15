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
    → メニューバーに🎤アイコンが表示される
    → 右Commandキーを押しながら話す → 離すとテキスト入力
"""

import time
from model.whisper import get_model
from ui.menu_bar import VoiceInputApp, HAS_RUMPS
from core.engine import VoiceInputEngine
from core.keyboard import run_keyboard_listener


def main() -> None:
    """メイン関数"""
    # モデルを事前ロード
    get_model()

    if HAS_RUMPS:
        app = VoiceInputApp()
        engine = VoiceInputEngine(app=app)
        run_keyboard_listener(engine)
        app.run()
    else:
        engine = VoiceInputEngine()
        run_keyboard_listener(engine)

        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            pass

if __name__ == "__main__":
    main()
