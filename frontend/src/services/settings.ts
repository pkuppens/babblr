import { encrypt, decrypt } from '../utils/encryption';
import { detectUserTimezone, detectTimeFormat, type TimeFormat } from '../utils/dateTime';
import type { NativeLanguage } from '../types';

const SETTINGS_KEYS = {
  ANTHROPIC_API_KEY: 'babblr_anthropic_api_key',
  GOOGLE_API_KEY: 'babblr_google_api_key',
  LLM_PROVIDER: 'babblr_llm_provider',
  OLLAMA_MODEL: 'babblr_ollama_model',
  CLAUDE_MODEL: 'babblr_claude_model',
  GEMINI_MODEL: 'babblr_gemini_model',
  TIMEZONE: 'babblr_timezone',
  TIME_FORMAT: 'babblr_time_format',
  NATIVE_LANGUAGE: 'babblr_native_language',
};

// Available models per provider
export const AVAILABLE_MODELS = {
  ollama: [
    { value: 'llama3.2:latest', label: 'Llama 3.2 (Default)' },
    { value: 'llama3.1:latest', label: 'Llama 3.1' },
    { value: 'mistral:latest', label: 'Mistral' },
    { value: 'mixtral:latest', label: 'Mixtral' },
    { value: 'codellama:latest', label: 'Code Llama' },
    { value: 'gemma2:latest', label: 'Gemma 2' },
    { value: 'phi3:latest', label: 'Phi-3' },
    { value: 'qwen2:latest', label: 'Qwen 2' },
  ],
  claude: [
    { value: 'claude-sonnet-4-20250514', label: 'Claude Sonnet 4 (Latest)' },
    { value: 'claude-3-5-sonnet-20241022', label: 'Claude 3.5 Sonnet' },
    { value: 'claude-3-opus-20240229', label: 'Claude 3 Opus' },
    { value: 'claude-3-haiku-20240307', label: 'Claude 3 Haiku (Fast)' },
  ],
  gemini: [
    { value: 'gemini-1.5-pro', label: 'Gemini 1.5 Pro (Default)' },
    { value: 'gemini-1.5-flash', label: 'Gemini 1.5 Flash (Fast)' },
    { value: 'gemini-pro', label: 'Gemini Pro' },
  ],
};

export const DEFAULT_MODELS = {
  ollama: 'llama3.2:latest',
  claude: 'claude-sonnet-4-20250514',
  gemini: 'gemini-1.5-pro',
};

export type LLMProvider = 'ollama' | 'claude' | 'gemini' | 'mock';

export interface AppSettings {
  llmProvider: LLMProvider;
  anthropicApiKey?: string;
  googleApiKey?: string;
  ollamaModel: string;
  claudeModel: string;
  geminiModel: string;
  timezone: string;
  timeFormat: TimeFormat;
  nativeLanguage: NativeLanguage;
}

export type { TimeFormat };

/**
 * Settings service for managing encrypted API keys and app configuration
 */
class SettingsService {
  /**
   * Save API key with encryption
   */
  async saveApiKey(provider: 'anthropic' | 'google', apiKey: string): Promise<void> {
    try {
      const encrypted = await encrypt(apiKey);
      const key =
        provider === 'anthropic' ? SETTINGS_KEYS.ANTHROPIC_API_KEY : SETTINGS_KEYS.GOOGLE_API_KEY;
      localStorage.setItem(key, encrypted);
    } catch (error) {
      console.error(`Failed to save ${provider} API key:`, error);
      throw new Error(
        `Failed to save API key: ${error instanceof Error ? error.message : 'Unknown error'}`
      );
    }
  }

  /**
   * Load API key with decryption
   */
  async loadApiKey(provider: 'anthropic' | 'google'): Promise<string | null> {
    try {
      const key =
        provider === 'anthropic' ? SETTINGS_KEYS.ANTHROPIC_API_KEY : SETTINGS_KEYS.GOOGLE_API_KEY;
      const encrypted = localStorage.getItem(key);

      if (!encrypted) {
        return null;
      }

      return await decrypt(encrypted);
    } catch (error) {
      console.error(`Failed to load ${provider} API key:`, error);
      // If decryption fails, remove the corrupted data
      this.removeApiKey(provider);
      return null;
    }
  }

  /**
   * Remove API key from storage
   */
  removeApiKey(provider: 'anthropic' | 'google'): void {
    const key =
      provider === 'anthropic' ? SETTINGS_KEYS.ANTHROPIC_API_KEY : SETTINGS_KEYS.GOOGLE_API_KEY;
    localStorage.removeItem(key);
  }

  /**
   * Save LLM provider preference
   */
  saveLLMProvider(provider: LLMProvider): void {
    localStorage.setItem(SETTINGS_KEYS.LLM_PROVIDER, provider);
  }

