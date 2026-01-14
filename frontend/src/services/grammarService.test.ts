/**
 * Tests for grammar service API calls.
 * Following TDD: tests written first, then implementation.
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { grammarService, api } from './api';

// Mock axios
vi.mock('axios', () => {
  return {
    default: {
      create: vi.fn(() => ({
        get: vi.fn(),
        post: vi.fn(),
        put: vi.fn(),
      })),
    },
  };
});

describe('grammarService', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('when listing grammar lessons', () => {
    it('should fetch lessons for a language', async () => {
      const mockLessons = [
        {
          id: 1,
          title: 'Present Tense',
          language: 'es',
          lesson_type: 'grammar',
          difficulty_level: 'A1',
        },
      ];

      vi.mocked(api.get).mockResolvedValue({ data: mockLessons });

      const result = await grammarService.listLessons('es');

      expect(api.get).toHaveBeenCalledWith('/grammar/lessons?language=es');
      expect(result).toEqual(mockLessons);
    });

    it('should include level filter when provided', async () => {
      vi.mocked(api.get).mockResolvedValue({ data: [] });

      await grammarService.listLessons('es', 'A1');

      expect(api.get).toHaveBeenCalledWith('/grammar/lessons?language=es&level=A1');
    });

    it('should include type filter when provided', async () => {
      vi.mocked(api.get).mockResolvedValue({ data: [] });

      await grammarService.listLessons('es', undefined, 'recap');

      expect(api.get).toHaveBeenCalledWith('/grammar/lessons?language=es&type=recap');
    });
  });

  describe('when getting a specific lesson', () => {
    it('should fetch lesson with full content', async () => {
      const mockLesson = {
        id: 1,
        title: 'Present Tense',
        rules: [],
        examples: [],
        exercises: [],
      };

      vi.mocked(api.get).mockResolvedValue({ data: mockLesson });

      const result = await grammarService.getLesson(1);

      expect(api.get).toHaveBeenCalledWith('/grammar/lessons/1');
      expect(result).toEqual(mockLesson);
    });
  });

  describe('when updating progress', () => {
    it('should post progress with mastery score', async () => {
      const mockProgress = {
        id: 1,
        lesson_id: 1,
        status: 'completed',
        completion_percentage: 100,
        mastery_score: 0.9,
      };

      vi.mocked(api.post).mockResolvedValue({ data: mockProgress });

      const result = await grammarService.updateProgress({
        lesson_id: 1,
        language: 'es',
        status: 'completed',
        completion_percentage: 100,
        mastery_score: 0.9,
      });

      expect(api.post).toHaveBeenCalledWith('/grammar/progress', {
        lesson_id: 1,
        language: 'es',
        status: 'completed',
        completion_percentage: 100,
        mastery_score: 0.9,
      });
      expect(result).toEqual(mockProgress);
    });
  });

  describe('when getting recaps', () => {
    it('should fetch lessons due for review', async () => {
      const mockRecaps = [
        {
          id: 1,
          title: 'Past Tense Review',
          language: 'es',
        },
      ];

      vi.mocked(api.get).mockResolvedValue({ data: mockRecaps });

      const result = await grammarService.getRecaps('es');

      expect(api.get).toHaveBeenCalledWith('/grammar/recaps?language=es');
      expect(result).toEqual(mockRecaps);
    });

    it('should include level filter when provided', async () => {
      vi.mocked(api.get).mockResolvedValue({ data: [] });

      await grammarService.getRecaps('es', 'A1');

      expect(api.get).toHaveBeenCalledWith('/grammar/recaps?language=es&level=A1');
    });
  });
});
