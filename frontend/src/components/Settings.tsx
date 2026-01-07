import { useState, useEffect } from 'react';
import { X, Eye, EyeOff, CheckCircle, AlertCircle } from 'lucide-react';
import { settingsService, type LLMProvider } from '../services/settings';
import { maskApiKey } from '../utils/encryption';
import toast from 'react-hot-toast';
import './Settings.css';

interface SettingsProps {
  isOpen: boolean;
  onClose: () => void;
}

// API key validation constants
const ANTHROPIC_KEY_PREFIX = 'sk-ant-api03-';
const GOOGLE_KEY_PREFIX = 'AI';

function Settings({ isOpen, onClose }: SettingsProps) {
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

  useEffect(() => {
    if (isOpen) {
      loadSettings();
    }
  }, [isOpen]);

  const loadSettings = async () => {
    try {
      const settings = await settingsService.loadSettings();
      setLlmProvider(settings.llmProvider);

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

  return (
    <div className="settings-overlay">
      <div className="settings-modal">
        <div className="settings-header">
          <h2>Settings</h2>
          <button className="settings-close" onClick={onClose} aria-label="Close settings">
            <X size={24} />
          </button>
        </div>

        <div className="settings-content">
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
            </div>
          )}
        </div>

        <div className="settings-footer">
          <button onClick={onClose} className="settings-button settings-button-secondary">
            Cancel
          </button>
          <button
            onClick={handleSave}
            disabled={isSaving}
            className="settings-button settings-button-primary"
          >
            {isSaving ? 'Saving...' : 'Save Settings'}
          </button>
        </div>
      </div>
    </div>
  );
}

export default Settings;
