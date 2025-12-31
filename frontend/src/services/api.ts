import axios from 'axios';
import type { 
  Conversation, 
  Message, 
  ChatResponse, 
  TranscriptionResponse,
  VocabularyItem 
} from '../types';

const API_BASE_URL = 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const conversationService = {
  async create(language: string, difficulty_level: string): Promise<Conversation> {
    const response = await api.post('/conversations', { language, difficulty_level });
    return response.data;
  },

  async list(): Promise<Conversation[]> {
    const response = await api.get('/conversations');
    return response.data;
  },

  async get(id: number): Promise<Conversation> {
    const response = await api.get(`/conversations/${id}`);
    return response.data;
  },

  async getMessages(id: number): Promise<Message[]> {
    const response = await api.get(`/conversations/${id}/messages`);
    return response.data;
  },

  async getVocabulary(id: number): Promise<VocabularyItem[]> {
    const response = await api.get(`/conversations/${id}/vocabulary`);
    return response.data;
  },

  async delete(id: number): Promise<void> {
    await api.delete(`/conversations/${id}`);
  },
};

export const chatService = {
  async sendMessage(
    conversation_id: number,
    user_message: string,
    language: string,
    difficulty_level: string
  ): Promise<ChatResponse> {
    const response = await api.post('/chat', {
      conversation_id,
      user_message,
      language,
      difficulty_level,
    });
    return response.data;
  },
};

export const speechService = {
  async transcribe(
    audioBlob: Blob,
    conversation_id: number,
    language: string
  ): Promise<TranscriptionResponse> {
    const formData = new FormData();
    formData.append('audio', audioBlob, 'recording.webm');

    const response = await api.post(
      `/speech/transcribe?conversation_id=${conversation_id}&language=${language}`,
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      }
    );
    return response.data;
  },
};

export const ttsService = {
  async synthesize(text: string, language: string): Promise<Blob> {
    const response = await api.post(
      '/tts/synthesize',
      { text, language },
      { responseType: 'blob' }
    );
    return response.data;
  },
};
