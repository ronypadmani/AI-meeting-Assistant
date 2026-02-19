/**
 * WebSocket service for real-time communication with the backend
 */
import { io, Socket } from 'socket.io-client';

export interface ChunkData {
  chunk_id: number;
  timestamp: string;
  start_time: number;
  end_time: number;
  duration: number;
  transcript: {
    full_text: string;
    segments: Array<{
      start: number;
      end: number;
      text: string;
      confidence: number;
      speaker?: string;
    }>;
    language: string;
    language_probability: number;
  };
  speakers: {
    speakers: string[];
    speaker_mapping: Record<string, any[]>;
  };
  emotions: Record<string, {
    dominant_emotion: string;
    confidence: number;
    all_emotions: Record<string, number>;
  }>;
  jargon: Array<{
    term: string;
    score: number;
    definition: string;
    source: string;
  }>;
  micro_summary: string;
  processing_status: string;
}

export interface MeetingSummary {
  session_id: string;
  timestamp: string;
  combined_transcript: string;
  final_summary: string;
  speakers_summary: Record<string, {
    speaker_id: string;
    total_segments: number;
    total_duration: number;
    word_count: number;
    dominant_emotion: string;
    emotion_distribution: Record<string, number>;
  }>;
  emotions_summary: Record<string, number>;
  jargon_summary: Array<{
    term: string;
    score: number;
    definition: string;
    source: string;
  }>;
  total_chunks: number;
  total_duration: number;
  meeting_metadata: Record<string, any>;
}

export interface WebSocketMessage {
  type: string;
  timestamp?: string;
  session_id?: string;
  [key: string]: any;
}

class WebSocketService {
  private socket: Socket | null = null;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectDelay = 1000; // Start with 1 second
  
  // Event handlers
  private onConnectedHandler: (() => void) | null = null;
  private onDisconnectedHandler: (() => void) | null = null;
  private onChunkUpdateHandler: ((sessionId: string, chunk: ChunkData) => void) | null = null;
  private onSummaryUpdateHandler: ((sessionId: string, summary: MeetingSummary) => void) | null = null;
  private onStatusUpdateHandler: ((sessionId: string | null, status: string, details?: any) => void) | null = null;
  private onErrorHandler: ((error: string) => void) | null = null;

  connect(serverUrl = 'ws://localhost:8000/ws'): Promise<void> {
    return new Promise((resolve, reject) => {
      try {
        // Convert WebSocket URL to Socket.IO format
        const socketUrl = serverUrl.replace('/ws', '').replace('ws://', 'http://');
        
        this.socket = io(socketUrl, {
          transports: ['websocket', 'polling'],
          timeout: 5000,
        });

        this.socket.on('connect', () => {
          console.log('Connected to WebSocket server');
          this.reconnectAttempts = 0;
          this.onConnectedHandler?.();
          resolve();
        });

        this.socket.on('disconnect', (reason) => {
          console.log('Disconnected from WebSocket server:', reason);
          this.onDisconnectedHandler?.();
          
          // Auto-reconnect logic
          if (reason === 'io server disconnect') {
            // Server disconnected, try to reconnect
            this.reconnect();
          }
        });

        this.socket.on('connect_error', (error) => {
          console.error('WebSocket connection error:', error);
          this.onErrorHandler?.(`Connection error: ${error.message}`);
          
          if (this.reconnectAttempts === 0) {
            reject(error);
          }
        });

        // Handle different message types
        this.socket.on('message', (data) => {
          this.handleMessage(data);
        });

        // Handle chunk updates
        this.socket.on('chunk_update', (data) => {
          if (data.type === 'chunk_update' && data.session_id && data.chunk) {
            this.onChunkUpdateHandler?.(data.session_id, data.chunk);
          }
        });

        // Handle summary updates
        this.socket.on('summary_update', (data) => {
          if (data.type === 'summary_update' && data.session_id && data.summary) {
            this.onSummaryUpdateHandler?.(data.session_id, data.summary);
          }
        });

        // Handle status updates
        this.socket.on('status', (data) => {
          if (data.type === 'status') {
            this.onStatusUpdateHandler?.(data.session_id, data.status, data.details);
          }
        });

      } catch (error) {
        reject(error);
      }
    });
  }

  private handleMessage(message: WebSocketMessage) {
    console.log('Received WebSocket message:', message);

    switch (message.type) {
      case 'connection':
        if (message.status === 'connected') {
          console.log('WebSocket connection confirmed');
        }
        break;

      case 'chunk_update':
        if (message.session_id && message.chunk) {
          this.onChunkUpdateHandler?.(message.session_id, message.chunk);
        }
        break;

      case 'summary_update':
        if (message.session_id && message.summary) {
          this.onSummaryUpdateHandler?.(message.session_id, message.summary);
        }
        break;

      case 'status':
        this.onStatusUpdateHandler?.(message.session_id, message.status, message.details);
        break;

      case 'heartbeat':
        // Respond to heartbeat
        this.send({ type: 'heartbeat' });
        break;

      default:
        console.log('Unknown message type:', message.type);
    }
  }

  private reconnect() {
    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      console.error('Max reconnect attempts reached');
      this.onErrorHandler?.('Connection lost. Please refresh the page.');
      return;
    }

    this.reconnectAttempts++;
    const delay = this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1); // Exponential backoff

    console.log(`Attempting to reconnect in ${delay}ms (attempt ${this.reconnectAttempts})`);

    setTimeout(() => {
      if (this.socket) {
        this.socket.connect();
      }
    }, delay);
  }

  disconnect() {
    if (this.socket) {
      this.socket.disconnect();
      this.socket = null;
    }
  }

  send(message: any) {
    if (this.socket && this.socket.connected) {
      this.socket.emit('message', message);
    } else {
      console.error('WebSocket not connected');
    }
  }

  subscribeToSession(sessionId: string) {
    this.send({
      type: 'subscribe',
      session_id: sessionId
    });
  }

  unsubscribeFromSession(sessionId: string) {
    this.send({
      type: 'unsubscribe',
      session_id: sessionId
    });
  }

  // Event handler setters
  onConnected(handler: () => void) {
    this.onConnectedHandler = handler;
  }

  onDisconnected(handler: () => void) {
    this.onDisconnectedHandler = handler;
  }

  onChunkUpdate(handler: (sessionId: string, chunk: ChunkData) => void) {
    this.onChunkUpdateHandler = handler;
  }

  onSummaryUpdate(handler: (sessionId: string, summary: MeetingSummary) => void) {
    this.onSummaryUpdateHandler = handler;
  }

  onStatusUpdate(handler: (sessionId: string | null, status: string, details?: any) => void) {
    this.onStatusUpdateHandler = handler;
  }

  onError(handler: (error: string) => void) {
    this.onErrorHandler = handler;
  }

  isConnected(): boolean {
    return this.socket?.connected ?? false;
  }
}

// Export singleton instance
export const webSocketService = new WebSocketService();