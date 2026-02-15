"""
Whisperモデル管理
"""
import threading
from typing import Optional, Any
from config.settings import config

# グローバル変数（シングルトンパターン）
_model: Optional[Any] = None
_model_lock = threading.Lock()


def get_model() -> Any:
    """Whisperモデルをシングルトンパターンで取得"""
    global _model
    if _model is None:
        with _model_lock:
            if _model is None:
                print(f"🔄 Whisperモデル ({config.whisper_model}) をロード中...")
                from faster_whisper import WhisperModel
                _model = WhisperModel(
                    config.whisper_model,
                    device="cpu",       # Apple Silicon: "auto" でも可
                    compute_type="int8" # CPU向け最適化
                )
                print("✅ モデルロード完了")
    return _model
