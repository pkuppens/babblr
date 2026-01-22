import React, { useState, useEffect } from 'react';
import type { VocabularyLesson, VocabularyProgress, DifficultyLevel } from '../../types';
import LessonCard from './LessonCard';
import { vocabularyService } from '../../services/vocabularyService';
import './LessonList.css';

interface LessonListProps {
  language: string;
  selectedLevel?: DifficultyLevel;
  onLessonSelect: (lesson: VocabularyLesson) => void;
}

/**
 * LessonList Component
 *
 * Displays a filtered list of vocabulary lessons with:
 * - Display lessons grouped by category (if available)
 * - Show progress indicator per lesson
 * - Filter by CEFR level
 * - Loading and error states
 * - Empty state when no lessons available
 */
const LessonList: React.FC<LessonListProps> = ({ language, selectedLevel, onLessonSelect }) => {
  const [lessons, setLessons] = useState<VocabularyLesson[]>([]);
  const [progressMap, setProgressMap] = useState<Record<number, VocabularyProgress>>({});
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Fetch lessons on mount or when language/level changes
  useEffect(() => {
    const fetchLessons = async () => {
      setLoading(true);
      setError(null);

      try {
        const levelFilter = selectedLevel?.toUpperCase();
        const data = await vocabularyService.getLessons(language, levelFilter);
        setLessons(data);

        // Fetch progress for each lesson
        const progress: Record<number, VocabularyProgress> = {};
        for (const lesson of data) {
          try {
            const lessonProgress = await vocabularyService.getProgress(lesson.id);
            progress[lesson.id] = lessonProgress;
          } catch {
            // Progress might not exist yet, continue
          }
        }
        setProgressMap(progress);
      } catch (err) {
        const message = err instanceof Error ? err.message : 'Failed to load lessons';
        setError(message);
        console.error('[LessonList] Error fetching lessons:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchLessons();
  }, [language, selectedLevel]);

  if (loading) {
    return (
      <div className="lesson-list">
        <div className="lesson-list-loading">Loading lessons...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="lesson-list">
        <div className="lesson-list-error">Error: {error}</div>
      </div>
    );
  }

  if (lessons.length === 0) {
    return (
      <div className="lesson-list">
        <div className="lesson-list-empty">
          No vocabulary lessons available for {language}
          {selectedLevel && ` at level ${selectedLevel}`}
        </div>
      </div>
    );
  }

  // Group lessons by subject/category if available
  const groupedLessons = lessons.reduce<Record<string, VocabularyLesson[]>>((acc, lesson) => {
    const category = lesson.subject || 'Other';
    if (!acc[category]) {
      acc[category] = [];
    }
    acc[category].push(lesson);
    return acc;
  }, {});

  return (
    <div className="lesson-list">
      {Object.entries(groupedLessons).map(([category, categoryLessons]) => (
        <div key={category} className="lesson-category">
          <h3 className="category-title">{category}</h3>
          <div className="lesson-cards-grid">
            {categoryLessons.map(lesson => (
              <LessonCard
                key={lesson.id}
                lesson={lesson}
                progress={progressMap[lesson.id]}
                onClick={() => onLessonSelect(lesson)}
              />
            ))}
          </div>
        </div>
      ))}
    </div>
  );
};

export default LessonList;
