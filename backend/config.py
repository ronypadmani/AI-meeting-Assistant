"""
Configuration settings for the Meeting Transcription System
"""
import os
from typing import Optional

class Settings:
    # Server Configuration
    HOST: str = "localhost"
    PORT: int = 8000
    DEBUG: bool = True
    
    # MongoDB Configuration
    MONGODB_URL: str = "mongodb://localhost:27017"
    DATABASE_NAME: str = "meeting_transcription"
    CHUNKS_COLLECTION: str = "chunks"
    SUMMARIES_COLLECTION: str = "summaries"
    
    # Audio Configuration
    CHUNK_DURATION: int = 15  # seconds
    SAMPLE_RATE: int = 16000
    CHANNELS: int = 1
    AUDIO_FORMAT: str = "wav"
    AUDIO_DEVICE_NAME: str = "Stereo Mix"  # Windows Stereo Mix
    
    # AI Model Configuration
    WHISPER_MODEL: str = "medium"
    WHISPER_DEVICE: str = "cpu"  # Change to "cuda" if GPU available
    
    # HuggingFace Models
    EMOTION_MODEL: str = "j-hartmann/emotion-english-distilroberta-base"
    SUMMARIZATION_MODEL: str = "facebook/bart-large-cnn"
    
    # Pyannote Configuration
    PYANNOTE_AUTH_TOKEN: Optional[str] = None  # HuggingFace token for pyannote
    
    # Processing Configuration
    MAX_WORKERS: int = 4
    ENABLE_GPU: bool = False
    
    # File Paths
    BASE_DIR: str = os.path.dirname(os.path.abspath(__file__))
    DATA_DIR: str = os.path.join(os.path.dirname(BASE_DIR), "data")
    AUDIO_CHUNKS_DIR: str = os.path.join(DATA_DIR, "audio_chunks")
    TEMP_DIR: str = os.path.join(DATA_DIR, "temp")
    
    # WebSocket Configuration
    WS_HEARTBEAT_INTERVAL: int = 30
    WS_MAX_CONNECTIONS: int = 100
    
    # Jargon Detection Configuration
    MIN_JARGON_SCORE: float = 0.5
    MAX_JARGON_TERMS: int = 10
    
    # Logging Configuration
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "meeting_transcription.log"

# Global settings instance
settings = Settings()

# Environment variable overrides
def load_env_settings():
    """Load settings from environment variables if available"""
    if os.getenv("MONGODB_URL"):
        settings.MONGODB_URL = os.getenv("MONGODB_URL")
    
    if os.getenv("WHISPER_DEVICE"):
        settings.WHISPER_DEVICE = os.getenv("WHISPER_DEVICE")
    
    if os.getenv("PYANNOTE_AUTH_TOKEN"):
        settings.PYANNOTE_AUTH_TOKEN = os.getenv("PYANNOTE_AUTH_TOKEN")
    
    if os.getenv("DEBUG"):
        settings.DEBUG = os.getenv("DEBUG").lower() == "true"

# Load environment settings on import
load_env_settings()