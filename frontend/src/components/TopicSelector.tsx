import React, { useState, useEffect, useMemo } from 'react';
import { Search } from 'lucide-react';
import TopicCard from './TopicCard';
import ConversationStarters from './ConversationStarters';
import type { Topic, Language, DifficultyLevel } from '../types';
import { topicsService } from '../services/api';
import './TopicSelector.css';

interface TopicSelectorProps {
  language: Language;
  onSelectStarter: (starter: string) => void;
}

const RECENT_TOPICS_KEY = 'babblr_recent_topics';
const MAX_RECENT_TOPICS = 3;

const TopicSelector: React.FC<TopicSelectorProps> = ({ language, onSelectStarter }) => {
  const [topics, setTopics] = useState<Topic[]>([]);
  const [selectedTopic, setSelectedTopic] = useState<Topic | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [levelFilter, setLevelFilter] = useState<DifficultyLevel | 'all'>('all');
  const [recentTopicIds, setRecentTopicIds] = useState<string[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  // Load topics from API
  useEffect(() => {
    const loadTopics = async () => {
      try {
        setIsLoading(true);
        const data = await topicsService.getTopics();
        setTopics(data.topics);
      } catch (error) {
        console.error('Failed to load topics:', error);
      } finally {
        setIsLoading(false);
      }
    };

    loadTopics();
  }, []);

  // Load recent topics from localStorage
  useEffect(() => {
    try {
      const stored = localStorage.getItem(RECENT_TOPICS_KEY);
      if (stored) {
        setRecentTopicIds(JSON.parse(stored));
      }
    } catch (error) {
      console.error('Failed to load recent topics:', error);
    }
  }, []);

  // Save topic to recent when selected
  const handleTopicClick = (topic: Topic) => {
    setSelectedTopic(topic);

    // Update recent topics
    const newRecent = [topic.id, ...recentTopicIds.filter(id => id !== topic.id)].slice(
      0,
      MAX_RECENT_TOPICS
    );
    setRecentTopicIds(newRecent);
    try {
      localStorage.setItem(RECENT_TOPICS_KEY, JSON.stringify(newRecent));
    } catch (error) {
      console.error('Failed to save recent topics:', error);
    }
  };

  // Filter topics based on search and level
  const filteredTopics = useMemo(() => {
    return topics.filter(topic => {
      // Level filter
      if (levelFilter !== 'all' && topic.level !== levelFilter) {
        return false;
      }

      // Search filter
      if (searchQuery) {
        const query = searchQuery.toLowerCase();
        const name = topic.names[language].toLowerCase();
        const description = topic.descriptions[language].toLowerCase();
        return name.includes(query) || description.includes(query);
      }

      return true;
    });
  }, [topics, searchQuery, levelFilter, language]);

  // Get recent topics
  const recentTopics = useMemo(() => {
    return recentTopicIds
      .map(id => topics.find(t => t.id === id))
      .filter((t): t is Topic => t !== undefined);
  }, [recentTopicIds, topics]);

  if (isLoading) {
    return (
      <div className="topic-selector">
        <div className="loading-message">Loading topics...</div>
      </div>
    );
  }

  return (
    <div className="topic-selector">
      <div className="topic-selector-header">
        <h2>Choose a Conversation Topic</h2>
        <p className="topic-selector-subtitle">
          Select a scenario to start practicing {language}
        </p>
      </div>

      <div className="topic-controls">
        <div className="search-box">
          <Search size={20} />
          <input
            type="text"
            placeholder="Search topics..."
            value={searchQuery}
            onChange={e => setSearchQuery(e.target.value)}
            className="search-input"
          />
        </div>

        <select
          value={levelFilter}
          onChange={e => setLevelFilter(e.target.value as DifficultyLevel | 'all')}
          className="level-filter"
        >
          <option value="all">All Levels</option>
          <option value="A1">A1 - Beginner</option>
          <option value="A2">A2 - Elementary</option>
          <option value="B1">B1 - Intermediate</option>
          <option value="B2">B2 - Upper Intermediate</option>
          <option value="C1">C1 - Advanced</option>
          <option value="C2">C2 - Proficient</option>
        </select>
      </div>

      {recentTopics.length > 0 && (
        <div className="recent-topics-section">
          <h3>Recently Used</h3>
          <div className="topics-grid recent-grid">
            {recentTopics.map(topic => (
              <TopicCard
                key={topic.id}
                topic={topic}
                language={language}
                onClick={() => handleTopicClick(topic)}
                isRecent
              />
            ))}
          </div>
        </div>
      )}

      <div className="all-topics-section">
        {recentTopics.length > 0 && <h3>All Topics</h3>}
        <div className="topics-grid">
          {filteredTopics.map(topic => (
            <TopicCard
              key={topic.id}
              topic={topic}
              language={language}
              onClick={() => handleTopicClick(topic)}
            />
          ))}
        </div>

        {filteredTopics.length === 0 && (
          <div className="no-results">
            <p>No topics found matching your criteria.</p>
            <button onClick={() => { setSearchQuery(''); setLevelFilter('all'); }} className="reset-filters-button">
              Reset Filters
            </button>
          </div>
        )}
      </div>

      {selectedTopic && (
        <ConversationStarters
          topic={selectedTopic}
          language={language}
          onSelectStarter={onSelectStarter}
          onClose={() => setSelectedTopic(null)}
        />
      )}
    </div>
  );
};

export default TopicSelector;
