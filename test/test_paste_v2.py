"""
keyDown/keyUp を使ったペーストのテスト
"""
import subprocess
import time
import pyautogui

# クリップボードにテキストをコピー
test_text = "print部分はSTTの結果だけにして"
print(f"クリップボードにコピー: {test_text}")
process = subprocess.Popen(["pbcopy"], stdin=subprocess.PIPE)
process.communicate(test_text.encode("utf-8"))

print("\n5秒後にCmd+Vを実行します...")
print("ターミナルをアクティブにしてください")
time.sleep(5)

print("Cmd+V 実行中...")
pyautogui.keyDown('command')
pyautogui.press('v')
pyautogui.keyUp('command')
print("完了！")
