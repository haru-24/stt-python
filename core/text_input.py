"""
テキスト入力処理
"""
import time
from Quartz.CoreGraphics import (
    CGEventCreateKeyboardEvent,
    CGEventKeyboardSetUnicodeString,
    CGEventPost,
    kCGHIDEventTap,
)


def type_text(text: str) -> None:
    """
    テキストをアクティブウィンドウに直接入力。
    CoreGraphics APIでUnicodeキーイベントを送信。
    クリップボードを使用しない。
    """
    if not text:
        return

    # 少し待ってから入力（フォーカス安定のため）
    time.sleep(0.1)

    for char in text:
        # キーダウンイベント
        event_down = CGEventCreateKeyboardEvent(None, 0, True)
        CGEventKeyboardSetUnicodeString(event_down, len(char), char)
        CGEventPost(kCGHIDEventTap, event_down)

        # キーアップイベント
        event_up = CGEventCreateKeyboardEvent(None, 0, False)
        CGEventKeyboardSetUnicodeString(event_up, len(char), char)
        CGEventPost(kCGHIDEventTap, event_up)

        time.sleep(0.01)
