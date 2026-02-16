"""
Google Speech Recognition APIによる音声認識
"""
import threading
from typing import Optional

import numpy as np
import numpy.typing as npt
import speech_recognition as sr

from app.config import config


class GoogleSpeechTranscriber:
    """Google Speech Recognition APIによる音声認識（スレッドセーフ）"""

    def __init__(self) -> None:
        self._recognizer: Optional[sr.Recognizer] = None
        self._lock = threading.Lock()

    def load(self) -> None:
        """認識エンジンを事前初期化"""
        self._get_recognizer()

    def _get_recognizer(self) -> sr.Recognizer:
        """認識エンジンを取得（遅延ロード・ダブルチェックロッキング）"""
        if self._recognizer is None:
            with self._lock:
                if self._recognizer is None:
                    self._recognizer = sr.Recognizer()
                    print("[Google Speech] 認識エンジンの初期化完了")
        return self._recognizer

    def transcribe(self, audio: npt.NDArray[np.float32]) -> str:
        """音声データをテキストに変換"""
        recognizer = self._get_recognizer()

        # numpy float32配列 -> int16 bytes -> AudioData
        # SpeechRecognitionは16-bit PCMを期待
        audio_int16 = (audio * 32767).astype(np.int16)
        audio_bytes = audio_int16.tobytes()

        # AudioData作成 (sample_width=2は16-bit PCM)
        audio_data = sr.AudioData(audio_bytes, config.sample_rate, 2)

        try:
            # Google Speech Recognition APIで認識
            # 言語コードを "ja" -> "ja-JP" に変換
            language_code = config.language
            if language_code == "ja":
                language_code = "ja-JP"
            elif language_code == "en":
                language_code = "en-US"

            text = recognizer.recognize_google(audio_data, language=language_code)
            return text.strip()

        except sr.UnknownValueError:
            print("[Google Speech] 音声を認識できませんでした")
            return ""
        except sr.RequestError as e:
            print(f"[Google Speech] APIエラー: {e}")
            return ""
