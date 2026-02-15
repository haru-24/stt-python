"""
Cmd+V (ペースト) のテスト
"""
import subprocess
import time
import pyautogui

# まずクリップボードにテキストをコピー
test_text = "🎉 ペーストテスト成功！Python、JSON、React"
print(f"クリップボードにコピー: {test_text}")
process = subprocess.Popen(["pbcopy"], stdin=subprocess.PIPE)
process.communicate(test_text.encode("utf-8"))

print("\n5秒後にCmd+Vを実行します...")
print("ターミナルまたはテキストエディタをアクティブにしてください")
time.sleep(5)

print("Cmd+V 実行中...")
try:
    # 方法1: hotkey
    pyautogui.hotkey('command', 'v')
    print("✅ pyautogui.hotkey('command', 'v') 実行完了")
except Exception as e:
    print(f"❌ エラー: {e}")

time.sleep(1)

# 確認
result = subprocess.run(["pbpaste"], capture_output=True, text=True)
print(f"\nクリップボードの内容: {result.stdout}")
