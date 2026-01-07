import { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import { sanitizeTtsText } from '../utils/ttsSanitizer';

export interface TTSConfig {
  language: string;
  rate: number; // 0.5 - 1.5
  autoPlay: boolean;
  voiceURI?: string;
}

export interface UseTTS {
  speak: (text: string, config: TTSConfig) => void;
  stop: () => void;
  pause: () => void;
  resume: () => void;
  isSpeaking: boolean;
  isPaused: boolean;
  supported: boolean;
  voices: SpeechSynthesisVoice[];
  lastError: string | null;
}

function clamp(value: number, min: number, max: number): number {
  return Math.min(max, Math.max(min, value));
}

function languageToBCP47(language: string): string {
  const key = language.trim().toLowerCase();
  switch (key) {
    case 'spanish':
      return 'es-ES';
    case 'italian':
      return 'it-IT';
    case 'german':
      return 'de-DE';
    case 'french':
      return 'fr-FR';
    case 'dutch':
      return 'nl-NL';
    case 'english':
      return 'en-US';
    default:
      // If user passed something like "es" or "es-ES", keep it.
      return language;
  }
}

function getBaseLanguageTag(tag: string): string {
  return tag.split('-')[0]?.toLowerCase() ?? '';
}

function rankVoice(voice: SpeechSynthesisVoice): number {
  // Prefer local voices (usually higher quality and faster).
  // Prefer non-default voices when multiple are available.
  // Keep it simple to avoid platform-specific heuristics.
  let score = 0;
  if (voice.localService) score += 10;
  if (!voice.default) score += 1;
  return score;
}

function selectVoicesForLanguage(
  allVoices: SpeechSynthesisVoice[],
  targetBCP47: string
): SpeechSynthesisVoice[] {
  const base = getBaseLanguageTag(targetBCP47);
  if (!base) return [];

  const matches = allVoices.filter((v) => getBaseLanguageTag(v.lang) === base);
  return matches.sort((a, b) => rankVoice(b) - rankVoice(a));
}

export function useTTS(): UseTTS {
  const synth = useMemo(() => {
    if (typeof window === 'undefined') return null;
    return 'speechSynthesis' in window ? window.speechSynthesis : null;
  }, []);
  const [supported, setSupported] = useState<boolean>(synth !== null);
  const [voices, setVoices] = useState<SpeechSynthesisVoice[]>([]);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [isPaused, setIsPaused] = useState(false);
  const [lastError, setLastError] = useState<string | null>(null);

  const activeUtteranceRef = useRef<SpeechSynthesisUtterance | null>(null);

  useEffect(() => {
    if (!synth) {
      setSupported(false);
      setVoices([]);
      return;
    }

    const load = () => {
      try {
        const list = synth.getVoices();
        setVoices(list);
      } catch (e) {
        setVoices([]);
      }
    };

    load();
    synth.addEventListener('voiceschanged', load);

    return () => {
      synth.removeEventListener('voiceschanged', load);
    };
  }, [synth]);

  const stop = useCallback(() => {
    if (!supported) return;
    try {
      synth?.cancel();
    } finally {
      activeUtteranceRef.current = null;
      setIsSpeaking(false);
      setIsPaused(false);
    }
  }, [supported, synth]);

  const pause = useCallback(() => {
    if (!supported) return;
    if (!synth || !synth.speaking || synth.paused) return;
    synth.pause();
    setIsPaused(true);
  }, [supported, synth]);

  const resume = useCallback(() => {
    if (!supported) return;
    if (!synth || !synth.paused) return;
    synth.resume();
    setIsPaused(false);
  }, [supported, synth]);

  const speak = useCallback(
    (text: string, config: TTSConfig) => {
      if (!supported) {
        setLastError('Text-to-speech is not supported in this environment.');
        return;
      }
      if (!synth) {
        setLastError('Text-to-speech is not available.');
        return;
      }

      const cleaned = sanitizeTtsText(text);
      if (!cleaned) return;

      setLastError(null);

      // Cancel any previous utterance to prevent overlap.
      synth.cancel();

      const utterance = new SpeechSynthesisUtterance(cleaned);
      utterance.rate = clamp(Number(config.rate) || 1, 0.5, 1.5);
      utterance.lang = languageToBCP47(config.language);

      const candidates = selectVoicesForLanguage(voices, utterance.lang);
      const preferred = config.voiceURI
        ? voices.find((v) => v.voiceURI === config.voiceURI)
        : undefined;
      utterance.voice = preferred ?? candidates[0] ?? null;

      utterance.onstart = () => {
        setIsSpeaking(true);
        setIsPaused(false);
      };
      utterance.onend = () => {
        setIsSpeaking(false);
        setIsPaused(false);
        activeUtteranceRef.current = null;
      };
      utterance.onerror = (event) => {
        setIsSpeaking(false);
        setIsPaused(false);
        activeUtteranceRef.current = null;
        setLastError(event.error ? `TTS error: ${event.error}` : 'TTS error');
      };
      utterance.onpause = () => setIsPaused(true);
      utterance.onresume = () => setIsPaused(false);

      activeUtteranceRef.current = utterance;
      synth.speak(utterance);
    },
    [supported, synth, voices]
  );

  return {
    speak,
    stop,
    pause,
    resume,
    isSpeaking,
    isPaused,
    supported,
    voices,
    lastError,
  };
}


