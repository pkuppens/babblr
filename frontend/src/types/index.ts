export type Language = 'spanish' | 'italian' | 'german' | 'french' | 'dutch';
export type DifficultyLevel = 'beginner' | 'intermediate' | 'advanced';
export type MessageRole = 'user' | 'assistant';

export interface Conversation {
  id: number;
  language: string;
  difficulty_level: string;
  created_at: string;
  updated_at: string;
}

export interface Message {
  id: number;
  conversation_id: number;
  role: MessageRole;
  content: string;
  audio_path?: string;
  corrections?: string;
  created_at: string;
}

export interface Correction {
  original: string;
  corrected: string;
  explanation: string;
  type: 'grammar' | 'vocabulary' | 'style';
}

export interface VocabularyItem {
  id: number;
  word: string;
  translation: string;
  context?: string;
  difficulty: string;
  times_encountered: number;
  created_at: string;
  last_seen: string;
}

export interface ChatResponse {
  assistant_message: string;
  corrections?: Correction[];
  vocabulary_items?: VocabularyItem[];
}

export interface TranscriptionResponse {
  text: string;
  corrections?: Correction[];
}
