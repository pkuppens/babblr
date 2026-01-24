import { api } from './api';
import type { Language, ProgressSummary } from '../types';
import { getLanguageCode } from '../utils/language';

export const progressService = {
  /**
   * Get progress summary for a specific language.
   *
   * @param language - Language type (e.g., 'spanish', 'french', 'german')
   * @returns ProgressSummary with vocabulary, grammar, and assessment stats
   */
  async getProgressSummary(language: Language): Promise<ProgressSummary> {
    const languageCode = getLanguageCode(language);
    const response = await api.get(`/progress/summary?language=${languageCode}`);
    return response.data;
  },
};
