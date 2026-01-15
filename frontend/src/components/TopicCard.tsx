import React from 'react';
import type { Topic, Language } from '../types';
import './TopicCard.css';

interface TopicCardProps {
  topic: Topic;
  language: Language;
  onClick: () => void;
  isRecent?: boolean;
}

const TopicCard: React.FC<TopicCardProps> = ({ topic, language, onClick, isRecent = false }) => {
  const name = topic.names[language];
  const description = topic.descriptions[language];

  return (
    <button
      className={`topic-card ${isRecent ? 'recent' : ''}`}
      onClick={onClick}
      data-testid={`topic-card-${topic.id}`}
    >
      <div className="topic-icon">{topic.icon}</div>
      <div className="topic-content">
        <h3 className="topic-name">{name}</h3>
        <p className="topic-description">{description}</p>
      </div>
      <div className="topic-level-badge">{topic.level}</div>
    </button>
  );
};

export default TopicCard;
