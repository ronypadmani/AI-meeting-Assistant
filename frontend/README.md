# Meeting Transcription Frontend

React-based dashboard for real-time meeting transcription and analysis.

## Features

- 🎤 Real-time audio transcription
- 👥 Speaker identification and tracking
- 😊 Emotion analysis per speaker
- 📝 Technical jargon detection with definitions
- 📊 Live analytics with charts
- 📋 Final meeting summaries
- 🔄 WebSocket-based real-time updates

## Setup Instructions

### Prerequisites

- Node.js 16+ installed
- Backend server running on `http://localhost:8000`

### Installation

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Start the development server:
   ```bash
   npm start
   ```

4. Open your browser and navigate to `http://localhost:3000`

### Build for Production

```bash
npm run build
```

## Usage

1. **Start a Session**: Click the "Start Session" button to begin recording
2. **Live Transcript**: View real-time transcription in the left panel
3. **Analytics**: Monitor emotions, speakers, and technical terms in the right panel
4. **Stop Session**: Click "Stop Session" to end recording and generate final summary

## Technologies Used

- **React 18** with TypeScript
- **Material-UI** for components and styling
- **Recharts** for data visualization
- **Socket.IO Client** for WebSocket communication
- **Axios** for HTTP requests
- **Moment.js** for date formatting

## Project Structure

```
src/
├── components/          # React components
│   └── MainDashboard.tsx   # Main dashboard component
├── services/           # API and WebSocket services
│   ├── apiService.ts      # HTTP API client
│   └── websocketService.ts # WebSocket client
├── App.tsx            # Main application component
├── index.tsx          # Application entry point
└── index.css          # Global styles
```

## Configuration

The frontend automatically connects to the backend at `http://localhost:8000`. To change this, set the `REACT_APP_API_URL` environment variable:

```bash
REACT_APP_API_URL=http://your-backend-url:port npm start
```