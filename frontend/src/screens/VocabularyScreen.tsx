import React from 'react';
import './Screen.css';

/**
 * VocabularyScreen displays vocabulary lessons and practice.
 *
 * This is a placeholder for future vocabulary lesson functionality.
 * Will be implemented in issue #62.
 */
const VocabularyScreen: React.FC = () => {
  return (
    <div className="screen-container">
      <div className="placeholder-screen">
        <h2>Vocabulary Lessons</h2>
        <p>Vocabulary lessons and practice will be available here soon.</p>
        <p className="placeholder-note">This feature is planned for issue #62.</p>
      </div>
    </div>
  );
};

export default VocabularyScreen;
