import React, { useState, useEffect } from 'react';
import type { VocabularyLessonDetail, VocabularyProgressCreate } from '../../types';
import VocabularyCard from './VocabularyCard';
import { vocabularyService } from '../../services/vocabularyService';
import { getUIStrings } from '../../utils/uiTranslations';
import './LessonPlayer.css';

interface LessonPlayerProps {
  lesson: VocabularyLessonDetail;
  onLessonComplete: () => void;
  onExit: () => void;
}

/**
 * LessonPlayer Component
 *
 * Main lesson interface for studying vocabulary:
 * - Display lesson items one at a time
 * - Flashcard-style interface with VocabularyCard
 * - Track progress through lesson
 * - Save progress after each item
 * - Handle lesson completion
 * - Show lesson metadata (title, description)
 */
const LessonPlayer: React.FC<LessonPlayerProps> = ({ lesson, onLessonComplete, onExit }) => {
  const [currentItemIndex, setCurrentItemIndex] = useState(0);
  const [isSavingProgress, setIsSavingProgress] = useState(false);
  const [saveError, setSaveError] = useState<string | null>(null);
  const [completedItemsSet, setCompletedItemsSet] = useState<Set<number>>(new Set());
  const uiStrings = getUIStrings(lesson.language);

  const currentItem = lesson.items[currentItemIndex];
  const totalItems = lesson.items.length;
  const completedItems = completedItemsSet.size;
  const completionPercentage = (completedItems / totalItems) * 100;

  // Auto-save progress when current item changes
  useEffect(() => {
    const saveProgress = async () => {
      if (!currentItem || totalItems === 0) return;

      setIsSavingProgress(true);
      setSaveError(null);

      try {
        const progressUpdate: VocabularyProgressCreate = {
          lesson_id: lesson.id,
          language: lesson.language,
          status: completedItems >= totalItems ? 'completed' : 'in_progress',
          completion_percentage: completionPercentage,
          mastery_score: completionPercentage / 100, // Simple scoring
        };

        await vocabularyService.saveProgress(progressUpdate);
        console.log('[LessonPlayer] Progress saved:', progressUpdate);
      } catch (error) {
        console.error('[LessonPlayer] Failed to save progress:', error);
        setSaveError(error instanceof Error ? error.message : 'Failed to save progress');
      } finally {
        setIsSavingProgress(false);
      }
    };

    const debounceTimer = setTimeout(saveProgress, 500);
    return () => clearTimeout(debounceTimer);
  }, [currentItemIndex, completedItems, lesson, currentItem, totalItems, completionPercentage]);

  // Mark item as completed when card is flipped
  const handleCardFlipped = () => {
    setCompletedItemsSet(prev => {
      const newSet = new Set(prev);
      newSet.add(currentItemIndex);
      return newSet;
    });
  };

  const handleNext = () => {
    if (currentItemIndex < totalItems - 1) {
      setCurrentItemIndex(currentItemIndex + 1);
    } else if (currentItemIndex === totalItems - 1 && completedItems >= totalItems) {
      // Lesson complete - only when all items are completed
      onLessonComplete();
    }
  };

  const handlePrevious = () => {
    if (currentItemIndex > 0) {
      setCurrentItemIndex(currentItemIndex - 1);
    }
  };

  const canGoNext = currentItemIndex < totalItems - 1 || completedItems >= totalItems;
  const canGoPrevious = currentItemIndex > 0;

  return (
    <div className="lesson-player">
      <div className="lesson-player-header">
        <button className="exit-button" onClick={onExit} aria-label={`${uiStrings.exit} lesson`}>
          ← {uiStrings.exit}
        </button>

        <div className="lesson-info">
          <h1 className="lesson-title">
            {lesson.title}
            {lesson.title_en && (
              <span
                className="lesson-help"
                data-tooltip={lesson.title_en}
                aria-label="English title"
              >
                ?
              </span>
            )}
          </h1>
          {lesson.oneliner && (
            <p className="lesson-subtitle">
              {lesson.oneliner}
              {lesson.oneliner_en && (
                <span
                  className="lesson-help"
                  data-tooltip={lesson.oneliner_en}
                  aria-label="English oneliner"
                >
                  ?
                </span>
              )}
            </p>
          )}
        </div>

        <div className="lesson-progress-indicator">
          <div className="progress-bar">
            <div className="progress-bar-fill" style={{ width: `${completionPercentage}%` }} />
          </div>
          <span className="progress-text">
            {completedItems} / {totalItems} {uiStrings.completed}
          </span>
        </div>
      </div>

      {saveError && <div className="save-error">{saveError}</div>}

      {isSavingProgress && <div className="saving-indicator">Saving progress...</div>}

      {currentItem && (
        <VocabularyCard
          item={currentItem}
          language={lesson.language}
          onNext={handleNext}
          onPrevious={handlePrevious}
          onCardFlipped={handleCardFlipped}
          isCompleted={completedItemsSet.has(currentItemIndex)}
          canGoNext={canGoNext}
          canGoPrevious={canGoPrevious}
          itemNumber={currentItemIndex + 1}
          totalItems={totalItems}
        />
      )}

      {completedItems >= totalItems && (
        <div className="lesson-complete">
          <div className="complete-message">
            <h2>🎉 {uiStrings.lessonComplete}</h2>
            <p>{uiStrings.lessonCompleteMessage.replace('{count}', totalItems.toString())}</p>
            <button className="continue-button" onClick={onExit}>
              {uiStrings.continue}
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default LessonPlayer;
