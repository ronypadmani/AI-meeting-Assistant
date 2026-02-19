# Audio to Text Converter Guide

This guide explains how to convert your raw audio recordings to text using the audio_to_text.py script.

## Overview

The audio_to_text.py script converts raw audio files (.raw) captured by the audio streaming system into text files using speech recognition technology.

## Features

- Converts raw audio to WAV format automatically
- Supports multiple speech recognition engines:
  - **Google Speech Recognition** (free, requires internet)
  - **OpenAI Whisper** (local processing, more accurate but requires model download)
- Saves transcriptions with metadata in organized text files
- Batch processing of multiple audio files
- Command-line interface with various options

## Usage

### Basic Usage (Process All Audio Files)

```bash
# Using Google Speech Recognition (recommended for quick results)
python audio_to_text.py --method speech_recognition

# Using OpenAI Whisper (more accurate but slower)
python audio_to_text.py --method whisper --model-size base
```

### Process Specific File

```bash
# Process a single audio file
python audio_to_text.py --file audio_recordings/meeting_audio_20250919_000119.raw --method speech_recognition
```

### Advanced Options

```bash
# Use different Whisper model sizes (tiny, base, small, medium, large)
python audio_to_text.py --method whisper --model-size small

# Clean up temporary WAV files after processing
python audio_to_text.py --method speech_recognition --cleanup

# Combine options
python audio_to_text.py --method whisper --model-size base --cleanup
```

## Command Line Arguments

- `--method`: Choose transcription method
  - `speech_recognition`: Google Web Speech API (free, internet required)
  - `whisper`: OpenAI Whisper (local processing, no internet required after model download)
- `--model-size`: Whisper model size (tiny, base, small, medium, large)
  - Larger models are more accurate but slower
  - Default: "base"
- `--cleanup`: Delete temporary WAV files after transcription
- `--file`: Process a specific raw audio file instead of all files

## Output

Transcriptions are saved in the `transcriptions/` directory with the following format:
- Filename: `{original_filename}_{method}_{timestamp}.txt`
- Content includes:
  - Original audio file path
  - Transcription method used
  - Transcription timestamp
  - The transcribed text

## File Structure

```
r:\MSBC/
├── audio_recordings/          # Raw audio files (.raw)
│   ├── meeting_audio_20250919_000119.raw
│   └── meeting_audio_20250919_000134.raw
├── transcriptions/            # Generated text files (.txt)
│   └── meeting_audio_20250919_000119_speech_recognition_20250919_000450.txt
└── audio_to_text.py           # Main conversion script
```

## Troubleshooting

### Whisper Model Download Issues
If Whisper fails to load the model, try:
- Use a smaller model size (`--model-size tiny`)
- Ensure you have enough disk space (models range from 39MB to 2.9GB)
- Check internet connection for initial model download

### Speech Recognition Issues
If Google Speech Recognition fails:
- Check internet connection (requires online access)
- Audio quality might be too poor - try recording in a quieter environment
- Audio might be too short or contain only silence

### Audio Conversion Issues
If raw to WAV conversion fails:
- Check if raw audio files are corrupted
- Verify the audio was recorded with the expected format (float32, 16kHz, mono)
- Try playing the raw audio with audio software to verify it's valid

## Tips for Better Transcription

1. **Recording Quality**: Ensure clear audio with minimal background noise
2. **Speaker Distance**: Keep microphone close to speaker(s)
3. **Speech Clarity**: Speak clearly and at a moderate pace
4. **File Size**: Longer recordings may take more time to process
5. **Model Choice**: Use Whisper for better accuracy, Google Speech for speed

## Examples

```bash
# Quick transcription of all files
python audio_to_text.py --method speech_recognition

# High-quality transcription with cleanup
python audio_to_text.py --method whisper --model-size small --cleanup

# Process latest recording only
python audio_to_text.py --file audio_recordings/meeting_audio_20250919_000134.raw --method whisper
```

## Privacy Note

- **Google Speech Recognition**: Audio is sent to Google's servers for processing
- **OpenAI Whisper**: All processing happens locally on your computer (privacy-friendly)

Choose the method based on your privacy requirements and accuracy needs.