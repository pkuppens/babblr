/**
 * Tests for vocabulary service API calls.
 * Tests CRUD operations for vocabulary lessons and progress tracking.
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { vocabularyService } from './vocabularyService';
import { api } from './api';

vi.mock('./api', () => ({
  api: {
    get: vi.fn(),
    post: vi.fn(),
  },
  handleError: vi.fn(),
}));

describe('vocabularyService', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('getLessons', () => {
    it('should fetch vocabulary lessons for a language', async () => {
      const mockLessons = [
        {
          id: 1,
          language: 'es',
          lesson_type: 'vocabulary',
          title: 'Greetings',
          difficulty_level: 'A1',
          order_index: 0,
          is_active: true,
          created_at: '2026-01-22T00:00:00Z',
          updated_at: '2026-01-22T00:00:00Z',
        },
      ];

      vi.mocked(api.get).mockResolvedValue({ data: mockLessons });

      const result = await vocabularyService.getLessons('es');

      expect(api.get).toHaveBeenCalledWith('/vocabulary/lessons?language=es');
      expect(result).toEqual(mockLessons);
    });

    it('should include CEFR level filter when provided', async () => {
      vi.mocked(api.get).mockResolvedValue({ data: [] });

      await vocabularyService.getLessons('es', 'A1');

      expect(api.get).toHaveBeenCalledWith('/vocabulary/lessons?language=es&level=A1');
    });

    it('should handle API errors', async () => {
      const error = new Error('Network error');
      vi.mocked(api.get).mockRejectedValue(error);

      await expect(vocabularyService.getLessons('es')).rejects.toThrow('Network error');
    });
  });

  describe('getLesson', () => {
    it('should fetch a single lesson with items', async () => {
      const mockLesson = {
        id: 1,
        language: 'es',
        lesson_type: 'vocabulary',
        title: 'Greetings',
        difficulty_level: 'A1',
        order_index: 0,
        is_active: true,
        created_at: '2026-01-22T00:00:00Z',
        updated_at: '2026-01-22T00:00:00Z',
        items: [
          {
            id: 1,
            lesson_id: 1,
            word: 'Hola',
            translation: 'Hello',
            example: 'Hola, ¿cómo estás?',
          },
        ],
      };

      vi.mocked(api.get).mockResolvedValue({ data: mockLesson });

      const result = await vocabularyService.getLesson(1);

      expect(api.get).toHaveBeenCalledWith('/vocabulary/lessons/1');
      expect(result).toEqual(mockLesson);
      expect(result.items).toBeDefined();
      expect(result.items.length).toBe(1);
    });

    it('should handle API errors', async () => {
      const error = new Error('Lesson not found');
      vi.mocked(api.get).mockRejectedValue(error);

      await expect(vocabularyService.getLesson(999)).rejects.toThrow('Lesson not found');
    });
  });

  describe('saveProgress', () => {
    it('should save vocabulary lesson progress', async () => {
      const mockProgress = {
        id: 1,
        lesson_id: 1,
        language: 'es',
        status: 'in_progress',
        completion_percentage: 50,
        mastery_score: 0.65,
        last_accessed_at: '2026-01-22T00:00:00Z',
      };

      vi.mocked(api.post).mockResolvedValue({ data: mockProgress });

      const result = await vocabularyService.saveProgress({
        lesson_id: 1,
        language: 'es',
        status: 'in_progress',
        completion_percentage: 50,
        mastery_score: 0.65,
      });

      expect(api.post).toHaveBeenCalledWith('/vocabulary/lessons/1/progress', {
        lesson_id: 1,
        language: 'es',
        status: 'in_progress',
        completion_percentage: 50,
        mastery_score: 0.65,
      });
      expect(result).toEqual(mockProgress);
    });

    it('should update progress with completion', async () => {
      const mockProgress = {
        id: 1,
        lesson_id: 1,
        language: 'es',
        status: 'completed',
        completion_percentage: 100,
        mastery_score: 0.9,
        last_accessed_at: '2026-01-22T00:00:00Z',
      };

      vi.mocked(api.post).mockResolvedValue({ data: mockProgress });

      const result = await vocabularyService.saveProgress({
        lesson_id: 1,
        language: 'es',
        status: 'completed',
        completion_percentage: 100,
        mastery_score: 0.9,
      });

      expect(result.status).toBe('completed');
      expect(result.completion_percentage).toBe(100);
    });

    it('should handle API errors', async () => {
      const error = new Error('Failed to save progress');
      vi.mocked(api.post).mockRejectedValue(error);

      await expect(
        vocabularyService.saveProgress({
          lesson_id: 1,
          language: 'es',
          completion_percentage: 50,
        })
      ).rejects.toThrow('Failed to save progress');
    });
  });

  describe('getProgress', () => {
    it('should fetch progress for a lesson', async () => {
      const mockProgress = {
        id: 1,
        lesson_id: 1,
        language: 'es',
        status: 'in_progress',
        completion_percentage: 50,
        last_accessed_at: '2026-01-22T00:00:00Z',
      };

      vi.mocked(api.get).mockResolvedValue({ data: mockProgress });

      const result = await vocabularyService.getProgress(1);

      expect(api.get).toHaveBeenCalledWith('/vocabulary/lessons/1/progress');
      expect(result).toEqual(mockProgress);
    });

    it('should return default empty progress for 404 (not yet started)', async () => {
      const error = new Error('Not found') as Error & { response: { status: number } };
      error.response = { status: 404 };
      vi.mocked(api.get).mockRejectedValue(error);

      const result = await vocabularyService.getProgress(1);

      expect(result.status).toBe('not_started');
      expect(result.completion_percentage).toBe(0);
      expect(result.lesson_id).toBe(1);
    });

    it('should throw error for non-404 errors', async () => {
      const error = new Error('Server error') as Error & { response: { status: number } };
      error.response = { status: 500 };
      vi.mocked(api.get).mockRejectedValue(error);

      await expect(vocabularyService.getProgress(1)).rejects.toThrow();
    });
  });
});
