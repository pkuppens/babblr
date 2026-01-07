import type { DifficultyLevel } from '../types';

const CEFR_LEVELS: DifficultyLevel[] = ['A1', 'A2', 'B1', 'B2', 'C1', 'C2'];

const LEGACY_TO_CEFR: Record<string, DifficultyLevel> = {
  beginner: 'A1',
  intermediate: 'B1',
  advanced: 'C1',
};

const DEFAULT_TTS_RATE_BY_LEVEL: Record<DifficultyLevel, number> = {
  A1: 0.75,
  A2: 0.8,
  B1: 0.85,
  B2: 0.9,
  C1: 0.95,
  C2: 1.0,
};

export function normalizeToCefrLevel(level: string): DifficultyLevel | null {
  const trimmed = (level ?? '').trim();
  if (!trimmed) return null;

  const upper = trimmed.toUpperCase();
  if ((CEFR_LEVELS as string[]).includes(upper)) {
    return upper as DifficultyLevel;
  }

  const lower = trimmed.toLowerCase();
  if (lower in LEGACY_TO_CEFR) {
    return LEGACY_TO_CEFR[lower];
  }

  return null;
}

export function formatLevelLabel(level: string): string {
  const normalized = normalizeToCefrLevel(level);
  return normalized ?? level;
}

export function getDefaultTtsRateForLevel(level: string): number {
  const normalized = normalizeToCefrLevel(level);
  if (!normalized) return 1.0;
  return DEFAULT_TTS_RATE_BY_LEVEL[normalized] ?? 1.0;
}


