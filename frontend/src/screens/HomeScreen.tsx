import React from 'react';
import LanguageSelector from '../components/LanguageSelector';
import ConversationList from '../components/ConversationList';
import type { Conversation, Language, DifficultyLevel } from '../types';
import type { TimeFormat } from '../services/settings';
import './Screen.css';

interface HomeScreenProps {
  onStartNewConversation: (language: Language, difficulty: DifficultyLevel) => void;
  conversations: Conversation[];
  onSelectConversation: (conversation: Conversation) => void;
  onDeleteConversation: (id: number) => Promise<void>;
  timezone: string;
  timeFormat: TimeFormat;
}

/**
 * HomeScreen displays the language selector and conversation list.
 *
 * This is the default landing screen where users can:
 * - Select a language and difficulty level to start a new conversation
 * - View and select from their existing conversations
 *
 * Future: This screen will also host the progress dashboard (issue #11).
 */
const HomeScreen: React.FC<HomeScreenProps> = ({
  onStartNewConversation,
  conversations,
  onSelectConversation,
  onDeleteConversation,
  timezone,
  timeFormat,
}) => {
  return (
    <div className="screen-container">
      <div className="home-container">
        <LanguageSelector onStart={onStartNewConversation} />
        <ConversationList
          conversations={conversations}
          onSelect={onSelectConversation}
          onDelete={onDeleteConversation}
          timezone={timezone}
          timeFormat={timeFormat}
        />
      </div>
    </div>
  );
};

export default HomeScreen;
