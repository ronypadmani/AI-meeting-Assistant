# Meeting Transcription System - Project Structure

## Directory Layout
```
MSBC/
├── backend/                    # FastAPI backend
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py            # FastAPI app entry point
│   │   ├── models/            # Pydantic models
│   │   ├── services/          # AI processing services
│   │   ├── database/          # MongoDB connection and models
│   │   ├── websocket/         # WebSocket handlers
│   │   └── audio/             # Audio capture and processing
│   ├── requirements.txt       # Python dependencies
│   └── config.py             # Configuration settings
├── frontend/                  # React frontend
│   ├── src/
│   │   ├── components/        # React components
│   │   ├── services/          # WebSocket and API services
│   │   ├── pages/             # Dashboard pages
│   │   └── utils/             # Utility functions
│   ├── package.json
│   └── public/
├── data/                      # Audio chunks and temp files
│   ├── audio_chunks/
│   └── temp/
└── docs/                      # Documentation
```

## Technology Stack
- **Backend**: FastAPI, Python 3.8+
- **Frontend**: React 18+, TypeScript
- **Database**: MongoDB
- **AI Models**: Faster-Whisper, pyannote.audio, HuggingFace Transformers
- **Real-time**: WebSocket
- **Audio**: PyAudio, wave