  /**
   * Load LLM provider preference
   */
  loadLLMProvider(): LLMProvider {
    const provider = localStorage.getItem(SETTINGS_KEYS.LLM_PROVIDER);
    if (provider && ['ollama', 'claude', 'gemini', 'mock'].includes(provider)) {
      return provider as LLMProvider;
    }
    return 'ollama'; // Default to ollama
  }

  /**
   * Save model for a specific provider
   */
  saveModel(provider: 'ollama' | 'claude' | 'gemini', model: string): void {
    const key =
      provider === 'ollama'
        ? SETTINGS_KEYS.OLLAMA_MODEL
        : provider === 'claude'
          ? SETTINGS_KEYS.CLAUDE_MODEL
          : SETTINGS_KEYS.GEMINI_MODEL;
    localStorage.setItem(key, model);
  }

  /**
   * Load model for a specific provider
   */
  loadModel(provider: 'ollama' | 'claude' | 'gemini'): string {
    const key =
      provider === 'ollama'
        ? SETTINGS_KEYS.OLLAMA_MODEL
        : provider === 'claude'
          ? SETTINGS_KEYS.CLAUDE_MODEL
          : SETTINGS_KEYS.GEMINI_MODEL;
    return localStorage.getItem(key) || DEFAULT_MODELS[provider];
  }

  /**
   * Save timezone preference
   */
  saveTimezone(timezone: string): void {
    localStorage.setItem(SETTINGS_KEYS.TIMEZONE, timezone);
  }

  /**
   * Load timezone preference (defaults to detected or Europe/Amsterdam)
   */
  loadTimezone(): string {
    const stored = localStorage.getItem(SETTINGS_KEYS.TIMEZONE);
    if (stored) return stored;
    // Auto-detect from browser
    return detectUserTimezone();
  }

  /**
   * Save time format preference
   */
  saveTimeFormat(format: TimeFormat): void {
    localStorage.setItem(SETTINGS_KEYS.TIME_FORMAT, format);
  }

  /**
   * Load time format preference (defaults to detected or 24h)
   */
  loadTimeFormat(): TimeFormat {
    const stored = localStorage.getItem(SETTINGS_KEYS.TIME_FORMAT);
    if (stored === '24h' || stored === '12h') return stored;
    // Auto-detect from browser locale
    return detectTimeFormat();
  }

  /**
   * Save native/reference language preference
   */
  saveNativeLanguage(language: NativeLanguage): void {
    localStorage.setItem(SETTINGS_KEYS.NATIVE_LANGUAGE, language);
  }

  /**
   * Load native/reference language preference (defaults to 'english' if not set)
   */
  loadNativeLanguage(): NativeLanguage {
    const stored = localStorage.getItem(SETTINGS_KEYS.NATIVE_LANGUAGE);
    if (stored && ['spanish', 'italian', 'german', 'french', 'dutch', 'english'].includes(stored)) {
      return stored as NativeLanguage;
    }
    // Default to English as the most common reference language
    return 'english';
  }

  /**
   * Load all settings
   */
  async loadSettings(): Promise<AppSettings> {
    const [anthropicApiKey, googleApiKey] = await Promise.all([
      this.loadApiKey('anthropic'),
      this.loadApiKey('google'),
    ]);

    return {
      llmProvider: this.loadLLMProvider(),
      anthropicApiKey: anthropicApiKey || undefined,
      googleApiKey: googleApiKey || undefined,
      ollamaModel: this.loadModel('ollama'),
      claudeModel: this.loadModel('claude'),
      geminiModel: this.loadModel('gemini'),
      timezone: this.loadTimezone(),
      timeFormat: this.loadTimeFormat(),
      nativeLanguage: this.loadNativeLanguage(),
    };
  }

  /**
   * Clear all settings
   */
  clearAllSettings(): void {
    localStorage.removeItem(SETTINGS_KEYS.ANTHROPIC_API_KEY);
    localStorage.removeItem(SETTINGS_KEYS.GOOGLE_API_KEY);
    localStorage.removeItem(SETTINGS_KEYS.LLM_PROVIDER);
    localStorage.removeItem(SETTINGS_KEYS.OLLAMA_MODEL);
    localStorage.removeItem(SETTINGS_KEYS.CLAUDE_MODEL);
    localStorage.removeItem(SETTINGS_KEYS.GEMINI_MODEL);
    localStorage.removeItem(SETTINGS_KEYS.TIMEZONE);
    localStorage.removeItem(SETTINGS_KEYS.TIME_FORMAT);
    localStorage.removeItem(SETTINGS_KEYS.NATIVE_LANGUAGE);
  }
}

export const settingsService = new SettingsService();
