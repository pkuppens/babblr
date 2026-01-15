import React from 'react';
import { Home, BookOpen, FileText, MessageSquare, ClipboardCheck, Settings } from 'lucide-react';
import type { TabKey } from '../types';
import './TabBar.css';

interface TabBarProps {
  activeTab: TabKey;
  onTabChange: (tab: TabKey) => void;
}

interface TabConfig {
  key: TabKey;
  label: string;
  icon: React.ReactNode;
  ariaLabel: string;
}

const TABS: TabConfig[] = [
  { key: 'home', label: 'Home', icon: <Home size={20} />, ariaLabel: 'Home tab' },
  {
    key: 'vocabulary',
    label: 'Vocabulary',
    icon: <BookOpen size={20} />,
    ariaLabel: 'Vocabulary lessons tab',
  },
  {
    key: 'grammar',
    label: 'Grammar',
    icon: <FileText size={20} />,
    ariaLabel: 'Grammar lessons tab',
  },
  {
    key: 'conversations',
    label: 'Conversations',
    icon: <MessageSquare size={20} />,
    ariaLabel: 'Conversations tab',
  },
  {
    key: 'assessments',
    label: 'Assessments',
    icon: <ClipboardCheck size={20} />,
    ariaLabel: 'CEFR assessments tab',
  },
  {
    key: 'configuration',
    label: 'Configuration',
    icon: <Settings size={20} />,
    ariaLabel: 'Configuration settings tab',
  },
];

/**
 * TabBar component provides top-level navigation between different sections of the app.
 *
 * Features:
 * - Keyboard accessible (Arrow keys, Home, End, Enter/Space)
 * - Clear visual indication of active tab
 * - Preserves state when switching tabs
 */
const TabBar: React.FC<TabBarProps> = ({ activeTab, onTabChange }) => {
  const handleKeyDown = (event: React.KeyboardEvent<HTMLButtonElement>, tabKey: TabKey) => {
    const currentIndex = TABS.findIndex(tab => tab.key === activeTab);
    let newIndex = currentIndex;

    switch (event.key) {
      case 'ArrowLeft':
        event.preventDefault();
        newIndex = currentIndex > 0 ? currentIndex - 1 : TABS.length - 1;
        onTabChange(TABS[newIndex].key);
        break;
      case 'ArrowRight':
        event.preventDefault();
        newIndex = currentIndex < TABS.length - 1 ? currentIndex + 1 : 0;
        onTabChange(TABS[newIndex].key);
        break;
      case 'Home':
        event.preventDefault();
        onTabChange(TABS[0].key);
        break;
      case 'End':
        event.preventDefault();
        onTabChange(TABS[TABS.length - 1].key);
        break;
      case 'Enter':
      case ' ':
        event.preventDefault();
        onTabChange(tabKey);
        break;
    }
  };

  return (
    <div className="tab-bar-wrapper">
      <nav className="tab-bar" role="tablist" aria-label="Main navigation">
        {TABS.map(tab => {
          const isActive = tab.key === activeTab;
          return (
            <button
              key={tab.key}
              role="tab"
              aria-selected={isActive}
              aria-controls={`tabpanel-${tab.key}`}
              aria-label={tab.ariaLabel}
              className={`tab-button ${isActive ? 'tab-button-active' : ''}`}
              onClick={() => onTabChange(tab.key)}
              onKeyDown={e => handleKeyDown(e, tab.key)}
              tabIndex={isActive ? 0 : -1}
            >
              <span className="tab-icon">{tab.icon}</span>
              <span className="tab-label">{tab.label}</span>
            </button>
          );
        })}
      </nav>
    </div>
  );
};

export default TabBar;
