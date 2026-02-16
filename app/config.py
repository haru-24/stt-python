"""
アプリケーション設定
"""
import os
import json
import threading
from pathlib import Path
from pydantic import BaseModel, Field, field_validator, PrivateAttr
from pynput.keyboard import Key
from dotenv import load_dotenv

# 環境変数を読み込み
load_dotenv()

# デフォルトのGemini補正プロンプト
DEFAULT_PROMPT = """あなたはプログラミング用AIチャット向けの音声認識テキスト補正アシスタントです。
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


class AppConfig(BaseModel):
    """アプリケーション設定"""
    hotkey: Key = Field(default=Key.cmd_r, description="録音用ホットキー")
    sample_rate: int = Field(default=16000, ge=8000, le=48000, description="サンプリングレート")

    # STT バックエンド設定
    stt_backend: str = Field(
        default_factory=lambda: os.getenv("STT_BACKEND", "whisper"),
        description="STTバックエンド (whisper|google)"
    )

    # Whisper 設定
    whisper_model: str = Field(default="medium", description="Whisperモデル")
    whisper_compute_type: str = Field(default="float32", description="Whisper計算精度")
    whisper_initial_prompt: str = Field(
        default="Python、JavaScript、TypeScript、Docker、Git、SSH、API、JSON、React、Vue、Node.js、AWS、GitHub、VS Code",
        description="Whisperの認識ヒント用プロンプト",
    )

    language: str = Field(default="ja", description="言語")
    min_duration: float = Field(default=0.3, ge=0.1, description="最小録音時間（秒）")

    # Gemini API 設定
    gemini_api_key: str = Field(
        default_factory=lambda: os.getenv("GEMINI_API_KEY", ""),
        description="Gemini API キー"
    )
    gemini_model: str = Field(
        default_factory=lambda: os.getenv("GEMINI_MODEL", "gemini-2.0-flash-exp"),
        description="使用するGeminiモデル"
    )
    gemini_timeout: int = Field(
        default=5,
        ge=1,
        le=30,
        description="APIタイムアウト時間（秒）"
    )
    gemini_prompt_file: Path = Field(
        default=Path(__file__).parent.parent / "config" / "prompts.json",
        description="プロンプト設定ファイルパス"
    )
    gemini_prompt: str = Field(default="", description="Gemini補正プロンプト")

    # プライベート属性
    _lock: threading.Lock = PrivateAttr(default_factory=threading.Lock)

    @property
    def gemini_enabled(self) -> bool:
        """Gemini補正機能の有効/無効（APIキーが設定されていれば自動的に有効）"""
        return bool(self.gemini_api_key)

    @field_validator("stt_backend")
    @classmethod
    def validate_stt_backend(cls, v: str) -> str:
        valid_backends = ["whisper", "google"]
        if v not in valid_backends:
            raise ValueError(f"STTバックエンドは {valid_backends} のいずれかである必要があります")
        return v

    @field_validator("whisper_model")
    @classmethod
    def validate_model(cls, v: str) -> str:
        valid_models = ["tiny", "base", "small", "medium", "large-v3"]
        if v not in valid_models:
            raise ValueError(f"モデルは {valid_models} のいずれかである必要があります")
        return v

    def model_post_init(self, _context) -> None:
        """モデル初期化後の処理"""
        self._load_prompt()

    def _load_prompt(self) -> None:
        """プロンプトをJSONから読み込み、なければデフォルトを保存"""
        if not self.gemini_prompt_file.exists():
            self.gemini_prompt_file.parent.mkdir(parents=True, exist_ok=True)
            self._save_default_prompt()

        try:
            with open(self.gemini_prompt_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.gemini_prompt = data.get("current_prompt", DEFAULT_PROMPT)
        except (json.JSONDecodeError, IOError) as e:
            print(f"[設定] プロンプト読み込みエラー、デフォルトを使用: {e}")
            self.gemini_prompt = DEFAULT_PROMPT
            self._save_default_prompt()

    def _save_default_prompt(self) -> None:
        """デフォルトプロンプトをJSONに保存"""
        data = {
            "current_prompt": DEFAULT_PROMPT,
            "default_prompt": DEFAULT_PROMPT
        }
        with open(self.gemini_prompt_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def save_prompt(self, new_prompt: str) -> None:
        """新しいプロンプトを保存してリロード（スレッドセーフ）"""
        with self._lock:
            try:
                with open(self.gemini_prompt_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
            except (json.JSONDecodeError, IOError):
                data = {"default_prompt": DEFAULT_PROMPT}

            data["current_prompt"] = new_prompt
            with open(self.gemini_prompt_file, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            self.gemini_prompt = new_prompt

    def reset_prompt_to_default(self) -> str:
        """プロンプトをデフォルトにリセット"""
        with self._lock:
            try:
                with open(self.gemini_prompt_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                default = data.get("default_prompt", DEFAULT_PROMPT)
            except (json.JSONDecodeError, IOError):
                default = DEFAULT_PROMPT

            self.save_prompt(default)
            return default

    class Config:
        arbitrary_types_allowed = True


# グローバル設定インスタンス
config = AppConfig()
