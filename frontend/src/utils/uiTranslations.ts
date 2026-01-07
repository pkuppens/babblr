/**
 * UI translations for study language elements.
 * These translations are used to display UI elements in the target language
 * to immerse the student in the language they're learning.
 */

interface UIStrings {
  placeholder: string;
  send: string;
  originalStt: string;
  correctedStt: string;
  listenNative: string;
}

const UI_TRANSLATIONS: Record<string, UIStrings> = {
  spanish: {
    placeholder: 'Escribe tu mensaje...',
    send: 'Enviar',
    originalStt: 'Lo que escuché',
    correctedStt: 'Corrección',
    listenNative: 'Escuchar',
  },
  italian: {
    placeholder: 'Scrivi il tuo messaggio...',
    send: 'Invia',
    originalStt: 'Quello che ho sentito',
    correctedStt: 'Correzione',
    listenNative: 'Ascolta',
  },
  german: {
    placeholder: 'Schreibe deine Nachricht...',
    send: 'Senden',
    originalStt: 'Was ich gehört habe',
    correctedStt: 'Korrektur',
    listenNative: 'Anhören',
  },
  french: {
    placeholder: 'Écris ton message...',
    send: 'Envoyer',
    originalStt: "Ce que j'ai entendu",
    correctedStt: 'Correction',
    listenNative: 'Écouter',
  },
  dutch: {
    placeholder: 'Typ je bericht...',
    send: 'Verstuur',
    originalStt: 'Wat ik hoorde',
    correctedStt: 'Correctie',
    listenNative: 'Luister',
  },
};

const DEFAULT_STRINGS: UIStrings = {
  placeholder: 'Type your message...',
  send: 'Send',
  originalStt: 'What I heard',
  correctedStt: 'Correction',
  listenNative: 'Listen',
};

export function getUIStrings(language: string): UIStrings {
  const key = (language ?? '').trim().toLowerCase();
  return UI_TRANSLATIONS[key] ?? DEFAULT_STRINGS;
}
