import React from 'react';
import { Home, BookOpen, FileText, MessageSquare, ClipboardCheck, Settings } from 'lucide-react';
import type { TabKey } from '../types';
import { getUIStrings } from '../utils/uiTranslations';
import './TabBar.css';

interface TabBarProps {
  activeTab: TabKey;
  onTabChange: (tab: TabKey) => void;
  language?: string;
}

interface TabConfig {
  key: TabKey;
  labelKey: keyof ReturnType<typeof getUIStrings>;
  icon: React.ReactNode;
  ariaLabelSuffix: string;
}

const TABS: TabConfig[] = [
  { key: 'home', labelKey: 'home', icon: <Home size={20} />, ariaLabelSuffix: 'tab' },
  {
    key: 'vocabulary',
    labelKey: 'vocabulary',
    icon: <BookOpen size={20} />,
    ariaLabelSuffix: 'lessons tab',
  },
  {
    key: 'grammar',
    labelKey: 'grammar',
    icon: <FileText size={20} />,
    ariaLabelSuffix: 'lessons tab',
  },
  {
    key: 'conversations',
    labelKey: 'conversations',
    icon: <MessageSquare size={20} />,
    ariaLabelSuffix: 'tab',
  },
  {
    key: 'assessments',
    labelKey: 'assessments',
    icon: <ClipboardCheck size={20} />,
    ariaLabelSuffix: 'tab',
  },
  {
    key: 'configuration',
    labelKey: 'configuration',
    icon: <Settings size={20} />,
    ariaLabelSuffix: 'settings tab',
  },
];

/**
 * TabBar component provides top-level navigation between different sections of the app.
 *
 * Features:
 * - Keyboard accessible (Arrow keys, Home, End, Enter/Space)
 * - Clear visual indication of active tab
 * - Preserves state when switching tabs
 * - Displays tabs in target language for immersion
 */
const TabBar: React.FC<TabBarProps> = ({ activeTab, onTabChange, language }) => {
  const uiStrings = getUIStrings(language || 'english');
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
          const label = uiStrings[tab.labelKey];
          const ariaLabel = `${label} ${tab.ariaLabelSuffix}`;
          return (
            <button
              key={tab.key}
              role="tab"
              aria-selected={isActive}
              aria-controls={`tabpanel-${tab.key}`}
              aria-label={ariaLabel}
              className={`tab-button ${isActive ? 'tab-button-active' : ''}`}
              onClick={() => onTabChange(tab.key)}
              onKeyDown={e => handleKeyDown(e, tab.key)}
              tabIndex={isActive ? 0 : -1}
            >
              <span className="tab-icon">{tab.icon}</span>
              <span className="tab-label">{label}</span>
            </button>
          );
        })}
      </nav>
    </div>
  );
};

export default TabBar;
