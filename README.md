# stt-python

macOS push-to-talk voice input tool. Hold right Command key to record, release to transcribe and type.

## Requirements

- macOS 10.14+
- Python 3.8+
- Microphone and Accessibility permissions

## Installation

```bash
git clone <repository-url>
cd sst-python
pip install -r requirements.txt
```

Grant permissions: **System Settings > Privacy & Security > Accessibility**

## Usage

```bash
python main.py
```

**Voice Input**: Hold right Command → Speak → Release

**Menu Bar**: Sound toggle, Settings, Quit

## Configuration

### STT Backend

```bash
# Use Whisper (default)
export STT_BACKEND=whisper

# Use Google Speech
export STT_BACKEND=google
```

### Gemini Correction (Optional)

```bash
export GEMINI_API_KEY=your_api_key_here
```

### Settings Files

- `config/prompts.json` - Gemini prompts
- `config/settings.json` - App settings
- `~/.sst-python/logs/voice_input.log` - Logs

## Architecture

```
app/config.py          # Configuration (Pydantic)
app/whisper.py         # Whisper transcriber
app/google_speech.py   # Google Speech transcriber
app/gemini.py          # Gemini corrector
app/engine.py          # Voice input engine
ui/settings_window.py  # Settings UI (PyQt6)
main.py                # Entry point
```

**Dependencies**: config → transcribers/corrector → engine → main

## Development

```bash
# Test
python -m py_compile app/*.py ui/*.py main.py
python main.py

# Style
- Type hints required
- PascalCase (classes), snake_case (functions)
- Private members: _ prefix
```

## Troubleshooting

**No audio**: Grant microphone permissions
**No text input**: Grant accessibility permissions
**Slow transcription**: Use smaller Whisper model (`tiny` or `base`)

## License

Personal use project.
