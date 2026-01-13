import axios from 'axios';
import { handleError } from '../utils/errorHandler';
import type {
  Conversation,
  Message,
  ChatResponse,
  TranscriptionResponse,
  TopicsData,
} from '../types';

const API_BASE_URL = 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const conversationService = {
  async create(
    language: string,
    difficulty_level: string,
    topic_id?: string
  ): Promise<Conversation> {
    try {
      const response = await api.post('/conversations', {
        language,
        difficulty_level,
        topic_id,
      });
      return response.data;
    } catch (error) {
      handleError(error);
      throw error;
    }
  },

  async list(): Promise<Conversation[]> {
    try {
      const response = await api.get('/conversations');
      return response.data;
    } catch (error) {
      handleError(error);
      throw error;
    }
  },

  async get(id: number): Promise<Conversation> {
    try {
      const response = await api.get(`/conversations/${id}`);
      return response.data;
    } catch (error) {
      handleError(error);
      throw error;
    }
  },

  async getMessages(id: number): Promise<Message[]> {
    try {
      const response = await api.get(`/conversations/${id}/messages`);
      return response.data;
    } catch (error) {
      handleError(error);
      throw error;
    }
  },

  async delete(id: number): Promise<void> {
    try {
      await api.delete(`/conversations/${id}`);
    } catch (error) {
      handleError(error);
      throw error;
    }
  },
};

export const chatService = {
  async sendMessage(
    conversation_id: number,
    user_message: string,
    language: string,
    difficulty_level: string
  ): Promise<ChatResponse> {
    // Avoid logging raw user messages to reduce accidental sensitive-data exposure.
    console.log('[Chat] Sending message:', {
      conversation_id,
      language,
      difficulty_level,
      messageLength: user_message.length,
    });
    try {
      const response = await api.post('/chat', {
        conversation_id,
        user_message,
        language,
        difficulty_level,
      });
      console.log('[Chat] Response received:', response.data);
      return response.data;
    } catch (error) {
      console.error('[Chat] Request failed');
      handleError(error);
      throw error;
    }
  },

  async generateInitialMessage(
    conversation_id: number,
    language: string,
    difficulty_level: string,
    topic_id: string
  ): Promise<ChatResponse> {
    try {
      const response = await api.post('/chat/initial-message', {
        conversation_id,
        language,
        difficulty_level,
        topic_id,
      });
      return response.data;
    } catch (error) {
      handleError(error);
      throw error;
    }
  },
};

export const speechService = {
  async transcribe(
    audioBlob: Blob,
    conversation_id: number,
    language: string
  ): Promise<TranscriptionResponse> {
    console.log('[Speech] Transcribing audio:', {
      conversation_id,
      language,
      blobSize: audioBlob.size,
      blobType: audioBlob.type,
    });

    try {
      const formData = new FormData();
      formData.append('audio', audioBlob, 'recording.webm');

      const response = await api.post(
        `/stt/transcribe?conversation_id=${conversation_id}&language=${language}`,
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        }
      );

      console.log('[Speech] Transcription response:', response.data);
      return response.data;
    } catch (error) {
      console.error('[Speech] Transcription failed');
      handleError(error);
      throw error;
    }
  },

  async getSttConfig(): Promise<{
    current_model: string;
    available_models: string[];
    cuda: {
      available: boolean;
      device: string;
      device_name?: string | null;
      memory_total_gb?: number | null;
      memory_free_gb?: number | null;
    };
    device: string;
  }> {
    try {
      const response = await api.get('/stt/config');
      return response.data;
    } catch (error) {
      handleError(error);
      throw error;
    }
  },

  async updateSttModel(model: string): Promise<{
    message: string;
    requested_model: string;
    current_model: string;
    note: string;
  }> {
    try {
      const response = await api.post('/stt/config/model', { model });
      return response.data;
    } catch (error) {
      handleError(error);
      throw error;
    }
  },
};

export const ttsService = {
  async synthesize(text: string, language: string): Promise<Blob> {
    try {
      const response = await api.post(
        '/tts/synthesize',
        { text, language },
        { responseType: 'blob' }
      );
      return response.data;
    } catch (error) {
      handleError(error);
      throw error;
    }
  },
};

export const topicsService = {
  async getTopics(): Promise<TopicsData> {
    try {
      const response = await api.get('/topics');
      return response.data;
    } catch (error) {
      handleError(error);
      throw error;
    }
  },
};
