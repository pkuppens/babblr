import { encrypt, decrypt } from '../utils/encryption';

const SETTINGS_KEYS = {
  ANTHROPIC_API_KEY: 'babblr_anthropic_api_key',
  GOOGLE_API_KEY: 'babblr_google_api_key',
  LLM_PROVIDER: 'babblr_llm_provider',
};

export type LLMProvider = 'ollama' | 'claude' | 'gemini' | 'mock';

export interface AppSettings {
  llmProvider: LLMProvider;
  anthropicApiKey?: string;
  googleApiKey?: string;
}

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
    };
  }

  /**
   * Clear all settings
   */
  clearAllSettings(): void {
    localStorage.removeItem(SETTINGS_KEYS.ANTHROPIC_API_KEY);
    localStorage.removeItem(SETTINGS_KEYS.GOOGLE_API_KEY);
    localStorage.removeItem(SETTINGS_KEYS.LLM_PROVIDER);
  }
}

export const settingsService = new SettingsService();
