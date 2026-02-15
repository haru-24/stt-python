"""
テキスト入力処理
"""
import subprocess
import time
from pynput.keyboard import Controller, Key


def type_text(text: str) -> None:
    """
    テキストをアクティブウィンドウに入力。
    日本語対応のため、pbcopy + Cmd+V (ペースト) を使用。
    pynput.type() は日本語非対応のため。
    """
    kb = Controller()

    # デバッグ: 入力するテキストを表示
    print(f"[DEBUG] type_text() 呼び出し: text='{text}'")

    # クリップボードに保存
    process = subprocess.Popen(
        ["pbcopy"],
        stdin=subprocess.PIPE,
    )
    process.communicate(text.encode("utf-8"))
    print(f"[DEBUG] クリップボードにコピー完了")

    # Cmd+V でペースト（タイミングを調整）
    time.sleep(0.2)  # 0.05秒 → 0.2秒に増やす
    print(f"[DEBUG] Cmd+V 実行中...")
    kb.press(Key.cmd)
    kb.press("v")
    kb.release("v")
    kb.release(Key.cmd)
    print(f"[DEBUG] Cmd+V 完了")
