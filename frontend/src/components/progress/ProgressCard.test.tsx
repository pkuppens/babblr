import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import ProgressCard from './ProgressCard';

describe('ProgressCard', () => {
  it('should render with vocabulary progress', () => {
    render(
      <ProgressCard
        title="Vocabulary Lessons"
        completed={5}
        inProgress={2}
        total={12}
        lastActivity="2024-01-15T10:00:00Z"
        type="vocabulary"
      />
    );

    expect(screen.getByText('Vocabulary Lessons')).toBeInTheDocument();
    expect(screen.getByText('5')).toBeInTheDocument();
    expect(screen.getByText('Completed')).toBeInTheDocument();
    expect(screen.getByText('2')).toBeInTheDocument();
    expect(screen.getByText('In Progress')).toBeInTheDocument();
  });

  it('should calculate completion percentage correctly', () => {
    render(
      <ProgressCard
        title="Grammar Lessons"
        completed={6}
        inProgress={2}
        total={10}
        lastActivity={null}
        type="grammar"
      />
    );

    expect(screen.getByText('60%')).toBeInTheDocument();
  });

  it('should handle zero total lessons', () => {
    render(
      <ProgressCard
        title="Vocabulary Lessons"
        completed={0}
        inProgress={0}
        total={0}
        lastActivity={null}
        type="vocabulary"
      />
    );

    expect(screen.getByText('0%')).toBeInTheDocument();
  });

  it('should display last activity when provided', () => {
    render(
      <ProgressCard
        title="Vocabulary Lessons"
        completed={5}
        inProgress={2}
        total={12}
        lastActivity="2024-01-15T10:00:00Z"
        type="vocabulary"
      />
    );

    expect(screen.getByText(/Last activity:/)).toBeInTheDocument();
  });

  it('should not display last activity when null', () => {
    render(
      <ProgressCard
        title="Vocabulary Lessons"
        completed={5}
        inProgress={2}
        total={12}
        lastActivity={null}
        type="vocabulary"
      />
    );

    expect(screen.queryByText(/Last activity:/)).not.toBeInTheDocument();
  });
});
