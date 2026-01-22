import React, { useState, useEffect } from 'react';
import type { VocabularyItem } from '../../types';
import { ttsService } from '../../services/api';
import { getUIStrings } from '../../utils/uiTranslations';
import './VocabularyCard.css';

interface VocabularyCardProps {
  item: VocabularyItem;
  language: string;
  onNext: () => void;
  onPrevious: () => void;
  onCardFlipped: () => void;
  isCompleted: boolean;
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
  onCardFlipped,
  isCompleted,
  canGoNext,
  canGoPrevious,
  itemNumber,
  totalItems,
}) => {
  const [isFlipped, setIsFlipped] = useState(false);
  const [isPlayingAudio, setIsPlayingAudio] = useState(false);
  const [audioError, setAudioError] = useState<string | null>(null);
  const uiStrings = getUIStrings(language);

  // Reset to covered (front) state when navigating to a different item
  useEffect(() => {
    setIsFlipped(false);
  }, [item.id]);

  const handleFlipCard = () => {
    const newFlippedState = !isFlipped;
    setIsFlipped(newFlippedState);
    
    // Mark as completed when flipping to show translation (front to back)
    if (newFlippedState && !isCompleted) {
      onCardFlipped();
    }
  };

  const handleNext = () => {
    // Reset flip state immediately to prevent flash of next card's solution
    setIsFlipped(false);
    
    // Mark card as completed when clicking Next
    if (!isCompleted) {
      onCardFlipped();
    }
    
    // Small delay to ensure flip animation starts before item changes
    setTimeout(() => {
      onNext();
    }, 50);
  };

  const handlePrevious = () => {
    // Reset flip state immediately to prevent flash of previous card's solution
    setIsFlipped(false);
    
    // Small delay to ensure flip animation starts before item changes
    setTimeout(() => {
      onPrevious();
    }, 50);
  };

  const handlePlayAudio = async () => {
    if (isPlayingAudio) return;

    setIsPlayingAudio(true);
    setAudioError(null);

    try {
      // Use 90% speed for vocabulary exercises (short words/sentences)
      const audioBlob = await ttsService.synthesize(item.word, language, 0.9);
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
          {itemNumber} {uiStrings.of} {totalItems}
        </h2>
      </div>

      {/* Flashcard */}
      <div
        className={`vocabulary-flashcard ${isFlipped ? 'flipped' : ''}`}
        onClick={handleFlipCard}
      >
        <div className="flashcard-front">
          <div className="card-word-container">
            <div className="card-word">{item.word}</div>
            {item.example && (
              <div
                className="example-hint"
                data-tooltip={`${uiStrings.example}: ${item.example}`}
                onClick={e => e.stopPropagation()}
              >
                ?
              </div>
            )}
          </div>
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
          <p className="card-hint">{uiStrings.clickToReveal}</p>
        </div>

        <div className="flashcard-back">
          <div className="card-translation">{item.translation}</div>
          <p className="card-example">
            <strong>{uiStrings.example}:</strong> {item.example}
          </p>
          <p className="card-hint">{uiStrings.clickToShowWord}</p>
        </div>
      </div>

      {audioError && <div className="audio-error">{audioError}</div>}

      {/* Navigation Controls */}
      <div className="vocabulary-card-navigation">
        <button
          className="nav-button prev-button"
          onClick={handlePrevious}
          disabled={!canGoPrevious}
          aria-label={`${uiStrings.previous} word`}
        >
          ← {uiStrings.previous}
        </button>

        <div className="progress-indicator">
          {itemNumber} / {totalItems}
        </div>

        <button
          className="nav-button next-button"
          onClick={handleNext}
          disabled={!canGoNext}
          aria-label={`${uiStrings.next} word`}
        >
          {uiStrings.next} →
        </button>
      </div>
    </div>
  );
};

export default VocabularyCard;
