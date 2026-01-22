import React, { useState, useEffect } from 'react';
import type { VocabularyLessonDetail, VocabularyProgressCreate } from '../../types';
import VocabularyCard from './VocabularyCard';
import { vocabularyService } from '../../services/vocabularyService';
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
  const [completedItems, setCompletedItems] = useState(0);

  const currentItem = lesson.items[currentItemIndex];
  const totalItems = lesson.items.length;
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
  }, [currentItemIndex, completedItems, lesson]);

  const handleNext = () => {
    if (currentItemIndex < totalItems - 1) {
      setCurrentItemIndex(currentItemIndex + 1);
      setCompletedItems(Math.max(completedItems, currentItemIndex + 2));
    } else if (currentItemIndex === totalItems - 1) {
      // Lesson complete
      setCompletedItems(totalItems);
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
        <button className="exit-button" onClick={onExit} aria-label="Exit lesson">
          ← Exit
        </button>

        <div className="lesson-info">
          <h1 className="lesson-title">{lesson.title}</h1>
          {lesson.oneliner && <p className="lesson-subtitle">{lesson.oneliner}</p>}
        </div>

        <div className="lesson-progress-indicator">
          <div className="progress-bar">
            <div
              className="progress-bar-fill"
              style={{ width: `${completionPercentage}%` }}
            />
          </div>
          <span className="progress-text">
            {completedItems} / {totalItems} completed
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
          canGoNext={canGoNext}
          canGoPrevious={canGoPrevious}
          itemNumber={currentItemIndex + 1}
          totalItems={totalItems}
        />
      )}

      {completedItems >= totalItems && (
        <div className="lesson-complete">
          <div className="complete-message">
            <h2>🎉 Lesson Complete!</h2>
            <p>You've completed all {totalItems} vocabulary items.</p>
            <button className="continue-button" onClick={onExit}>
              Continue
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default LessonPlayer;
