import { describe, it, expect, vi, beforeEach } from 'vitest';
import { progressService } from './progressService';
import { api } from './api';

vi.mock('./api');
vi.mock('../utils/language', () => ({
  getLanguageCode: vi.fn((lang: string) => {
    const codes: Record<string, string> = {
      spanish: 'es',
      italian: 'it',
      german: 'de',
      french: 'fr',
      dutch: 'nl',
      english: 'en',
    };
    return codes[lang];
  }),
}));

describe('progressService', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('getProgressSummary', () => {
    it('should fetch progress summary for a language', async () => {
      const mockProgress = {
        language: 'es',
        vocabulary: {
          completed: 5,
          in_progress: 2,
          total: 12,
          last_activity: '2024-01-15T10:00:00Z',
        },
        grammar: {
          completed: 3,
          in_progress: 1,
          total: 8,
          last_activity: '2024-01-14T09:00:00Z',
        },
        assessment: {
          latest_score: 75.5,
          recommended_level: 'B1',
          skill_scores: null,
          last_attempt: '2024-01-13T08:00:00Z',
        },
      };

      vi.mocked(api.get).mockResolvedValue({ data: mockProgress });

      const result = await progressService.getProgressSummary('spanish');

      expect(api.get).toHaveBeenCalledWith('/progress/summary?language=es');
      expect(result).toEqual(mockProgress);
    });

    it('should throw error when API call fails', async () => {
      const error = new Error('Network error');
      vi.mocked(api.get).mockRejectedValue(error);

      await expect(progressService.getProgressSummary('spanish')).rejects.toThrow();
    });
  });
});
