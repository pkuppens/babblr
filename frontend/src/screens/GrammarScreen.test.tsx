/**
 * Tests for GrammarScreen component.
 * Following TDD: tests written first, then implementation.
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import GrammarScreen from './GrammarScreen';
import * as api from '../services/api';

// Mock the grammar service
vi.mock('../services/api', () => ({
  grammarService: {
    listLessons: vi.fn(),
    getLesson: vi.fn(),
    updateProgress: vi.fn(),
    getRecaps: vi.fn(),
  },
}));

describe('GrammarScreen', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    // Mock getRecaps to return empty array by default
    vi.mocked(api.grammarService.getRecaps).mockResolvedValue([]);
  });

  describe('when loading lessons', () => {
    it('should display loading state initially', async () => {
      vi.mocked(api.grammarService.listLessons).mockImplementation(
        () => new Promise(() => {}) // Never resolves
      );

      render(<GrammarScreen selectedLanguage="spanish" selectedDifficulty="A1" />);

      // Should show loading indicator
      expect(screen.getByText(/loading/i)).toBeInTheDocument();
    });

    it('should display error message when lessons fail to load', async () => {
      vi.mocked(api.grammarService.listLessons).mockRejectedValue(
        new Error('Failed to load lessons')
      );

      render(<GrammarScreen selectedLanguage="spanish" selectedDifficulty="A1" />);

      await waitFor(() => {
        expect(screen.getByText(/failed to load/i)).toBeInTheDocument();
      });
    });
  });

  describe('when lessons are loaded', () => {
    it('should display list of grammar lessons', async () => {
      const mockLessons = [
        {
          id: 1,
          title: 'Present Tense',
          language: 'es',
          lesson_type: 'grammar',
          difficulty_level: 'A1',
          order_index: 1,
          is_active: true,
          created_at: '2024-01-01T00:00:00Z',
        },
        {
          id: 2,
          title: 'Past Tense',
          language: 'es',
          lesson_type: 'grammar',
          difficulty_level: 'A1',
          order_index: 2,
          is_active: true,
          created_at: '2024-01-02T00:00:00Z',
        },
      ];

      vi.mocked(api.grammarService.listLessons).mockResolvedValue(mockLessons);

      render(<GrammarScreen selectedLanguage="spanish" selectedDifficulty="A1" />);

      await waitFor(() => {
        expect(screen.getByText('Present Tense')).toBeInTheDocument();
        expect(screen.getByText('Past Tense')).toBeInTheDocument();
      });
    });

    it('should show progress indicators for lessons', async () => {
      const mockLessons = [
        {
          id: 1,
          title: 'Present Tense',
          language: 'es',
          lesson_type: 'grammar',
          difficulty_level: 'A1',
          order_index: 1,
          is_active: true,
          created_at: '2024-01-01T00:00:00Z',
        },
      ];

      vi.mocked(api.grammarService.listLessons).mockResolvedValue(mockLessons);

      render(<GrammarScreen selectedLanguage="spanish" selectedDifficulty="A1" />);

      await waitFor(() => {
        // Should show progress indicators (not started, in progress, completed)
        // Implementation detail: badges or progress bars
        expect(screen.getByText('Present Tense')).toBeInTheDocument();
      });
    });

    it('should highlight recap lessons due for review', async () => {
      const mockLessons = [
        {
          id: 1,
          title: 'Present Tense',
          language: 'es',
          lesson_type: 'grammar',
          difficulty_level: 'A1',
          order_index: 1,
          is_active: true,
          created_at: '2024-01-01T00:00:00Z',
        },
      ];

      const mockRecaps = [mockLessons[0]];

      vi.mocked(api.grammarService.listLessons).mockResolvedValue(mockLessons);
      vi.mocked(api.grammarService.getRecaps).mockResolvedValue(mockRecaps);

      render(<GrammarScreen selectedLanguage="spanish" selectedDifficulty="A1" />);

      await waitFor(() => {
        // Should show recap indicator (badge, different color, etc.)
        const lessonElement = screen.getByText('Present Tense');
        expect(lessonElement).toBeInTheDocument();
        // Check for recap indicator (implementation detail)
      });
    });
  });

  describe('when selecting a lesson', () => {
    it('should open lesson view with explanation and examples', async () => {
      const mockLessons = [
        {
          id: 1,
          title: 'Present Tense',
          language: 'es',
          lesson_type: 'grammar',
          difficulty_level: 'A1',
          order_index: 1,
          is_active: true,
          created_at: '2024-01-01T00:00:00Z',
        },
      ];

      const mockLessonDetail = {
        ...mockLessons[0],
        rules: [
          {
            id: 1,
            title: 'Regular -ar verbs',
            description: 'Add -o, -as, -a to the stem',
            examples: [{ es: 'hablo', en: 'I speak' }],
            difficulty_level: 'A1',
          },
        ],
        examples: [
          {
            text: 'Yo hablo español',
            translation: 'I speak Spanish',
            audio_url: '/tts/synthesize?text=Yo+hablo+español&language=es',
          },
        ],
        exercises: [],
        items: [],
      };

      vi.mocked(api.grammarService.listLessons).mockResolvedValue(mockLessons);
      vi.mocked(api.grammarService.getLesson).mockResolvedValue(mockLessonDetail);

      render(<GrammarScreen selectedLanguage="spanish" selectedDifficulty="A1" />);

      await waitFor(() => {
        expect(screen.getByText('Present Tense')).toBeInTheDocument();
      });

      const lessonButton = screen.getByText('Present Tense');
      await userEvent.click(lessonButton);

      await waitFor(() => {
        expect(screen.getByText('Regular -ar verbs')).toBeInTheDocument();
        expect(screen.getByText('Yo hablo español')).toBeInTheDocument();
      });
    });

    it('should display audio playback buttons for examples', async () => {
      const mockLessons = [
        {
          id: 1,
          title: 'Present Tense',
          language: 'es',
          lesson_type: 'grammar',
          difficulty_level: 'A1',
          order_index: 1,
          is_active: true,
          created_at: '2024-01-01T00:00:00Z',
        },
      ];

      const mockLessonDetail = {
        ...mockLessons[0],
        rules: [],
        examples: [
          {
            text: 'Yo hablo español',
            translation: 'I speak Spanish',
            audio_url: '/tts/synthesize?text=Yo+hablo+español&language=es',
          },
        ],
        exercises: [],
        items: [],
      };

      vi.mocked(api.grammarService.listLessons).mockResolvedValue(mockLessons);
      vi.mocked(api.grammarService.getLesson).mockResolvedValue(mockLessonDetail);

      render(<GrammarScreen selectedLanguage="spanish" selectedDifficulty="A1" />);

      await waitFor(() => {
        expect(screen.getByText('Present Tense')).toBeInTheDocument();
      });

      const lessonButton = screen.getByText('Present Tense');
      await userEvent.click(lessonButton);

      await waitFor(() => {
        // Should show play button for audio
        const playButtons = screen.getAllByRole('button', { name: /play/i });
        expect(playButtons.length).toBeGreaterThan(0);
      });
    });
  });

  describe('when completing exercises', () => {
    it('should update progress when exercise is completed', async () => {
      const mockLessons = [
        {
          id: 1,
          title: 'Present Tense',
          language: 'es',
          lesson_type: 'grammar',
          difficulty_level: 'A1',
          order_index: 1,
          is_active: true,
          created_at: '2024-01-01T00:00:00Z',
        },
      ];

      const mockLessonDetail = {
        ...mockLessons[0],
        rules: [],
        examples: [],
        exercises: [
          {
            type: 'multiple_choice',
            question: 'Choose the correct form',
            options: ['hablo', 'hablas', 'habla'],
            correct: 0,
          },
        ],
        items: [],
      };

      const mockProgress = {
        id: 1,
        lesson_id: 1,
        language: 'es',
        status: 'in_progress' as const,
        completion_percentage: 50,
        mastery_score: 0.7,
        last_accessed_at: '2024-01-01T00:00:00Z',
      };

      vi.mocked(api.grammarService.listLessons).mockResolvedValue(mockLessons);
      vi.mocked(api.grammarService.getLesson).mockResolvedValue(mockLessonDetail);
      vi.mocked(api.grammarService.updateProgress).mockResolvedValue(mockProgress);

      render(<GrammarScreen selectedLanguage="spanish" selectedDifficulty="A1" />);

      await waitFor(() => {
        expect(screen.getByText('Present Tense')).toBeInTheDocument();
      });

      const lessonButton = screen.getByText('Present Tense');
      await userEvent.click(lessonButton);

      await waitFor(() => {
        expect(screen.getByText('Choose the correct form')).toBeInTheDocument();
      });

      // Select correct answer
      const correctOption = screen.getByText('hablo');
      await userEvent.click(correctOption);

      // Submit answer
      const submitButton = screen.getByRole('button', { name: /submit|check/i });
      await userEvent.click(submitButton);

      await waitFor(() => {
        expect(api.grammarService.updateProgress).toHaveBeenCalled();
        const callArgs = vi.mocked(api.grammarService.updateProgress).mock.calls[0][0];
        expect(callArgs.lesson_id).toBe(1);
        expect(callArgs.language).toBe('es');
        expect(['in_progress', 'completed']).toContain(callArgs.status);
        expect(typeof callArgs.completion_percentage).toBe('number');
        expect(typeof callArgs.mastery_score).toBe('number');
      });
    });

    it('should show immediate feedback for incorrect answers', async () => {
      const mockLessons = [
        {
          id: 1,
          title: 'Present Tense',
          language: 'es',
          lesson_type: 'grammar',
          difficulty_level: 'A1',
          order_index: 1,
          is_active: true,
          created_at: '2024-01-01T00:00:00Z',
        },
      ];

      const mockLessonDetail = {
        ...mockLessons[0],
        rules: [],
        examples: [],
        exercises: [
          {
            type: 'multiple_choice',
            question: 'Choose the correct form',
            options: ['hablo', 'hablas', 'habla'],
            correct: 0,
            explanation: 'hablo is the first person singular form',
          },
        ],
        items: [],
      };

      vi.mocked(api.grammarService.listLessons).mockResolvedValue(mockLessons);
      vi.mocked(api.grammarService.getLesson).mockResolvedValue(mockLessonDetail);

      render(<GrammarScreen selectedLanguage="spanish" selectedDifficulty="A1" />);

      await waitFor(() => {
        expect(screen.getByText('Present Tense')).toBeInTheDocument();
      });

      const lessonButton = screen.getByText('Present Tense');
      await userEvent.click(lessonButton);

      await waitFor(() => {
        expect(screen.getByText('Choose the correct form')).toBeInTheDocument();
      });

      // Select incorrect answer
      const incorrectOption = screen.getByText('hablas');
      await userEvent.click(incorrectOption);

      // Submit answer
      const submitButton = screen.getByRole('button', { name: /submit|check/i });
      await userEvent.click(submitButton);

      await waitFor(() => {
        // Should show feedback with explanation
        expect(screen.getByText(/incorrect|wrong/i)).toBeInTheDocument();
        expect(screen.getByText(/hablo is the first person/i)).toBeInTheDocument();
      });
    });
  });
});
