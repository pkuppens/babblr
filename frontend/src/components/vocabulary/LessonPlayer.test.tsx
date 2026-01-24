import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import LessonPlayer from './LessonPlayer';
import * as vocabularyService from '../../services/vocabularyService';
import type { VocabularyLessonDetail } from '../../types';

vi.mock('../../services/vocabularyService');

describe('LessonPlayer', () => {
  const mockLesson: VocabularyLessonDetail = {
    id: 1,
    language: 'es',
    lesson_type: 'vocabulary',
    title: 'Basic Greetings',
    oneliner: 'Learn basic greetings',
    description: 'Master basic Spanish greetings',
    subject: 'Basics',
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
        order_index: 0,
      },
      {
        id: 2,
        lesson_id: 1,
        word: 'Adiós',
        translation: 'Goodbye',
        example: 'Adiós, hasta luego.',
        order_index: 1,
      },
      {
        id: 3,
        lesson_id: 1,
        word: 'Buenos días',
        translation: 'Good morning',
        example: 'Buenos días, señor.',
        order_index: 2,
      },
    ],
  };

  beforeEach(() => {
    vi.clearAllMocks();
    vi.mocked(vocabularyService.vocabularyService.saveProgress).mockResolvedValue({
      id: 1,
      lesson_id: 1,
      language: 'es',
      status: 'in_progress',
      completion_percentage: 0,
      last_accessed_at: new Date().toISOString(),
    });
  });

  it('renders lesson title and metadata', () => {
    const onLessonComplete = vi.fn();
    const onExit = vi.fn();

    render(
      <LessonPlayer lesson={mockLesson} onLessonComplete={onLessonComplete} onExit={onExit} />
    );

    expect(screen.getByText('Basic Greetings')).toBeInTheDocument();
    expect(screen.getByText('Learn basic greetings')).toBeInTheDocument();
  });

  it('displays current vocabulary item', () => {
    const onLessonComplete = vi.fn();
    const onExit = vi.fn();

    render(
      <LessonPlayer lesson={mockLesson} onLessonComplete={onLessonComplete} onExit={onExit} />
    );

    // First item should be displayed
    expect(screen.getByText('Hola')).toBeInTheDocument();
    expect(screen.getByText('1 of 3')).toBeInTheDocument();
  });

  it('shows progress bar with completion percentage', () => {
    const onLessonComplete = vi.fn();
    const onExit = vi.fn();

    render(
      <LessonPlayer lesson={mockLesson} onLessonComplete={onLessonComplete} onExit={onExit} />
    );

    expect(screen.getByText('0 / 3 completed')).toBeInTheDocument();
  });

  it('navigates to next item when Next button clicked', async () => {
    const user = userEvent.setup();
    const onLessonComplete = vi.fn();
    const onExit = vi.fn();

    render(
      <LessonPlayer lesson={mockLesson} onLessonComplete={onLessonComplete} onExit={onExit} />
    );

    const nextButton = screen.getByText(/Next/);
    await user.click(nextButton);

    await waitFor(() => {
      expect(screen.getByText('Adiós')).toBeInTheDocument();
      expect(screen.getByText('2 of 3')).toBeInTheDocument();
    });
  });

  it('navigates to previous item when Previous button clicked', async () => {
    const user = userEvent.setup();
    const onLessonComplete = vi.fn();
    const onExit = vi.fn();

    const { rerender } = render(
      <LessonPlayer lesson={mockLesson} onLessonComplete={onLessonComplete} onExit={onExit} />
    );

    // Move to second item
    const nextButton = screen.getByText(/Next/);
    await user.click(nextButton);

    await waitFor(() => {
      expect(screen.getByText('Adiós')).toBeInTheDocument();
    });

    // Move back to first item
    const prevButton = screen.getByText(/Previous/);
    await user.click(prevButton);

    await waitFor(() => {
      expect(screen.getByText('Hola')).toBeInTheDocument();
    });
  });

  it('disables Previous button on first item', () => {
    const onLessonComplete = vi.fn();
    const onExit = vi.fn();

    render(
      <LessonPlayer lesson={mockLesson} onLessonComplete={onLessonComplete} onExit={onExit} />
    );

    const prevButton = screen
      .getAllByRole('button')
      .find(btn => btn.getAttribute('aria-label') === 'Previous word');
    expect(prevButton).toBeDisabled();
  });

  it('calls onExit when Exit button clicked', async () => {
    const user = userEvent.setup();
    const onLessonComplete = vi.fn();
    const onExit = vi.fn();

    render(
      <LessonPlayer lesson={mockLesson} onLessonComplete={onLessonComplete} onExit={onExit} />
    );

    const exitButton = screen.getByText(/Exit/);
    await user.click(exitButton);

    expect(onExit).toHaveBeenCalledTimes(1);
  });

  it('saves progress when moving through items', async () => {
    const user = userEvent.setup();
    const onLessonComplete = vi.fn();
    const onExit = vi.fn();

    render(
      <LessonPlayer lesson={mockLesson} onLessonComplete={onLessonComplete} onExit={onExit} />
    );

    const nextButton = screen.getByText(/Next/);
    await user.click(nextButton);

    await waitFor(() => {
      expect(vocabularyService.vocabularyService.saveProgress).toHaveBeenCalled();
    });
  });

  it('calls onLessonComplete when all items are completed', async () => {
    const user = userEvent.setup();
    const onLessonComplete = vi.fn();
    const onExit = vi.fn();

    render(
      <LessonPlayer lesson={mockLesson} onLessonComplete={onLessonComplete} onExit={onExit} />
    );

    const nextButton = screen.getByText(/Next/);

    // Navigate through all items
    await user.click(nextButton); // Move to item 2
    await user.click(nextButton); // Move to item 3
    await user.click(nextButton); // Trigger completion

    await waitFor(() => {
      expect(onLessonComplete).toHaveBeenCalledTimes(1);
    });
  });

  it('shows completion message when lesson is complete', async () => {
    const user = userEvent.setup();
    const onLessonComplete = vi.fn();
    const onExit = vi.fn();

    render(
      <LessonPlayer lesson={mockLesson} onLessonComplete={onLessonComplete} onExit={onExit} />
    );

    const nextButton = screen.getByText(/Next/);

    // Navigate through all items to completion
    await user.click(nextButton);
    await user.click(nextButton);
    await user.click(nextButton);

    await waitFor(() => {
      expect(screen.getByText(/Lesson Complete/)).toBeInTheDocument();
      expect(screen.getByText(/completed all 3 vocabulary items/)).toBeInTheDocument();
    });
  });
});
