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
  topic_id?: string | null;
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
  translation?: string;
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
  translation?: string;
}

export interface TranscriptionResponse {
  text: string;
  language: string;
  confidence: number;
  duration: number;
  corrections?: STTCorrection[];
}

// Assessment types
export interface Assessment {
  id: number;
  language: string;
  assessment_type: string;
  title: string;
  description?: string;
  difficulty_level: string;
  duration_minutes: number;
  skill_categories: string[];
  is_active: boolean;
  created_at: string;
  question_count: number;
}

export interface AssessmentQuestion {
  id: number;
  assessment_id: number;
  question_type: string;
  skill_category: string;
  question_text: string;
  options?: string[];
  points: number;
  order_index: number;
}

export interface AssessmentDetail extends Assessment {
  questions: AssessmentQuestion[];
}

export interface SkillScore {
  skill: string;
  score: number;
  total: number;
  correct: number;
}

export interface AttemptResult {
  id: number;
  assessment_id: number;
  language: string;
  score: number;
  recommended_level: string;
  skill_scores: SkillScore[];
  total_questions: number;
  correct_answers: number;
  started_at: string;
  completed_at: string;
  practice_recommendations: string[];
}

export interface AttemptSummary {
  id: number;
  assessment_id: number;
  assessment_title: string;
  language: string;
  score: number;
  recommended_level: string;
  completed_at: string;
}

export interface UserLevel {
  id: number;
  language: string;
  cefr_level: string;
  proficiency_score: number;
  assessed_at: string;
}
