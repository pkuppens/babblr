import React from 'react';
import { formatLevelLabel } from '../../utils/cefr';
import './AssessmentCard.css';

interface AssessmentCardProps {
  latestScore: number | null;
  recommendedLevel: string | null;
  lastAttempt: string | null;
}

/**
 * AssessmentCard Component
 *
 * Displays assessment progress including latest score and recommended CEFR level
 */
const AssessmentCard: React.FC<AssessmentCardProps> = ({
  latestScore,
  recommendedLevel,
  lastAttempt,
}) => {
  const hasData = latestScore !== null || recommendedLevel !== null;

  return (
    <div className="assessment-card">
      <h3 className="assessment-card-title">Assessment Progress</h3>

      {!hasData ? (
        <div className="assessment-empty">
          <p>No assessments completed yet.</p>
          <p className="assessment-hint">Take an assessment to see your progress here.</p>
        </div>
      ) : (
        <div className="assessment-content">
          {recommendedLevel && (
            <div className="recommended-level">
              <span className="level-label">Your Level</span>
              <span className="level-badge">{formatLevelLabel(recommendedLevel)}</span>
            </div>
          )}

          {latestScore !== null && (
            <div className="latest-score">
              <span className="score-label">Latest Score</span>
              <span className="score-value">{Math.round(latestScore)}%</span>
            </div>
          )}

          {lastAttempt && (
            <div className="last-attempt">
              Last assessment: {new Date(lastAttempt).toLocaleDateString()}
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default AssessmentCard;
