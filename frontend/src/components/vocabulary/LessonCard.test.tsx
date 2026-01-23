import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import LessonCard from './LessonCard';
import type { VocabularyLesson, VocabularyProgress } from '../../types';

describe('LessonCard', () => {
  const mockLesson: VocabularyLesson = {
    id: 1,
    language: 'es',
    lesson_type: 'vocabulary',
    title: 'Greetings',
    oneliner: 'Learn common Spanish greetings',
    description: 'Master basic greetings in Spanish',
    subject: 'Basics',
    difficulty_level: 'A1',
    order_index: 0,
    is_active: true,
    created_at: '2026-01-22T00:00:00Z',
    updated_at: '2026-01-22T00:00:00Z',
  };

  const mockProgress: VocabularyProgress = {
    id: 1,
    lesson_id: 1,
    language: 'es',
    status: 'in_progress',
    completion_percentage: 50,
    mastery_score: 0.65,
    last_accessed_at: new Date().toISOString(),
  };

  it('renders lesson title and description', () => {
    const onClick = vi.fn();
    render(<LessonCard lesson={mockLesson} onClick={onClick} />);

    expect(screen.getByText('Greetings')).toBeInTheDocument();
    expect(screen.getByText('Learn common Spanish greetings')).toBeInTheDocument();
  });

  it('displays CEFR level badge', () => {
    const onClick = vi.fn();
    render(<LessonCard lesson={mockLesson} onClick={onClick} />);

    expect(screen.getByText(/A1/)).toBeInTheDocument();
  });

  it('shows progress bar with completion percentage', () => {
    const onClick = vi.fn();
    render(<LessonCard lesson={mockLesson} progress={mockProgress} onClick={onClick} />);

    const progressBar = screen.getByRole('progressbar');
    expect(progressBar).toHaveAttribute('aria-valuenow', '50');
    expect(screen.getByText('50%')).toBeInTheDocument();
  });

  it('displays mastery score when available', () => {
    const onClick = vi.fn();
    render(<LessonCard lesson={mockLesson} progress={mockProgress} onClick={onClick} />);

    expect(screen.getByText(/Mastery: 65%/)).toBeInTheDocument();
  });

  it('shows "Start" button when no progress', () => {
    const onClick = vi.fn();
    render(<LessonCard lesson={mockLesson} onClick={onClick} />);

    expect(screen.getByText('Start')).toBeInTheDocument();
  });

  it('shows "Continue" button when in progress', () => {
    const onClick = vi.fn();
    render(<LessonCard lesson={mockLesson} progress={mockProgress} onClick={onClick} />);

    expect(screen.getByText('Continue')).toBeInTheDocument();
  });

  it('shows "Review" button when completed', () => {
    const onClick = vi.fn();
    const completedProgress: VocabularyProgress = {
      ...mockProgress,
      status: 'completed',
      completion_percentage: 100,
    };
    render(
      <LessonCard lesson={mockLesson} progress={completedProgress} onClick={onClick} />
    );

    expect(screen.getByText('Review')).toBeInTheDocument();
  });

  it('calls onClick handler when button is clicked', () => {
    const onClick = vi.fn();
    const { getByTestId } = render(<LessonCard lesson={mockLesson} onClick={onClick} />);

    getByTestId('lesson-1').click();
    expect(onClick).toHaveBeenCalledTimes(1);
  });

  it('shows 0% progress when no progress data', () => {
    const onClick = vi.fn();
    render(<LessonCard lesson={mockLesson} onClick={onClick} />);

    expect(screen.getByText('0%')).toBeInTheDocument();
  });
});
