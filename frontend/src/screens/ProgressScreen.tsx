import React, { useEffect, useState } from 'react';
import { progressService } from '../services/progressService';
import ProgressCard from '../components/progress/ProgressCard';
import AssessmentCard from '../components/progress/AssessmentCard';
import type { Language, ProgressSummary } from '../types';
import { getLanguageDisplayName } from '../utils/language';
import './Screen.css';
import './ProgressScreen.css';

interface ProgressScreenProps {
  selectedLanguage: Language;
}

/**
 * ProgressScreen displays learning progress dashboard
 *
 * Shows vocabulary, grammar, and assessment progress for the selected language
 * Fetches data from GET /progress/summary endpoint
 */
const ProgressScreen: React.FC<ProgressScreenProps> = ({ selectedLanguage }) => {
  const [progress, setProgress] = useState<ProgressSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchProgress = async () => {
      setLoading(true);
      setError(null);

      try {
        const data = await progressService.getProgressSummary(selectedLanguage);
        setProgress(data);
      } catch (err) {
        console.error('Failed to fetch progress:', err);
        setError('Failed to load progress data. Please try again.');
      } finally {
        setLoading(false);
      }
    };

    fetchProgress();
  }, [selectedLanguage]);

  if (loading) {
    return (
      <div className="screen-container">
        <div className="progress-loading">Loading progress...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="screen-container">
        <div className="progress-error">
          <p>{error}</p>
        </div>
      </div>
    );
  }

  if (!progress) {
    return (
      <div className="screen-container">
        <div className="progress-error">
          <p>No progress data available.</p>
        </div>
      </div>
    );
  }

  const languageDisplayName = getLanguageDisplayName(selectedLanguage);

  return (
    <div className="screen-container">
      <div className="progress-container">
        <div className="progress-header">
          <h2 className="progress-title">Your Progress</h2>
          <p className="progress-subtitle">Learning {languageDisplayName}</p>
        </div>

        <div className="progress-cards">
          <ProgressCard
            title="Vocabulary Lessons"
            completed={progress.vocabulary.completed}
            inProgress={progress.vocabulary.in_progress}
            total={progress.vocabulary.total}
            lastActivity={progress.vocabulary.last_activity}
            type="vocabulary"
          />

          <ProgressCard
            title="Grammar Lessons"
            completed={progress.grammar.completed}
            inProgress={progress.grammar.in_progress}
            total={progress.grammar.total}
            lastActivity={progress.grammar.last_activity}
            type="grammar"
          />

          <AssessmentCard
            latestScore={progress.assessment.latest_score}
            recommendedLevel={progress.assessment.recommended_level}
            lastAttempt={progress.assessment.last_attempt}
          />
        </div>
      </div>
    </div>
  );
};

export default ProgressScreen;
