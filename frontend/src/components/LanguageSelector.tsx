import React from 'react';
import type { Language, DifficultyLevel } from '../types';
import './LanguageSelector.css';

interface LanguageSelectorProps {
  selectedLanguage: Language;
  selectedDifficulty: DifficultyLevel;
  onSelectionChange: (language: Language, difficulty: DifficultyLevel) => void;
  onStart: (language: Language, difficulty: DifficultyLevel) => void;
}

const LANGUAGES: { value: Language; label: string; flag: string }[] = [
  { value: 'spanish', label: 'Spanish', flag: '🇪🇸' },
  { value: 'italian', label: 'Italian', flag: '🇮🇹' },
  { value: 'german', label: 'German', flag: '🇩🇪' },
  { value: 'french', label: 'French', flag: '🇫🇷' },
  { value: 'dutch', label: 'Dutch', flag: '🇳🇱' },
  { value: 'english', label: 'English', flag: '🇬🇧' },
];

const DIFFICULTIES: { value: DifficultyLevel; label: string; description: string }[] = [
  { value: 'A1', label: 'A1', description: 'Beginner: simple phrases and basic needs' },
  { value: 'A2', label: 'A2', description: 'Elementary: everyday topics and routines' },
  { value: 'B1', label: 'B1', description: 'Intermediate: handle common situations and plans' },
  {
    value: 'B2',
    label: 'B2',
    description: 'Upper-intermediate: discuss abstract topics with detail',
  },
  { value: 'C1', label: 'C1', description: 'Advanced: fluent, flexible, and nuanced language' },
  { value: 'C2', label: 'C2', description: 'Proficient: near-native comprehension and expression' },
];

const LanguageSelector: React.FC<LanguageSelectorProps> = ({
  selectedLanguage,
  selectedDifficulty,
  onSelectionChange,
  onStart,
}) => {
  const handleLanguageChange = (language: Language) => {
    onSelectionChange(language, selectedDifficulty);
  };

  const handleDifficultyChange = (difficulty: DifficultyLevel) => {
    onSelectionChange(selectedLanguage, difficulty);
  };

  const handleStart = () => {
    onStart(selectedLanguage, selectedDifficulty);
  };

  return (
    <div className="language-selector">
      <h2>Start a New Conversation</h2>

      <div className="selector-section">
        <h3>Choose Your Language</h3>
        <div className="language-grid">
          {LANGUAGES.map(lang => (
            <button
              key={lang.value}
              className={`language-card ${selectedLanguage === lang.value ? 'selected' : ''}`}
              onClick={() => handleLanguageChange(lang.value)}
            >
              <span className="flag">{lang.flag}</span>
              <span className="label">{lang.label}</span>
            </button>
          ))}
        </div>
      </div>

      <div className="selector-section">
        <h3>Choose Your Level</h3>
        <div className="difficulty-grid">
          {DIFFICULTIES.map(diff => (
            <button
              key={diff.value}
              className={`difficulty-card ${selectedDifficulty === diff.value ? 'selected' : ''}`}
              onClick={() => handleDifficultyChange(diff.value)}
            >
              <span className="label">{diff.label}</span>
              <span className="description">{diff.description}</span>
            </button>
          ))}
        </div>
      </div>

      <button className="start-button" onClick={handleStart}>
        Start Learning
      </button>
    </div>
  );
};

export default LanguageSelector;
