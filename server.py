from flask import Flask
from flask_socketio import SocketIO, emit
import os
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev')
socketio = SocketIO(app, cors_allowed_origins="*")

# Create audio directory if it doesn't exist
os.makedirs("audio_recordings", exist_ok=True)

@socketio.on('connect')
def on_connect():
    print(f"Client connected at {datetime.now()}")
    emit('connection_status', {'status': 'connected', 'message': 'Successfully connected to audio server'})

@socketio.on('disconnect')
def on_disconnect():
    print(f"Client disconnected at {datetime.now()}")

@socketio.on('audio_chunk')
def handle_audio(data):
    """
    Handle incoming audio chunks from clients
    data: binary audio data (raw audio bytes)
    """
    try:
        # Generate filename with timestamp for each session
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"audio_recordings/meeting_audio_{timestamp}.raw"
        
        # Append audio chunk to file
        with open(filename, "ab") as f:
            f.write(data)
        
        print(f"Received audio chunk of {len(data)} bytes")
        
        # Send acknowledgment back to client
        emit('ack', {
            'status': 'received', 
            'bytes_received': len(data),
            'timestamp': datetime.now().isoformat()
        })
        
        # Optional: Add real-time processing here
        # - Speech-to-text transcription
        # - Emotion analysis
        # - Voice activity detection
        
    except Exception as e:
        print(f"Error handling audio chunk: {e}")
        emit('error', {'status': 'error', 'message': str(e)})

@socketio.on('start_recording')
def handle_start_recording():
    """Handle recording start signal"""
    print("Recording session started")
    emit('recording_status', {'status': 'started', 'message': 'Recording session initiated'})

@socketio.on('stop_recording')
def handle_stop_recording():
    """Handle recording stop signal"""
    print("Recording session stopped")
    emit('recording_status', {'status': 'stopped', 'message': 'Recording session ended'})

@app.route('/')
def index():
    return """
    <h1>Audio Streaming Server</h1>
    <p>WebSocket server is running for real-time audio streaming.</p>
    <p>Connect clients to: <code>ws://localhost:8000/socket.io/</code></p>
    <p>Audio files are saved in the <code>audio_recordings/</code> directory.</p>
    """

if __name__ == "__main__":
    print("Starting Flask-SocketIO server...")
    print("Server will be available at: http://localhost:8000")
    print("WebSocket endpoint: ws://localhost:8000/socket.io/")
    print("Audio recordings will be saved in: ./audio_recordings/")
    
    socketio.run(app, host="0.0.0.0", port=8000, debug=True)
