#!/usr/bin/env python3
"""
Audio to Text Converter
Converts raw audio files to text using speech recognition
"""

import numpy as np
import soundfile as sf
import speech_recognition as sr
import whisper
import os
import glob
from datetime import datetime
import json

def convert_raw_to_wav(raw_file_path, sample_rate=16000, channels=1):
    """
    Convert raw audio file to WAV format
    
    Args:
        raw_file_path: Path to raw audio file
        sample_rate: Sample rate in Hz (default: 16000)
        channels: Number of channels (default: 1 for mono)
    
    Returns:
        Path to converted WAV file
    """
    try:
        # Read raw audio data (float32 format)
        with open(raw_file_path, 'rb') as f:
            raw_data = f.read()
        
        # Convert bytes to numpy array
        audio_data = np.frombuffer(raw_data, dtype=np.float32)
        
        # Create output WAV filename
        base_name = os.path.splitext(os.path.basename(raw_file_path))[0]
        wav_file_path = os.path.join(os.path.dirname(raw_file_path), f"{base_name}.wav")
        
        # Write as WAV file
        sf.write(wav_file_path, audio_data, sample_rate)
        
        print(f"✅ Converted {raw_file_path} to {wav_file_path}")
        return wav_file_path
        
    except Exception as e:
        print(f"❌ Error converting {raw_file_path}: {e}")
        return None

def transcribe_with_speech_recognition(wav_file_path):
    """
    Transcribe audio using SpeechRecognition library (Google Web Speech API)
    
    Args:
        wav_file_path: Path to WAV audio file
    
    Returns:
        Transcribed text or None if failed
    """
    try:
        recognizer = sr.Recognizer()
        
        with sr.AudioFile(wav_file_path) as source:
            audio_data = recognizer.record(source)
        
        print(f"🎤 Transcribing {wav_file_path} with Google Speech Recognition...")
        text = recognizer.recognize_google(audio_data)
        
        return text
        
    except sr.UnknownValueError:
        print(f"❌ Could not understand audio in {wav_file_path}")
        return None
    except sr.RequestError as e:
        print(f"❌ Error with speech recognition service: {e}")
        return None
    except Exception as e:
        print(f"❌ Error transcribing {wav_file_path}: {e}")
        return None

def transcribe_with_whisper(wav_file_path, model_size="base"):
    """
    Transcribe audio using OpenAI Whisper
    
    Args:
        wav_file_path: Path to WAV audio file
        model_size: Whisper model size (tiny, base, small, medium, large)
    
    Returns:
        Transcribed text or None if failed
    """
    try:
        print(f"🤖 Loading Whisper model '{model_size}'...")
        model = whisper.load_model(model_size)
        
        print(f"🎤 Transcribing {wav_file_path} with Whisper...")
        result = model.transcribe(wav_file_path)
        
        return result["text"]
        
    except Exception as e:
        print(f"❌ Error with Whisper transcription: {e}")
        return None

def save_transcription(text, audio_file_path, method="whisper"):
    """
    Save transcription to text file
    
    Args:
        text: Transcribed text
        audio_file_path: Path to original audio file
        method: Transcription method used
    """
    try:
        # Create output filename
        base_name = os.path.splitext(os.path.basename(audio_file_path))[0]
        output_dir = "transcriptions"
        os.makedirs(output_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        text_file_path = os.path.join(output_dir, f"{base_name}_{method}_{timestamp}.txt")
        
        # Save transcription with metadata
        with open(text_file_path, 'w', encoding='utf-8') as f:
            f.write(f"Audio File: {audio_file_path}\n")
            f.write(f"Transcription Method: {method}\n")
            f.write(f"Transcription Date: {datetime.now().isoformat()}\n")
            f.write("-" * 50 + "\n\n")
            f.write(text)
        
        print(f"💾 Transcription saved to: {text_file_path}")
        return text_file_path
        
    except Exception as e:
        print(f"❌ Error saving transcription: {e}")
        return None

def process_audio_files(method="whisper", model_size="base", cleanup_wav=False):
    """
    Process all raw audio files in the audio_recordings directory
    
    Args:
        method: Transcription method ('whisper' or 'speech_recognition')
        model_size: Whisper model size (if using whisper)
        cleanup_wav: Whether to delete temporary WAV files after transcription
    """
    audio_dir = "audio_recordings"
    
    if not os.path.exists(audio_dir):
        print(f"❌ Audio directory '{audio_dir}' not found!")
        return
    
    # Find all raw audio files
    raw_files = glob.glob(os.path.join(audio_dir, "*.raw"))
    
    if not raw_files:
        print(f"❌ No raw audio files found in '{audio_dir}'!")
        return
    
    print(f"🎵 Found {len(raw_files)} raw audio files to process")
    
    success_count = 0
    
    for raw_file in raw_files:
        print(f"\n📁 Processing: {raw_file}")
        
        # Convert raw to WAV
        wav_file = convert_raw_to_wav(raw_file)
        if not wav_file:
            continue
        
        # Transcribe based on chosen method
        if method == "whisper":
            text = transcribe_with_whisper(wav_file, model_size)
        elif method == "speech_recognition":
            text = transcribe_with_speech_recognition(wav_file)
        else:
            print(f"❌ Unknown transcription method: {method}")
            continue
        
        if text:
            # Save transcription
            save_transcription(text, raw_file, method)
            success_count += 1
        
        # Cleanup temporary WAV file if requested
        if cleanup_wav and os.path.exists(wav_file):
            os.remove(wav_file)
            print(f"🗑️ Removed temporary WAV file: {wav_file}")
    
    print(f"\n✅ Processing complete! Successfully transcribed {success_count}/{len(raw_files)} files")

def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Convert raw audio files to text")
    parser.add_argument("--method", choices=["whisper", "speech_recognition"], 
                       default="whisper", help="Transcription method")
    parser.add_argument("--model-size", choices=["tiny", "base", "small", "medium", "large"],
                       default="base", help="Whisper model size (only for whisper method)")
    parser.add_argument("--cleanup", action="store_true", 
                       help="Delete temporary WAV files after transcription")
    parser.add_argument("--file", type=str, help="Process specific raw audio file")
    
    args = parser.parse_args()
    
    print("🎤 Audio to Text Converter")
    print("=" * 50)
    
    if args.file:
        # Process single file
        if not os.path.exists(args.file):
            print(f"❌ File not found: {args.file}")
            return
        
        print(f"📁 Processing single file: {args.file}")
        wav_file = convert_raw_to_wav(args.file)
        if wav_file:
            if args.method == "whisper":
                text = transcribe_with_whisper(wav_file, args.model_size)
            else:
                text = transcribe_with_speech_recognition(wav_file)
            
            if text:
                save_transcription(text, args.file, args.method)
                print(f"✅ Transcription: {text}")
            
            if args.cleanup and os.path.exists(wav_file):
                os.remove(wav_file)
    
    else:
        # Process all files in audio_recordings directory
        process_audio_files(args.method, args.model_size, args.cleanup)

if __name__ == "__main__":
    main()