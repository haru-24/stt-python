"""
アプリケーション設定
"""
from pydantic import BaseModel, Field, field_validator
from pynput.keyboard import Key


class AppConfig(BaseModel):
    """アプリケーション設定"""
    hotkey: Key = Field(default=Key.cmd_r, description="録音用ホットキー")
    sample_rate: int = Field(default=16000, ge=8000, le=48000, description="サンプリングレート")
    whisper_model: str = Field(default="base", description="Whisperモデル")
    language: str = Field(default="ja", description="言語")
    min_duration: float = Field(default=0.3, ge=0.1, description="最小録音時間（秒）")

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
