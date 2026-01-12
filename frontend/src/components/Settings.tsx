import { useState, useEffect, useMemo } from 'react';
import { X, Eye, EyeOff, CheckCircle, AlertCircle, Search } from 'lucide-react';
import {
  settingsService,
  type LLMProvider,
  type TimeFormat,
  AVAILABLE_MODELS,
  DEFAULT_MODELS,
} from '../services/settings';
import type { Language } from '../types';
import {
  TIMEZONE_OPTIONS,
  TIME_FORMAT_OPTIONS,
  filterTimezones,
  detectUserTimezone,
  detectTimeFormat,
  getCurrentTime,
} from '../utils/dateTime';
import { maskApiKey } from '../utils/encryption';
import toast from 'react-hot-toast';
import './Settings.css';

interface SettingsProps {
  isOpen: boolean;
  onClose: () => void;
  inline?: boolean;
}

// API key validation constants
const ANTHROPIC_KEY_PREFIX = 'sk-ant-api03-';
const GOOGLE_KEY_PREFIX = 'AI';

function Settings({ isOpen, onClose, inline = false }: SettingsProps) {
  const [llmProvider, setLlmProvider] = useState<LLMProvider>('ollama');
  const [anthropicApiKey, setAnthropicApiKey] = useState('');
  const [googleApiKey, setGoogleApiKey] = useState('');
  const [showAnthropicKey, setShowAnthropicKey] = useState(false);
  const [showGoogleKey, setShowGoogleKey] = useState(false);
  const [isValidatingAnthropic, setIsValidatingAnthropic] = useState(false);
  const [isValidatingGoogle, setIsValidatingGoogle] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [hasAnthropicKey, setHasAnthropicKey] = useState(false);
  const [hasGoogleKey, setHasGoogleKey] = useState(false);
  const [isAnthropicKeyMasked, setIsAnthropicKeyMasked] = useState(false);
  const [isGoogleKeyMasked, setIsGoogleKeyMasked] = useState(false);

  // Model selection state
  const [ollamaModel, setOllamaModel] = useState(DEFAULT_MODELS.ollama);
  const [claudeModel, setClaudeModel] = useState(DEFAULT_MODELS.claude);
  const [geminiModel, setGeminiModel] = useState(DEFAULT_MODELS.gemini);
  const [customOllamaModel, setCustomOllamaModel] = useState('');

  // Display settings state
  const [timezone, setTimezone] = useState(detectUserTimezone());
  const [timeFormat, setTimeFormat] = useState<TimeFormat>(detectTimeFormat());
  const [timezoneSearch, setTimezoneSearch] = useState('');
  const [isTimezoneDropdownOpen, setIsTimezoneDropdownOpen] = useState(false);
  const [nativeLanguage, setNativeLanguage] = useState<Language>('spanish');

  // Filtered timezone options based on search
  const filteredTimezones = useMemo(() => filterTimezones(timezoneSearch), [timezoneSearch]);

  // Current time preview
  const currentTimePreview = useMemo(
    () => getCurrentTime(timezone, timeFormat),
    [timezone, timeFormat]
  );

  useEffect(() => {
    if (isOpen) {
      loadSettings();
    }
  }, [isOpen]);

  const loadSettings = async () => {
    try {
      const settings = await settingsService.loadSettings();
      setLlmProvider(settings.llmProvider);

      // Load model selections
      setOllamaModel(settings.ollamaModel);
      setClaudeModel(settings.claudeModel);
      setGeminiModel(settings.geminiModel);

      // Check if Ollama model is custom (not in predefined list)
      const isOllamaCustom = !AVAILABLE_MODELS.ollama.some(m => m.value === settings.ollamaModel);
      if (isOllamaCustom) {
        setCustomOllamaModel(settings.ollamaModel);
        setOllamaModel('custom');
      }

      // Load display settings
      setTimezone(settings.timezone);
      setTimeFormat(settings.timeFormat);
      setNativeLanguage(settings.nativeLanguage);

      // Check if keys exist but don't show them for security
      setHasAnthropicKey(!!settings.anthropicApiKey);
      setHasGoogleKey(!!settings.googleApiKey);

      // Show masked keys
      if (settings.anthropicApiKey) {
        setAnthropicApiKey(maskApiKey(settings.anthropicApiKey));
        setIsAnthropicKeyMasked(true);
      }
      if (settings.googleApiKey) {
        setGoogleApiKey(maskApiKey(settings.googleApiKey));
        setIsGoogleKeyMasked(true);
      }
    } catch (error) {
      console.error('Failed to load settings:', error);
      toast.error('Failed to load settings');
    }
  };

  const validateAnthropicKey = async (key: string): Promise<boolean> => {
    setIsValidatingAnthropic(true);
    try {
      // Simple validation: Check if it looks like a valid Anthropic key
      if (!key.startsWith(ANTHROPIC_KEY_PREFIX)) {
        toast.error('Invalid Anthropic API key format');
        return false;
      }

      // Note: Full validation would require sending a test request to Anthropic's API
      // For now, we just validate the format
      toast.success('Anthropic API key format is valid');
      return true;
    } catch (error) {
      console.error('Anthropic API key validation failed:', error);
      toast.error('Failed to validate Anthropic API key');
      return false;
    } finally {
      setIsValidatingAnthropic(false);
    }
  };

  const validateGoogleKey = async (key: string): Promise<boolean> => {
    setIsValidatingGoogle(true);
    try {
      // Simple validation: Check if it looks like a valid Google API key
      if (!key.startsWith(GOOGLE_KEY_PREFIX)) {
        toast.error('Invalid Google API key format');
        return false;
      }

      // Note: Full validation would require sending a test request to Google's API
      // For now, we just validate the format
      toast.success('Google API key format is valid');
      return true;
    } catch (error) {
      console.error('Google API key validation failed:', error);
      toast.error('Failed to validate Google API key');
      return false;
    } finally {
      setIsValidatingGoogle(false);
    }
  };

  const handleSave = async () => {
    setIsSaving(true);
    try {
      // Save LLM provider
      settingsService.saveLLMProvider(llmProvider);

      // Save model selections
      const effectiveOllamaModel = ollamaModel === 'custom' ? customOllamaModel : ollamaModel;
      if (effectiveOllamaModel) {
        settingsService.saveModel('ollama', effectiveOllamaModel);
      }
      settingsService.saveModel('claude', claudeModel);
      settingsService.saveModel('gemini', geminiModel);

      // Save display settings
      settingsService.saveTimezone(timezone);
      settingsService.saveTimeFormat(timeFormat);
      settingsService.saveNativeLanguage(nativeLanguage);

      // Save API keys only if they were changed (not masked)
      if (anthropicApiKey && !isAnthropicKeyMasked) {
        await settingsService.saveApiKey('anthropic', anthropicApiKey);
        setHasAnthropicKey(true);
      }

      if (googleApiKey && !isGoogleKeyMasked) {
        await settingsService.saveApiKey('google', googleApiKey);
        setHasGoogleKey(true);
      }

      toast.success('Settings saved successfully');
      onClose();
    } catch (error) {
      console.error('Failed to save settings:', error);
      toast.error('Failed to save settings');
    } finally {
      setIsSaving(false);
    }
  };

  const handleTestAnthropicKey = async () => {
    if (anthropicApiKey && !isAnthropicKeyMasked) {
      await validateAnthropicKey(anthropicApiKey);
    } else {
      toast.error('Please enter a new API key to test');
    }
  };

  const handleTestGoogleKey = async () => {
    if (googleApiKey && !isGoogleKeyMasked) {
      await validateGoogleKey(googleApiKey);
    } else {
      toast.error('Please enter a new API key to test');
    }
  };

  const handleClearAnthropicKey = () => {
    settingsService.removeApiKey('anthropic');
    setAnthropicApiKey('');
    setHasAnthropicKey(false);
    setIsAnthropicKeyMasked(false);
    toast.success('Anthropic API key cleared');
  };

  const handleClearGoogleKey = () => {
    settingsService.removeApiKey('google');
    setGoogleApiKey('');
    setHasGoogleKey(false);
    setIsGoogleKeyMasked(false);
    toast.success('Google API key cleared');
  };

  if (!isOpen) return null;

  const settingsContent = (
    <>
      {!inline && (
        <div className="settings-header">
          <h2>Settings</h2>
          <button className="settings-close" onClick={onClose} aria-label="Close settings">
            <X size={24} />
          </button>
        </div>
      )}

      <div className="settings-content">
        {/* Display Settings */}
        <div className="settings-section">
          <h3>Display Settings</h3>
          <p className="settings-description">
            Configure how dates, times, and languages are displayed in the app.
          </p>

          {/* Native/Reference Language Selection */}
          <h4 className="settings-subsection-title">Native Language</h4>
          <p className="settings-description">
            Select your native or reference language. This is used for translations and
            explanations.
          </p>
          <select
            value={nativeLanguage}
            onChange={e => setNativeLanguage(e.target.value as Language)}
            className="settings-select"
          >
            <option value="spanish">Spanish</option>
            <option value="italian">Italian</option>
            <option value="german">German</option>
            <option value="french">French</option>
            <option value="dutch">Dutch</option>
          </select>

          {/* Timezone Selection */}
          <h4 className="settings-subsection-title">Timezone</h4>
          <div className="timezone-selector">
            <div
              className="timezone-input-wrapper"
              onClick={() => setIsTimezoneDropdownOpen(!isTimezoneDropdownOpen)}
            >
              <Search size={16} className="timezone-search-icon" />
              <input
                type="text"
                value={
                  isTimezoneDropdownOpen
                    ? timezoneSearch
                    : TIMEZONE_OPTIONS.find(tz => tz.value === timezone)?.label || timezone
                }
                onChange={e => {
                  setTimezoneSearch(e.target.value);
                  setIsTimezoneDropdownOpen(true);
                }}
                onFocus={() => {
                  setIsTimezoneDropdownOpen(true);
                  setTimezoneSearch('');
                }}
                placeholder="Search timezones..."
                className="settings-input timezone-input"
              />
            </div>
            {isTimezoneDropdownOpen && (
              <div className="timezone-dropdown">
                {filteredTimezones.length > 0 ? (
                  <>
                    {/* Group timezones by region */}
                    {['UTC', 'Europe', 'Americas', 'Asia', 'Oceania', 'Africa'].map(group => {
                      const groupTimezones = filteredTimezones.filter(tz => tz.group === group);
                      if (groupTimezones.length === 0) return null;
                      return (
                        <div key={group} className="timezone-group">
                          <div className="timezone-group-header">{group}</div>
                          {groupTimezones.map(tz => (
                            <div
                              key={tz.value}
                              className={`timezone-option ${timezone === tz.value ? 'selected' : ''}`}
                              onClick={() => {
                                setTimezone(tz.value);
                                setIsTimezoneDropdownOpen(false);
                                setTimezoneSearch('');
                              }}
                            >
                              {tz.label}
                            </div>
                          ))}
                        </div>
                      );
                    })}
                  </>
                ) : (
                  <div className="timezone-no-results">No timezones found</div>
                )}
              </div>
            )}
          </div>

          {/* Time Format Selection */}
          <h4 className="settings-subsection-title">Time Format</h4>
          <div className="time-format-options">
            {TIME_FORMAT_OPTIONS.map(option => (
              <label key={option.value} className="time-format-option">
                <input
                  type="radio"
                  name="timeFormat"
                  value={option.value}
                  checked={timeFormat === option.value}
                  onChange={() => setTimeFormat(option.value)}
                />
                <span>{option.label}</span>
              </label>
            ))}
          </div>

          {/* Preview */}
          <div className="time-preview">
            <span className="time-preview-label">Preview:</span>
            <span className="time-preview-value">{currentTimePreview}</span>
          </div>
        </div>

        {/* LLM Provider Selection */}
        <div className="settings-section">
          <h3>LLM Provider</h3>
          <p className="settings-description">
            Choose which AI provider to use for conversations. Ollama runs locally and requires no
            API key.
          </p>
          <select
            value={llmProvider}
            onChange={e => setLlmProvider(e.target.value as LLMProvider)}
            className="settings-select"
          >
            <option value="ollama">Ollama (Local - No API Key Required)</option>
            <option value="claude">Anthropic Claude (API Key Required)</option>
            <option value="gemini">Google Gemini (API Key Required)</option>
            <option value="mock">Mock (Testing Only)</option>
          </select>
        </div>

        {/* Anthropic API Key */}
        {llmProvider === 'claude' && (
          <div className="settings-section">
            <h3>Anthropic API Key</h3>
            <p className="settings-description">
              Get your API key from{' '}
              <a
                href="https://console.anthropic.com/settings/keys"
                target="_blank"
                rel="noopener noreferrer"
              >
                Anthropic Console
              </a>
            </p>
            <div className="settings-input-group">
              <div className="settings-input-wrapper">
                <input
                  type={showAnthropicKey ? 'text' : 'password'}
                  value={anthropicApiKey}
                  onChange={e => {
                    setAnthropicApiKey(e.target.value);
                    setIsAnthropicKeyMasked(false);
                  }}
                  placeholder="sk-ant-api03-..."
                  className="settings-input"
                />
                <button
                  className="settings-input-button"
                  onClick={() => setShowAnthropicKey(!showAnthropicKey)}
                  aria-label={showAnthropicKey ? 'Hide API key' : 'Show API key'}
                >
                  {showAnthropicKey ? <EyeOff size={20} /> : <Eye size={20} />}
                </button>
              </div>
              <div className="settings-button-group">
                <button
                  onClick={handleTestAnthropicKey}
                  disabled={isValidatingAnthropic || !anthropicApiKey}
                  className="settings-button settings-button-secondary"
                >
                  {isValidatingAnthropic ? 'Testing...' : 'Test Key'}
                </button>
                {hasAnthropicKey && (
                  <button
                    onClick={handleClearAnthropicKey}
                    className="settings-button settings-button-danger"
                  >
                    Clear Key
                  </button>
                )}
              </div>
            </div>
            {hasAnthropicKey && isAnthropicKeyMasked && (
              <div className="settings-status settings-status-success">
                <CheckCircle size={16} />
                <span>API key configured (enter new key to replace)</span>
              </div>
            )}

            <h4 className="settings-subsection-title">Model Selection</h4>
            <p className="settings-description">Select which Claude model to use.</p>
            <select
              value={claudeModel}
              onChange={e => setClaudeModel(e.target.value)}
              className="settings-select"
            >
              {AVAILABLE_MODELS.claude.map(model => (
                <option key={model.value} value={model.value}>
                  {model.label}
                </option>
              ))}
            </select>
          </div>
        )}

        {/* Google API Key */}
        {llmProvider === 'gemini' && (
          <div className="settings-section">
            <h3>Google API Key</h3>
            <p className="settings-description">
              Get your API key from{' '}
              <a
                href="https://aistudio.google.com/app/apikey"
                target="_blank"
                rel="noopener noreferrer"
              >
                Google AI Studio
              </a>
            </p>
            <div className="settings-input-group">
              <div className="settings-input-wrapper">
                <input
                  type={showGoogleKey ? 'text' : 'password'}
                  value={googleApiKey}
                  onChange={e => {
                    setGoogleApiKey(e.target.value);
                    setIsGoogleKeyMasked(false);
                  }}
                  placeholder="AIza..."
                  className="settings-input"
                />
                <button
                  className="settings-input-button"
                  onClick={() => setShowGoogleKey(!showGoogleKey)}
                  aria-label={showGoogleKey ? 'Hide API key' : 'Show API key'}
                >
                  {showGoogleKey ? <EyeOff size={20} /> : <Eye size={20} />}
                </button>
              </div>
              <div className="settings-button-group">
                <button
                  onClick={handleTestGoogleKey}
                  disabled={isValidatingGoogle || !googleApiKey}
                  className="settings-button settings-button-secondary"
                >
                  {isValidatingGoogle ? 'Testing...' : 'Test Key'}
                </button>
                {hasGoogleKey && (
                  <button
                    onClick={handleClearGoogleKey}
                    className="settings-button settings-button-danger"
                  >
                    Clear Key
                  </button>
                )}
              </div>
            </div>
            {hasGoogleKey && isGoogleKeyMasked && (
              <div className="settings-status settings-status-success">
                <CheckCircle size={16} />
                <span>API key configured (enter new key to replace)</span>
              </div>
            )}

            <h4 className="settings-subsection-title">Model Selection</h4>
            <p className="settings-description">Select which Gemini model to use.</p>
            <select
              value={geminiModel}
              onChange={e => setGeminiModel(e.target.value)}
              className="settings-select"
            >
              {AVAILABLE_MODELS.gemini.map(model => (
                <option key={model.value} value={model.value}>
                  {model.label}
                </option>
              ))}
            </select>
          </div>
        )}

        {/* Info about Ollama */}
        {llmProvider === 'ollama' && (
          <div className="settings-section">
            <div className="settings-info">
              <AlertCircle size={20} />
              <div>
                <h4>Using Ollama (Local AI)</h4>
                <p>
                  Ollama runs AI models locally on your computer. No API key needed! Make sure
                  Ollama is installed and running on <code>http://localhost:11434</code>
                </p>
                <p>
                  <a href="https://ollama.com/" target="_blank" rel="noopener noreferrer">
                    Download Ollama
                  </a>
                </p>
              </div>
            </div>

            <h4 className="settings-subsection-title">Model Selection</h4>
            <p className="settings-description">
              Select an Ollama model to use. Make sure the model is pulled locally.
            </p>
            <select
              value={ollamaModel}
              onChange={e => {
                setOllamaModel(e.target.value);
                if (e.target.value !== 'custom') {
                  setCustomOllamaModel('');
                }
              }}
              className="settings-select"
            >
              {AVAILABLE_MODELS.ollama.map(model => (
                <option key={model.value} value={model.value}>
                  {model.label}
                </option>
              ))}
              <option value="custom">Custom Model...</option>
            </select>

            {ollamaModel === 'custom' && (
              <input
                type="text"
                value={customOllamaModel}
                onChange={e => setCustomOllamaModel(e.target.value)}
                placeholder="e.g., llama3:8b, codellama:13b"
                className="settings-input settings-input-model"
              />
            )}

            {/* Model Pull Indicator */}
            <div className="settings-info" style={{ marginTop: '1rem' }}>
              <AlertCircle size={20} />
              <div>
                <h4>Make sure the model is pulled locally</h4>
                <p>
                  Before using this model, ensure it's downloaded to your local Ollama installation.
                </p>
                <div className="ollama-command">
                  <code>
                    ollama pull{' '}
                    {ollamaModel === 'custom' ? customOllamaModel || 'MODEL_NAME' : ollamaModel}
                  </code>
                  <button
                    className="settings-button settings-button-secondary"
                    style={{
                      marginLeft: '0.5rem',
                      padding: '0.25rem 0.5rem',
                      fontSize: '0.875rem',
                    }}
                    onClick={() => {
                      const command = `ollama pull ${ollamaModel === 'custom' ? customOllamaModel || 'MODEL_NAME' : ollamaModel}`;
                      navigator.clipboard.writeText(command);
                      toast.success('Command copied to clipboard');
                    }}
                  >
                    Copy
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}

        <div className="settings-footer">
          {!inline && (
            <button onClick={onClose} className="settings-button settings-button-secondary">
              Cancel
            </button>
          )}
          <button
            onClick={handleSave}
            disabled={isSaving}
            className="settings-button settings-button-primary"
          >
            {isSaving ? 'Saving...' : 'Save Settings'}
          </button>
        </div>
      </div>
    </>
  );

  if (inline) {
    return <div className="settings-inline">{settingsContent}</div>;
  }

  return (
    <div className="settings-overlay">
      <div className="settings-modal">{settingsContent}</div>
    </div>
  );
}

export default Settings;
