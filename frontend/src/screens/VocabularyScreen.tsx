import React, { useState } from 'react';
import LessonList from '../components/vocabulary/LessonList';
import LessonPlayer from '../components/vocabulary/LessonPlayer';
import { vocabularyService } from '../services/vocabularyService';
import type { Language, DifficultyLevel } from '../types';
import type { VocabularyLessonDetail } from '../types';
import './Screen.css';
import './VocabularyScreen.css';

/**
 * Maps Language type to API language codes.
 */
const languageToCode = (language: Language): string => {
  const mapping: Record<Language, string> = {
    spanish: 'es',
    italian: 'it',
    german: 'de',
    french: 'fr',
    dutch: 'nl',
    english: 'en',
  };
  return mapping[language];
};

/**
 * Gets display name for language.
 */
const getLanguageDisplayName = (language: Language): string => {
  const mapping: Record<Language, string> = {
    spanish: 'Spanish',
    italian: 'Italian',
    german: 'German',
    french: 'French',
    dutch: 'Dutch',
    english: 'English',
  };
  return mapping[language];
};

interface VocabularyScreenProps {
  selectedLanguage: Language;
  selectedDifficulty: DifficultyLevel;
}

/**
 * VocabularyScreen displays vocabulary lessons with flashcard-based practice.
 *
 * Features:
 * - Lists vocabulary lessons filtered by language/level from Home screen selection
 * - Shows progress indicators (not started, in progress, completed)
 * - Interactive flashcard interface with audio pronunciation
 * - Progress tracking with mastery scores
 * - Completion celebration screen
 */
const VocabularyScreen: React.FC<VocabularyScreenProps> = ({
  selectedLanguage,
  selectedDifficulty,
}) => {
  const [selectedLesson, setSelectedLesson] = useState<VocabularyLessonDetail | null>(null);

  const language: Language = selectedLanguage;
  const difficulty: DifficultyLevel = selectedDifficulty;
  const languageCode = languageToCode(language);

  const handleLessonSelect = async (lesson: any) => {
    try {
      // Fetch the full lesson detail (with items)
      const lessonDetail = await vocabularyService.getLesson(lesson.id);
      setSelectedLesson(lessonDetail);
    } catch (error) {
      console.error('Error loading lesson:', error);
    }
  };

  const handleLessonComplete = () => {
    // Return to lesson list after completion
    setSelectedLesson(null);
  };

  const handleExit = () => {
    // Return to lesson list when exiting player
    setSelectedLesson(null);
  };

  if (selectedLesson) {
    return (
      <div className="screen-container">
        <LessonPlayer
          lesson={selectedLesson}
          onLessonComplete={handleLessonComplete}
          onExit={handleExit}
        />
      </div>
    );
  }

  return (
    <div className="screen-container">
      <div className="vocabulary-screen">
        <h1>Vocabulary Lessons</h1>

        {/* Display current language and level (read-only) */}
        <div className="vocabulary-selection-info">
          <div className="selection-badge">
            <span className="selection-label">Language:</span>
            <span className="selection-value">{getLanguageDisplayName(language)}</span>
          </div>
          <div className="selection-badge">
            <span className="selection-label">Level:</span>
            <span className="selection-value">{difficulty}</span>
          </div>
        </div>

        {/* Lessons List */}
        <LessonList language={languageCode} onLessonSelect={handleLessonSelect} />
      </div>
    </div>
  );
};

export default VocabularyScreen;
