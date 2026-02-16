"""テキスト入力（CoreGraphics API）のテスト"""
from Quartz.CoreGraphics import (
    CGEventCreateKeyboardEvent,
    CGEventKeyboardSetUnicodeString,
)


def test_cg_event_creation() -> None:
    """CoreGraphics APIでキーイベントが作成できるか"""
    event = CGEventCreateKeyboardEvent(None, 0, True)
    assert event is not None


def test_unicode_event() -> None:
    """Unicode文字をキーイベントに設定できるか"""
    for char in ["P", "あ", "漢"]:
        event = CGEventCreateKeyboardEvent(None, 0, True)
        CGEventKeyboardSetUnicodeString(event, len(char), char)
        assert event is not None


def test_type_text_import() -> None:
    """type_text関数がインポートできるか"""
    from app.engine import type_text
    assert callable(type_text)
