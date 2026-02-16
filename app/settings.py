"""
Geminiプロンプト設定ウィンドウ（PyQt6ベース）
"""
import sys
import multiprocessing
from pathlib import Path
from typing import Optional

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QTextCursor
from PyQt6.QtWidgets import (
    QApplication,
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QTextEdit,
    QPushButton,
    QMessageBox,
    QFrame,
    QTabWidget,
    QWidget,
)

from app.config import config

# ログファイルパス
LOG_FILE = Path.home() / ".sst-python" / "logs" / "voice_input.log"


class SettingsDialog(QDialog):
    """Geminiプロンプト設定ダイアログ"""

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("🥷🏻 音声入力設定")
        self.setMinimumSize(900, 700)
        self._setup_ui()

    def _setup_ui(self) -> None:
        """UIをセットアップ"""
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(10, 10, 10, 10)

        # タブウィジェット
        self.tabs = QTabWidget()
        self.tabs.setFont(QFont("Helvetica", 12))

        # 設定タブ
        settings_tab = self._create_settings_tab()
        self.tabs.addTab(settings_tab, "⚙️ 設定")

        # ログタブ
        log_tab = self._create_log_tab()
        self.tabs.addTab(log_tab, "📋 ログ")

        main_layout.addWidget(self.tabs)
        self.setLayout(main_layout)

    def _create_settings_tab(self) -> QWidget:
        """設定タブを作成"""
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(25, 25, 25, 25)

        # ヘッダー
        header = QLabel("🤖 Gemini 補正プロンプト設定")
        header.setFont(QFont("Helvetica", 18, QFont.Weight.Bold))
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(header)

        # 説明
        description = QLabel(
            "音声認識結果を補正するためのプロンプトを編集できます\n"
            "{text} の部分に音声認識結果が挿入されます"
        )
        description.setFont(QFont("Helvetica", 11))
        description.setAlignment(Qt.AlignmentFlag.AlignCenter)
        description.setStyleSheet("color: gray;")
        layout.addWidget(description)

        # 区切り線
        line1 = QFrame()
        line1.setFrameShape(QFrame.Shape.HLine)
        line1.setFrameShadow(QFrame.Shadow.Sunken)
        layout.addWidget(line1)

        # テキストエリア
        self.text_edit = QTextEdit()
        self.text_edit.setPlainText(config.gemini_prompt)
        self.text_edit.setFont(QFont("Monaco", 12))
        self.text_edit.setMinimumHeight(350)
        layout.addWidget(self.text_edit)

        # ステータスラベル
        self.status_label = QLabel("")
        self.status_label.setFont(QFont("Helvetica", 10))
        self.status_label.setStyleSheet("color: gray;")
        self.status_label.setMinimumHeight(20)
        layout.addWidget(self.status_label)

        # 区切り線
        line2 = QFrame()
        line2.setFrameShape(QFrame.Shape.HLine)
        line2.setFrameShadow(QFrame.Shadow.Sunken)
        layout.addWidget(line2)

        # ボタン群
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        # キャンセルボタン
        cancel_btn = QPushButton("✖️ キャンセル")
        cancel_btn.setMinimumSize(140, 40)
        cancel_btn.setFont(QFont("Helvetica", 12, QFont.Weight.Bold))
        cancel_btn.setStyleSheet(
            """
            QPushButton {
                background-color: #757575;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px;
            }
            QPushButton:hover {
                background-color: #616161;
            }
            QPushButton:pressed {
                background-color: #424242;
            }
        """
        )
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)

        # デフォルトに戻すボタン
        reset_btn = QPushButton("🔄 デフォルトに戻す")
        reset_btn.setMinimumSize(180, 40)
        reset_btn.setFont(QFont("Helvetica", 12, QFont.Weight.Bold))
        reset_btn.setStyleSheet(
            """
            QPushButton {
                background-color: #FF9800;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px;
            }
            QPushButton:hover {
                background-color: #F57C00;
            }
            QPushButton:pressed {
                background-color: #E65100;
            }
        """
        )
        reset_btn.clicked.connect(self._on_reset)
        button_layout.addWidget(reset_btn)

        # 保存ボタン
        save_btn = QPushButton("💾 保存")
        save_btn.setMinimumSize(140, 40)
        save_btn.setFont(QFont("Helvetica", 12, QFont.Weight.Bold))
        save_btn.setStyleSheet(
            """
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #388E3C;
            }
        """
        )
        save_btn.clicked.connect(self._on_save)
        button_layout.addWidget(save_btn)

        layout.addLayout(button_layout)
        widget.setLayout(layout)
        return widget

    def _create_log_tab(self) -> QWidget:
        """ログタブを作成"""
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(25, 25, 25, 25)

        # ヘッダー
        header = QLabel("📋 音声入力ログ")
        header.setFont(QFont("Helvetica", 18, QFont.Weight.Bold))
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(header)

        # 説明
        description = QLabel("音声認識と入力のログをリアルタイムで表示します")
        description.setFont(QFont("Helvetica", 11))
        description.setAlignment(Qt.AlignmentFlag.AlignCenter)
        description.setStyleSheet("color: gray;")
        layout.addWidget(description)

        # 区切り線
        line1 = QFrame()
        line1.setFrameShape(QFrame.Shape.HLine)
        line1.setFrameShadow(QFrame.Shadow.Sunken)
        layout.addWidget(line1)

        # ログテキストエリア
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setFont(QFont("Monaco", 11))
        self.log_text.setMinimumHeight(400)
        self.log_text.setStyleSheet(
            """
            QTextEdit {
                background-color: #1E1E1E;
                color: #D4D4D4;
                border: 1px solid #3E3E3E;
                border-radius: 5px;
                padding: 10px;
            }
        """
        )
        layout.addWidget(self.log_text)

        # ボタン群
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        # クリアボタン
        clear_btn = QPushButton("🗑️ クリア")
        clear_btn.setMinimumSize(140, 40)
        clear_btn.setFont(QFont("Helvetica", 12, QFont.Weight.Bold))
        clear_btn.setStyleSheet(
            """
            QPushButton {
                background-color: #F44336;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px;
            }
            QPushButton:hover {
                background-color: #D32F2F;
            }
            QPushButton:pressed {
                background-color: #B71C1C;
            }
        """
        )
        clear_btn.clicked.connect(self._on_clear_log)
        button_layout.addWidget(clear_btn)

        # 更新ボタン
        refresh_btn = QPushButton("🔄 更新")
        refresh_btn.setMinimumSize(140, 40)
        refresh_btn.setFont(QFont("Helvetica", 12, QFont.Weight.Bold))
        refresh_btn.setStyleSheet(
            """
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
            QPushButton:pressed {
                background-color: #0D47A1;
            }
        """
        )
        refresh_btn.clicked.connect(self._on_refresh_log)
        button_layout.addWidget(refresh_btn)

        layout.addLayout(button_layout)
        widget.setLayout(layout)

        # 初回ロード
        self._load_log()

        return widget

    def _on_save(self) -> None:
        """保存ボタンのコールバック"""
        new_prompt = self.text_edit.toPlainText().strip()

        if not new_prompt:
            self.status_label.setText("❌ エラー: プロンプトを入力してください")
            self.status_label.setStyleSheet("color: red;")
            return

        if "{text}" not in new_prompt:
            # 警告ダイアログ
            reply = QMessageBox.question(
                self,
                "警告",
                "プロンプトに {text} が含まれていません。\n"
                "音声認識結果が挿入されない可能性があります。\n\n"
                "保存しますか？",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No,
            )
            if reply != QMessageBox.StandardButton.Yes:
                return

        try:
            config.save_prompt(new_prompt)
            self.status_label.setText(
                "✅ プロンプトを保存しました。次回の音声入力から反映されます。"
            )
            self.status_label.setStyleSheet("color: #4CAF50;")
        except Exception as ex:
            self.status_label.setText(f"❌ エラー: 保存に失敗しました: {ex}")
            self.status_label.setStyleSheet("color: red;")

    def _on_reset(self) -> None:
        """デフォルトに戻すボタンのコールバック"""
        reply = QMessageBox.question(
            self,
            "確認",
            "プロンプトをデフォルトに戻しますか？\n\n" "現在の内容は失われます。",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            try:
                default_prompt = config.reset_prompt_to_default()
                self.text_edit.setPlainText(default_prompt)
                self.status_label.setText("✅ デフォルトプロンプトに戻しました")
                self.status_label.setStyleSheet("color: #4CAF50;")
            except Exception as ex:
                self.status_label.setText(f"❌ エラー: リセットに失敗しました: {ex}")
                self.status_label.setStyleSheet("color: red;")

    def _load_log(self) -> None:
        """ログファイルを読み込んで表示"""
        try:
            if LOG_FILE.exists():
                with open(LOG_FILE, "r", encoding="utf-8") as f:
                    log_content = f.read()
                    self.log_text.setPlainText(log_content)
                    # 最後の行にスクロール
                    cursor = self.log_text.textCursor()
                    cursor.movePosition(QTextCursor.MoveOperation.End)
                    self.log_text.setTextCursor(cursor)
            else:
                self.log_text.setPlainText("ログファイルがまだ作成されていません。\n音声入力を開始するとログが記録されます。")
        except Exception as ex:
            self.log_text.setPlainText(f"エラー: ログファイルの読み込みに失敗しました\n{ex}")

    def _on_refresh_log(self) -> None:
        """ログを更新"""
        self._load_log()

    def _on_clear_log(self) -> None:
        """ログをクリア"""
        reply = QMessageBox.question(
            self,
            "確認",
            "ログファイルをクリアしますか？\n\n" "この操作は元に戻せません。",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            try:
                if LOG_FILE.exists():
                    LOG_FILE.unlink()
                self.log_text.setPlainText("ログをクリアしました。")
            except Exception as ex:
                self.log_text.setPlainText(f"エラー: ログのクリアに失敗しました\n{ex}")


class SettingsWindow:
    """設定ウィンドウ管理クラス"""

    def __init__(self) -> None:
        self._window_process: Optional[multiprocessing.Process] = None
        self._is_open: bool = False

    def show(self) -> None:
        """設定ウィンドウを表示（既に開いている場合は無視）"""
        if self._is_open and self._window_process and self._window_process.is_alive():
            print("[設定] ウィンドウは既に開いています")
            return

        self._is_open = True
        # 別プロセスでGUIを実行
        self._window_process = multiprocessing.Process(
            target=_run_settings_window, daemon=True
        )
        self._window_process.start()


def _run_settings_window() -> None:
    """PyQt6ウィンドウを実行（別プロセス用）"""
    app = QApplication(sys.argv)
    dialog = SettingsDialog()
    dialog.exec()
    sys.exit()


# グローバルインスタンス
settings_window = SettingsWindow()
