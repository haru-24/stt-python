# PyVoiceDictation

macOS 用 Push-to-Talk 音声入力ツール。
右 Command キーを押している間だけ録音し、離すと音声をテキストに変換してアクティブなウィンドウへ自動入力します。

---

## 動作環境

- macOS 10.14 以上
- Python 3.10 以上
- [Poetry](https://python-poetry.org/)

---

## セットアップ

### 1. リポジトリをクローン

```bash
git clone <repository-url>
cd stt-python
```

### 2. 依存関係をインストール

```bash
poetry install
```

### 3. macOS の権限を許可

**システム設定 → プライバシーとセキュリティ** で以下を許可してください。

| 権限             | 用途             |
| ---------------- | ---------------- |
| マイク           | 音声録音         |
| アクセシビリティ | テキスト自動入力 |

### 4. 起動

```bash
make dev
# または
poetry run python main.py
```

メニューバーにマイクアイコンが表示されれば起動完了です。

---

## 使い方

| 操作                           | 動作                                    |
| ------------------------------ | --------------------------------------- |
| 右 Command を押したまま話す    | 録音開始                                |
| 右 Command を離す              | 文字起こし → アクティブウィンドウへ入力 |
| メニューバーアイコンをクリック | 設定・サウンドON/OFF・終了              |

---

## 設定

### STT バックエンド

`.env` ファイルをプロジェクトルートに作成して設定します。

```env
# Google Speech（デフォルト・インターネット必須）
STT_BACKEND=google

# Whisper（オフライン・初回モデルダウンロードあり）
STT_BACKEND=whisper
```

### Gemini 補正機能（任意）

音声認識結果を AI で補正する機能です。
**アプリ内の設定画面（⚙️ 設定タブ）から API キーとモデルを設定できます。**

設定しない場合は補正機能が無効になります。

> **`.env` で設定する場合**
>
> ```env
> GEMINI_API_KEY=your_api_key_here
> GEMINI_MODEL=gemini-2.0-flash
> ```
>
> GUI で保存した値は `.env` より優先されます。

---

## ファイル構成

```
app/
  config.py          # 設定管理（Pydantic）
  engine.py          # 録音・文字起こし・入力の統合
  gemini.py          # Gemini 補正
  whisper.py         # Whisper 文字起こし
  google_speech.py   # Google Speech 文字起こし
  word_replacement.py# ワード変換ルール
ui/
  settings_window.py # 設定 UI（PyQt6）
main.py              # エントリポイント
config/
  settings.json      # アプリ設定（自動生成）
__generated__/
  prompts.json       # Gemini プロンプト（自動生成）
  word_replacement.csv # ワード変換ルール（自動生成）
```

ログ: `~/.sst-python/logs/voice_input.log`

---

## 開発

```bash
# 起動
make dev

# 構文チェック
poetry run python -m py_compile app/*.py main.py

# テスト
poetry run python -m pytest test/ -v

# パッケージ追加
poetry add <package>
```

### .app バンドルのビルド（配布用）

```bash
# .app を生成
make build

# DMG を生成
make dist
```

---

## トラブルシューティング

| 症状                   | 対処                                                    |
| ---------------------- | ------------------------------------------------------- |
| 録音されない           | システム設定でマイク権限を許可                          |
| テキストが入力されない | システム設定でアクセシビリティ権限を許可                |
| 文字起こしが遅い       | Whisper 使用時は `tiny` / `base` モデルへ変更           |
| Gemini 補正が動かない  | 設定画面で API キーとモデルが正しく入力されているか確認 |

### サンプルプロンプト

```
補正ルール：
  - プログラミング・技術用語のカタカナ読みを正しい英語表記に直す
    例：ジムニー→Gemini、パイソン→Python、ジャバスクリプト→JavaScript、
        ドッカー→Docker、ギットハブ→GitHub、エーピーアイ→API、
        リアクト→React、タイプスクリプト→TypeScript
  - 明らかな誤変換・誤認識を文脈から推測して修正する
  - 語尾は変換しない、して->して、やって->やって, NG して->します、やります->やって
  - 。はつけない、疑問系は?をつける
  - 自然な日本語に整える（ただし意味は変えない）
  - 補正不要な場合はそのまま出力する
以下のテキストを補正してください。補正後のテキストのみを出力してください：
{text}
```
