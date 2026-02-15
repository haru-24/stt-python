"""
キーボードイベント監視
"""
from typing import Union, TYPE_CHECKING
from pynput import keyboard
from pynput.keyboard import Key, KeyCode
from config.settings import config

if TYPE_CHECKING:
    from core.engine import VoiceInputEngine


def run_keyboard_listener(engine: "VoiceInputEngine") -> keyboard.Listener:
    """キーボードリスナーを起動"""
    def on_press(key: Union[Key, KeyCode, None]) -> None:
        if key == config.hotkey:
            engine.start_recording()

    def on_release(key: Union[Key, KeyCode, None]) -> None:
        if key == config.hotkey:
            if engine.is_recording:
                engine.stop_recording()

    listener = keyboard.Listener(on_press=on_press, on_release=on_release)
    listener.start()
    return listener
