import React from 'react';
import './ProgressCard.css';

interface ProgressCardProps {
  title: string;
  completed: number;
  inProgress: number;
  total: number;
  lastActivity: string | null;
  type: 'vocabulary' | 'grammar';
}

/**
 * ProgressCard Component
 *
 * Displays progress for a single learning module (vocabulary or grammar)
 * Shows completion stats and last activity timestamp
 */
const ProgressCard: React.FC<ProgressCardProps> = ({
  title,
  completed,
  inProgress,
  total,
  lastActivity,
  type: _type,
}) => {
  const completionPercentage = total > 0 ? Math.round((completed / total) * 100) : 0;
  const notStarted = total - completed - inProgress;

  return (
    <div className="progress-card">
      <h3 className="progress-card-title">{title}</h3>

      <div className="progress-stats">
        <div className="progress-stat">
          <span className="stat-value">{completed}</span>
          <span className="stat-label">Completed</span>
        </div>
        <div className="progress-stat">
          <span className="stat-value">{inProgress}</span>
          <span className="stat-label">In Progress</span>
        </div>
        <div className="progress-stat">
          <span className="stat-value">{notStarted}</span>
          <span className="stat-label">Not Started</span>
        </div>
        <div className="progress-stat">
          <span className="stat-value">{total}</span>
          <span className="stat-label">Total</span>
        </div>
      </div>

      <div className="progress-bar-container">
        <div className="progress-bar-background">
          <div
            className="progress-bar-fill"
            style={{ width: `${completionPercentage}%` }}
            aria-valuenow={completionPercentage}
            aria-valuemin={0}
            aria-valuemax={100}
            role="progressbar"
            aria-label={`${title} completion`}
          />
        </div>
        <span className="progress-percentage">{completionPercentage}%</span>
      </div>

      {lastActivity && (
        <div className="last-activity">
          Last activity: {new Date(lastActivity).toLocaleDateString()}
        </div>
      )}
    </div>
  );
};

export default ProgressCard;
