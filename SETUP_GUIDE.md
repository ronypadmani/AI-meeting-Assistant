# 🎙️ Real-Time Meeting Transcription System - Complete Setup Guide

This comprehensive guide will help you set up and run the complete meeting transcription system.

## 🎯 System Overview

Your meeting transcription system is now **COMPLETE** and includes:

✅ **Audio Capture** - Stereo Mix recording with 15-second chunking  
✅ **AI Processing** - Transcription, speaker ID, emotion analysis, jargon detection  
✅ **FastAPI Backend** - WebSocket streaming and MongoDB storage  
✅ **React Frontend** - Real-time dashboard with live analytics  
✅ **Final Summarization** - Complete meeting summaries with speaker consistency  

## 🚀 Quick Start Guide

### 1. Prerequisites Installation

**Python Environment:**
```bash
# Ensure Python 3.8+ is installed
python --version

# Install MongoDB (or use cloud instance)
# Download from: https://www.mongodb.com/try/download/community
```

**Node.js Environment:**
```bash
# Ensure Node.js 16+ is installed
node --version
npm --version
```

### 2. Backend Setup (FastAPI + AI)

```bash
# Navigate to backend
cd C:\MSBC\backend

# Create and activate virtual environment
python -m venv venv
venv\Scripts\activate

# Install all Python dependencies
pip install -r requirements.txt

# Download required AI models
python -m spacy download en_core_web_sm

# Optional: Set up HuggingFace token for pyannote (for better speaker identification)
# export PYANNOTE_AUTH_TOKEN="your_token_here"

# Start the FastAPI server
python -m app.main
```

**Expected Output:**
```
INFO:     Starting Meeting Transcription System
INFO:     Successfully connected to MongoDB
INFO:     All AI services initialized
INFO:     Uvicorn running on http://localhost:8000
```

### 3. Frontend Setup (React Dashboard)

```bash
# Open new terminal, navigate to frontend
cd C:\MSBC\frontend

# Install Node.js dependencies
npm install

# Start React development server
npm start
```

**Expected Output:**
```
Compiled successfully!

You can now view meeting-transcription-frontend in the browser.

  Local:            http://localhost:3000
  On Your Network:  http://192.168.1.x:3000
```

### 4. Enable Stereo Mix (Windows Audio)

1. **Right-click** the speaker icon in system tray
2. Select **"Open Sound settings"**
3. Click **"Sound Control Panel"** (additional sound settings)
4. Go to **"Recording"** tab
5. **Right-click** in empty space → **"Show Disabled Devices"**
6. **Right-click "Stereo Mix"** → **"Enable"**
7. **Right-click "Stereo Mix"** → **"Set as Default Device"**

## 🎮 Using the System

### Step 1: Access the Dashboard
- Open browser to `http://localhost:3000`
- You should see "Meeting Transcription Dashboard"
- Check that "Connected" status is green

### Step 2: Start a Session
1. Click **"Start Session"** button
2. Enter optional session name
3. Click **"Start Session"** to begin recording

### Step 3: Real-Time Transcription
- **Live Transcript** appears in left panel
- **Analytics** update in right panel:
  - Emotion distribution (pie chart)
  - Speaker identification (pie chart) 
  - Technical terms with definitions
- **Status updates** show at bottom

### Step 4: Stop and Get Summary
1. Click **"Stop Session"** when meeting ends
2. System generates comprehensive final summary
3. Summary includes:
   - Complete transcript with speakers
   - Overall emotion analysis
   - Technical terms glossary
   - Meeting statistics

## 🏗️ System Architecture

```
Audio Flow:
Stereo Mix → 15s Chunks → AI Pipeline → WebSocket → React Dashboard
                     ↓
                  MongoDB (Storage)
```

### AI Processing Pipeline (Per Chunk):
1. **Faster-Whisper** → Speech to text transcription
2. **pyannote.audio** → Speaker identification and labeling
3. **HuggingFace** → Emotion analysis per speaker
4. **spaCy + KeyBERT** → Technical jargon detection
5. **BART/T5** → Micro-summary generation

### Final Processing:
1. **Chunk Stitching** → Combine all chunks chronologically
2. **Speaker Consistency** → Maintain speaker labels across meeting
3. **Final Summarization** → Comprehensive meeting summary
4. **Data Storage** → Complete results saved to MongoDB

## 🔧 Configuration Options

### Backend Configuration (`backend/config.py`):

```python
# Audio Settings
CHUNK_DURATION = 15        # Seconds per audio chunk
SAMPLE_RATE = 16000       # Audio sample rate
AUDIO_DEVICE_NAME = "Stereo Mix"

# AI Model Settings
WHISPER_MODEL = "medium"   # Options: tiny, base, small, medium, large
WHISPER_DEVICE = "cpu"     # Change to "cuda" if you have GPU

# Performance Settings
MAX_WORKERS = 4           # Parallel processing threads
ENABLE_GPU = False        # Set True if you have CUDA GPU
```

