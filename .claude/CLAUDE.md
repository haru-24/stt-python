# sst-python - Mac Push-to-Talk Voice Input Tool

You are a software engineer. You will develop, maintain, and operate this project. Please respond in Japanese.

## Project Overview

This project is a Push-to-Talk voice input tool for macOS. It records audio only while the right Command key is pressed, transcribes it using the Whisper AI model when released, and inputs the text into the active window.

**Main Use Cases:**

- Command input in Terminal
- Voice-based prompt input in Claude Code
- Voice input in text editors

**Tech Stack:**

- Python 3.8+
- Whisper (faster-whisper) - Speech recognition
- sounddevice - Audio recording
- pynput - Keyboard control
- rumps - macOS menu bar UI (optional)
- pydantic - Strict typing

---

## Architecture Design

### Design Principles

1. **Single Responsibility Principle**: Each module has one clear role
2. **Clear Dependencies**: Unidirectional dependencies from lower to upper layers
3. **Testability**: Each module can be tested independently
4. **Simplicity First**: Avoid over-abstraction

**Important:** To avoid circular dependencies, `core/keyboard.py` uses `TYPE_CHECKING` to reference `engine` only for type hints.

---

### main.py

- **Role:** Application entry point
- **Process Flow:**
  1. Load settings and model
  2. Launch `VoiceInputApp` if UI available, otherwise CLI mode
  3. Start `VoiceInputEngine` and `keyboard.Listener`
  4. Main loop (rumps.App.run() or infinite loop)

---

## Important Implementation Details

### 2. Thread Safety

**Locations:**

- `model/whisper.py`: `_model_lock` protects singleton initialization
- `core/engine.py`: `_lock` protects recording state changes

**Reason:** Keyboard events fire from separate threads

### 3. Lazy Loading

**Location:** `get_model()` in `model/whisper.py`

**Reasons:**

- faster-whisper model loading takes several seconds
- Load on first startup, reuse thereafter
- Memory efficient

### 4. VAD Filter

**Location:** `model.transcribe()` in `core/engine.py`

```python
segments, _info = model.transcribe(
    audio,
    language=config.language,
    beam_size=5,
    vad_filter=True,  # Auto-filter silent parts
)
```

**Effect:** Removes noise and silence, improving recognition accuracy

---

## Development Guidelines

### Coding Conventions

1. **Type Hints Required**: Add type annotations to all functions and methods
2. **Docstrings**: Write docstrings in Japanese for public functions
3. **Naming Conventions:**
   - Classes: PascalCase (`VoiceInputEngine`)
   - Functions/Variables: snake_case (`get_model`, `audio_chunks`)
   - Constants: UPPER_SNAKE_CASE (`HAS_RUMPS`)
   - Private Methods: `_` prefix (`_transcribe_and_type`)

4. **Import Order:**

   ```python
   # Standard library
   import threading
   import time

   # Third-party
   import numpy as np
   from pynput import keyboard

   # Local
   from config.settings import config
   from model.whisper import get_model
   ```

### Notes for Adding New Features

1. **Check Dependencies**: Maintain unidirectional flow from lower to upper layers
2. **Avoid Circular Imports**: Use `TYPE_CHECKING` if necessary
3. **Centralize Settings in `config/settings.py`**: No hardcoding
4. **Consider Thread Safety**: Use locks for shared state

### Testing Recommendations

```bash
# Import test
python -c "from config.settings import config; from model.whisper import get_model; print('OK')"

# Settings test
python -c "from config.settings import config; print(config.whisper_model)"

# Syntax check
python -m py_compile config/*.py model/*.py core/*.py ui/*.py main.py

# Integration test
python main.py
```
