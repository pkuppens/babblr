import React from 'react';
import Settings from '../components/Settings';
import './Screen.css';

interface ConfigurationScreenProps {
  isOpen: boolean;
  onClose: () => void;
  // Note: isOpen and onClose are kept for compatibility but not used in inline mode
}

/**
 * ConfigurationScreen displays application settings inline.
 *
 * This screen hosts the Settings component for configuring:
 * - Timezone and time format preferences
 * - LLM provider and API keys
 * - Other application settings (as they are added)
 *
 * Settings are displayed inline within the screen-container, not as a modal.
 */
const ConfigurationScreen: React.FC<ConfigurationScreenProps> = ({ onClose }) => {
  return (
    <div className="screen-container">
      <div className="configuration-screen">
        <Settings isOpen={true} onClose={onClose} inline={true} />
      </div>
    </div>
  );
};

export default ConfigurationScreen;
