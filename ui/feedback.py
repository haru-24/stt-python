"""
ユーザーフィードバック（音声通知）
"""
import subprocess


def play_sound(name: str = "Tink") -> None:
    """macOS標準サウンドを再生"""
    try:
        subprocess.Popen(
            ["afplay", f"/System/Library/Sounds/{name}.aiff"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except Exception:
        pass
