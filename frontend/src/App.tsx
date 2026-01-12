import { useState, useEffect } from 'react';
import TabBar from './components/TabBar';
import HomeScreen from './screens/HomeScreen';
import VocabularyScreen from './screens/VocabularyScreen';
import GrammarScreen from './screens/GrammarScreen';
import ConversationsScreen from './screens/ConversationsScreen';
import AssessmentsScreen from './screens/AssessmentsScreen';
import ConfigurationScreen from './screens/ConfigurationScreen';
import { conversationService, chatService } from './services/api';
import { settingsService, type TimeFormat } from './services/settings';
import type { Conversation, Language, DifficultyLevel, TabKey } from './types';
import './App.css';

function App() {
  // Tab navigation state
  const [activeTab, setActiveTab] = useState<TabKey>('home');

  // Conversation state (preserved across tab switches)
  const [currentConversation, setCurrentConversation] = useState<Conversation | null>(null);
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [showTopicSelector, setShowTopicSelector] = useState(false);
  const [selectedLanguage, setSelectedLanguage] = useState<Language | null>(null);
  const [selectedDifficulty, setSelectedDifficulty] = useState<DifficultyLevel | null>(null);

  // Settings state
  const [showSettings, setShowSettings] = useState(false);
  const [timezone, setTimezone] = useState<string>('UTC');
  const [timeFormat, setTimeFormat] = useState<TimeFormat>('24h');

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

  const handleStartNewConversation = async (language: Language, difficulty: DifficultyLevel) => {
    // Store the selection and switch to conversations tab with topic selector
    setSelectedLanguage(language);
    setSelectedDifficulty(difficulty);
    setShowTopicSelector(true);
    setActiveTab('conversations');
  };

  const handleTopicStarterSelected = async (starter: string) => {
    // Create the conversation and send the starter message
    if (!selectedLanguage || !selectedDifficulty) return;

    try {
      const conversation = await conversationService.create(selectedLanguage, selectedDifficulty);
      setCurrentConversation(conversation);
      setShowTopicSelector(false);

      // Send the starter message immediately
      await chatService.sendMessage(conversation.id, starter, selectedLanguage, selectedDifficulty);

      await loadConversations();
    } catch (error) {
      console.error('Failed to create conversation with starter:', error);
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
        return <VocabularyScreen />;
      case 'grammar':
        return <GrammarScreen />;
      case 'conversations':
        return (
          <ConversationsScreen
            currentConversation={currentConversation}
            selectedLanguage={selectedLanguage}
            selectedDifficulty={selectedDifficulty}
            showTopicSelector={showTopicSelector}
            onTopicStarterSelected={handleTopicStarterSelected}
            onSelectConversation={handleSelectConversation}
            timezone={timezone}
            timeFormat={timeFormat}
          />
        );
      case 'assessments':
        return <AssessmentsScreen />;
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
      </header>

      <TabBar activeTab={activeTab} onTabChange={handleTabChange} />

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
