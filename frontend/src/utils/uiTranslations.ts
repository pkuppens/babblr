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
  // Navigation
  next: string;
  previous: string;
  exit: string;
  continue: string;
  // Lesson progress
  completed: string;
  of: string; // "2 of 8"
  lessonComplete: string;
  lessonCompleteMessage: string;
  // Tab names
  home: string;
  vocabulary: string;
  grammar: string;
  conversations: string;
  assessments: string;
  configuration: string;
  // Flashcard hints
  clickToReveal: string;
  clickToShowWord: string;
  example: string;
}

const UI_TRANSLATIONS: Record<string, UIStrings> = {
  spanish: {
    placeholder: 'Escribe tu mensaje...',
    send: 'Enviar',
    originalStt: 'Lo que escuché',
    correctedStt: 'Corrección',
    listenNative: 'Escuchar',
    next: 'Siguiente',
    previous: 'Anterior',
    exit: 'Salir',
    continue: 'Continuar',
    completed: 'completado',
    of: 'de',
    lessonComplete: '¡Lección completada!',
    lessonCompleteMessage: 'Has completado todos los {count} elementos de vocabulario.',
    home: 'Inicio',
    vocabulary: 'Vocabulario',
    grammar: 'Gramática',
    conversations: 'Conversaciones',
    assessments: 'Evaluaciones',
    configuration: 'Configuración',
    clickToReveal: 'Haz clic para ver la traducción',
    clickToShowWord: 'Haz clic para mostrar la palabra',
    example: 'Ejemplo',
  },
  italian: {
    placeholder: 'Scrivi il tuo messaggio...',
    send: 'Invia',
    originalStt: 'Quello che ho sentito',
    correctedStt: 'Correzione',
    listenNative: 'Ascolta',
    next: 'Avanti',
    previous: 'Indietro',
    exit: 'Esci',
    continue: 'Continua',
    completed: 'completato',
    of: 'di',
    lessonComplete: 'Lezione completata!',
    lessonCompleteMessage: 'Hai completato tutti i {count} elementi di vocabolario.',
    home: 'Home',
    vocabulary: 'Vocabolario',
    grammar: 'Grammatica',
    conversations: 'Conversazioni',
    assessments: 'Valutazioni',
    configuration: 'Configurazione',
    clickToReveal: 'Clicca per vedere la traduzione',
    clickToShowWord: 'Clicca per mostrare la parola',
    example: 'Esempio',
  },
  german: {
    placeholder: 'Schreibe deine Nachricht...',
    send: 'Senden',
    originalStt: 'Was ich gehört habe',
    correctedStt: 'Korrektur',
    listenNative: 'Anhören',
    next: 'Weiter',
    previous: 'Zurück',
    exit: 'Beenden',
    continue: 'Weiter',
    completed: 'abgeschlossen',
    of: 'von',
    lessonComplete: 'Lektion abgeschlossen!',
    lessonCompleteMessage: 'Du hast alle {count} Vokabeln abgeschlossen.',
    home: 'Startseite',
    vocabulary: 'Wortschatz',
    grammar: 'Grammatik',
    conversations: 'Gespräche',
    assessments: 'Bewertungen',
    configuration: 'Konfiguration',
    clickToReveal: 'Klicken, um die Übersetzung anzuzeigen',
    clickToShowWord: 'Klicken, um das Wort anzuzeigen',
    example: 'Beispiel',
  },
  french: {
    placeholder: 'Écris ton message...',
    send: 'Envoyer',
    originalStt: "Ce que j'ai entendu",
    correctedStt: 'Correction',
    listenNative: 'Écouter',
    next: 'Suivant',
    previous: 'Précédent',
    exit: 'Quitter',
    continue: 'Continuer',
    completed: 'terminé',
    of: 'sur',
    lessonComplete: 'Leçon terminée !',
    lessonCompleteMessage: 'Vous avez terminé tous les {count} éléments de vocabulaire.',
    home: 'Accueil',
    vocabulary: 'Vocabulaire',
    grammar: 'Grammaire',
    conversations: 'Conversations',
    assessments: 'Évaluations',
    configuration: 'Configuration',
    clickToReveal: 'Cliquer pour voir la traduction',
    clickToShowWord: 'Cliquer pour afficher le mot',
    example: 'Exemple',
  },
  dutch: {
    placeholder: 'Typ je bericht...',
    send: 'Verstuur',
    originalStt: 'Wat ik hoorde',
    correctedStt: 'Correctie',
    listenNative: 'Luister',
    next: 'Volgende',
    previous: 'Vorige',
    exit: 'Verlaat',
    continue: 'Doorgaan',
    completed: 'voltooid',
    of: 'van',
    lessonComplete: 'Les voltooid!',
    lessonCompleteMessage: 'Je hebt alle {count} vocabulaire-items voltooid.',
    home: 'Home',
    vocabulary: 'Woordenschat',
    grammar: 'Grammatica',
    conversations: 'Gesprekken',
    assessments: 'Beoordelingen',
    configuration: 'Configuratie',
    clickToReveal: 'Klik om de vertaling te zien',
    clickToShowWord: 'Klik om het woord te tonen',
    example: 'Voorbeeld',
  },
};

const DEFAULT_STRINGS: UIStrings = {
  placeholder: 'Type your message...',
  send: 'Send',
  originalStt: 'What I heard',
  correctedStt: 'Correction',
  listenNative: 'Listen',
  next: 'Next',
  previous: 'Previous',
  exit: 'Exit',
  continue: 'Continue',
  completed: 'completed',
  of: 'of',
  lessonComplete: 'Lesson Complete!',
  lessonCompleteMessage: "You've completed all {count} vocabulary items.",
  home: 'Home',
  vocabulary: 'Vocabulary',
  grammar: 'Grammar',
  conversations: 'Conversations',
  assessments: 'Assessments',
  configuration: 'Configuration',
  clickToReveal: 'Click to reveal translation',
  clickToShowWord: 'Click to show word',
  example: 'Example',
};

export function getUIStrings(language: string): UIStrings {
  const key = (language ?? '').trim().toLowerCase();
  return UI_TRANSLATIONS[key] ?? DEFAULT_STRINGS;
}
