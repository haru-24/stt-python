"""
Mac用 Push-to-Talk 音声入力ツール
==================================
右Commandキーを押している間だけ録音し、離すとWhisperで文字起こしして
アクティブなウィンドウ（ターミナル、Claude Code等）にテキスト入力する。

セットアップ:
    pip install faster-whisper sounddevice numpy pynput rumps pyobjc-framework-Cocoa

macOSの設定:
    システム設定 → プライバシーとセキュリティ → アクセシビリティ
    → ターミナル（またはPythonの実行環境）を許可

使い方:
    python voice_input.py
    → メニューバーに🎤アイコンが表示される
    → 右Commandキーを押しながら話す → 離すとテキスト入力
"""

import threading
import time
import numpy as np
import sounddevice as sd
from pynput import keyboard
from pynput.keyboard import Controller, Key
import subprocess
import sys
import os

# ============================================================
# 設定
# ============================================================
HOTKEY = Key.cmd_r           # 右Commandキー（押している間だけ録音）
SAMPLE_RATE = 16000
WHISPER_MODEL = "base"      # tiny / base / small / medium / large-v3
LANGUAGE = "ja"
MIN_DURATION = 0.3          # これより短い録音は無視 (秒)

# ============================================================
# メニューバーUI (rumps)
# ============================================================
try:
    import rumps

    class VoiceInputApp(rumps.App):
        def __init__(self):
            super().__init__("🎤", quit_button="終了")
            self.menu = [
                rumps.MenuItem("待機中..."),
                None,  # separator
                rumps.MenuItem("モデル: " + WHISPER_MODEL),
            ]
            self._status_item = self.menu["待機中..."]

        def set_recording(self):
            self.title = "🔴"
            self._status_item.title = "🎙️ 録音中..."

        def set_processing(self):
            self.title = "⏳"
            self._status_item.title = "⏳ 変換中..."

        def set_idle(self):
            self.title = "🎤"
            self._status_item.title = "待機中..."

        def set_error(self, msg):
            self.title = "⚠️"
            self._status_item.title = f"⚠️ {msg}"

    HAS_RUMPS = True
except ImportError:
    HAS_RUMPS = False
    print("⚠️  rumps未インストール。メニューバーUIなしで動作します。")
    print("   pip install rumps でインストールできます。")

