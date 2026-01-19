import React, { useState, useEffect } from 'react';
import {
  Clock,
  HelpCircle,
  AlertCircle,
  CheckCircle,
  ChevronLeft,
  ChevronRight,
  Award,
  Lightbulb,
  History,
  Trash2,
  RotateCcw,
  Eye,
  Check,
} from 'lucide-react';
import { assessmentService } from '../services/api';
import { formatDateAndTime } from '../utils/dateTime';
import type {
  Language,
  DifficultyLevel,
  Assessment,
  AssessmentDetail,
  AttemptResult,
  AttemptSummary,
} from '../types';
import './Screen.css';
import './AssessmentsScreen.css';

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

interface AssessmentsScreenProps {
  selectedLanguage: Language;
  selectedDifficulty: DifficultyLevel;
  onLevelApplied?: (language: Language, level: DifficultyLevel) => void;
  timezone?: string;
  timeFormat?: '24h' | '12h';
}

type ViewState = 'list' | 'quiz' | 'results' | 'review';

/**
 * AssessmentsScreen displays CEFR assessment tests.
 *
 * Features:
 * - Lists available assessments for selected language
 * - Interactive quiz with progress tracking
 * - Skill breakdown results with CEFR recommendations
 * - Attempt history
 * - Apply recommended level functionality
 */
