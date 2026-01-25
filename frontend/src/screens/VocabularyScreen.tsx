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

const getVocabularyLabels = (language: Language) => {
  const labels: Record<
    Language,
    {
      title: string;
      title_en: string;
      languageLabel: string;
      languageLabel_en: string;
      levelLabel: string;
      levelLabel_en: string;
    }
  > = {
    spanish: {
      title: 'Lecciones de vocabulario',
      title_en: 'Vocabulary Lessons',
      languageLabel: 'Idioma',
      languageLabel_en: 'Language',
      levelLabel: 'Nivel',
      levelLabel_en: 'Level',
    },
    italian: {
      title: 'Lezioni di vocabolario',
      title_en: 'Vocabulary Lessons',
      languageLabel: 'Lingua',
      languageLabel_en: 'Language',
      levelLabel: 'Livello',
      levelLabel_en: 'Level',
    },
    german: {
      title: 'Wortschatzlektionen',
      title_en: 'Vocabulary Lessons',
      languageLabel: 'Sprache',
      languageLabel_en: 'Language',
      levelLabel: 'Niveau',
      levelLabel_en: 'Level',
    },
    french: {
      title: 'Leçons de vocabulaire',
      title_en: 'Vocabulary Lessons',
      languageLabel: 'Langue',
      languageLabel_en: 'Language',
      levelLabel: 'Niveau',
      levelLabel_en: 'Level',
    },
    dutch: {
      title: 'Woordenschatlessen',
      title_en: 'Vocabulary Lessons',
      languageLabel: 'Taal',
      languageLabel_en: 'Language',
      levelLabel: 'Niveau',
      levelLabel_en: 'Level',
    },
    english: {
      title: 'Vocabulary Lessons',
      title_en: 'Vocabulary Lessons',
      languageLabel: 'Language',
      languageLabel_en: 'Language',
      levelLabel: 'Level',
      levelLabel_en: 'Level',
    },
  };
  return labels[language];
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
  const labels = getVocabularyLabels(language);

  const handleLessonSelect = async (lesson: VocabularyLesson) => {
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
        <h1 className="vocabulary-title">
          {labels.title}
          {labels.title_en !== labels.title && (
            <span className="lesson-help" data-tooltip={labels.title_en} aria-label="English title">
              ?
            </span>
          )}
        </h1>

        {/* Display current language and level (read-only) */}
        <div className="vocabulary-selection-info">
          <div className="selection-badge">
            <span className="selection-label">
              {labels.languageLabel}
              {labels.languageLabel_en !== labels.languageLabel && (
                <span
                  className="lesson-help"
                  data-tooltip={labels.languageLabel_en}
                  aria-label="English label"
                >
                  ?
                </span>
              )}
              :
            </span>
            <span className="selection-value">{getLanguageDisplayName(language)}</span>
          </div>
          <div className="selection-badge">
            <span className="selection-label">
              {labels.levelLabel}
              {labels.levelLabel_en !== labels.levelLabel && (
                <span
                  className="lesson-help"
                  data-tooltip={labels.levelLabel_en}
                  aria-label="English label"
                >
                  ?
                </span>
              )}
              :
            </span>
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
