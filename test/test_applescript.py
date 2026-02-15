"""
AppleScriptでテキスト入力をテスト
"""
import subprocess
import time

print("5秒後にテキストを入力します...")
print("ターミナルまたはテキストエディタをアクティブにしてください")
time.sleep(5)

# AppleScriptでテキスト入力
text = "テスト入力：Python、JSON、React"
script = f'tell application "System Events" to keystroke "{text}"'

print(f"入力中: {text}")
result = subprocess.run(['osascript', '-e', script], capture_output=True, text=True)

if result.returncode == 0:
    print("✅ 成功！")
else:
    print(f"❌ エラー: {result.stderr}")
