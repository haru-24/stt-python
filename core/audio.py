"""
音声録音処理
"""
from typing import List, Any, Optional
import numpy as np
import numpy.typing as npt
import sounddevice as sd
from config.settings import config


def create_audio_stream(
    audio_chunks: List[npt.NDArray[np.float32]]
) -> sd.InputStream:
    """
    オーディオストリームを作成。

    Args:
        audio_chunks: 録音データを格納するリスト（参照渡し）

    Returns:
        作成されたInputStreamオブジェクト
    """
    def audio_callback(
        indata: npt.NDArray[np.float32],
        _frames: int,
        _time_info: Any,
        status: sd.CallbackFlags
    ) -> None:
        if status:
            print(f"⚠️ Audio: {status}")
        audio_chunks.append(indata.copy())

    stream = sd.InputStream(
        samplerate=config.sample_rate,
        channels=1,
        dtype="float32",
        callback=audio_callback,
    )
    return stream
