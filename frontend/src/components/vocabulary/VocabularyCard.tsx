import React, { useState } from 'react';
import type { VocabularyItem } from '../../types';
import { ttsService } from '../../services/api';
import './VocabularyCard.css';

interface VocabularyCardProps {
  item: VocabularyItem;
  language: string;
  onNext: () => void;
  onPrevious: () => void;
  canGoNext: boolean;
  canGoPrevious: boolean;
  itemNumber: number;
  totalItems: number;
}

/**
 * VocabularyCard Component
 *
 * Flashcard-style interface for learning vocabulary:
 * - Display word with optional pronunciation via TTS
 * - Show translation (hidden by default, revealed on click/flip)
 * - Display example sentence
 * - Audio playback button for word pronunciation
 * - Navigation controls
 */
const VocabularyCard: React.FC<VocabularyCardProps> = ({
  item,
  language,
  onNext,
  onPrevious,
  canGoNext,
  canGoPrevious,
  itemNumber,
  totalItems,
}) => {
  const [isFlipped, setIsFlipped] = useState(false);
  const [isPlayingAudio, setIsPlayingAudio] = useState(false);
  const [audioError, setAudioError] = useState<string | null>(null);

  const handlePlayAudio = async () => {
    if (isPlayingAudio) return;

    setIsPlayingAudio(true);
    setAudioError(null);

    try {
      const audioBlob = await ttsService.synthesize(item.word, language);
      const audioUrl = URL.createObjectURL(audioBlob);
      const audio = new Audio(audioUrl);

      audio.onended = () => {
        setIsPlayingAudio(false);
        URL.revokeObjectURL(audioUrl);
      };

      audio.onerror = () => {
        setAudioError('Failed to play audio');
        setIsPlayingAudio(false);
        URL.revokeObjectURL(audioUrl);
      };

      await audio.play();
    } catch (error) {
      setAudioError(error instanceof Error ? error.message : 'Audio playback failed');
      setIsPlayingAudio(false);
    }
  };

  return (
    <div className="vocabulary-card-container">
      <div className="vocabulary-card-header">
        <h2 className="vocabulary-card-title">
          {itemNumber} of {totalItems}
        </h2>
      </div>

      {/* Flashcard */}
      <div
        className={`vocabulary-flashcard ${isFlipped ? 'flipped' : ''}`}
        onClick={() => setIsFlipped(!isFlipped)}
      >
        <div className="flashcard-front">
          <div className="card-word">{item.word}</div>
          <button
            className={`audio-button ${isPlayingAudio ? 'playing' : ''}`}
            onClick={e => {
              e.stopPropagation();
              handlePlayAudio();
            }}
            disabled={isPlayingAudio}
            aria-label={`Pronounce: ${item.word}`}
          >
            🔊
          </button>
          <p className="card-hint">Click to reveal translation</p>
        </div>

        <div className="flashcard-back">
          <div className="card-translation">{item.translation}</div>
          <p className="card-example">
            <strong>Example:</strong> {item.example}
          </p>
          <p className="card-hint">Click to show word</p>
        </div>
      </div>

      {audioError && <div className="audio-error">{audioError}</div>}

      {/* Navigation Controls */}
      <div className="vocabulary-card-navigation">
        <button
          className="nav-button prev-button"
          onClick={onPrevious}
          disabled={!canGoPrevious}
          aria-label="Previous word"
        >
          ← Previous
        </button>

        <div className="progress-indicator">
          {itemNumber} / {totalItems}
        </div>

        <button
          className="nav-button next-button"
          onClick={onNext}
          disabled={!canGoNext}
          aria-label="Next word"
        >
          Next →
        </button>
      </div>
    </div>
  );
};

export default VocabularyCard;
