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

    # クリップボードに保存
    process = subprocess.Popen(
        ["pbcopy"],
        stdin=subprocess.PIPE,
    )
    process.communicate(text.encode("utf-8"))

    # Cmd+V でペースト
    time.sleep(0.05)
    kb.press(Key.cmd)
    kb.press("v")
    kb.release("v")
    kb.release(Key.cmd)
