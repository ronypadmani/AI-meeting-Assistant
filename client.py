import socketio
import sounddevice as sd
import numpy as np
import time
import sys
from datetime import datetime

class AudioClient:
    def __init__(self, server_url="http://localhost:8000"):
        self.server_url = server_url
        self.sio = socketio.Client()
        self.is_recording = False
        self.setup_socket_events()
    
    def setup_socket_events(self):
        """Setup WebSocket event handlers"""
        
        @self.sio.event
        def connect():
            print(f"✅ Connected to server at {self.server_url}")
            self.sio.emit('start_recording')
        
        @self.sio.event
        def disconnect():
            print("❌ Disconnected from server")
        
        @self.sio.event
        def connection_status(data):
            print(f"📡 {data['message']}")
        
        @self.sio.event
        def ack(data):
            print(f"📨 Server received {data['bytes_received']} bytes at {data['timestamp']}")
        
        @self.sio.event
        def recording_status(data):
            print(f"🎙️ Recording {data['status']}: {data['message']}")
        
        @self.sio.event
        def error(data):
            print(f"❌ Server error: {data['message']}")
    
    def audio_callback(self, indata, frames, time, status):
        """
        Callback function for audio input stream
        Called for each audio block captured from microphone
        """
        if status:
            print(f"⚠️ Audio status: {status}")
        
        if self.is_recording and self.sio.connected:
            # Convert float32 numpy array to bytes
            audio_bytes = indata.tobytes()
            
            # Send audio chunk to server
            self.sio.emit('audio_chunk', audio_bytes)
    
    def start_streaming(self, sample_rate=16000, channels=1, block_size=240000):
        """
        Start audio streaming to server
        
        Args:
            sample_rate: Audio sample rate (Hz)
            channels: Number of audio channels (1 for mono, 2 for stereo)
            block_size: Number of samples per block (240000 = 15 seconds at 16kHz)
        """
        try:
            # Connect to server
            print(f"🔌 Connecting to server: {self.server_url}")
            self.sio.connect(self.server_url)
            
            # Start recording
            self.is_recording = True
            
            print(f"🎤 Starting audio capture...")
            print(f"   Sample rate: {sample_rate} Hz")
            print(f"   Channels: {channels}")
            print(f"   Block size: {block_size} samples")
            print(f"   Block duration: {block_size/sample_rate:.2f} seconds")
            print("   Press Ctrl+C to stop recording")
            
            # Start audio input stream
            with sd.InputStream(
                samplerate=sample_rate,
                channels=channels,
                dtype='float32',
                callback=self.audio_callback,
                blocksize=block_size
            ):
                # Keep the stream alive
                while self.is_recording:
                    self.sio.sleep(0.1)
                    
        except KeyboardInterrupt:
            print("\n🛑 Recording stopped by user")
        except Exception as e:
            print(f"❌ Error: {e}")
        finally:
            self.stop_streaming()
    
    def stop_streaming(self):
        """Stop audio streaming and disconnect"""
        self.is_recording = False
        if self.sio.connected:
            self.sio.emit('stop_recording')
            self.sio.disconnect()
        print("👋 Disconnected from server")
    
    def list_audio_devices(self):
        """List available audio input devices"""
        print("🎧 Available audio input devices:")
        input_devices = []
        try:
            devices = sd.query_devices()
            for i, device in enumerate(devices):
                if device['max_input_channels'] > 0:
                    input_devices.append(i)
                    status = "✅" if device['max_input_channels'] > 0 else "❌"
                    print(f"   {status} {i}: {device['name']} (channels: {device['max_input_channels']}, rate: {device['default_samplerate']} Hz)")
            
            if not input_devices:
                print("   ❌ No input devices found!")
                print("   💡 Check microphone permissions in Windows Settings")
                
            return input_devices
        except Exception as e:
            print(f"   ❌ Error listing devices: {e}")
            return []

def main():
    """Main function to run the audio client"""
    
    # Default server URL
    server_url = "http://localhost:8000"
    
    # Parse command line arguments
    if len(sys.argv) > 1:
        server_url = sys.argv[1]
    
    print("🎵 Audio Streaming Client")
    print("=" * 50)
    
    # Create client instance
    client = AudioClient(server_url)
    
    # List available audio devices
    input_devices = client.list_audio_devices()
    print()
    
    if not input_devices:
        print("❌ No audio input devices available!")
        print("\n🔧 Troubleshooting steps:")
        print("1. Check Windows Privacy Settings:")
        print("   Settings > Privacy & Security > Microphone")
        print("   Make sure 'Allow apps to access your microphone' is ON")
        print("2. Check if microphone is connected and enabled")
        print("3. Try running Python as administrator")
        print("4. Check Windows Sound Settings (right-click speaker icon)")
        return
    
    # Test default device first
    print("🧪 Testing default audio device...")
    try:
        # Quick test recording
        test_duration = 0.1  # 100ms test
        default_device = sd.query_devices(kind='input')
        sample_rate = int(default_device['default_samplerate'])
        
        test_recording = sd.rec(int(test_duration * sample_rate), 
                               samplerate=sample_rate, 
                               channels=1, 
                               dtype='float32')
        sd.wait()
        print("✅ Default device test successful!")
        
    except Exception as e:
        print(f"❌ Default device test failed: {e}")
        print("🔄 Trying alternative devices...")
        
        # Try other devices
        working_device = None
        for device_id in input_devices:
            try:
                print(f"   Testing device {device_id}...")
                device_info = sd.query_devices(device_id)
                sample_rate = int(device_info['default_samplerate'])
                
                test_recording = sd.rec(int(test_duration * sample_rate),
                                       samplerate=sample_rate,
                                       channels=1,
                                       dtype='float32',
                                       device=device_id)
                sd.wait()
                
                print(f"   ✅ Device {device_id} works!")
                working_device = device_id
                break
                
            except Exception as device_error:
                print(f"   ❌ Device {device_id} failed: {device_error}")
        
        if working_device is not None:
            sd.default.device[0] = working_device
            print(f"🎤 Using working device {working_device}")
        else:
            print("❌ No working audio devices found!")
            print("\n🔧 Please check:")
            print("- Microphone permissions in Windows Settings")
            print("- Audio drivers are up to date")
            print("- No other apps are using the microphone exclusively")
            return
    
    # Ask user for device selection (optional)
    try:
        device_input = input("\nEnter device number (or press Enter to continue): ").strip()
        if device_input:
            device_id = int(device_input)
            if device_id in input_devices:
                sd.default.device[0] = device_id  # Set input device
                print(f"🎤 Using device {device_id}")
            else:
                print(f"❌ Invalid device {device_id}")
                return
    except (ValueError, IndexError):
        print("🎤 Using current audio device")
    
    print()
    
    # Start streaming
    try:
        client.start_streaming()
    except Exception as e:
        print(f"❌ Failed to start streaming: {e}")
        print("\n🔧 If the error persists:")
        print("1. Run the diagnostic script: python test_audio_devices.py")
        print("2. Check Windows audio settings")
        print("3. Restart your computer")
        print("4. Try running as administrator")

if __name__ == "__main__":
    main()
