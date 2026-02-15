"""テキスト入力（CoreGraphics API）のテスト"""
import pytest
import Quartz


def test_cg_event_creation() -> None:
    """CoreGraphics APIでキーイベントが作成できるか"""
    event = Quartz.CGEventCreateKeyboardEvent(None, 0, True)
    assert event is not None


def test_unicode_event() -> None:
    """Unicode文字をキーイベントに設定できるか"""
    for char in ["P", "あ", "漢"]:
        event = Quartz.CGEventCreateKeyboardEvent(None, 0, True)
        Quartz.CGEventKeyboardSetUnicodeString(event, len(char), char)
        assert event is not None


def test_type_text_import() -> None:
    """type_text関数がインポートできるか"""
    from core.text_input import type_text
    assert callable(type_text)
