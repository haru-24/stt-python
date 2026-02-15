"""
Gemini APIを使用したテキスト補正モジュール
"""
import threading
from typing import Optional
from google import genai
from google.genai import types

from config.settings import config


# シングルトンパターン
_client: Optional[genai.Client] = None
_client_lock = threading.Lock()


def get_gemini_client() -> genai.Client:
    """
    Gemini APIクライアントを取得（シングルトン）

    Returns:
        genai.Client: Geminiクライアントインスタンス
    """
    global _client

    if _client is not None:
        return _client

    with _client_lock:
        # ダブルチェックロッキング
        if _client is not None:
            return _client

        # クライアントを初期化
        _client = genai.Client(api_key=config.gemini_api_key)

        return _client


def correct_with_gemini(text: str) -> str:
    """
    Whisper出力をGemini APIで補正する

    Args:
        text: Whisperで生成されたテキスト

    Returns:
        str: Geminiで補正されたテキスト（エラー時は元のテキスト）
    """
    if not text.strip():
        return text

    if not config.gemini_api_key:
        print("⚠️ GEMINI_API_KEY が設定されていません")
        return text

    try:
        client = get_gemini_client()

        # Few-shotプロンプト
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

        # API呼び出し
        response = client.models.generate_content(
            model=config.gemini_model,
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.3,  # 低めの値で正確性重視
                max_output_tokens=500,
            )
        )

        # レスポンスの検証
        if response.text:
            corrected_text = response.text.strip()
            if corrected_text:
                print(f"🔧 Gemini補正: 「{text}」→「{corrected_text}」")
                return corrected_text

        print(f"⚠️ Gemini APIから空のレスポンス（元のテキストを使用）")
        return text

    except Exception as e:
        print(f"⚠️ Gemini API エラー（元のテキストを使用）: {e}")
        return text
