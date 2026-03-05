"""
Gemini APIによるテキスト補正
"""
import logging
import threading
from typing import Optional, Any

from app.config import config

logger = logging.getLogger(__name__)


class GeminiCorrector:
    """Gemini APIによるテキスト補正（スレッドセーフ・遅延ロード）"""

    def __init__(self) -> None:
        self._client: Optional[Any] = None
        self._lock = threading.Lock()

    @property
    def enabled(self) -> bool:
        """Gemini補正が利用可能かどうか"""
        return config.gemini_enabled

    def _get_client(self) -> Any:
        """クライアントを取得（遅延ロード・ダブルチェックロッキング）"""
        if self._client is None:
            with self._lock:
                if self._client is None:
                    from google import genai
                    self._client = genai.Client(api_key=config.gemini_api_key)
        return self._client

    def reset_client(self) -> None:
        """APIキー変更時にクライアントをリセット"""
        with self._lock:
            self._client = None
            logger.debug("[Gemini] クライアントをリセットしました")

    def correct(self, text: str) -> str:
        """音声認識テキストをGemini APIで補正する"""
        if not text.strip():
            return text

        if not config.gemini_api_key:
            return text

        try:
            from google.genai import types

            client = self._get_client()
            prompt = config.gemini_prompt.replace("{text}", text)

            response = client.models.generate_content(
                model=config.gemini_model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.3,
                    max_output_tokens=500,
                    http_options=types.HttpOptions(timeout=config.gemini_timeout * 1000),
                )
            )

            if response.text:
                corrected_text = response.text.strip()
                if corrected_text:
                    return corrected_text

            return text

        except Exception as e:
            logger.error(f"[Gemini] APIエラー（元のテキストを使用）: {e}")
            return text


gemini = GeminiCorrector()
