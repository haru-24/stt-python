"""
CoreGraphics APIを使ったUnicodeテキスト直接入力テスト
クリップボードを使わない方法
"""
import time
import Quartz


def type_unicode(text: str) -> None:
    """CoreGraphics APIでUnicodeテキストを直接入力"""
    for char in text:
        # キーダウンイベント
        event_down = Quartz.CGEventCreateKeyboardEvent(None, 0, True)
        Quartz.CGEventKeyboardSetUnicodeString(event_down, len(char), char)
        Quartz.CGEventPost(Quartz.kCGHIDEventTap, event_down)

        # キーアップイベント
        event_up = Quartz.CGEventCreateKeyboardEvent(None, 0, False)
        Quartz.CGEventKeyboardSetUnicodeString(event_up, len(char), char)
        Quartz.CGEventPost(Quartz.kCGHIDEventTap, event_up)

        time.sleep(0.01)


print("5秒後に日本語テキストを直接入力します...")
print("ターミナルをアクティブにしてください")
time.sleep(5)

test_text = "PythonでJSONをパースする"
print(f"\n入力中: {test_text}")
type_unicode(test_text)
print("\n\n完了！")
