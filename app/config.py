"""
アプリケーション設定
"""
import os
from pydantic import BaseModel, Field, field_validator
from pynput.keyboard import Key
from dotenv import load_dotenv

# 環境変数を読み込み
load_dotenv()


class AppConfig(BaseModel):
    """アプリケーション設定"""
    hotkey: Key = Field(default=Key.cmd_r, description="録音用ホットキー")
    sample_rate: int = Field(default=16000, ge=8000, le=48000, description="サンプリングレート")
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

    @property
    def gemini_enabled(self) -> bool:
        """Gemini補正機能の有効/無効（APIキーが設定されていれば自動的に有効）"""
        return bool(self.gemini_api_key)

    @field_validator("whisper_model")
    @classmethod
    def validate_model(cls, v: str) -> str:
        valid_models = ["tiny", "base", "small", "medium", "large-v3"]
        if v not in valid_models:
            raise ValueError(f"モデルは {valid_models} のいずれかである必要があります")
        return v

    class Config:
        arbitrary_types_allowed = True


# グローバル設定インスタンス
config = AppConfig()