const AssessmentsScreen: React.FC<AssessmentsScreenProps> = ({
  selectedLanguage,
  selectedDifficulty,
  onLevelApplied,
  timezone = 'UTC',
  timeFormat = '24h',
}) => {
  // View state
  const [viewState, setViewState] = useState<ViewState>('list');

  // List state
  const [assessments, setAssessments] = useState<Assessment[]>([]);
  const [attempts, setAttempts] = useState<AttemptSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Quiz state
  const [currentAssessment, setCurrentAssessment] = useState<AssessmentDetail | null>(null);
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [answers, setAnswers] = useState<Record<string, string>>({});
  const [submitting, setSubmitting] = useState(false);

  // Results state
  const [result, setResult] = useState<AttemptResult | null>(null);
  const [showConfirmDialog, setShowConfirmDialog] = useState(false);
  const [applyingLevel, setApplyingLevel] = useState(false);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  const languageCode = languageToCode(selectedLanguage);

  // Load assessments and attempts on mount and language change
  useEffect(() => {
    loadAssessments();
    loadAttempts();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [selectedLanguage]);

  const loadAssessments = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await assessmentService.listAssessments(languageCode);
      setAssessments(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load assessments');
      console.error('Error loading assessments:', err);
    } finally {
      setLoading(false);
    }
  };

  const loadAttempts = async () => {
    try {
      const data = await assessmentService.listAttempts(languageCode, 5);
      setAttempts(data);
    } catch (err) {
      console.error('Error loading attempts:', err);
    }
  };

  const handleStartAssessment = async (assessmentId: number) => {
    try {
      setError(null);
      const detail = await assessmentService.getAssessment(assessmentId);
      // Randomize question order
      const shuffledQuestions = [...detail.questions].sort(() => Math.random() - 0.5);
      setCurrentAssessment({
        ...detail,
        questions: shuffledQuestions,
      });
      setCurrentQuestionIndex(0);
      setAnswers({});
      setResult(null);
      setSuccessMessage(null);
      setViewState('quiz');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load assessment');
      console.error('Error loading assessment:', err);
    }
  };

  const handleSelectAnswer = (questionId: number, answer: string) => {
    setAnswers(prev => ({
      ...prev,
      [questionId.toString()]: answer,
    }));
  };

  const handleNextQuestion = () => {
    if (currentAssessment && currentQuestionIndex < currentAssessment.questions.length - 1) {
      setCurrentQuestionIndex(prev => prev + 1);
    }
  };

  const handlePrevQuestion = () => {
    if (currentQuestionIndex > 0) {
      setCurrentQuestionIndex(prev => prev - 1);
    }
  };

  const handleSubmitAssessment = async () => {
    if (!currentAssessment) return;

    try {
      setSubmitting(true);
      setError(null);
      const attemptResult = await assessmentService.submitAttempt(currentAssessment.id, answers);
      setResult(attemptResult);
      setViewState('results');
      loadAttempts(); // Refresh attempt history
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to submit assessment');
      console.error('Error submitting assessment:', err);
    } finally {
      setSubmitting(false);
    }
  };

  const handleApplyLevel = async () => {
    if (!result) return;

    try {
      setApplyingLevel(true);
      await assessmentService.updateUserLevel(languageCode, result.recommended_level, result.score);
      setSuccessMessage(
        `Your ${getLanguageDisplayName(selectedLanguage)} level has been updated to ${result.recommended_level}!`
      );
      setShowConfirmDialog(false);
      // Notify parent component to update difficulty level
      if (onLevelApplied) {
        onLevelApplied(selectedLanguage, result.recommended_level as DifficultyLevel);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to update level');
      console.error('Error updating level:', err);
    } finally {
      setApplyingLevel(false);
    }
  };

  const handleRetake = () => {
    if (currentAssessment) {
      // Randomize question order again
      const shuffledQuestions = [...currentAssessment.questions].sort(() => Math.random() - 0.5);
      setCurrentAssessment({
        ...currentAssessment,
        questions: shuffledQuestions,
      });
    }
    setResult(null);
    setCurrentQuestionIndex(0);
    setAnswers({});
    setViewState('quiz');
    setSuccessMessage(null);
  };

  const handleBackToList = () => {
    setViewState('list');
    setCurrentAssessment(null);
    setResult(null);
    setCurrentQuestionIndex(0);
    setAnswers({});
    setSuccessMessage(null);
  };

  const handleApplyLevelFromAttempt = async (attempt: AttemptSummary) => {
    try {
      setError(null);
      await assessmentService.updateUserLevel(
        languageCode,
        attempt.recommended_level,
        attempt.score
      );
      setSuccessMessage(
        `Your ${getLanguageDisplayName(selectedLanguage)} level has been updated to ${attempt.recommended_level}!`
      );
      // Notify parent component to update difficulty level
      if (onLevelApplied) {
        onLevelApplied(selectedLanguage, attempt.recommended_level as DifficultyLevel);
      }
      loadAttempts(); // Refresh attempt list
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to update level');
      console.error('Error updating level:', err);
    }
  };

  const handleDeleteAttempt = async (attemptId: number) => {
    if (!window.confirm('Delete this assessment attempt?')) return;

    try {
      setError(null);
      await assessmentService.deleteAttempt(attemptId);
      loadAttempts(); // Refresh attempt list
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to delete attempt');
      console.error('Error deleting attempt:', err);
    }
  };

  const handleRetakeFromAttempt = async (attempt: AttemptSummary) => {
    try {
      setError(null);
      const detail = await assessmentService.getAssessment(attempt.assessment_id);
      // Randomize question order
      const shuffledQuestions = [...detail.questions].sort(() => Math.random() - 0.5);
      setCurrentAssessment({
        ...detail,
        questions: shuffledQuestions,
      });
      setCurrentQuestionIndex(0);
      setAnswers({});
      setResult(null);
      setSuccessMessage(null);
      setViewState('quiz');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load assessment');
      console.error('Error loading assessment:', err);
    }
  };

  const handleReviewAttempt = async (attempt: AttemptSummary) => {
    try {
      setError(null);
      const attemptDetail = await assessmentService.getAttempt(attempt.id);
      // Convert AttemptResult to display format
      setResult({
        id: attemptDetail.id,
        assessment_id: attemptDetail.assessment_id,
        language: attemptDetail.language,
        score: attemptDetail.score,
        recommended_level: attemptDetail.recommended_level,
        skill_scores: attemptDetail.skill_scores,
        total_questions: attemptDetail.total_questions,
        correct_answers: attemptDetail.correct_answers,
        started_at: attemptDetail.started_at,
        completed_at: attemptDetail.completed_at,
        practice_recommendations: attemptDetail.practice_recommendations || [],
        question_answers: attemptDetail.question_answers || [],
      });
      setViewState('review');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load attempt details');
      console.error('Error loading attempt details:', err);
    }
  };

  const formatDate = (dateString: string): string => {
    return formatDateAndTime(dateString, timezone, timeFormat);
  };

  // Render Quiz View
  if (viewState === 'quiz' && currentAssessment) {
    const question = currentAssessment.questions[currentQuestionIndex];
    const isLastQuestion = currentQuestionIndex === currentAssessment.questions.length - 1;
    const hasAnswer = answers[question.id.toString()] !== undefined;
    const progress = ((currentQuestionIndex + 1) / currentAssessment.questions.length) * 100;

    return (
      <div className="screen-container">
        <div className="quiz-view">
          <button className="back-button" onClick={handleBackToList}>
            <ChevronLeft size={16} />
            Exit Assessment
          </button>

          <div className="quiz-progress">
            <div className="progress-text">
              <span>
                Question {currentQuestionIndex + 1} of {currentAssessment.questions.length}
              </span>
              <span>{Math.round(progress)}% complete</span>
            </div>
            <div className="progress-bar-bg">
              <div className="progress-bar-fill" style={{ width: `${progress}%` }} />
            </div>
          </div>

          <div className="quiz-question">
            <span className="question-skill">{question.skill_category}</span>
            <p className="question-text">{question.question_text}</p>

            {question.options && (
              <div className="answer-options">
                {question.options.map((option, idx) => (
                  <button
                    key={idx}
                    type="button"
                    className={`answer-option ${answers[question.id.toString()] === option ? 'selected' : ''}`}
                    onClick={() => handleSelectAnswer(question.id, option)}
                  >
                    {option}
                  </button>
                ))}
              </div>
            )}
          </div>

          {error && (
            <div className="error-message">
              <AlertCircle size={16} />
              <span>{error}</span>
            </div>
          )}

          <div className="quiz-navigation">
            <button
              className="nav-button secondary"
              onClick={handlePrevQuestion}
              disabled={currentQuestionIndex === 0}
            >
              <ChevronLeft size={16} />
              Previous
            </button>

            {isLastQuestion ? (
              <button
                className="nav-button primary"
                onClick={handleSubmitAssessment}
                disabled={!hasAnswer || submitting}
              >
                {submitting ? 'Submitting...' : 'Submit Assessment'}
              </button>
            ) : (
              <button
                className="nav-button primary"
                onClick={handleNextQuestion}
                disabled={!hasAnswer}
              >
                Next
                <ChevronRight size={16} />
              </button>
            )}
          </div>
        </div>
      </div>
    );
  }

  // Render Results View
  if (viewState === 'results' && result) {
    return (
      <div className="screen-container">
        <div className="results-view">
          <button className="back-button" onClick={handleBackToList}>
            <ChevronLeft size={16} />
            Back to Assessments
          </button>

          {successMessage && (
            <div className="success-message">
              <CheckCircle size={16} />
              <span>{successMessage}</span>
            </div>
          )}

          <div className="results-header">
            <h2>Assessment Complete!</h2>
            <p className="results-subtitle">
              Here&apos;s how you performed in the {getLanguageDisplayName(selectedLanguage)}{' '}
              placement test
            </p>
          </div>

          <div className="score-display">
            <div className="score-circle">
              <span className="score-value">{Math.round(result.score)}%</span>
              <span className="score-label">Overall Score</span>
            </div>
            <div className="recommended-level">
              <Award size={20} />
              <span>Recommended Level:</span>
              <span className="level">{result.recommended_level}</span>
            </div>
          </div>

          <div className="skill-breakdown">
            <h3>Skill Breakdown</h3>
            <div className="skill-scores">
              {result.skill_scores.map(skill => (
                <div key={skill.skill} className="skill-score-item">
                  <div className="skill-score-header">
                    <span className="skill-name">{skill.skill}</span>
                    <span className="skill-score-value">{Math.round(skill.score)}%</span>
                  </div>
                  <div className="skill-bar-bg">
                    <div className="skill-bar-fill" style={{ width: `${skill.score}%` }} />
                  </div>
                  <div className="skill-details">
                    {skill.correct} of {skill.total} correct
                  </div>
                </div>
              ))}
            </div>
          </div>

          {result.practice_recommendations.length > 0 && (
            <div className="recommendations">
              <h3>Practice Recommendations</h3>
              <div className="recommendation-list">
                {result.practice_recommendations.map((rec, idx) => (
                  <div key={idx} className="recommendation-item">
                    <Lightbulb size={16} />
                    <span>{rec}</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          <div className="results-actions">
            {!successMessage && (
              <button className="apply-button" onClick={() => setShowConfirmDialog(true)}>
                Apply Level {result.recommended_level} to My Profile
              </button>
            )}
            <div className="results-secondary-actions">
              <button className="retake-button" onClick={handleRetake}>
                Retake Assessment
              </button>
              <button className="done-button" onClick={handleBackToList}>
                Done
              </button>
            </div>
          </div>

          {/* Confirm Dialog */}
          {showConfirmDialog && (
            <div className="confirm-overlay">
              <div className="confirm-dialog">
                <h4>Update Your Level?</h4>
                <p>
                  This will set your {getLanguageDisplayName(selectedLanguage)} proficiency level to{' '}
                  <strong>{result.recommended_level}</strong>. Your conversation difficulty and
                  lesson recommendations will be adjusted accordingly.
                </p>
                <div className="confirm-actions">
                  <button
                    className="confirm-cancel"
                    onClick={() => setShowConfirmDialog(false)}
                    disabled={applyingLevel}
                  >
                    Cancel
                  </button>
                  <button
                    className="confirm-confirm"
                    onClick={handleApplyLevel}
                    disabled={applyingLevel}
                  >
                    {applyingLevel ? 'Updating...' : 'Apply Level'}
                  </button>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    );
  }

  // Render Review View
  if (viewState === 'review' && result && result.question_answers) {
    return (
      <div className="screen-container">
        <div className="review-view">
          <button className="back-button" onClick={handleBackToList}>
            <ChevronLeft size={16} />
            Back to Assessments
          </button>

          <div className="results-header">
            <h2>Assessment Review</h2>
            <p className="results-subtitle">
              Review your answers for the {getLanguageDisplayName(selectedLanguage)} placement test
            </p>
          </div>

          <div className="score-display">
            <div className="score-circle">
              <span className="score-value">{Math.round(result.score)}%</span>
              <span className="score-label">Overall Score</span>
            </div>
            <div className="recommended-level">
              <Award size={20} />
              <span>Recommended Level:</span>
              <span className="level">{result.recommended_level}</span>
            </div>
          </div>

          <div className="question-review-list">
            <h3>Question Review</h3>
            {result.question_answers.map((qa, idx) => (
              <div key={qa.question_id} className="question-review-item">
                <div className="question-review-header">
                  <span className="question-number">Question {idx + 1}</span>
                  <span className={`question-status ${qa.is_correct ? 'correct' : 'incorrect'}`}>
                    {qa.is_correct ? (
                      <>
                        <CheckCircle size={16} />
                        Correct
                      </>
                    ) : (
                      <>
                        <AlertCircle size={16} />
                        Incorrect
                      </>
                    )}
                  </span>
                </div>
                <div className="question-review-skill">
                  <span className="skill-tag">{qa.skill_category}</span>
                </div>
                <p className="question-review-text">{qa.question_text}</p>
                {qa.options && qa.options.length > 0 && (
                  <div className="question-review-options">
                    {qa.options.map((option, optIdx) => {
                      const isUserAnswer = option === qa.user_answer;
                      const isCorrectAnswer = option === qa.correct_answer;
                      let optionClass = 'review-option';
                      if (isCorrectAnswer) optionClass += ' correct-option';
                      if (isUserAnswer && !qa.is_correct) optionClass += ' incorrect-selected';

                      return (
                        <div key={optIdx} className={optionClass}>
                          {isCorrectAnswer && <CheckCircle size={14} />}
                          {isUserAnswer && !qa.is_correct && <AlertCircle size={14} />}
                          <span>{option}</span>
                        </div>
                      );
                    })}
                  </div>
                )}
                <div className="question-review-answers">
                  <div className={`answer-review ${qa.is_correct ? 'correct' : 'incorrect'}`}>
                    <span className="answer-label">Your answer:</span>
                    <span className="answer-value">{qa.user_answer}</span>
                  </div>
                  {!qa.is_correct && (
                    <div className="answer-review correct">
                      <span className="answer-label">Correct answer:</span>
                      <span className="answer-value">{qa.correct_answer}</span>
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>

          <div className="results-actions">
            <button className="done-button" onClick={handleBackToList}>
              Done
            </button>
          </div>
        </div>
      </div>
    );
  }

  // Render List View
  return (
    <div className="screen-container">
      <div className="assessments-screen">
        <h1>CEFR Assessments</h1>

        <div className="assessment-selection-info">
          <div className="selection-badge">
            <span className="selection-label">Language:</span>
            <span className="selection-value">{getLanguageDisplayName(selectedLanguage)}</span>
          </div>
          <div className="selection-badge">
            <span className="selection-label">Current Level:</span>
            <span className="selection-value">{selectedDifficulty}</span>
          </div>
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
            <span>Loading assessments...</span>
          </div>
        ) : assessments.length === 0 ? (
          <p className="empty-message">
            No assessments available for {getLanguageDisplayName(selectedLanguage)} yet.
          </p>
        ) : (
          <div className="assessments-list">
            {assessments.map(assessment => (
              <div key={assessment.id} className="assessment-card">
                <div className="assessment-card-header">
                  <h3>{assessment.title}</h3>
                </div>
                {assessment.description && (
                  <p className="assessment-description">{assessment.description}</p>
                )}
                <div className="assessment-meta">
                  <span className="meta-item">
                    <Clock size={14} />
                    {assessment.duration_minutes} min
                  </span>
                  <span className="meta-item">
                    <HelpCircle size={14} />
                    {assessment.question_count} questions
                  </span>
                </div>
                <div className="skill-tags">
                  {assessment.skill_categories.map(skill => (
                    <span key={skill} className="skill-tag">
                      {skill}
                    </span>
                  ))}
                </div>
                <button
                  className="start-button"
                  onClick={() => handleStartAssessment(assessment.id)}
                >
                  Start Assessment
                </button>
              </div>
            ))}
          </div>
        )}

        {/* Attempt History */}
        {attempts.length > 0 && (
          <div className="attempt-history">
            <h3>
              <History size={18} style={{ verticalAlign: 'middle', marginRight: '0.5rem' }} />
              Recent Attempts
            </h3>
            <div className="attempt-list">
              {attempts.map(attempt => (
                <div key={attempt.id} className="attempt-item">
                  <div className="attempt-info">
                    <span className="attempt-title">{attempt.assessment_title}</span>
                    <span className="attempt-date">{formatDate(attempt.completed_at)}</span>
                  </div>
                  <div className="attempt-results">
                    <span className="attempt-score">{Math.round(attempt.score)}%</span>
                    <span className="attempt-level">{attempt.recommended_level}</span>
                  </div>
                  <div className="attempt-actions">
                    <button
                      className="attempt-action-button"
                      onClick={() => handleApplyLevelFromAttempt(attempt)}
                      title={`Apply level ${attempt.recommended_level} to profile`}
                    >
                      <Check size={14} />
                      Apply Level
                    </button>
                    <button
                      className="attempt-action-button"
                      onClick={() => handleReviewAttempt(attempt)}
                      title="Review assessment results"
                    >
                      <Eye size={14} />
                      Review
                    </button>
                    <button
                      className="attempt-action-button"
                      onClick={() => handleRetakeFromAttempt(attempt)}
                      title="Retake this assessment"
                    >
                      <RotateCcw size={14} />
                      Retake
                    </button>
                    <button
                      className="attempt-action-button danger"
                      onClick={() => handleDeleteAttempt(attempt.id)}
                      title="Delete this attempt"
                    >
                      <Trash2 size={14} />
                      Delete
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default AssessmentsScreen;
