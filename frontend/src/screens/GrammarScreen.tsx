import React from 'react';
import './Screen.css';

/**
 * GrammarScreen displays grammar lessons and exercises.
 *
 * This is a placeholder for future grammar lesson functionality.
 * Will be implemented in issue #64.
 */
const GrammarScreen: React.FC = () => {
  return (
    <div className="screen-container">
      <div className="placeholder-screen">
        <h2>Grammar Lessons</h2>
        <p>Grammar lessons and exercises will be available here soon.</p>
        <p className="placeholder-note">This feature is planned for issue #64.</p>
      </div>
    </div>
  );
};

export default GrammarScreen;
