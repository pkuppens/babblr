import React from 'react';
import type { VocabularyLesson, VocabularyProgress } from '../../types';
import { formatLevelLabel } from '../../utils/cefr';
import './LessonCard.css';

interface LessonCardProps {
  lesson: VocabularyLesson;
  progress?: VocabularyProgress;
  onClick: () => void;
}

/**
 * LessonCard Component
 *
 * Displays a single vocabulary lesson card with:
 * - Lesson title and description
 * - CEFR level badge
 * - Progress bar showing completion percentage
 * - "Continue" or "Start" button based on progress status
 */
const LessonCard: React.FC<LessonCardProps> = ({ lesson, progress, onClick }) => {
  const completionPercentage = progress?.completion_percentage || 0;
  const isCompleted = progress?.status === 'completed';
  const isInProgress = progress?.status === 'in_progress';
  const buttonLabel = isCompleted ? 'Review' : isInProgress ? 'Continue' : 'Start';

  return (
    <div className="lesson-card">
      <div className="lesson-card-header">
        <div className="lesson-title-section">
          <h3 className="lesson-title">
            {lesson.title}
            {lesson.title_en && (
              <span
                className="lesson-help"
                data-tooltip={lesson.title_en}
                aria-label="English title"
              >
                ?
              </span>
            )}
          </h3>
          <span className="lesson-level-badge">{formatLevelLabel(lesson.difficulty_level)}</span>
        </div>
      </div>

      {lesson.oneliner && (
        <p className="lesson-description">
          {lesson.oneliner}
          {lesson.oneliner_en && (
            <span
              className="lesson-help"
              data-tooltip={lesson.oneliner_en}
              aria-label="English oneliner"
            >
              ?
            </span>
          )}
        </p>
      )}

      <div className="lesson-progress-section">
        <div className="progress-bar-container">
          <div className="progress-bar-background">
            <div
              className="progress-bar-fill"
              style={{ width: `${completionPercentage}%` }}
              aria-valuenow={completionPercentage}
              aria-valuemin={0}
              aria-valuemax={100}
            />
          </div>
          <span className="progress-percentage">{Math.round(completionPercentage)}%</span>
        </div>

        {progress?.mastery_score !== undefined && (
          <div className="mastery-score">
            Mastery: {Math.round(progress.mastery_score * 100)}%
          </div>
        )}
      </div>

      <button className="lesson-action-button" onClick={onClick} data-testid={`lesson-${lesson.id}`}>
        {buttonLabel}
      </button>
    </div>
  );
};

export default LessonCard;
