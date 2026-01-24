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
  | 'progress'
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

export interface QuestionAnswer {
  question_id: number;
  question_text: string;
  skill_category: string;
  user_answer: string;
  correct_answer: string;
  is_correct: boolean;
  options?: string[];
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
  question_answers?: QuestionAnswer[];
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

// Vocabulary lesson types
export interface VocabularyLesson {
  id: number;
  language: string;
  lesson_type: string;
  title: string;
  title_en?: string;
  oneliner?: string;
  oneliner_en?: string;
  description?: string;
  description_en?: string;
  subject?: string;
  difficulty_level: string;
  order_index: number;
  is_active: boolean;
  created_at: string;
  updated_at: string;
  last_accessed_at?: string;
}

export interface VocabularyLessonDetail extends VocabularyLesson {
  items: VocabularyItem[];
}

export interface VocabularyItem {
  id: number;
  lesson_id: number;
  word: string;
  translation: string;
  example: string;
  audio_url?: string;
  order_index?: number;
}

export interface VocabularyProgress {
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

export interface VocabularyProgressCreate {
  lesson_id: number;
  language: string;
  status?: 'not_started' | 'in_progress' | 'completed';
  completion_percentage?: number;
  mastery_score?: number;
}

// Progress Dashboard Types
export interface VocabularyProgressSummary {
  completed: number;
  in_progress: number;
  total: number;
  last_activity: string | null;
}

export interface GrammarProgress {
  completed: number;
  in_progress: number;
  total: number;
  last_activity: string | null;
}

export interface AssessmentProgress {
  latest_score: number | null;
  recommended_level: string | null;
  skill_scores: any | null;
  last_attempt: string | null;
}

export interface ProgressSummary {
  language: string;
  vocabulary: VocabularyProgressSummary;
  grammar: GrammarProgress;
  assessment: AssessmentProgress;
}
