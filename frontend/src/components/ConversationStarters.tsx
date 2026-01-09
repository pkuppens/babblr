import React from 'react';
import { X } from 'lucide-react';
import type { Topic, Language } from '../types';
import './ConversationStarters.css';

interface ConversationStartersProps {
  topic: Topic;
  language: Language;
  onSelectStarter: (starter: string) => void;
  onClose: () => void;
}

const ConversationStarters: React.FC<ConversationStartersProps> = ({
  topic,
  language,
  onSelectStarter,
  onClose,
}) => {
  const starters = topic.starters[language] || [];
  const topicName = topic.names[language];

  return (
    <div className="conversation-starters-overlay" onClick={onClose}>
      <div className="conversation-starters-modal" onClick={e => e.stopPropagation()}>
        <div className="starters-header">
          <div className="starters-title-row">
            <span className="starters-icon">{topic.icon}</span>
            <h2 className="starters-title">{topicName}</h2>
          </div>
          <button className="starters-close-button" onClick={onClose} aria-label="Close">
            <X size={24} />
          </button>
        </div>

        <div className="starters-content">
          <p className="starters-instruction">Click a phrase to start your conversation:</p>
          <div className="starters-list">
            {starters.map((starter, index) => (
              <button
                key={index}
                className="starter-button"
                onClick={() => {
                  onSelectStarter(starter);
                  onClose();
                }}
              >
                {starter}
              </button>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default ConversationStarters;
