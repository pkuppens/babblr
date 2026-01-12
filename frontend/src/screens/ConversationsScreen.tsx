import React from 'react';
import TopicSelector from '../components/TopicSelector';
import ConversationInterface from '../components/ConversationInterface';
import type { Conversation, Language, DifficultyLevel } from '../types';
import type { TimeFormat } from '../services/settings';
import './Screen.css';

interface ConversationsScreenProps {
  currentConversation: Conversation | null;
  selectedLanguage: Language | null;
  selectedDifficulty: DifficultyLevel | null;
  showTopicSelector: boolean;
  onTopicStarterSelected: (starter: string) => Promise<void>;
  onSelectConversation: (conversation: Conversation | null) => void;
  timezone: string;
  timeFormat: TimeFormat;
}

/**
 * ConversationsScreen handles the conversation flow.
 *
 * This screen manages:
 * - Topic selection when starting a new conversation
 * - Active conversation interface
 * - Conversation state preservation across tab switches
 *
 * The conversation flow behavior is documented in docs/CONVERSATION_FLOW.md.
 */
const ConversationsScreen: React.FC<ConversationsScreenProps> = ({
  currentConversation,
  selectedLanguage,
  showTopicSelector,
  onTopicStarterSelected,
  onSelectConversation,
  timezone,
  timeFormat,
}) => {
  // Note: selectedDifficulty is kept in props for future use but not currently needed
  if (showTopicSelector && selectedLanguage) {
    return (
      <div className="screen-container">
        <TopicSelector language={selectedLanguage} onSelectStarter={onTopicStarterSelected} />
      </div>
    );
  }

  if (currentConversation) {
    return (
      <div className="screen-container">
        <ConversationInterface
          conversation={currentConversation}
          onBack={() => onSelectConversation(null)}
          timezone={timezone}
          timeFormat={timeFormat}
        />
      </div>
    );
  }

  return (
    <div className="screen-container">
      <div className="placeholder-screen">
        <h2>Conversations</h2>
        <p>Select a conversation from the Home tab to continue, or start a new conversation.</p>
      </div>
    </div>
  );
};

export default ConversationsScreen;
