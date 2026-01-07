import { useState, useEffect } from 'react';
import LanguageSelector from './components/LanguageSelector';
import ConversationInterface from './components/ConversationInterface';
import ConversationList from './components/ConversationList';
import Settings from './components/Settings';
import { conversationService } from './services/api';
import { settingsService, type TimeFormat } from './services/settings';
import type { Conversation, Language, DifficultyLevel } from './types';
import { Settings as SettingsIcon } from 'lucide-react';
import './App.css';

function App() {
  const [currentConversation, setCurrentConversation] = useState<Conversation | null>(null);
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [showLanguageSelector, setShowLanguageSelector] = useState(true);
  const [showSettings, setShowSettings] = useState(false);

  // Display settings
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
    try {
      const conversation = await conversationService.create(language, difficulty);
      setCurrentConversation(conversation);
      setShowLanguageSelector(false);
      await loadConversations();
    } catch (error) {
      // Error is already handled by errorHandler in api.ts
      console.error('Failed to create conversation:', error);
    }
  };

  const handleSelectConversation = (conversation: Conversation) => {
    setCurrentConversation(conversation);
    setShowLanguageSelector(false);
  };

  const handleBackToHome = () => {
    setCurrentConversation(null);
    setShowLanguageSelector(true);
    loadConversations();
  };

  return (
    <div className="app">
      <header className="app-header">
        <div className="app-header-left">
          <h1 onClick={handleBackToHome} style={{ cursor: 'pointer' }}>
            🗣️ Babblr
          </h1>
        </div>
        <p className="app-subtitle">Learn languages naturally through conversation</p>
        <button
          className="settings-button-header"
          onClick={() => setShowSettings(true)}
          aria-label="Open settings"
        >
          <SettingsIcon size={24} />
        </button>
      </header>

      <main className="app-main">
        {showLanguageSelector ? (
          <div className="home-container">
            <LanguageSelector onStart={handleStartNewConversation} />
            <ConversationList
              conversations={conversations}
              onSelect={handleSelectConversation}
              onDelete={async id => {
                await conversationService.delete(id);
                await loadConversations();
              }}
              timezone={timezone}
              timeFormat={timeFormat}
            />
          </div>
        ) : currentConversation ? (
          <ConversationInterface
            conversation={currentConversation}
            onBack={handleBackToHome}
            timezone={timezone}
            timeFormat={timeFormat}
          />
        ) : null}
      </main>

      <Settings
        isOpen={showSettings}
        onClose={() => {
          setShowSettings(false);
          loadDisplaySettings(); // Reload settings when modal closes
        }}
      />
    </div>
  );
}

export default App;
