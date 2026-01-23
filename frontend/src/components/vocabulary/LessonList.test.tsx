import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import LessonList from './LessonList';
import * as vocabularyService from '../../services/vocabularyService';

vi.mock('../../services/vocabularyService');

describe('LessonList', () => {
  const mockLessons = [
    {
      id: 1,
      language: 'es',
      lesson_type: 'vocabulary',
      title: 'Greetings',
      oneliner: 'Learn greetings',
      subject: 'Basics',
      difficulty_level: 'A1',
      order_index: 0,
      is_active: true,
      created_at: '2026-01-22T00:00:00Z',
      updated_at: '2026-01-22T00:00:00Z',
    },
    {
      id: 2,
      language: 'es',
      lesson_type: 'vocabulary',
      title: 'Numbers',
      oneliner: 'Learn numbers',
      subject: 'Basics',
      difficulty_level: 'A1',
      order_index: 1,
      is_active: true,
      created_at: '2026-01-22T00:00:00Z',
      updated_at: '2026-01-22T00:00:00Z',
    },
  ];

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('shows loading state initially', () => {
    vi.mocked(vocabularyService.vocabularyService.getLessons).mockImplementation(
      () => new Promise(() => {}) // Never resolves
    );

    render(
      <LessonList language="es" onLessonSelect={() => {}} />
    );

    expect(screen.getByText('Loading lessons...')).toBeInTheDocument();
  });

  it('renders lessons when data is loaded', async () => {
    vi.mocked(vocabularyService.vocabularyService.getLessons).mockResolvedValue(
      mockLessons
    );
    vi.mocked(vocabularyService.vocabularyService.getProgress).mockRejectedValue(
      new Error('404')
    );

    render(
      <LessonList language="es" onLessonSelect={() => {}} />
    );

    await waitFor(() => {
      expect(screen.getByText('Greetings')).toBeInTheDocument();
      expect(screen.getByText('Numbers')).toBeInTheDocument();
    });
  });

  it('groups lessons by category', async () => {
    vi.mocked(vocabularyService.vocabularyService.getLessons).mockResolvedValue(
      mockLessons
    );
    vi.mocked(vocabularyService.vocabularyService.getProgress).mockRejectedValue(
      new Error('404')
    );

    render(
      <LessonList language="es" onLessonSelect={() => {}} />
    );

    await waitFor(() => {
      expect(screen.getByText('Basics')).toBeInTheDocument();
    });
  });

  it('shows empty state when no lessons available', async () => {
    vi.mocked(vocabularyService.vocabularyService.getLessons).mockResolvedValue([]);

    render(
      <LessonList language="es" onLessonSelect={() => {}} />
    );

    await waitFor(() => {
      expect(
        screen.getByText(/No vocabulary lessons available/)
      ).toBeInTheDocument();
    });
  });

  it('shows error when lessons fail to load', async () => {
    const errorMessage = 'Network error';
    vi.mocked(vocabularyService.vocabularyService.getLessons).mockRejectedValue(
      new Error(errorMessage)
    );

    render(
      <LessonList language="es" onLessonSelect={() => {}} />
    );

    await waitFor(() => {
      expect(screen.getByText(new RegExp(errorMessage))).toBeInTheDocument();
    });
  });

  it('calls onLessonSelect when lesson is clicked', async () => {
    const onLessonSelect = vi.fn();
    vi.mocked(vocabularyService.vocabularyService.getLessons).mockResolvedValue(
      mockLessons
    );
    vi.mocked(vocabularyService.vocabularyService.getProgress).mockRejectedValue(
      new Error('404')
    );

    const { getByTestId } = render(
      <LessonList language="es" onLessonSelect={onLessonSelect} />
    );

    await waitFor(() => {
      getByTestId('lesson-1').click();
    });

    expect(onLessonSelect).toHaveBeenCalledWith(mockLessons[0]);
  });

  it('filters lessons by CEFR level', async () => {
    vi.mocked(vocabularyService.vocabularyService.getLessons).mockResolvedValue([
      mockLessons[0],
    ]);
    vi.mocked(vocabularyService.vocabularyService.getProgress).mockRejectedValue(
      new Error('404')
    );

    render(
      <LessonList language="es" selectedLevel="A1" onLessonSelect={() => {}} />
    );

    await waitFor(() => {
      expect(vi.mocked(vocabularyService.vocabularyService.getLessons)).toHaveBeenCalledWith(
        'es',
        'A1'
      );
    });
  });

  it('fetches progress for each lesson', async () => {
    vi.mocked(vocabularyService.vocabularyService.getLessons).mockResolvedValue(
      mockLessons
    );
    vi.mocked(vocabularyService.vocabularyService.getProgress)
      .mockResolvedValueOnce({
        id: 1,
        lesson_id: 1,
        language: 'es',
        status: 'in_progress',
        completion_percentage: 50,
        last_accessed_at: new Date().toISOString(),
      })
      .mockResolvedValueOnce({
        id: 2,
        lesson_id: 2,
        language: 'es',
        status: 'not_started',
        completion_percentage: 0,
        last_accessed_at: new Date().toISOString(),
      });

    render(
      <LessonList language="es" onLessonSelect={() => {}} />
    );

    await waitFor(() => {
      expect(vocabularyService.vocabularyService.getProgress).toHaveBeenCalledTimes(2);
    });
  });
});
