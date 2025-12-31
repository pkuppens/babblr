import React from 'react';
import type { Conversation } from '../types';
import './ConversationList.css';

interface ConversationListProps {
  conversations: Conversation[];
  onSelect: (conversation: Conversation) => void;
  onDelete: (id: number) => void;
}

const ConversationList: React.FC<ConversationListProps> = ({
  conversations,
  onSelect,
  onDelete,
}) => {
  if (conversations.length === 0) {
    return null;
  }

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  const getLanguageFlag = (language: string) => {
    const flags: { [key: string]: string } = {
      spanish: '🇪🇸',
      italian: '🇮🇹',
      german: '🇩🇪',
      french: '🇫🇷',
      dutch: '🇳🇱',
    };
    return flags[language.toLowerCase()] || '🌐';
  };

  return (
    <div className="conversation-list">
      <h2>Recent Conversations</h2>
      <div className="conversation-cards">
        {conversations.map((conv) => (
          <div key={conv.id} className="conversation-card">
            <div className="conversation-info" onClick={() => onSelect(conv)}>
              <div className="conversation-header">
                <span className="flag">{getLanguageFlag(conv.language)}</span>
                <span className="language">{conv.language}</span>
                <span className="difficulty">{conv.difficulty_level}</span>
              </div>
              <div className="conversation-date">
                {formatDate(conv.updated_at)}
              </div>
            </div>
            <button
              className="delete-button"
              onClick={(e) => {
                e.stopPropagation();
                if (window.confirm('Delete this conversation?')) {
                  onDelete(conv.id);
                }
              }}
            >
              🗑️
            </button>
          </div>
        ))}
      </div>
    </div>
  );
};

export default ConversationList;
