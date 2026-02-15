"""
クリップボードを使わずに直接テキスト入力をテスト
"""
import time
import pyautogui

print("5秒後に日本語テキストを直接入力します...")
print("ターミナルまたはテキストエディタをアクティブにしてください")
time.sleep(5)

# テストテキスト（日本語含む）
test_texts = [
    "Python",
    "こんにちは",
    "PythonでJSONをパースする",
    "Reactのコンポーネント",
]

for text in test_texts:
    print(f"\n入力中: {text}")
    try:
        pyautogui.write(text, interval=0.05)
        print("✅ 成功")
        time.sleep(1)
    except Exception as e:
        print(f"❌ エラー: {e}")

print("\n\nテスト完了！")
