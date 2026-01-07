import React, { useMemo } from 'react';
import './TTSControls.css';

export interface TTSControlsProps {
  language: string;
  supported: boolean;
  voices: SpeechSynthesisVoice[];
  selectedVoiceURI: string | null;
  rate: number;
  autoPlay: boolean;
  isSpeaking: boolean;
  isPaused: boolean;
  lastError: string | null;
  onSelectVoiceURI: (voiceURI: string | null) => void;
  onRateChange: (rate: number) => void;
  onAutoPlayChange: (autoPlay: boolean) => void;
  onPause: () => void;
  onResume: () => void;
  onStop: () => void;
}

function getBaseLanguageTag(tag: string): string {
  return tag.split('-')[0]?.toLowerCase() ?? '';
}

function languageToBaseTag(language: string): string {
  const key = language.trim().toLowerCase();
  switch (key) {
    case 'spanish':
      return 'es';
    case 'italian':
      return 'it';
    case 'german':
      return 'de';
    case 'french':
      return 'fr';
    case 'dutch':
      return 'nl';
    case 'english':
      return 'en';
    default:
      return getBaseLanguageTag(language);
  }
}

export const TTSControls: React.FC<TTSControlsProps> = ({
  language,
  supported,
  voices,
  selectedVoiceURI,
  rate,
  autoPlay,
  isSpeaking,
  isPaused,
  lastError,
  onSelectVoiceURI,
  onRateChange,
  onAutoPlayChange,
  onPause,
  onResume,
  onStop,
}) => {
  const languageVoices = useMemo(() => {
    const base = languageToBaseTag(language);
    if (!base) return [];
    return voices.filter(v => getBaseLanguageTag(v.lang) === base);
  }, [language, voices]);

  const showVoiceSelector = supported && languageVoices.length > 0;

  return (
    <div className="tts-controls" aria-label="Text-to-speech controls">
      <div className="tts-controls-row">
        <div className="tts-controls-buttons">
          <button
            type="button"
            className="tts-button"
            onClick={isPaused ? onResume : onPause}
            disabled={!supported || !isSpeaking}
            aria-label={isPaused ? 'Resume speech' : 'Pause speech'}
            title={isPaused ? 'Resume' : 'Pause'}
          >
            {isPaused ? 'Resume' : 'Pause'}
          </button>
          <button
            type="button"
            className="tts-button tts-button-danger"
            onClick={onStop}
            disabled={!supported || !isSpeaking}
            aria-label="Stop speech"
            title="Stop"
          >
            Stop
          </button>

          {isSpeaking && (
            <div className="tts-speaking-indicator" aria-label="Speaking">
              <span className="bar" />
              <span className="bar" />
              <span className="bar" />
            </div>
          )}
        </div>

        <label className="tts-toggle">
          <input
            type="checkbox"
            checked={autoPlay}
            onChange={e => onAutoPlayChange(e.target.checked)}
            disabled={!supported}
          />
          <span>Auto-play</span>
        </label>
      </div>

      <div className="tts-controls-row tts-controls-row-secondary">
        <label className="tts-rate">
          <span className="tts-label">Rate</span>
          <input
            type="range"
            min={0.5}
            max={1.5}
            step={0.05}
            value={rate}
            onChange={e => onRateChange(Number(e.target.value))}
            disabled={!supported}
          />
          <span className="tts-rate-value">{rate.toFixed(2)}×</span>
        </label>

        {showVoiceSelector && (
          <label className="tts-voice">
            <span className="tts-label">Voice</span>
            <select
              value={selectedVoiceURI ?? ''}
              onChange={e => onSelectVoiceURI(e.target.value || null)}
              disabled={!supported}
            >
              <option value="">Default</option>
              {languageVoices.map(v => (
                <option key={v.voiceURI} value={v.voiceURI}>
                  {v.name} ({v.lang})
                </option>
              ))}
            </select>
          </label>
        )}
      </div>

      {!supported && <div className="tts-warning">TTS is not available in this environment.</div>}
      {supported && lastError && <div className="tts-warning">{lastError}</div>}
    </div>
  );
};
