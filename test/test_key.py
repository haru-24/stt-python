"""キー検出テスト - アクセシビリティ権限の確認用"""
from pynput import keyboard
from pynput.keyboard import Key
import time

print("=" * 40)
print("キー検出テスト（10秒間）")
print("何かキーを押してください")
print("左Optionキーも試してください")
print("=" * 40)

def on_press(key):
    print(f"  [押] {key}")

def on_release(key):
    print(f"  [離] {key}")

listener = keyboard.Listener(on_press=on_press, on_release=on_release)
listener.start()

try:
    for i in range(10, 0, -1):
        print(f"  残り {i}秒...", end="\r")
        time.sleep(1)
except KeyboardInterrupt:
    pass

listener.stop()
print("\nテスト終了")