# ============================================================
# macOS通知音 (録音開始/終了のフィードバック)
# ============================================================
def play_sound(name="Tink"):
    """macOS標準サウンドを再生"""
    try:
        subprocess.Popen(
            ["afplay", f"/System/Library/Sounds/{name}.aiff"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except Exception:
        pass

# ============================================================
# Whisperモデル (遅延ロード)
# ============================================================
_model = None
_model_lock = threading.Lock()

def get_model():
    global _model
    if _model is None:
        with _model_lock:
            if _model is None:
                print(f"🔄 Whisperモデル ({WHISPER_MODEL}) をロード中...")
                from faster_whisper import WhisperModel
                _model = WhisperModel(
                    WHISPER_MODEL,
                    device="cpu",       # Apple Silicon: "auto" でも可
                    compute_type="int8" # CPU向け最適化
                )
                print("✅ モデルロード完了")
    return _model

# ============================================================
# 録音 & 文字起こし & 入力
# ============================================================
class VoiceInputEngine:
    def __init__(self, app=None):
        self.app = app
        self.kb = Controller()
        self.is_recording = False
        self.audio_chunks = []
        self.stream = None
        self._lock = threading.Lock()

    def start_recording(self):
        with self._lock:
            if self.is_recording:
                return
            self.is_recording = True
            self.audio_chunks = []

        play_sound("Tink")  # 録音開始音
        if self.app:
            self.app.set_recording()
        else:
            print("🔴 録音中...")

        def audio_callback(indata, frames, time_info, status):
            if status:
                print(f"⚠️ Audio: {status}")
            self.audio_chunks.append(indata.copy())

        self.stream = sd.InputStream(
            samplerate=SAMPLE_RATE,
            channels=1,
            dtype="float32",
            callback=audio_callback,
        )
        self.stream.start()

    def stop_recording(self):
        with self._lock:
            if not self.is_recording:
                return
            self.is_recording = False

        if self.stream:
            self.stream.stop()
            self.stream.close()
            self.stream = None

        play_sound("Pop")  # 録音終了音

        if not self.audio_chunks:
            if self.app:
                self.app.set_idle()
            return

        audio = np.concatenate(self.audio_chunks).flatten()
        duration = len(audio) / SAMPLE_RATE

        if duration < MIN_DURATION:
            print(f"⏭️ 短すぎる録音 ({duration:.1f}s) → スキップ")
            if self.app:
                self.app.set_idle()
            return

        # バックグラウンドで文字起こし
        threading.Thread(target=self._transcribe_and_type, args=(audio,), daemon=True).start()

    def _transcribe_and_type(self, audio):
        if self.app:
            self.app.set_processing()
        else:
            print("⏳ 変換中...")

        try:
            model = get_model()
            segments, info = model.transcribe(
                audio,
                language=LANGUAGE,
                beam_size=5,
                vad_filter=True,  # 無音部分をフィルタ
            )
            text = "".join(seg.text for seg in segments).strip()

            if text:
                print(f"📝 {text}")
                # 少し待ってからタイプ（フォーカス安定のため）
                time.sleep(0.1)
                self._type_text(text)
            else:
                print("🔇 音声が検出されませんでした")

        except Exception as e:
            print(f"❌ エラー: {e}")
            if self.app:
                self.app.set_error(str(e)[:30])
                time.sleep(2)
        finally:
            if self.app:
                self.app.set_idle()

    def _type_text(self, text):
        """
        テキストをアクティブウィンドウに入力。
        日本語対応のため、pbcopy + Cmd+V (ペースト) を使用。
        pynput.type() は日本語非対応のため。
        """
        # クリップボードに保存
        process = subprocess.Popen(
            ["pbcopy"],
            stdin=subprocess.PIPE,
        )
        process.communicate(text.encode("utf-8"))

        # Cmd+V でペースト
        time.sleep(0.05)
        self.kb.press(Key.cmd)
        self.kb.press("v")
        self.kb.release("v")
        self.kb.release(Key.cmd)

# ============================================================
# キーボードリスナー
# ============================================================
def run_keyboard_listener(engine):
    def on_press(key):
        if key == HOTKEY:
            engine.start_recording()

    def on_release(key):
        if key == HOTKEY:
            if engine.is_recording:
                engine.stop_recording()

    listener = keyboard.Listener(on_press=on_press, on_release=on_release)
    listener.start()
    return listener

# ============================================================
# メイン
# ============================================================
def main():
    print("=" * 50)
    print("🎤 Mac 音声入力ツール")
    print("=" * 50)
    print(f"  ホットキー  : 右Command")
    print(f"  モデル      : {WHISPER_MODEL}")
    print(f"  言語        : {LANGUAGE}")
    print(f"  サンプルレート: {SAMPLE_RATE}Hz")
    print("=" * 50)

    # モデルを事前ロード
    get_model()

    if HAS_RUMPS:
        app = VoiceInputApp()
        engine = VoiceInputEngine(app=app)
        listener = run_keyboard_listener(engine)

        print("\n✅ メニューバーの🎤アイコンを確認してください")
        print("   右Command を押しながら話してください\n")

        # rumps.App.run() はメインスレッドで実行が必要
        app.run()
    else:
        engine = VoiceInputEngine()
        listener = run_keyboard_listener(engine)

        print("\n✅ 右Command を押しながら話してください")
        print("   Ctrl+C で終了\n")

        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n👋 終了します")

if __name__ == "__main__":
    main()