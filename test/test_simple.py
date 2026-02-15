"""
シンプルなキーボード入力テスト
"""
import time
import pyautogui

print("現在のアクセシビリティ権限状況をテストします")
print("3秒後に 'a' キーを押します...")
time.sleep(3)

try:
    print("キー入力実行中...")
    pyautogui.press('a')
    print("✅ 成功！'a'キーが押されました")
except Exception as e:
    print(f"❌ エラー: {e}")

print("\n次に、3秒後に 'hello' とタイプします...")
time.sleep(3)

try:
    print("タイプ実行中...")
    pyautogui.typewrite('hello', interval=0.1)
    print("✅ 成功！'hello'がタイプされました")
except Exception as e:
    print(f"❌ エラー: {e}")
