"""
Whisperモデルによる音声認識
"""
import threading
from typing import Optional, Any

import numpy as np
import numpy.typing as npt

from app.config import config


class WhisperTranscriber:
    """Whisperモデルによる音声認識（スレッドセーフ・遅延ロード）"""

    def __init__(self) -> None:
        self._model: Optional[Any] = None
        self._lock = threading.Lock()

    def load(self) -> None:
        """モデルを事前ロード"""
        self._get_model()

    def _get_model(self) -> Any:
        """モデルを取得（遅延ロード・ダブルチェックロッキング）"""
        if self._model is None:
            with self._lock:
                if self._model is None:
                    from faster_whisper import WhisperModel
                    self._model = WhisperModel(
                        config.whisper_model,
                        device="cpu",
                        compute_type="int8",
                    )
        return self._model

    def transcribe(self, audio: npt.NDArray[np.float32]) -> str:
        """音声データをテキストに変換"""
        model = self._get_model()
        segments, _info = model.transcribe(
            audio,
            language=config.language,
            beam_size=5,
            vad_filter=True,
        )
        return "".join(seg.text for seg in segments).strip()
