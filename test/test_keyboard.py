"""
キーボード入力のテスト
"""
import time
from pynput.keyboard import Controller, Key

print("5秒後にCmd+Vを実行します...")
print("このウィンドウをアクティブにして待ってください")
time.sleep(5)

kb = Controller()
print("Cmd+V 実行中...")
kb.press(Key.cmd)
time.sleep(0.01)
kb.press("v")
time.sleep(0.01)
kb.release("v")
time.sleep(0.01)
kb.release(Key.cmd)
print("完了！")