### Frontend Configuration:

Create `frontend/.env` file:
```bash
REACT_APP_API_URL=http://localhost:8000
```

## 📊 API Endpoints

### Session Management:
- `POST /sessions/start` - Start new meeting session
- `POST /sessions/stop` - Stop active session and generate summary
- `GET /sessions/active` - List all active sessions

### System Information:
- `GET /health` - Check system health and AI model status
- `GET /audio/devices` - List available audio devices
- `GET /system/connections` - WebSocket connection statistics

### WebSocket Events:
- `chunk_update` - New processed chunk available
- `summary_update` - Final meeting summary ready
- `status` - System status and processing updates

## 🧪 Testing Your Setup

### 1. Test Backend API:
```bash
# Check system health
curl http://localhost:8000/health

# Expected response:
{
  "status": "healthy",
  "database_connected": true,
  "ai_models_loaded": true,
  "active_sessions": 0,
  "available_audio_devices": [...]
}
```

### 2. Test Audio Devices:
```bash
curl http://localhost:8000/audio/devices
```

### 3. Test Session Creation:
```bash
curl -X POST http://localhost:8000/sessions/start \
  -H "Content-Type: application/json" \
  -d '{"session_name": "Test Meeting"}'
```

### 4. Test Frontend:
- Open `http://localhost:3000`
- Check browser console for WebSocket connection
- Try starting a test session

## 🔍 Troubleshooting

### "Stereo Mix device not found"
```python
# Check available devices in Python:
import pyaudio
audio = pyaudio.PyAudio()
for i in range(audio.get_device_count()):
    info = audio.get_device_info_by_index(i)
    if info['maxInputChannels'] > 0:
        print(f"{i}: {info['name']}")
```

### "Database connection failed"
- Ensure MongoDB is running: `mongod --version`
- Check MongoDB service is started
- Verify connection string in config.py

### "AI models not loading"
- First run downloads models (can take 10-15 minutes)
- Check internet connection
- Monitor disk space (models are 1-5GB total)
- Check console output for specific errors

### "WebSocket connection failed"
- Verify backend is running on port 8000
- Check Windows Firewall settings
- Try accessing http://localhost:8000/health directly

## 🎯 Performance Optimization

### For Better Performance:
1. **GPU Acceleration**: Set `WHISPER_DEVICE = "cuda"` if you have NVIDIA GPU
2. **Model Size**: Use `WHISPER_MODEL = "small"` for faster processing
3. **Chunk Duration**: Reduce to 10 seconds for lower latency
4. **Memory**: Ensure 8GB+ RAM for optimal performance

### For Production Use:
1. Use cloud MongoDB (MongoDB Atlas)
2. Deploy backend with Gunicorn/Docker
3. Build and serve React frontend with Nginx
4. Use Redis for WebSocket scaling
5. Set up proper logging and monitoring

## 📋 File Structure Summary

```
C:\MSBC\
├── backend\              # ✅ FastAPI server + AI processing
│   ├── app\
│   │   ├── main.py       # ✅ FastAPI application
│   │   ├── audio\        # ✅ Stereo Mix capture
│   │   ├── services\     # ✅ AI processing pipeline
│   │   ├── database\     # ✅ MongoDB operations
│   │   ├── websocket\    # ✅ Real-time communication
│   │   └── models\       # ✅ Data validation schemas
│   ├── config.py         # ✅ System configuration
│   └── requirements.txt  # ✅ Python dependencies
├── frontend\             # ✅ React dashboard
│   ├── src\
│   │   ├── components\   # ✅ Dashboard components
│   │   ├── services\     # ✅ WebSocket & API clients
│   │   └── App.tsx       # ✅ Main application
│   ├── package.json      # ✅ Node.js dependencies
│   └── public\           # ✅ Static assets
└── data\                 # 📁 Audio storage (auto-created)
```

## 🎉 Success Indicators

Your system is working correctly when you see:

✅ Backend: "System initialization complete" message  
✅ Frontend: Green "Connected" status indicator  
✅ Dashboard: Real-time transcript updates during audio  
✅ Analytics: Emotion and speaker charts populate  
✅ Summary: Complete meeting summary generated at end  

## 🆘 Need Help?

If you encounter issues:

1. **Check Console Logs**: Both backend terminal and browser dev tools
2. **Verify Prerequisites**: Python, Node.js, MongoDB all installed
3. **Test Components**: Try each component individually
4. **Check Audio**: Ensure Stereo Mix is enabled and default
5. **Monitor Resources**: Ensure sufficient RAM and disk space

---

**🚀 Your real-time meeting transcription system is ready to use!**

Transform your meetings with AI-powered insights including live transcription, speaker identification, emotion analysis, and intelligent summarization.