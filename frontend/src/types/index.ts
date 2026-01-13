export type Language = 'spanish' | 'italian' | 'german' | 'french' | 'dutch' | 'english';
export type NativeLanguage = 'spanish' | 'italian' | 'german' | 'french' | 'dutch' | 'english';
export type DifficultyLevel = 'A1' | 'A2' | 'B1' | 'B2' | 'C1' | 'C2';
export type MessageRole = 'user' | 'assistant';
export type TabKey =
  | 'home'
  | 'vocabulary'
  | 'grammar'
  | 'conversations'
  | 'assessments'
  | 'configuration';

export interface Topic {
  id: string;
  icon: string;
  level: DifficultyLevel;
  names: Record<Language, string>;
  descriptions: Record<Language, string>;
  starters: Record<Language, string[]>;
}

export interface TopicsData {
  topics: Topic[];
}

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

export interface STTCorrection {
  original: string;
  corrected: string;
  reason: string;
}

export interface ChatResponse {
  assistant_message: string;
  corrections?: Correction[];
}

export interface TranscriptionResponse {
  text: string;
  language: string;
  confidence: number;
  duration: number;
  corrections?: STTCorrection[];
}
