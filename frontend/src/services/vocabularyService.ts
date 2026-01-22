import { api } from './api';
import { handleError } from '../utils/errorHandler';
import type {
  VocabularyLesson,
  VocabularyLessonDetail,
  VocabularyProgress,
  VocabularyProgressCreate,
} from '../types';

/**
 * Vocabulary Service
 *
 * Handles all API calls related to vocabulary lessons:
 * - Fetching vocabulary lessons by language and level
 * - Getting detailed lesson information with items
 * - Saving user progress for lessons
 * - Error handling and retry logic
 */
export const vocabularyService = {
  /**
   * Get all vocabulary lessons for a language and optional CEFR level
   * @param language - Target language code (e.g., 'es', 'it', 'de')
   * @param level - Optional CEFR level filter (A1, A2, B1, B2, C1, C2)
   * @returns Promise<VocabularyLesson[]> - List of vocabulary lessons
   */
  async getLessons(language: string, level?: string): Promise<VocabularyLesson[]> {
    try {
      console.log('[Vocabulary] Fetching lessons:', { language, level });
      const params = new URLSearchParams({ language });
      if (level) params.append('level', level);
      const response = await api.get(`/vocabulary/lessons?${params.toString()}`);
      console.log('[Vocabulary] Lessons fetched:', {
        language,
        level,
        count: response.data.length,
      });
      return response.data;
    } catch (error) {
      console.error('[Vocabulary] Failed to fetch lessons');
      handleError(error);
      throw error;
    }
  },

  /**
   * Get a single vocabulary lesson with all its items
   * @param lessonId - The ID of the lesson to fetch
   * @returns Promise<VocabularyLessonDetail> - Lesson with all items
   */
  async getLesson(lessonId: number): Promise<VocabularyLessonDetail> {
    try {
      console.log('[Vocabulary] Fetching lesson:', { lessonId });
      const response = await api.get(`/vocabulary/lessons/${lessonId}`);
      console.log('[Vocabulary] Lesson fetched:', {
        lessonId,
        itemCount: response.data.items?.length || 0,
      });
      return response.data;
    } catch (error) {
      console.error('[Vocabulary] Failed to fetch lesson');
      handleError(error);
      throw error;
    }
  },

  /**
   * Save progress for a vocabulary lesson
   * @param progress - Progress data to save (lesson_id, language, status, etc.)
   * @returns Promise<VocabularyProgress> - Updated progress
   */
  async saveProgress(progress: VocabularyProgressCreate): Promise<VocabularyProgress> {
    try {
      console.log('[Vocabulary] Saving progress:', {
        lesson_id: progress.lesson_id,
        language: progress.language,
        completion_percentage: progress.completion_percentage,
      });
      const response = await api.post(
        `/vocabulary/lessons/${progress.lesson_id}/progress`,
        progress
      );
      console.log('[Vocabulary] Progress saved:', {
        lesson_id: progress.lesson_id,
        status: response.data.status,
      });
      return response.data;
    } catch (error) {
      console.error('[Vocabulary] Failed to save progress');
      handleError(error);
      throw error;
    }
  },

  /**
   * Get progress for a specific lesson
   * @param lessonId - The ID of the lesson
   * @returns Promise<VocabularyProgress> - User's progress for the lesson
   */
  async getProgress(lessonId: number): Promise<VocabularyProgress> {
    try {
      console.log('[Vocabulary] Fetching progress:', { lessonId });
      const response = await api.get(`/vocabulary/lessons/${lessonId}/progress`);
      console.log('[Vocabulary] Progress fetched:', {
        lessonId,
        status: response.data.status,
      });
      return response.data;
    } catch (error) {
      // Progress might not exist yet (404), return default
      if ((error as any)?.response?.status === 404) {
        console.log('[Vocabulary] No progress found yet for lesson:', { lessonId });
        return {
          id: 0,
          lesson_id: lessonId,
          language: '',
          status: 'not_started',
          completion_percentage: 0,
          last_accessed_at: new Date().toISOString(),
        };
      }
      console.error('[Vocabulary] Failed to fetch progress');
      handleError(error);
      throw error;
    }
  },
};
