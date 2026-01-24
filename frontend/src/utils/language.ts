import type { Language } from '../types';

/**
 * Convert Language type to display name
 */
export function getLanguageDisplayName(language: Language): string {
  const displayNames: Record<Language, string> = {
    spanish: 'Spanish',
    italian: 'Italian',
    german: 'German',
    french: 'French',
    dutch: 'Dutch',
    english: 'English',
  };
  return displayNames[language];
}

/**
 * Convert Language type to language code
 */
export function getLanguageCode(language: Language): string {
  const codes: Record<Language, string> = {
    spanish: 'es',
    italian: 'it',
    german: 'de',
    french: 'fr',
    dutch: 'nl',
    english: 'en',
  };
  return codes[language];
}
