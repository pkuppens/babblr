import React from 'react';
import type { BackendErrorState } from '../hooks/useBackendError';
import './BackendErrorIndicator.css';

interface BackendErrorIndicatorProps {
  errorState: BackendErrorState;
}

/**
 * Persistent error indicator that shows when backend is unavailable.
 *
 * Displays an error icon in the header with a tooltip showing error details.
 * The indicator persists until the backend comes back online (detected via polling).
 */
const BackendErrorIndicator: React.FC<BackendErrorIndicatorProps> = ({ errorState }) => {
  if (!errorState.hasError) {
    return null;
  }

  const tooltipText = [
    errorState.message,
    errorState.action && `\n\nFix: ${errorState.action}`,
    errorState.technicalDetails && `\n\nTechnical: ${errorState.technicalDetails}`,
  ]
    .filter(Boolean)
    .join('');

  return (
    <div
      className="backend-error-indicator"
      title={tooltipText}
      aria-label="Backend connection error"
    >
      <span className="backend-error-icon" aria-hidden="true">
        ⚠️
      </span>
      <div className="backend-error-tooltip" role="tooltip">
        <div className="backend-error-tooltip-header">Backend Connection Error</div>
        <div className="backend-error-tooltip-message">{errorState.message}</div>
        {errorState.action && (
          <div className="backend-error-tooltip-action">
            <strong>Fix:</strong> {errorState.action}
          </div>
        )}
        {errorState.technicalDetails && (
          <div className="backend-error-tooltip-technical">
            <strong>Technical:</strong> {errorState.technicalDetails}
          </div>
        )}
        <div className="backend-error-tooltip-footer">Checking backend health automatically...</div>
      </div>
    </div>
  );
};

export default BackendErrorIndicator;
