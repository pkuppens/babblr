import React from 'react';
import type { Message } from '../types';
import { formatTime } from '../utils/dateTime';
import type { TimeFormat } from '../services/settings';
import './MessageBubble.css';

interface MessageBubbleProps {
  message: Message;
  ttsSupported?: boolean;
  isSpeaking?: boolean;
  isActive?: boolean;
  onPlay?: (text: string) => void;
  timezone?: string;
  timeFormat?: TimeFormat;
}

const MessageBubble: React.FC<MessageBubbleProps> = ({
  message,
  ttsSupported = false,
  isSpeaking = false,
  isActive = false,
  onPlay,
  timezone = 'UTC',
  timeFormat = '24h',
}) => {
  return (
    <div className={`message ${message.role}`}>
      <div className="message-content">
        <div className="message-content-row">
          <div className="message-text">{message.content}</div>

          {ttsSupported && (
            <div className="message-actions">
              <button
                type="button"
                className={`tts-message-button ${isActive && isSpeaking ? 'active' : ''}`}
                onClick={() => onPlay?.(message.content)}
                aria-label="Play this message with text-to-speech"
                title="Play"
              >
                {isActive && isSpeaking ? 'Speaking…' : 'Play'}
              </button>
            </div>
          )}
        </div>
      </div>
      <div className="message-time">{formatTime(message.created_at, timezone, timeFormat)}</div>
    </div>
  );
};

export default MessageBubble;
