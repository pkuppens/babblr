import { normalizeToCefrLevel } from './cefr';

type StarterTier = 'beginner' | 'intermediate' | 'advanced';

function getTier(level: string): StarterTier {
  const normalized = normalizeToCefrLevel(level);
  if (!normalized) return 'beginner';

  if (normalized === 'A1' || normalized === 'A2') return 'beginner';
  if (normalized === 'B1' || normalized === 'B2') return 'intermediate';
  return 'advanced';
}

const STARTER_MESSAGES: Record<string, Record<StarterTier, string>> = {
  spanish: {
    beginner: '¡Hola! Soy tu tutor de español.\n¿Cómo te llamas? ¿De dónde eres?',
    intermediate: '¡Hola! Soy tu tutor de español.\nCuéntame sobre tu día. ¿Qué has hecho hoy?',
    advanced:
      'Hola. Soy tu tutor de español.\nHablemos de un tema actual: ¿qué opinas sobre el impacto de la tecnología en la vida diaria?',
  },
  italian: {
    beginner: 'Ciao! Sono il tuo tutor di italiano.\nCome ti chiami? Di dove sei?',
    intermediate:
      'Ciao! Sono il tuo tutor di italiano.\nRaccontami la tua giornata. Che cosa hai fatto oggi?',
    advanced:
      "Ciao. Sono il tuo tutor di italiano.\nDiscutiamo un tema attuale: qual è, secondo te, l'impatto della tecnologia sulla vita quotidiana?",
  },
  german: {
    beginner: 'Hallo! Ich bin dein Deutsch-Tutor.\nWie heißt du? Woher kommst du?',
    intermediate:
      'Hallo! Ich bin dein Deutsch-Tutor.\nErzähl mir von deinem Tag. Was hast du heute gemacht?',
    advanced:
      'Hallo. Ich bin dein Deutsch-Tutor.\nLass uns über ein aktuelles Thema sprechen: Wie beeinflusst Technologie unser tägliches Leben?',
  },
  french: {
    beginner: "Bonjour ! Je suis ton tuteur de français.\nComment t'appelles-tu ? D'où viens-tu ?",
    intermediate:
      "Bonjour ! Je suis ton tuteur de français.\nParle-moi de ta journée. Qu'as-tu fait aujourd'hui ?",
    advanced:
      "Bonjour. Je suis ton tuteur de français.\nDiscutons d'un sujet actuel : quel est, selon toi, l'impact de la technologie sur la vie quotidienne ?",
  },
  dutch: {
    beginner: 'Hoi! Ik ben je docent Nederlands.\nHoe heet je? Waar kom je vandaan?',
    intermediate:
      'Hoi! Ik ben je docent Nederlands.\nVertel me over je dag. Wat heb je vandaag gedaan?',
    advanced:
      'Hoi. Ik ben je docent Nederlands.\nLaten we een actueel onderwerp bespreken: wat vind jij van de invloed van technologie op het dagelijks leven?',
  },
  english: {
    beginner: 'Hello! I am your English tutor.\nWhat is your name? Where are you from?',
    intermediate:
      'Hello! I am your English tutor.\nTell me about your day. What have you done today?',
    advanced:
      'Hello. I am your English tutor.\nLet us discuss a current topic: what do you think about the impact of technology on daily life?',
  },
};

export function getStarterMessage(language: string, level: string): string {
  const key = (language ?? '').trim().toLowerCase();
  const tier = getTier(level);
  const perLanguage = STARTER_MESSAGES[key];

  if (perLanguage) return perLanguage[tier];

  // Fallback: keep it simple and safe if a new language is added later.
  return 'Hello! I am your language tutor.\nIntroduce yourself and ask me a question.';
}
