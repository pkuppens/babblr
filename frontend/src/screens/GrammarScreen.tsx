import React, { useState, useEffect } from 'react';
import { grammarService, type GrammarLesson, type GrammarLessonDetail } from '../services/api';
import { Play, CheckCircle, Clock, AlertCircle } from 'lucide-react';
import type { Language, DifficultyLevel } from '../types';
import './Screen.css';
import './GrammarScreen.css';

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

interface GrammarScreenProps {
  selectedLanguage: Language;
  selectedDifficulty: DifficultyLevel;
}

/**
 * GrammarScreen displays grammar lessons with explanations, examples, exercises, and progress tracking.
 *
 * Features:
 * - Lists grammar lessons filtered by language/level from Home screen selection
 * - Shows progress indicators (not started, in progress, completed)
 * - Highlights recap lessons due for review
 * - Displays lesson content with audio playback
 * - Interactive exercises with immediate feedback
 * - Adaptive progress tracking with mastery scores
 */
const GrammarScreen: React.FC<GrammarScreenProps> = ({ selectedLanguage, selectedDifficulty }) => {
  const [lessons, setLessons] = useState<GrammarLesson[]>([]);
  const [recaps, setRecaps] = useState<GrammarLesson[]>([]);
  const [selectedLesson, setSelectedLesson] = useState<GrammarLessonDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [lessonType, setLessonType] = useState<'new' | 'practice' | 'test' | 'recap' | undefined>(
    undefined
  );
  const [exerciseAnswers, setExerciseAnswers] = useState<Record<number, number | string>>({});
  const [exerciseFeedback, setExerciseFeedback] = useState<
    Record<number, { correct: boolean; explanation?: string }>
  >({});
  const [playingAudio, setPlayingAudio] = useState<string | null>(null);

  // Use the selected language and difficulty (always provided from App state)
  const language: Language = selectedLanguage;
  const difficulty: DifficultyLevel = selectedDifficulty;

  // Convert Language type to API language code
  const languageCode = languageToCode(language);
  const level = difficulty;

  // Load lessons on mount and when filters change
  useEffect(() => {
    loadLessons();
    loadRecaps();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [language, difficulty, lessonType]);

  const loadLessons = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await grammarService.listLessons(languageCode, level, lessonType);
      setLessons(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load grammar lessons');
      console.error('Error loading grammar lessons:', err);
    } finally {
      setLoading(false);
    }
  };

  const loadRecaps = async () => {
    try {
      const data = await grammarService.getRecaps(languageCode, level);
      setRecaps(data);
    } catch (err) {
      console.error('Error loading recaps:', err);
    }
  };

  const handleLessonClick = async (lessonId: number) => {
    try {
      setError(null);
      const lessonDetail = await grammarService.getLesson(lessonId);
      setSelectedLesson(lessonDetail);
      setExerciseAnswers({});
      setExerciseFeedback({});
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load lesson');
      console.error('Error loading lesson:', err);
    }
  };

  const handleBackToList = () => {
    setSelectedLesson(null);
    setExerciseAnswers({});
    setExerciseFeedback({});
  };

  const handlePlayAudio = async (audioUrl: string) => {
    if (playingAudio === audioUrl) {
      setPlayingAudio(null);
      return;
    }

    setPlayingAudio(audioUrl);
    try {
      const audio = new Audio(audioUrl);
      audio.onended = () => setPlayingAudio(null);
      audio.onerror = () => {
        setPlayingAudio(null);
        console.error('Error playing audio');
      };
      await audio.play();
    } catch (err) {
      setPlayingAudio(null);
      console.error('Error playing audio:', err);
    }
  };

  const handleExerciseAnswer = (exerciseIndex: number, answer: number | string) => {
    setExerciseAnswers(prev => ({ ...prev, [exerciseIndex]: answer }));
    // Clear previous feedback for this exercise
    setExerciseFeedback(prev => {
      const newFeedback = { ...prev };
      delete newFeedback[exerciseIndex];
      return newFeedback;
    });
  };

  const handleSubmitExercise = async (
    exerciseIndex: number,
    exercise: GrammarLessonDetail['exercises'][number]
  ) => {
    const userAnswer = exerciseAnswers[exerciseIndex];
    if (userAnswer === undefined) return;

    const isCorrect =
      exercise.type === 'multiple_choice'
        ? userAnswer === exercise.correct
        : String(userAnswer).toLowerCase().trim() === String(exercise.correct).toLowerCase().trim();

    setExerciseFeedback(prev => ({
      ...prev,
      [exerciseIndex]: {
        correct: isCorrect,
        explanation:
          typeof exercise.explanation === 'string'
            ? exercise.explanation
            : isCorrect
              ? undefined
              : `Correct answer: ${exercise.correct}`,
      },
    }));

    // Update progress based on exercise performance
    if (selectedLesson) {
      try {
        const totalExercises = selectedLesson.exercises.length;
        const completedExercises = Object.keys(exerciseAnswers).length + 1;
        const correctExercises =
          Object.values(exerciseFeedback).filter(f => f.correct).length + (isCorrect ? 1 : 0);

        const completionPercentage = (completedExercises / totalExercises) * 100;
        const masteryScore = totalExercises > 0 ? correctExercises / totalExercises : 0.5;

        await grammarService.updateProgress({
          lesson_id: selectedLesson.id,
          language: languageCode,
          status: completionPercentage >= 100 ? 'completed' : 'in_progress',
          completion_percentage: completionPercentage,
          mastery_score: masteryScore,
        });

        // Reload recaps in case this lesson is now due for review
        await loadRecaps();
      } catch (err) {
        console.error('Error updating progress:', err);
      }
    }
  };

  const isRecapDue = (lessonId: number): boolean => {
    return recaps?.some(recap => recap.id === lessonId) ?? false;
  };

  if (selectedLesson) {
    return (
      <div className="screen-container">
        <div className="grammar-lesson-view">
          <button className="back-button" onClick={handleBackToList}>
            ← Back to Lessons
          </button>

          <h1>{selectedLesson.title}</h1>
          {selectedLesson.description && (
            <p className="lesson-description">{selectedLesson.description}</p>
          )}

          {/* Grammar Rules */}
          {selectedLesson.rules && selectedLesson.rules.length > 0 && (
            <section className="grammar-rules">
              <h2>Grammar Rules</h2>
              {selectedLesson.rules.map((rule, idx) => (
                <div key={rule.id || idx} className="grammar-rule">
                  <h3>{rule.title}</h3>
                  <p>{rule.description}</p>
                  {rule.examples && rule.examples.length > 0 && (
                    <ul className="rule-examples">
                      {rule.examples.map((example, exIdx) => (
                        <li key={exIdx}>
                          {example.es && <strong>{example.es}</strong>}
                          {example.en && <span> - {example.en}</span>}
                        </li>
                      ))}
                    </ul>
                  )}
                </div>
              ))}
            </section>
          )}

          {/* Examples with Audio */}
          {selectedLesson.examples && selectedLesson.examples.length > 0 && (
            <section className="lesson-examples">
              <h2>Examples</h2>
              {selectedLesson.examples.map((example, idx) => (
                <div key={idx} className="example-item">
                  <p className="example-text">{example.text}</p>
                  {example.translation && (
                    <p className="example-translation">{example.translation}</p>
                  )}
                  {example.audio_url && (
                    <button
                      className="audio-button"
                      onClick={() => handlePlayAudio(example.audio_url!)}
                      aria-label="Play audio"
                    >
                      <Play size={16} />
                      {playingAudio === example.audio_url ? 'Playing...' : 'Play'}
                    </button>
                  )}
                </div>
              ))}
            </section>
          )}

          {/* Exercises */}
          {selectedLesson.exercises && selectedLesson.exercises.length > 0 && (
            <section className="lesson-exercises">
              <h2>Practice Exercises</h2>
              {selectedLesson.exercises.map((exercise, idx) => {
                const feedback = exerciseFeedback[idx];
                const userAnswer = exerciseAnswers[idx];

                return (
                  <div key={idx} className="exercise-item">
                    <p className="exercise-question">
                      {exercise.question || 'Complete the exercise'}
                    </p>

                    {exercise.type === 'multiple_choice' && exercise.options && (
                      <div className="exercise-options">
                        {exercise.options.map((option, optIdx) => (
                          <button
                            key={optIdx}
                            className={`option-button ${userAnswer === optIdx ? 'selected' : ''}`}
                            onClick={() => handleExerciseAnswer(idx, optIdx)}
                            disabled={feedback !== undefined}
                          >
                            {option}
                          </button>
                        ))}
                      </div>
                    )}

                    {exercise.type === 'fill_blank' && (
                      <input
                        type="text"
                        className="exercise-input"
                        value={userAnswer || ''}
                        onChange={e => handleExerciseAnswer(idx, e.target.value)}
                        disabled={feedback !== undefined}
                        placeholder="Enter your answer"
                      />
                    )}

                    {feedback && (
                      <div
                        className={`exercise-feedback ${feedback.correct ? 'correct' : 'incorrect'}`}
                      >
                        {feedback.correct ? (
                          <>
                            <CheckCircle size={16} />
                            <span>Correct!</span>
                          </>
                        ) : (
                          <>
                            <AlertCircle size={16} />
                            <span>Incorrect. {feedback.explanation}</span>
                          </>
                        )}
                      </div>
                    )}

                    {!feedback && userAnswer !== undefined && (
                      <button
                        className="submit-button"
                        onClick={() => handleSubmitExercise(idx, exercise)}
                      >
                        Check Answer
                      </button>
                    )}
                  </div>
                );
              })}
            </section>
          )}
        </div>
      </div>
    );
  }

  return (
    <div className="screen-container">
      <div className="grammar-screen">
        <h1>Grammar Lessons</h1>

        {/* Display current language and level (read-only) */}
        <div className="grammar-selection-info">
          <div className="selection-badge">
            <span className="selection-label">Language:</span>
            <span className="selection-value">{getLanguageDisplayName(language)}</span>
          </div>
          <div className="selection-badge">
            <span className="selection-label">Level:</span>
            <span className="selection-value">{difficulty}</span>
          </div>
        </div>

        {/* Filters */}
        <div className="grammar-filters">
          <select
            value={lessonType || ''}
            onChange={e =>
              setLessonType(
                (e.target.value as 'new' | 'practice' | 'test' | 'recap' | '') || undefined
              )
            }
            className="filter-select"
          >
            <option value="">All Types</option>
            <option value="new">New Lessons</option>
            <option value="practice">Practice</option>
            <option value="test">Tests</option>
            <option value="recap">Recaps</option>
          </select>
        </div>

        {error && (
          <div className="error-message">
            <AlertCircle size={16} />
            <span>{error}</span>
          </div>
        )}

        {loading ? (
          <div className="loading-message">
            <Clock size={16} />
            <span>Loading lessons...</span>
          </div>
        ) : (
          <div className="lessons-list">
            {lessons.length === 0 ? (
              <p className="empty-message">No grammar lessons found.</p>
            ) : (
              lessons.map(lesson => {
                const isRecap = isRecapDue(lesson.id);
                return (
                  <div
                    key={lesson.id}
                    className={`lesson-card ${isRecap ? 'recap-due' : ''}`}
                    onClick={() => handleLessonClick(lesson.id)}
                  >
                    <div className="lesson-header">
                      <h3>{lesson.title}</h3>
                      {isRecap && (
                        <span className="recap-badge" title="Due for review">
                          Review Due
                        </span>
                      )}
                    </div>
                    {lesson.description && (
                      <p className="lesson-description-preview">{lesson.description}</p>
                    )}
                    <div className="lesson-meta">
                      <span className="level-badge">{lesson.difficulty_level}</span>
                    </div>
                  </div>
                );
              })
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default GrammarScreen;
