/**
 * API service for HTTP communication with the backend
 */
import axios from 'axios';

const BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: BASE_URL,
  timeout: 30000, // 30 seconds timeout
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor
api.interceptors.request.use(
  (config) => {
    console.log(`Making ${config.method?.toUpperCase()} request to ${config.url}`);
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor
api.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    console.error('API Error:', error);
    
    if (error.response) {
      // Server responded with error status
      const message = error.response.data?.detail || error.response.data?.error || error.message;
      throw new Error(message);
    } else if (error.request) {
      // Request was made but no response received
      throw new Error('No response from server. Please check your connection.');
    } else {
      // Something else happened
      throw new Error(error.message);
    }
  }
);

export interface SessionInfo {
  session_id: string;
  start_time: string;
  status: string;
  metadata: Record<string, any>;
  end_time?: string;
  summary_stats?: Record<string, any>;
}

export interface AudioDevice {
  device_id: number;
  name: string;
  channels: number;
  sample_rate: number;
}

export interface SystemStatus {
  status: string;
  database_connected: boolean;
  ai_models_loaded: boolean;
  active_sessions: number;
  available_audio_devices: AudioDevice[];
  version: string;
}

export interface StartSessionRequest {
  session_name?: string;
  metadata?: Record<string, any>;
}

export interface StartSessionResponse {
  session_id: string;
  status: string;
  message: string;
}

export interface StopSessionRequest {
  session_id: string;
}

export interface StopSessionResponse {
  session_id: string;
  status: string;
  total_chunks: number;
  total_duration: number;
  message: string;
}

class ApiService {
  
  // System endpoints
  async getSystemHealth(): Promise<SystemStatus> {
    const response = await api.get('/health');
    return response.data;
  }

  async getAudioDevices(): Promise<AudioDevice[]> {
    const response = await api.get('/audio/devices');
    return response.data;
  }

  async getConnectionStats(): Promise<any> {
    const response = await api.get('/system/connections');
    return response.data;
  }

  // Session management endpoints
  async startSession(request: StartSessionRequest = {}): Promise<StartSessionResponse> {
    const response = await api.post('/sessions/start', request);
    return response.data;
  }

  async stopSession(sessionId: string): Promise<StopSessionResponse> {
    const response = await api.post('/sessions/stop', { session_id: sessionId });
    return response.data;
  }

  async getActiveSessions(): Promise<SessionInfo[]> {
    const response = await api.get('/sessions/active');
    return response.data;
  }

  async getSessionStatus(sessionId: string): Promise<any> {
    const response = await api.get(`/sessions/${sessionId}/status`);
    return response.data;
  }

  // Helper methods
  async checkConnection(): Promise<boolean> {
    try {
      await api.get('/health');
      return true;
    } catch (error) {
      return false;
    }
  }

  async waitForHealthy(maxAttempts = 10, delay = 1000): Promise<boolean> {
    for (let attempt = 1; attempt <= maxAttempts; attempt++) {
      try {
        const status = await this.getSystemHealth();
        if (status.status === 'healthy') {
          return true;
        }
      } catch (error) {
        console.log(`Health check attempt ${attempt}/${maxAttempts} failed:`, error);
      }

      if (attempt < maxAttempts) {
        await new Promise(resolve => setTimeout(resolve, delay));
      }
    }
    return false;
  }
}

export const apiService = new ApiService();