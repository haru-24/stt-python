"""
Gemini APIによるテキスト補正
"""
import threading
from typing import Optional, Any

from app.config import config


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

    def correct(self, text: str) -> str:
        """Whisper出力をGemini APIで補正する"""
        if not text.strip():
            return text

        if not config.gemini_api_key:
            return text

        try:
            from google.genai import types

            client = self._get_client()

            prompt = f"""あなたはプログラミング用AIチャット向けの音声認識テキスト補正アシスタントです。
Whisperで生成された日本語テキストを、技術用語を正確に表記しながら自然な日本語に補正してください。

補正ルール:
1. プログラミング用語は正式な英語表記に変換（例：「ぱいそん」→「Python」）
2. 略語や頭字語は大文字表記（例：「えすえすえいち」→「SSH」）
3. 技術用語以外の日本語は自然な表記に修正
4. 元の意図を保ちながら、過度な補正は避ける
5. 補正後のテキストのみを出力し、引用符や説明は一切含めないこと

補正例：
「ぱいそんでじぇそんをぱーすする」→ PythonでJSONをパースする
「りあくとのゆーずえふぇくとふっくをつかう」→ ReactのuseEffectフックを使う
「どっかーこんてなをきどうしてえすえすえいちでせつぞくする」→ DockerコンテナをきどうしてSSHで接続する
「じっと こみっと でへんこうをほぞんする」→ git commitで変更を保存する

以下のテキストを補正してください。補正後のテキストのみを出力してください：
{text}"""

            response = client.models.generate_content(
                model=config.gemini_model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.3,
                    max_output_tokens=500,
                )
            )

            if response.text:
                corrected_text = response.text.strip()
                if corrected_text:
                    return corrected_text

            return text

        except Exception as e:
            print(f"Gemini API エラー（元のテキストを使用）: {e}")
            return text
