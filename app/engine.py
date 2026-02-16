"""
音声入力エンジン（録音・文字起こし・テキスト入力の統合制御）
"""
import logging
import subprocess
import threading
import time
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Any, Union

import numpy as np
import numpy.typing as npt
import sounddevice as sd
from pynput import keyboard
from pynput.keyboard import Key, KeyCode
from Quartz.CoreGraphics import (
    CGEventCreateKeyboardEvent,
    CGEventKeyboardSetUnicodeString,
    CGEventPost,
    kCGHIDEventTap,
)

from app.config import config
from app.whisper import WhisperTranscriber
from app.google_speech import GoogleSpeechTranscriber
from app.gemini import GeminiCorrector

# ログディレクトリとファイル設定
LOG_DIR = Path.home() / ".sst-python" / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE = LOG_DIR / "voice_input.log"

# ロガー設定
logger = logging.getLogger("voice_input")
logger.setLevel(logging.INFO)

# ファイルハンドラ
file_handler = logging.FileHandler(LOG_FILE, encoding="utf-8")
file_handler.setLevel(logging.INFO)
file_formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
file_handler.setFormatter(file_formatter)

# コンソールハンドラ
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_formatter = logging.Formatter("%(message)s")
console_handler.setFormatter(console_formatter)

# ハンドラを追加
logger.addHandler(file_handler)
logger.addHandler(console_handler)


def _play_sound(name: str = "Tink") -> None:
    """macOS標準サウンドを再生"""
    try:
        subprocess.Popen(
            ["afplay", f"/System/Library/Sounds/{name}.aiff"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except Exception:
        pass


def type_text(text: str) -> None:
    """
    テキストをアクティブウィンドウに直接入力。
    CoreGraphics APIでUnicodeキーイベントを送信。
    クリップボードを使用しない。
    """
    if not text:
        return

    time.sleep(0.1)

    for char in text:
        event_down = CGEventCreateKeyboardEvent(None, 0, True)
        CGEventKeyboardSetUnicodeString(event_down, len(char), char)
        CGEventPost(kCGHIDEventTap, event_down)

        event_up = CGEventCreateKeyboardEvent(None, 0, False)
        CGEventKeyboardSetUnicodeString(event_up, len(char), char)
        CGEventPost(kCGHIDEventTap, event_up)

        time.sleep(0.01)


class VoiceInputEngine:
    """音声入力エンジン（録音・文字起こし・テキスト入力を統合管理）"""

    def __init__(
        self,
        whisper: Union[WhisperTranscriber, GoogleSpeechTranscriber],
        gemini: GeminiCorrector,
        app: Optional[Any] = None,
    ) -> None:
        self.whisper = whisper
        self.gemini = gemini
        self.app = app
        self.is_recording: bool = False
        self.audio_chunks: List[npt.NDArray[np.float32]] = []
        self.stream: Optional[sd.InputStream] = None
        self._lock = threading.Lock()

    def start_keyboard_listener(self) -> keyboard.Listener:
        """キーボードリスナーを起動"""
        def on_press(key: Union[Key, KeyCode, None]) -> None:
            if key == config.hotkey:
                self.start_recording()

        def on_release(key: Union[Key, KeyCode, None]) -> None:
            if key == config.hotkey:
                if self.is_recording:
                    self.stop_recording()

        listener = keyboard.Listener(on_press=on_press, on_release=on_release)
        listener.start()
        return listener

    def _create_audio_stream(self) -> sd.InputStream:
        """オーディオストリームを作成"""
        def audio_callback(
            indata: npt.NDArray[np.float32],
            _frames: int,
            _time_info: Any,
            status: sd.CallbackFlags,
        ) -> None:
            if status:
                print(f"Audio: {status}")
            self.audio_chunks.append(indata.copy())

        return sd.InputStream(
            samplerate=config.sample_rate,
            channels=1,
            dtype="float32",
            callback=audio_callback,
        )

    def start_recording(self) -> None:
        """録音を開始"""
        with self._lock:
            if self.is_recording:
                return
            self.is_recording = True
            self.audio_chunks = []

        _play_sound("Tink")
        if self.app:
            self.app.set_recording()

        self.stream = self._create_audio_stream()
        self.stream.start()

    def stop_recording(self) -> None:
        """録音を停止し、文字起こしを開始"""
        with self._lock:
            if not self.is_recording:
                return
            self.is_recording = False

        if self.stream:
            self.stream.stop()
            self.stream.close()
            self.stream = None

        _play_sound("Pop")

        if not self.audio_chunks:
            if self.app:
                self.app.set_idle()
            return

        audio = np.concatenate(self.audio_chunks).flatten()
        duration = len(audio) / config.sample_rate

        if duration < config.min_duration:
            if self.app:
                self.app.set_idle()
            return

        threading.Thread(
            target=self._transcribe_and_type, args=(audio,), daemon=True
        ).start()

    def _transcribe_and_type(self, audio: npt.NDArray[np.float32]) -> None:
        """音声を文字起こしして入力"""
        if self.app:
            self.app.set_processing()

        try:
            text = self.whisper.transcribe(audio)
            print(f"[STT] {text}")

            if self.gemini.enabled and text:
                text = self.gemini.correct(text)

            if text:
                print(f"{text}")
                time.sleep(0.1)
                type_text(text)

        except Exception as e:
            print(f"エラー: {e}")
            if self.app:
                self.app.set_error(str(e)[:30])
                time.sleep(2)
        finally:
            if self.app:
                self.app.set_idle()
