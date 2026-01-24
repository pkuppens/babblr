import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import AssessmentCard from './AssessmentCard';

describe('AssessmentCard', () => {
  it('should render with assessment data', () => {
    render(
      <AssessmentCard
        latestScore={78.5}
        recommendedLevel="B1"
        lastAttempt="2024-01-15T10:00:00Z"
      />
    );

    expect(screen.getByText('Assessment Progress')).toBeInTheDocument();
    expect(screen.getByText('79%')).toBeInTheDocument(); // Rounded
    expect(screen.getByText('B1')).toBeInTheDocument();
  });

  it('should show empty state when no data', () => {
    render(
      <AssessmentCard
        latestScore={null}
        recommendedLevel={null}
        lastAttempt={null}
      />
    );

    expect(screen.getByText('No assessments completed yet.')).toBeInTheDocument();
    expect(screen.getByText(/Take an assessment/)).toBeInTheDocument();
  });

  it('should display last attempt date when provided', () => {
    render(
      <AssessmentCard
        latestScore={75}
        recommendedLevel="B1"
        lastAttempt="2024-01-15T10:00:00Z"
      />
    );

    expect(screen.getByText(/Last assessment:/)).toBeInTheDocument();
  });
});
