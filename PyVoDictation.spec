# -*- mode: python ; coding: utf-8 -*-
import os, importlib.util

def _pkg_dir(name):
    spec = importlib.util.find_spec(name)
    if spec is None or spec.origin is None:
        raise RuntimeError(
            f"パッケージ '{name}' が見つかりません。\n"
            f"'poetry install' を実行してから 'make build' で再試行してください。"
        )
    return os.path.dirname(spec.origin)

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        (os.path.join(_pkg_dir('speech_recognition'), 'flac-mac'), 'speech_recognition'),
    ],
    hiddenimports=[
        'app',
        'ui',
        'pynput.keyboard._darwin',
        'pynput.mouse._darwin',
        'rumps',
        'sounddevice',
        'numpy',
        'google.genai',
        'dotenv',
        'speech_recognition',
        'PyQt6.QtCore',
        'PyQt6.QtGui',
        'PyQt6.QtWidgets',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['test'],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='PyVoDictation',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=False,
    name='PyVoDictation',
)

app = BUNDLE(
    coll,
    name='PyVoDictation.app',
    icon=None,  # アイコンがあれば 'assets/icon.icns' に設定
    bundle_identifier='com.local.pyo-vo-dictation',
    info_plist={
        'LSUIElement': True,  # Dockに表示しない（メニューバーアプリ）
        'CFBundleName': 'PyVoDictation',
        'CFBundleDisplayName': 'PyVoDictation',
        'CFBundleVersion': '1.0.0',
        'NSMicrophoneUsageDescription': '音声入力のためマイクが必要です',
        'NSAppleEventsUsageDescription': 'テキスト入力のためアクセシビリティが必要です',
    },
)
