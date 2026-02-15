"""
音声入力エンジン（中心処理）
"""
import threading
import time
from typing import Optional, List, Any
import numpy as np
import numpy.typing as npt
import sounddevice as sd

from config.settings import config
from model.whisper import get_model
from model.gemini import correct_with_gemini
from ui.feedback import play_sound
from core.audio import create_audio_stream
from core.text_input import type_text


class VoiceInputEngine:
    """音声入力エンジン"""
    app: Optional[Any]
    is_recording: bool
    audio_chunks: List[npt.NDArray[np.float32]]
    stream: Optional[sd.InputStream]
    _lock: threading.Lock

    def __init__(self, app: Optional[Any] = None) -> None:
        self.app = app
        self.is_recording = False
        self.audio_chunks = []
        self.stream = None
        self._lock = threading.Lock()

    def start_recording(self) -> None:
        """録音を開始"""
        with self._lock:
            if self.is_recording:
                return
            self.is_recording = True
            self.audio_chunks = []

        play_sound("Tink")  # 録音開始音
        if self.app:
            self.app.set_recording()

        self.stream = create_audio_stream(self.audio_chunks)
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

        play_sound("Pop")  # 録音終了音

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

        # バックグラウンドで文字起こし
        threading.Thread(target=self._transcribe_and_type, args=(audio,), daemon=True).start()

    def _transcribe_and_type(self, audio: npt.NDArray[np.float32]) -> None:
        """音声を文字起こしして入力"""
        if self.app:
            self.app.set_processing()

        try:
            model = get_model()
            segments, _info = model.transcribe(
                audio,
                language=config.language,
                beam_size=5,
                vad_filter=True,  # 無音部分をフィルタ
            )
            text = "".join(seg.text for seg in segments).strip()

            # Gemini補正（有効な場合）
            if config.gemini_enabled and text:
                text = correct_with_gemini(text)

            if text:
                print(f"{text}")
                time.sleep(0.1)
                type_text(text)

        except Exception as e:
            print(f"❌ エラー: {e}")
            if self.app:
                self.app.set_error(str(e)[:30])
                time.sleep(2)
        finally:
            if self.app:
                self.app.set_idle()
