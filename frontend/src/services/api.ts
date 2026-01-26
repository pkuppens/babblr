import axios from 'axios';
import { handleError } from '../utils/errorHandler';
import type {
  Conversation,
  Message,
  ChatResponse,
  TranscriptionResponse,
  TopicsData,
  Assessment,
  AssessmentDetail,
  AttemptResult,
  AttemptSummary,
  UserLevel,
} from '../types';

const API_BASE_URL = 'http://localhost:8000';

export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000, // 30 second timeout for all requests
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
    previous_model: string;
    action: string;
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

  async getSttSwitchStatus(): Promise<{
    status: string;
    target_model: string | null;
    error: string | null;
  }> {
    try {
      const response = await api.get('/stt/config/status');
      return response.data;
    } catch (error) {
      handleError(error);
      throw error;
    }
  },
};

export const ttsService = {
  async synthesize(text: string, language: string, speed: number = 1.0): Promise<Blob> {
    try {
      const response = await api.post(
        '/tts/synthesize',
        { text, language, speed },
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

// Grammar lesson types
export interface GrammarLesson {
  id: number;
  language: string;
  lesson_type: string;
  title: string;
  description?: string;
  difficulty_level: string;
  order_index: number;
  is_active: boolean;
  created_at: string;
}

export interface GrammarLessonDetail extends GrammarLesson {
  rules: Array<{
    id: number;
    title: string;
    description: string;
    examples: Array<{ es?: string; en?: string; [key: string]: string | undefined }>;
    difficulty_level: string;
  }>;
  examples: Array<{
    text: string;
    translation?: string;
    audio_url?: string;
  }>;
  exercises: Array<{
    type: string;
    question?: string;
    options?: string[];
    correct?: number;
    [key: string]: unknown;
  }>;
  items: Array<{
    id: number;
    item_type: string;
    content: string;
    item_metadata?: string;
    order_index: number;
    created_at: string;
  }>;
}

export interface LessonProgress {
  id: number;
  lesson_id: number;
  language: string;
  status: 'not_started' | 'in_progress' | 'completed';
  completion_percentage: number;
  mastery_score?: number;
  started_at?: string;
  completed_at?: string;
  last_accessed_at: string;
}

export interface LessonProgressCreate {
  lesson_id: number;
  language: string;
  status: 'not_started' | 'in_progress' | 'completed';
  completion_percentage: number;
  mastery_score?: number;
}

export const grammarService = {
  async listLessons(
    language: string,
    level?: string,
    type?: 'new' | 'practice' | 'test' | 'recap'
  ): Promise<GrammarLesson[]> {
    try {
      const params = new URLSearchParams({ language });
      if (level) params.append('level', level);
      if (type) params.append('type', type);
      const response = await api.get(`/grammar/lessons?${params.toString()}`);
      return response.data;
    } catch (error) {
      handleError(error);
      throw error;
    }
  },

  async getLesson(lessonId: number): Promise<GrammarLessonDetail> {
    try {
      const response = await api.get(`/grammar/lessons/${lessonId}`);
      return response.data;
    } catch (error) {
      handleError(error);
      throw error;
    }
  },

  async updateProgress(progress: LessonProgressCreate): Promise<LessonProgress> {
    try {
      const response = await api.post('/grammar/progress', progress);
      return response.data;
    } catch (error) {
      handleError(error);
      throw error;
    }
  },

  async getRecaps(language: string, level?: string): Promise<GrammarLesson[]> {
    try {
      const params = new URLSearchParams({ language });
      if (level) params.append('level', level);
      const response = await api.get(`/grammar/recaps?${params.toString()}`);
      return response.data;
    } catch (error) {
      handleError(error);
      throw error;
    }
  },
};

export const assessmentService = {
  async listAssessments(language: string): Promise<Assessment[]> {
    try {
      const response = await api.get(`/assessments?language=${language}`);
      return response.data;
    } catch (error) {
      handleError(error);
      throw error;
    }
  },

  async getAssessment(assessmentId: number): Promise<AssessmentDetail> {
    try {
      const response = await api.get(`/assessments/${assessmentId}`);
      return response.data;
    } catch (error) {
      handleError(error);
      throw error;
    }
  },

  async submitAttempt(
    assessmentId: number,
    answers: Record<string, string>
  ): Promise<AttemptResult> {
    try {
      const response = await api.post(`/assessments/${assessmentId}/attempts`, {
        answers,
      });
      return response.data;
    } catch (error) {
      handleError(error);
      throw error;
    }
  },

  async listAttempts(language: string, limit?: number): Promise<AttemptSummary[]> {
    try {
      const params = new URLSearchParams({ language });
      if (limit) params.append('limit', limit.toString());
      const response = await api.get(`/assessments/attempts?${params.toString()}`);
      return response.data;
    } catch (error) {
      handleError(error);
      throw error;
    }
  },

  async getUserLevel(language: string): Promise<UserLevel> {
    try {
      const response = await api.get(`/user-levels/${language}`);
      return response.data;
    } catch (error) {
      handleError(error);
      throw error;
    }
  },

  async updateUserLevel(
    language: string,
    cefrLevel: string,
    proficiencyScore: number
  ): Promise<UserLevel> {
    try {
      const response = await api.put(`/user-levels/${language}`, {
        cefr_level: cefrLevel,
        proficiency_score: proficiencyScore,
      });
      return response.data;
    } catch (error) {
      handleError(error);
      throw error;
    }
  },

  async getAttempt(attemptId: number): Promise<AttemptResult> {
    try {
      const response = await api.get(`/assessments/attempts/${attemptId}`);
      return response.data;
    } catch (error) {
      handleError(error);
      throw error;
    }
  },

  async deleteAttempt(attemptId: number): Promise<void> {
    try {
      await api.delete(`/assessments/attempts/${attemptId}`);
    } catch (error) {
      handleError(error);
      throw error;
    }
  },
};
