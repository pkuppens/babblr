import React, { useState } from 'react';
import type { Language, DifficultyLevel } from '../types';
import './LanguageSelector.css';

interface LanguageSelectorProps {
  onStart: (language: Language, difficulty: DifficultyLevel) => void;
}

const LANGUAGES: { value: Language; label: string; flag: string }[] = [
  { value: 'spanish', label: 'Spanish', flag: '🇪🇸' },
  { value: 'italian', label: 'Italian', flag: '🇮🇹' },
  { value: 'german', label: 'German', flag: '🇩🇪' },
  { value: 'french', label: 'French', flag: '🇫🇷' },
  { value: 'dutch', label: 'Dutch', flag: '🇳🇱' },
];

const DIFFICULTIES: { value: DifficultyLevel; label: string; description: string }[] = [
  { value: 'beginner', label: 'Beginner', description: 'Just starting out' },
  { value: 'intermediate', label: 'Intermediate', description: 'Building fluency' },
  { value: 'advanced', label: 'Advanced', description: 'Refining skills' },
];

const LanguageSelector: React.FC<LanguageSelectorProps> = ({ onStart }) => {
  const [selectedLanguage, setSelectedLanguage] = useState<Language>('spanish');
  const [selectedDifficulty, setSelectedDifficulty] = useState<DifficultyLevel>('beginner');

  const handleStart = () => {
    onStart(selectedLanguage, selectedDifficulty);
  };

  return (
    <div className="language-selector">
      <h2>Start a New Conversation</h2>
      
      <div className="selector-section">
        <h3>Choose Your Language</h3>
        <div className="language-grid">
          {LANGUAGES.map((lang) => (
            <button
              key={lang.value}
              className={`language-card ${selectedLanguage === lang.value ? 'selected' : ''}`}
              onClick={() => setSelectedLanguage(lang.value)}
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
          {DIFFICULTIES.map((diff) => (
            <button
              key={diff.value}
              className={`difficulty-card ${selectedDifficulty === diff.value ? 'selected' : ''}`}
              onClick={() => setSelectedDifficulty(diff.value)}
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
