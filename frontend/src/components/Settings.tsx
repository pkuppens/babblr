import { useState, useEffect, useMemo } from 'react';
import { X, Eye, EyeOff, CheckCircle, AlertCircle, Search, Cpu, Zap } from 'lucide-react';
import {
  settingsService,
  type LLMProvider,
  type TimeFormat,
  AVAILABLE_MODELS,
  DEFAULT_MODELS,
} from '../services/settings';
import type { NativeLanguage } from '../types';
import { speechService } from '../services/api';
import {
  TIMEZONE_OPTIONS,
  TIME_FORMAT_OPTIONS,
  filterTimezones,
  detectUserTimezone,
  detectTimeFormat,
  getCurrentTime,
} from '../utils/dateTime';
import CostCalculator from './CostCalculator';
import ModelCombobox from './ModelCombobox';
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
const OPENAI_KEY_PREFIX = 'sk-';

function Settings({ isOpen, onClose, inline = false }: SettingsProps) {
  const [llmProvider, setLlmProvider] = useState<LLMProvider>('ollama');
  const [anthropicApiKey, setAnthropicApiKey] = useState('');
  const [googleApiKey, setGoogleApiKey] = useState('');
  const [openaiApiKey, setOpenaiApiKey] = useState('');
  const [showAnthropicKey, setShowAnthropicKey] = useState(false);
  const [showGoogleKey, setShowGoogleKey] = useState(false);
  const [showOpenaiKey, setShowOpenaiKey] = useState(false);
  const [isValidatingAnthropic, setIsValidatingAnthropic] = useState(false);
  const [isValidatingGoogle, setIsValidatingGoogle] = useState(false);
  const [isValidatingOpenai, setIsValidatingOpenai] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [hasAnthropicKey, setHasAnthropicKey] = useState(false);
  const [hasGoogleKey, setHasGoogleKey] = useState(false);
  const [hasOpenaiKey, setHasOpenaiKey] = useState(false);
  const [isAnthropicKeyMasked, setIsAnthropicKeyMasked] = useState(false);
  const [isGoogleKeyMasked, setIsGoogleKeyMasked] = useState(false);
  const [isOpenaiKeyMasked, setIsOpenaiKeyMasked] = useState(false);

  // Model selection state
  const [ollamaModel, setOllamaModel] = useState(DEFAULT_MODELS.ollama);
  const [claudeModel, setClaudeModel] = useState(DEFAULT_MODELS.claude);
  const [geminiModel, setGeminiModel] = useState(DEFAULT_MODELS.gemini);
  const [openaiModel, setOpenaiModel] = useState(DEFAULT_MODELS.openai);
  const [customOllamaModel, setCustomOllamaModel] = useState('');

  // Language settings state
  const [nativeLanguage, setNativeLanguage] = useState<NativeLanguage>('english');

  // Display settings state
  const [timezone, setTimezone] = useState(detectUserTimezone());
  const [timeFormat, setTimeFormat] = useState<TimeFormat>(detectTimeFormat());
  const [timezoneSearch, setTimezoneSearch] = useState('');
  const [isTimezoneDropdownOpen, setIsTimezoneDropdownOpen] = useState(false);

  // STT settings state
  const [sttConfig, setSttConfig] = useState<{
    current_model: string;
    available_models: string[];
    cuda: {
      available: boolean;
      device: string;
      device_name?: string | null;
      memory_total_gb?: number | null;
      memory_free_gb?: number | null;
    };
    device: string;
  } | null>(null);
  const [isLoadingSttConfig, setIsLoadingSttConfig] = useState(false);
  const [isSwitchingModel, setIsSwitchingModel] = useState(false);
  const [modelSwitchProgress, setModelSwitchProgress] = useState<string>('');

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
      loadSttConfig();
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
      setOpenaiModel(settings.openaiModel);

      // Check if Ollama model is custom (not in predefined list)
      const isOllamaCustom = !AVAILABLE_MODELS.ollama.some(m => m.value === settings.ollamaModel);
      if (isOllamaCustom) {
        setCustomOllamaModel(settings.ollamaModel);
        setOllamaModel('custom');
      }

      // Load language settings
      setNativeLanguage(settings.nativeLanguage);

      // Load display settings
      setTimezone(settings.timezone);
      setTimeFormat(settings.timeFormat);

      // Check if keys exist but don't show them for security
      // Store empty string in state, but mark as masked so we know a key exists
      setHasAnthropicKey(!!settings.anthropicApiKey);
      setHasGoogleKey(!!settings.googleApiKey);
      setHasOpenaiKey(!!settings.openaiApiKey);

      // Don't load actual keys into state for security - keep state empty
      // Mark as masked so we know keys exist and can display masked version
      if (settings.anthropicApiKey) {
        setAnthropicApiKey('');
        setIsAnthropicKeyMasked(true);
      }
      if (settings.googleApiKey) {
        setGoogleApiKey('');
        setIsGoogleKeyMasked(true);
      }
      if (settings.openaiApiKey) {
        setOpenaiApiKey('');
        setIsOpenaiKeyMasked(true);
      }
    } catch (error) {
      console.error('Failed to load settings:', error);
      toast.error('Failed to load settings');
    }
  };

  const loadSttConfig = async () => {
    setIsLoadingSttConfig(true);
    try {
      const config = await speechService.getSttConfig();
      setSttConfig(config);
    } catch (error) {
      console.error('Failed to load STT config:', error);
      toast.error('Failed to load STT configuration. Make sure the backend is running.');
      // Set to null so the error message is shown
      setSttConfig(null);
    } finally {
      setIsLoadingSttConfig(false);
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

  const validateOpenaiKey = async (key: string): Promise<boolean> => {
    setIsValidatingOpenai(true);
    try {
      // Simple validation: Check if it looks like a valid OpenAI key
      if (!key.startsWith(OPENAI_KEY_PREFIX)) {
        toast.error('Invalid OpenAI API key format');
        return false;
      }

      // Note: Full validation would require sending a test request to OpenAI's API
      // For now, we just validate the format
      toast.success('OpenAI API key format is valid');
      return true;
    } catch (error) {
      console.error('OpenAI API key validation failed:', error);
      toast.error('Failed to validate OpenAI API key');
      return false;
    } finally {
      setIsValidatingOpenai(false);
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
      settingsService.saveModel('openai', openaiModel);

      // Save language settings
      settingsService.saveNativeLanguage(nativeLanguage);

      // Save display settings
      settingsService.saveTimezone(timezone);
      settingsService.saveTimeFormat(timeFormat);

      // Save API keys only if they were changed (not masked)
      if (anthropicApiKey && !isAnthropicKeyMasked) {
        await settingsService.saveApiKey('anthropic', anthropicApiKey);
        setHasAnthropicKey(true);
      }

      if (googleApiKey && !isGoogleKeyMasked) {
        await settingsService.saveApiKey('google', googleApiKey);
        setHasGoogleKey(true);
      }

      if (openaiApiKey && !isOpenaiKeyMasked) {
        await settingsService.saveApiKey('openai', openaiApiKey);
        setHasOpenaiKey(true);
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
    let keyToTest = anthropicApiKey;
    if (isAnthropicKeyMasked && !anthropicApiKey) {
      // Load the actual key from storage for testing
      const loadedKey = await settingsService.loadApiKey('anthropic');
      if (loadedKey) {
        keyToTest = loadedKey;
      } else {
        toast.error('No API key found to test');
        return;
      }
    }
    if (keyToTest) {
      await validateAnthropicKey(keyToTest);
    } else {
      toast.error('Please enter a new API key to test');
    }
  };

  const handleTestGoogleKey = async () => {
    let keyToTest = googleApiKey;
    if (isGoogleKeyMasked && !googleApiKey) {
      // Load the actual key from storage for testing
      const loadedKey = await settingsService.loadApiKey('google');
      if (loadedKey) {
        keyToTest = loadedKey;
      } else {
        toast.error('No API key found to test');
        return;
      }
    }
    if (keyToTest) {
      await validateGoogleKey(keyToTest);
    } else {
      toast.error('Please enter a new API key to test');
    }
  };

  const handleTestOpenaiKey = async () => {
    let keyToTest = openaiApiKey;
    if (isOpenaiKeyMasked && !openaiApiKey) {
      // Load the actual key from storage for testing
      const loadedKey = await settingsService.loadApiKey('openai');
      if (loadedKey) {
        keyToTest = loadedKey;
      } else {
        toast.error('No API key found to test');
        return;
      }
    }
    if (keyToTest) {
      await validateOpenaiKey(keyToTest);
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

  const handleClearOpenaiKey = () => {
    settingsService.removeApiKey('openai');
    setOpenaiApiKey('');
    setHasOpenaiKey(false);
    setIsOpenaiKeyMasked(false);
    toast.success('OpenAI API key cleared');
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
        {/* Language Settings */}
        <div className="settings-section">
          <h3>Language Settings</h3>
          <p className="settings-description">
            Configure your native or reference language. This is used for translations and
            explanations throughout the app.
          </p>

          {/* Native/Reference Language Selection */}
          <h4 className="settings-subsection-title">Native Language</h4>
          <p className="settings-description">
            Select your native or reference language. This helps the tutor provide better
            explanations and translations.
          </p>
          <select
            value={nativeLanguage}
            onChange={e => setNativeLanguage(e.target.value as NativeLanguage)}
            className="settings-select"
          >
            <option value="english">English</option>
            <option value="spanish">Spanish</option>
            <option value="italian">Italian</option>
            <option value="german">German</option>
            <option value="french">French</option>
            <option value="dutch">Dutch</option>
          </select>
        </div>

        {/* Display Settings */}
        <div className="settings-section">
          <h3>Display Settings</h3>
          <p className="settings-description">
            Configure how dates and times are displayed in the app.
          </p>

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
            <option value="openai">OpenAI (API Key Required)</option>
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
                  value={
                    isAnthropicKeyMasked && !anthropicApiKey && !showAnthropicKey
                      ? '••••••••••••••••••••••••••••••••••••'
                      : anthropicApiKey
                  }
                  onChange={e => {
                    setAnthropicApiKey(e.target.value);
                    setIsAnthropicKeyMasked(false);
                  }}
                  placeholder="sk-ant-api03-..."
                  className="settings-input"
                  readOnly={isAnthropicKeyMasked && !anthropicApiKey && !showAnthropicKey}
                />
                <button
                  className="settings-input-button"
                  onClick={async () => {
                    if (!showAnthropicKey && isAnthropicKeyMasked && !anthropicApiKey) {
                      // Load the actual key when user wants to see it
                      const key = await settingsService.loadApiKey('anthropic');
                      if (key) {
                        setAnthropicApiKey(key);
                        setIsAnthropicKeyMasked(false);
                      }
                    }
                    setShowAnthropicKey(!showAnthropicKey);
                  }}
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
            <p className="settings-description">
              Select which Claude model to use, or type a custom model name.{' '}
              <a
                href="https://docs.anthropic.com/claude/docs/models-overview"
                target="_blank"
                rel="noopener noreferrer"
              >
                View available models and pricing
              </a>
            </p>
            <ModelCombobox
              value={claudeModel}
              onChange={setClaudeModel}
              options={AVAILABLE_MODELS.claude}
              placeholder="Select or type Claude model name..."
              className="settings-model-combobox"
            />
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
                  value={
                    isGoogleKeyMasked && !googleApiKey && !showGoogleKey
                      ? '••••••••••••••••••••••••••••••••••••'
                      : googleApiKey
                  }
                  onChange={e => {
                    setGoogleApiKey(e.target.value);
                    setIsGoogleKeyMasked(false);
                  }}
                  placeholder="AIza..."
                  className="settings-input"
                  readOnly={isGoogleKeyMasked && !googleApiKey && !showGoogleKey}
                />
                <button
                  className="settings-input-button"
                  onClick={async () => {
                    if (!showGoogleKey && isGoogleKeyMasked && !googleApiKey) {
                      // Load the actual key when user wants to see it
                      const key = await settingsService.loadApiKey('google');
                      if (key) {
                        setGoogleApiKey(key);
                        setIsGoogleKeyMasked(false);
                      }
                    }
                    setShowGoogleKey(!showGoogleKey);
                  }}
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
            <p className="settings-description">
              Select which Gemini model to use, or type a custom model name.{' '}
              <a
                href="https://ai.google.dev/models/gemini"
                target="_blank"
                rel="noopener noreferrer"
              >
                View available models and pricing
              </a>
            </p>
            <ModelCombobox
              value={geminiModel}
              onChange={setGeminiModel}
              options={AVAILABLE_MODELS.gemini}
              placeholder="Select or type Gemini model name..."
              className="settings-model-combobox"
            />
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
              Select an Ollama model to use. Make sure the model is pulled locally.{' '}
              <a href="https://ollama.com/library" target="_blank" rel="noopener noreferrer">
                Browse available models
              </a>
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

        {/* OpenAI API Key */}
        {llmProvider === 'openai' && (
          <div className="settings-section">
            <h3>OpenAI API Key</h3>
            <p className="settings-description">
              Get your API key from{' '}
              <a
                href="https://platform.openai.com/api-keys"
                target="_blank"
                rel="noopener noreferrer"
              >
                OpenAI Platform
              </a>
            </p>
            <div className="settings-input-group">
              <div className="settings-input-wrapper">
                <input
                  type={showOpenaiKey ? 'text' : 'password'}
                  value={
                    isOpenaiKeyMasked && !openaiApiKey && !showOpenaiKey
                      ? '••••••••••••••••••••••••••••••••••••'
                      : openaiApiKey
                  }
                  onChange={e => {
                    setOpenaiApiKey(e.target.value);
                    setIsOpenaiKeyMasked(false);
                  }}
                  placeholder="sk-..."
                  className="settings-input"
                  readOnly={isOpenaiKeyMasked && !openaiApiKey && !showOpenaiKey}
                />
                <button
                  className="settings-input-button"
                  onClick={async () => {
                    if (!showOpenaiKey && isOpenaiKeyMasked && !openaiApiKey) {
                      // Load the actual key when user wants to see it
                      const key = await settingsService.loadApiKey('openai');
                      if (key) {
                        setOpenaiApiKey(key);
                        setIsOpenaiKeyMasked(false);
                      }
                    }
                    setShowOpenaiKey(!showOpenaiKey);
                  }}
                  aria-label={showOpenaiKey ? 'Hide API key' : 'Show API key'}
                >
                  {showOpenaiKey ? <EyeOff size={20} /> : <Eye size={20} />}
                </button>
              </div>
              <div className="settings-button-group">
                <button
                  onClick={handleTestOpenaiKey}
                  disabled={isValidatingOpenai || !openaiApiKey}
                  className="settings-button settings-button-secondary"
                >
                  {isValidatingOpenai ? 'Testing...' : 'Test Key'}
                </button>
                {hasOpenaiKey && (
                  <button
                    onClick={handleClearOpenaiKey}
                    className="settings-button settings-button-danger"
                  >
                    Clear Key
                  </button>
                )}
              </div>
            </div>
            {hasOpenaiKey && isOpenaiKeyMasked && (
              <div className="settings-status settings-status-success">
                <CheckCircle size={16} />
                <span>API key configured (enter new key to replace)</span>
              </div>
            )}

            <h4 className="settings-subsection-title">Model Selection</h4>
            <p className="settings-description">
              Select which OpenAI model to use, or type a custom model name (e.g., gpt-5.2-pro).{' '}
              <a
                href="https://platform.openai.com/docs/models"
                target="_blank"
                rel="noopener noreferrer"
              >
                View available models and pricing
              </a>
            </p>
            <ModelCombobox
              value={openaiModel}
              onChange={setOpenaiModel}
              options={AVAILABLE_MODELS.openai}
              placeholder="Select or type OpenAI model name..."
              className="settings-model-combobox"
            />
          </div>
        )}

        {/* Cost Calculator */}
        <div className="settings-section">
          <CostCalculator
            selectedProvider={
              llmProvider === 'claude'
                ? 'anthropic'
                : llmProvider === 'gemini'
                  ? 'google'
                  : llmProvider === 'openai'
                    ? 'openai'
                    : 'ollama'
            }
            selectedModel={
              llmProvider === 'claude'
                ? claudeModel
                : llmProvider === 'gemini'
                  ? geminiModel
                  : llmProvider === 'openai'
                    ? openaiModel
                    : ollamaModel === 'custom'
                      ? customOllamaModel
                      : ollamaModel
            }
            onProviderChange={provider => {
              if (provider === 'anthropic') setLlmProvider('claude');
              else if (provider === 'google') setLlmProvider('gemini');
              else if (provider === 'openai') setLlmProvider('openai');
              else setLlmProvider('ollama');
            }}
            onModelChange={model => {
              if (llmProvider === 'claude') setClaudeModel(model);
              else if (llmProvider === 'gemini') setGeminiModel(model);
              else if (llmProvider === 'openai') setOpenaiModel(model);
              else {
                if (AVAILABLE_MODELS.ollama.some(m => m.value === model)) {
                  setOllamaModel(model);
                } else {
                  setOllamaModel('custom');
                  setCustomOllamaModel(model);
                }
              }
            }}
          />
        </div>

        {/* STT (Speech-to-Text) Settings */}
        <div className="settings-section">
          <h3>Speech-to-Text (STT) Settings</h3>
          <p className="settings-description">
            Configure Whisper model for speech recognition. Larger models offer better accuracy but
            require more resources.
          </p>

          {isLoadingSttConfig ? (
            <p className="settings-description">Loading STT configuration...</p>
          ) : sttConfig ? (
            <>
              {/* CUDA Status */}
              <div className="stt-cuda-status">
                <h4 className="settings-subsection-title">GPU (CUDA) Status</h4>
                <div className="stt-cuda-info">
                  {sttConfig.cuda.available ? (
                    <>
                      <div className="stt-cuda-badge available">
                        <Zap size={16} />
                        <span>CUDA Available</span>
                      </div>
                      {sttConfig.cuda.device_name && (
                        <p className="settings-description">
                          Device: <strong>{sttConfig.cuda.device_name}</strong>
                        </p>
                      )}
                      {sttConfig.cuda.memory_total_gb !== null &&
                        sttConfig.cuda.memory_total_gb !== undefined && (
                          <p className="settings-description">
                            GPU Memory: {sttConfig.cuda.memory_free_gb?.toFixed(1)} GB free /{' '}
                            {sttConfig.cuda.memory_total_gb.toFixed(1)} GB total
                          </p>
                        )}
                    </>
                  ) : (
                    <div className="stt-cuda-badge unavailable">
                      <Cpu size={16} />
                      <span>CUDA Not Available (Using CPU)</span>
                    </div>
                  )}
                </div>
              </div>

              {/* Model Selection */}
              <h4 className="settings-subsection-title">Whisper Model</h4>
              <p className="settings-description">
                Current model: <strong>{sttConfig.current_model}</strong>
              </p>
              <p className="settings-description">
                <strong>Recommended models:</strong>
                <br />• <strong>large-v3</strong>: Best accuracy (requires ~10GB GPU memory)
                <br />• <strong>turbo</strong>: Fast with high accuracy (requires ~10GB GPU memory)
                <br />• <strong>medium</strong>: Good accuracy, moderate resources (~5GB GPU memory)
                <br />• <strong>base</strong>: Balanced accuracy/speed (~1GB, works on CPU)
                <br />• <strong>tiny</strong>: Fastest, least accurate (~1GB, works on CPU)
              </p>
              <select
                value={sttConfig.current_model}
                onChange={async e => {
                  const newModel = e.target.value;
                  if (newModel === sttConfig.current_model) return;

                  setIsSwitchingModel(true);
                  setModelSwitchProgress('Initiating model switch...');

                  try {
                    // Start the model switch (returns immediately)
                    const result = await speechService.updateSttModel(newModel);
                    const action = result.action || 'switching'; // 'switching' or 'downloading'

                    // Update progress message based on action
                    if (action === 'downloading') {
                      setModelSwitchProgress(
                        `Downloading model ${newModel}... (this may take a few minutes)`
                      );
                    } else {
                      setModelSwitchProgress(`Switching to model ${newModel}...`);
                    }

                    toast.success(result.message);

                    // Poll for completion
                    const pollInterval = setInterval(async () => {
                      try {
                        // Check switch status
                        const status = await speechService.getSttSwitchStatus();

                        if (status.status === 'idle') {
                          clearInterval(pollInterval);

                          if (status.error) {
                            setModelSwitchProgress('Model switch failed');
                            toast.error(`Failed to switch model: ${status.error}`);
                            setIsSwitchingModel(false);
                            setModelSwitchProgress('');
                            await loadSttConfig();
                            return;
                          }

                          // Check if model actually changed
                          const config = await speechService.getSttConfig();
                          if (config.current_model === newModel) {
                            setModelSwitchProgress('Model loaded successfully!');
                            setTimeout(() => {
                              setIsSwitchingModel(false);
                              setModelSwitchProgress('');
                            }, 1000);
                          } else {
                            // Still switching, keep polling
                            return;
                          }

                          await loadSttConfig();
                        } else if (status.status === 'downloading') {
                          setModelSwitchProgress(
                            `Downloading model ${newModel}... (this may take a few minutes)`
                          );
                        } else if (status.status === 'switching') {
                          setModelSwitchProgress(`Switching to model ${newModel}...`);
                        }
                      } catch (error) {
                        clearInterval(pollInterval);
                        setIsSwitchingModel(false);
                        setModelSwitchProgress('');
                        console.error('Failed to check switch status:', error);
                      }
                    }, 1000); // Poll every second

                    // Set a maximum timeout (5 minutes for downloads)
                    setTimeout(() => {
                      clearInterval(pollInterval);
                      if (isSwitchingModel) {
                        setIsSwitchingModel(false);
                        setModelSwitchProgress('');
                        toast.error('Model switch timed out. Check server logs for details.');
                      }
                    }, 300000); // 5 minutes
                  } catch (error) {
                    console.error('Failed to update STT model:', error);
                    setIsSwitchingModel(false);
                    setModelSwitchProgress('');
                    toast.error('Failed to initiate model switch. Check server logs for details.');
                  }
                }}
                className="settings-select"
                disabled={isLoadingSttConfig || isSwitchingModel}
              >
                {sttConfig.available_models.map(model => (
                  <option key={model} value={model}>
                    {model}
                  </option>
                ))}
              </select>
              {isSwitchingModel && (
                <div className="stt-model-switch-progress" style={{ marginTop: '1rem' }}>
                  <div className="stt-progress-spinner"></div>
                  <p className="settings-description" style={{ margin: '0.5rem 0 0 0' }}>
                    {modelSwitchProgress || 'Switching model...'}
                  </p>
                  <p
                    className="settings-description"
                    style={{ fontSize: '0.8rem', color: '#6b7280' }}
                  >
                    This may take a few minutes if the model needs to be downloaded. Progress is
                    shown in the server console.
                  </p>
                </div>
              )}
              <p
                className="settings-description"
                style={{ marginTop: '0.5rem', fontSize: '0.875rem' }}
              >
                <strong>Note:</strong> Model changes take effect immediately. The model will be
                automatically downloaded if not already cached. To persist the model choice across
                server restarts, update the <code>WHISPER_MODEL</code> environment variable or{' '}
                <code>.env</code> file.
              </p>
            </>
          ) : (
            <p className="settings-description" style={{ color: '#ef4444' }}>
              Failed to load STT configuration. Make sure the backend is running.
            </p>
          )}
        </div>

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
