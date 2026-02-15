"""
メニューバーUI管理
"""
from config.settings import config

# rumpsのインポート試行
try:
    import rumps

    class VoiceInputApp(rumps.App):
        _status_item: rumps.MenuItem

        def __init__(self) -> None:
            super().__init__("🎤", quit_button="終了")
            self._status_item = rumps.MenuItem("待機中...")
            self.menu = [
                self._status_item,
                None,  # separator
                rumps.MenuItem("モデル: " + config.whisper_model),
            ]

        def set_recording(self) -> None:
            self.title = "🔴"
            self._status_item.title = "🎙️ 録音中..."

        def set_processing(self) -> None:
            self.title = "⏳"
            self._status_item.title = "⏳ 変換中..."

        def set_idle(self) -> None:
            self.title = "🎤"
            self._status_item.title = "待機中..."

        def set_error(self, msg: str) -> None:
            self.title = "⚠️"
            self._status_item.title = f"⚠️ {msg}"

    HAS_RUMPS = True
except ImportError:
    HAS_RUMPS = False
    VoiceInputApp = None  # type: ignore
    print("⚠️  rumps未インストール。メニューバーUIなしで動作します。")
    print("   pip install rumps でインストールできます。")
