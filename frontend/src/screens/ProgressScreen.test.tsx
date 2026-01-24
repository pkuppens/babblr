import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import ProgressScreen from './ProgressScreen';
import { progressService } from '../services/progressService';

vi.mock('../services/progressService');

describe('ProgressScreen', () => {
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

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('should display loading state initially', () => {
    vi.mocked(progressService.getProgressSummary).mockImplementation(
      () => new Promise(() => {}) // Never resolves
    );

    render(<ProgressScreen selectedLanguage="spanish" />);

    expect(screen.getByText('Loading progress...')).toBeInTheDocument();
  });

  it('should display progress data when loaded', async () => {
    vi.mocked(progressService.getProgressSummary).mockResolvedValue(mockProgress);

    render(<ProgressScreen selectedLanguage="spanish" />);

    await waitFor(() => {
      expect(screen.getByText('Your Progress')).toBeInTheDocument();
    });

    expect(screen.getByText('Vocabulary Lessons')).toBeInTheDocument();
    expect(screen.getByText('Grammar Lessons')).toBeInTheDocument();
    expect(screen.getByText('Assessment Progress')).toBeInTheDocument();
  });

  it('should display error when fetch fails', async () => {
    vi.mocked(progressService.getProgressSummary).mockRejectedValue(
      new Error('Network error')
    );

    render(<ProgressScreen selectedLanguage="spanish" />);

    await waitFor(() => {
      expect(screen.getByText(/Failed to load progress data/)).toBeInTheDocument();
    });
  });

  it('should refetch data when language changes', async () => {
    vi.mocked(progressService.getProgressSummary).mockResolvedValue(mockProgress);

    const { rerender } = render(<ProgressScreen selectedLanguage="spanish" />);

    await waitFor(() => {
      expect(progressService.getProgressSummary).toHaveBeenCalledWith('spanish');
    });

    rerender(<ProgressScreen selectedLanguage="french" />);

    await waitFor(() => {
      expect(progressService.getProgressSummary).toHaveBeenCalledWith('french');
    });

    expect(progressService.getProgressSummary).toHaveBeenCalledTimes(2);
  });
});
