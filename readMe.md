# M4A to MP3 & Speech Extractor

A GUI application that converts M4A audio files to MP3 format and extracts speech using OpenAI's Whisper model.

## Features

- Convert M4A, MP3, or WAV files to MP3 format
- Extract speech from audio files using Whisper
- User-friendly interface with progress indicators
- Supports Portuguese language transcription

## Requirements

- Python 3.x
- Tkinter (usually included with Python)
- Pydub (`pip install pydub`)
- FFmpeg (required by Pydub)
- OpenAI Whisper (`pip install openai-whisper`)

## Installation

1. Install Python 3.x from [python.org](https://www.python.org/downloads/)
2. Install required libraries:

```bash
pip install pydub openai-whisper
```

3. Install FFmpeg:
- On Windows: Download from [FFmpeg website](https://ffmpeg.org/) and add to PATH
- On macOS: `brew install ffmpeg`
- On Linux: `sudo apt install ffmpeg` (Debian/Ubuntu)

## Usage

1. Run the application:

```bash
python m4a_to_mp3_and_extract_speech.py
```

2. Select an input audio file (M4A, MP3, or WAV)
3. Choose an output path for MP3 conversion (optional)
4. Click "Convert to MP3" or "Extract Speech" as needed

## Notes

- For speech extraction, the application uses Whisper's "base" model
- Processing time depends on audio length and your system's performance
- The application will automatically load the Whisper model on startup

## License

This project is open source. Feel free to use and modify it.
