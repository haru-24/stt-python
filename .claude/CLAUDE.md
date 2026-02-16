# stt-python - Mac Push-to-Talk Voice Input Tool

You are a software engineer. You will develop, maintain, and operate this project. Please respond in Japanese.

## Project Overview

macOS用のPush-to-Talk音声入力ツール。右Commandキーを押している間だけ録音し、離すとWhisperで文字起こししてアクティブなウィンドウにテキスト入力する。

**Tech Stack:** Python 3.8+, faster-whisper, sounddevice, pynput, rumps (optional), pydantic, google-genai (optional)

## Architecture

`app/` パッケージに4ファイル + エントリポイント。1ファイル1クラス。依存関係は一方向（下→上）。

```
app/config.py   ← 依存なし（AppConfig）
app/whisper.py  ← config（WhisperTranscriber）
app/gemini.py   ← config（GeminiCorrector）
app/engine.py   ← config, whisper, gemini（VoiceInputEngine）
main.py         ← app（エントリポイント + VoiceInputApp）
```

### app/config.py
- `AppConfig`（Pydantic）: ホットキー、サンプルレート、モデル、Gemini設定
- グローバルインスタンス `config`

### app/whisper.py
- `WhisperTranscriber`: スレッドセーフ・遅延ロードでWhisperモデルを管理。`load()`, `transcribe(audio)`
- モジュールレベルインスタンス: `whisper`

### app/gemini.py
- `GeminiCorrector`: Gemini APIでテキスト補正。`enabled`, `correct(text)`
- モジュールレベルインスタンス: `gemini`

### app/engine.py
- `VoiceInputEngine`: 録音・文字起こし・テキスト入力を統合管理
  - `start_keyboard_listener()` - キーボード監視
  - `start_recording()` / `stop_recording()` - 録音制御
  - `_transcribe_and_type()` - バックグラウンド文字起こし
- `type_text()` - CoreGraphicsでテキスト入力
- `_play_sound()` - macOSサウンド再生

### main.py
- `VoiceInputApp(rumps.App)` - メニューバーUI（rumps利用可能時のみ）
- `main()` - エントリポイント

## Development Guidelines

### Coding Conventions
- Type Hints必須、docstringは日本語
- PascalCase（クラス）、snake_case（関数/変数）、UPPER_SNAKE_CASE（定数）
- プライベートは `_` prefix

### Testing

```bash
# インポートテスト
python -c "from app.config import config; from app.transcriber import whisper, gemini; from app.engine import VoiceInputEngine; print('OK')"

# 構文チェック
python -m py_compile app/config.py app/transcriber.py app/engine.py main.py

# pytest
python -m pytest test/ -v

# 統合テスト
python main.py
```

### Notes
- 設定は `app/config.py` に集約。ハードコーディング禁止
- スレッドセーフ: ロックで共有状態を保護
- 依存関係は一方向を維持
