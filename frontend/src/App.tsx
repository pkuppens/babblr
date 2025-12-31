import React, { useState, useEffect } from 'react';
import LanguageSelector from './components/LanguageSelector';
import ConversationInterface from './components/ConversationInterface';
import ConversationList from './components/ConversationList';
import { conversationService } from './services/api';
import type { Conversation, Language, DifficultyLevel } from './types';
import './App.css';

function App() {
  const [currentConversation, setCurrentConversation] = useState<Conversation | null>(null);
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [showLanguageSelector, setShowLanguageSelector] = useState(true);

  useEffect(() => {
    loadConversations();
  }, []);

  const loadConversations = async () => {
    try {
      const convs = await conversationService.list();
      setConversations(convs);
    } catch (error) {
      console.error('Failed to load conversations:', error);
    }
  };

  const handleStartNewConversation = async (language: Language, difficulty: DifficultyLevel) => {
    try {
      const conversation = await conversationService.create(language, difficulty);
      setCurrentConversation(conversation);
      setShowLanguageSelector(false);
      await loadConversations();
    } catch (error) {
      console.error('Failed to create conversation:', error);
      alert('Failed to create conversation. Make sure the backend is running.');
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
        <h1 onClick={handleBackToHome} style={{ cursor: 'pointer' }}>
          🗣️ Babblr
        </h1>
        <p className="app-subtitle">Learn languages naturally through conversation</p>
      </header>

      <main className="app-main">
        {showLanguageSelector ? (
          <div className="home-container">
            <LanguageSelector onStart={handleStartNewConversation} />
            <ConversationList
              conversations={conversations}
              onSelect={handleSelectConversation}
              onDelete={async (id) => {
                await conversationService.delete(id);
                await loadConversations();
              }}
            />
          </div>
        ) : currentConversation ? (
          <ConversationInterface
            conversation={currentConversation}
            onBack={handleBackToHome}
          />
        ) : null}
      </main>
    </div>
  );
}

export default App;
