import { useState, useEffect } from 'react';
import TabBar from './components/TabBar';
import UserDisplay from './components/UserDisplay';
import Settings from './components/Settings';
import BackendErrorIndicator from './components/BackendErrorIndicator';
import HomeScreen from './screens/HomeScreen';
import VocabularyScreen from './screens/VocabularyScreen';
import GrammarScreen from './screens/GrammarScreen';
import ConversationsScreen from './screens/ConversationsScreen';
import AssessmentsScreen from './screens/AssessmentsScreen';
import ProgressScreen from './screens/ProgressScreen';
import ConfigurationScreen from './screens/ConfigurationScreen';
import { conversationService, chatService } from './services/api';
import { settingsService, type TimeFormat } from './services/settings';
import { useBackendErrorContext } from './contexts/BackendErrorContext';
import {
  registerPersistentErrorSetter,
  unregisterPersistentErrorSetter,
} from './utils/errorHandler';
import type { Conversation, Language, DifficultyLevel, TabKey, Topic } from './types';
import './App.css';

function App() {
  // Backend error state management
  const { errorState, setError } = useBackendErrorContext();

  // Register persistent error setter so errorHandler can update error state
  useEffect(() => {
    registerPersistentErrorSetter(setError);
    return () => {
      unregisterPersistentErrorSetter();
    };
  }, [setError]);

  // Tab navigation state
  const [activeTab, setActiveTab] = useState<TabKey>('home');

  // Conversation state (preserved across tab switches)
  const [currentConversation, setCurrentConversation] = useState<Conversation | null>(null);
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [showTopicSelector, setShowTopicSelector] = useState(false);

  // Language/level selection (persisted in localStorage)
  const loadLanguageSelection = (): { language: Language; difficulty: DifficultyLevel } => {
    try {
      const stored = localStorage.getItem('babblr_language_selection');
      if (stored) {
        const parsed = JSON.parse(stored);
        if (parsed.language && parsed.difficulty) {
          return { language: parsed.language, difficulty: parsed.difficulty };
        }
      }
    } catch (error) {
      console.error('Failed to load language selection:', error);
    }
    // Defaults
    return { language: 'spanish', difficulty: 'A1' };
  };

  const saveLanguageSelection = (language: Language, difficulty: DifficultyLevel) => {
    try {
      localStorage.setItem('babblr_language_selection', JSON.stringify({ language, difficulty }));
    } catch (error) {
      console.error('Failed to save language selection:', error);
    }
  };

  const initialSelection = loadLanguageSelection();
  const [selectedLanguage, setSelectedLanguage] = useState<Language | null>(
    initialSelection.language
  );
  const [selectedDifficulty, setSelectedDifficulty] = useState<DifficultyLevel | null>(
    initialSelection.difficulty
  );

  // Save to localStorage whenever selection changes
  useEffect(() => {
    saveLanguageSelection(selectedLanguage, selectedDifficulty);
  }, [selectedLanguage, selectedDifficulty]);

  // Settings state
  const [showSettings, setShowSettings] = useState(false);
  const [timezone, setTimezone] = useState<string>('UTC');
  const [timeFormat, setTimeFormat] = useState<TimeFormat>('24h');

  // User state (for now, just 'dev' user without password)
  const [currentUser] = useState({ username: 'dev', isLoggedIn: true });

  const loadConversations = async () => {
    try {
      const convs = await conversationService.list();
      setConversations(convs);
    } catch (error) {
      console.error('Failed to load conversations:', error);
    }
  };

  const loadDisplaySettings = () => {
    setTimezone(settingsService.loadTimezone());
    setTimeFormat(settingsService.loadTimeFormat());
  };

  useEffect(() => {
    loadConversations();
    loadDisplaySettings();
  }, []);

  const handleLanguageSelectionChange = (language: Language, difficulty: DifficultyLevel) => {
    // Update selection immediately (persists across tabs)
    setSelectedLanguage(language);
    setSelectedDifficulty(difficulty);
  };

  const handleStartNewConversation = async (language: Language, difficulty: DifficultyLevel) => {
    // Ensure selection is updated (should already be set, but ensure consistency)
    setSelectedLanguage(language);
    setSelectedDifficulty(difficulty);
    setShowTopicSelector(true);
    setActiveTab('conversations');
  };

  const handleTopicSelected = async (topic: Topic) => {
    // Create the conversation with topic and generate initial tutor message
    if (!selectedLanguage || !selectedDifficulty) return;

    try {
      // Create conversation with topic_id
      const conversation = await conversationService.create(
        selectedLanguage,
        selectedDifficulty,
        topic.id
      );
      setCurrentConversation(conversation);
      setShowTopicSelector(false);

      // Generate initial tutor message based on topic
      await chatService.generateInitialMessage(
        conversation.id,
        selectedLanguage,
        selectedDifficulty,
        topic.id
      );

      // Reload conversation to get updated state
      const updatedConversation = await conversationService.get(conversation.id);
      setCurrentConversation(updatedConversation);

      await loadConversations();
    } catch (error) {
      console.error('Failed to create conversation with topic:', error);
      // The error handler in api.ts will show a toast notification to the user
    }
  };

  const handleSelectConversation = (conversation: Conversation | null) => {
    setCurrentConversation(conversation);
    setShowTopicSelector(false);
    // Switch to conversations tab when a conversation is selected
    if (conversation) {
      setActiveTab('conversations');
    }
  };

  const handleTabChange = (tab: TabKey) => {
    setActiveTab(tab);
  };

  const handleCloseSettings = () => {
    setShowSettings(false);
    loadDisplaySettings(); // Reload settings when modal closes
  };

  const renderActiveScreen = () => {
    switch (activeTab) {
      case 'home':
        return (
          <HomeScreen
            selectedLanguage={selectedLanguage}
            selectedDifficulty={selectedDifficulty}
            onLanguageSelectionChange={handleLanguageSelectionChange}
            onStartNewConversation={handleStartNewConversation}
            conversations={conversations}
            onSelectConversation={handleSelectConversation}
            onDeleteConversation={async id => {
              await conversationService.delete(id);
              await loadConversations();
              // If the deleted conversation was active, clear it
              if (currentConversation?.id === id) {
                setCurrentConversation(null);
              }
            }}
            timezone={timezone}
            timeFormat={timeFormat}
          />
        );
      case 'vocabulary':
        return (
          <VocabularyScreen
            selectedLanguage={selectedLanguage}
            selectedDifficulty={selectedDifficulty}
          />
        );
      case 'grammar':
        return (
          <GrammarScreen
            selectedLanguage={selectedLanguage}
            selectedDifficulty={selectedDifficulty}
          />
        );
      case 'conversations':
        return (
          <ConversationsScreen
            currentConversation={currentConversation}
            selectedLanguage={selectedLanguage}
            selectedDifficulty={selectedDifficulty}
            showTopicSelector={showTopicSelector}
            onTopicSelected={handleTopicSelected}
            onSelectConversation={handleSelectConversation}
            timezone={timezone}
            timeFormat={timeFormat}
          />
        );
      case 'assessments':
        return (
          <AssessmentsScreen
            selectedLanguage={selectedLanguage}
            selectedDifficulty={selectedDifficulty}
            onLevelApplied={(language, level) => {
              // Update difficulty level when applied from assessment
              if (language === selectedLanguage) {
                setSelectedDifficulty(level);
              }
            }}
            timezone={timezone}
            timeFormat={timeFormat}
          />
        );
      case 'progress':
        return <ProgressScreen selectedLanguage={selectedLanguage} />;
      case 'configuration':
        return <ConfigurationScreen isOpen={showSettings} onClose={handleCloseSettings} />;
      default:
        return null;
    }
  };

  return (
    <div className="app">
      <header className="app-header">
        <div className="app-header-left">
          <h1
            onClick={() => {
              setActiveTab('home');
              setCurrentConversation(null);
              setSelectedLanguage(null);
              setSelectedDifficulty(null);
              setShowTopicSelector(false);
            }}
            style={{ cursor: 'pointer' }}
          >
            🗣️ Babblr
          </h1>
        </div>
        <p className="app-subtitle">Learn languages naturally through conversation</p>
        <div className="app-header-right">
          <BackendErrorIndicator errorState={errorState} />
          <UserDisplay username={currentUser.username} isLoggedIn={currentUser.isLoggedIn} />
        </div>
      </header>

      <TabBar activeTab={activeTab} onTabChange={handleTabChange} language={selectedLanguage} />

      <main className="app-main" role="main">
        {renderActiveScreen()}
      </main>

      {/* Settings modal (shown when opened from header, not when on configuration tab) */}
      {showSettings && activeTab !== 'configuration' && (
        <Settings isOpen={showSettings} onClose={handleCloseSettings} />
      )}
    </div>
  );
}

export default App;
