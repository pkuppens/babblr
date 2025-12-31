import React, { useState, useEffect, useRef } from 'react';
import type { Conversation, Message, Correction } from '../types';
import { conversationService, chatService, speechService, ttsService } from '../services/api';
import VoiceRecorder from './VoiceRecorder';
import MessageBubble from './MessageBubble';
import './ConversationInterface.css';

interface ConversationInterfaceProps {
  conversation: Conversation;
  onBack: () => void;
}

const ConversationInterface: React.FC<ConversationInterfaceProps> = ({
  conversation,
  onBack,
}) => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputText, setInputText] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [corrections, setCorrections] = useState<Correction[]>([]);
  const [isRecording, setIsRecording] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    loadMessages();
  }, [conversation.id]);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const loadMessages = async () => {
    try {
      const msgs = await conversationService.getMessages(conversation.id);
      setMessages(msgs);
    } catch (error) {
      console.error('Failed to load messages:', error);
    }
  };

  const handleSendMessage = async (text: string) => {
    if (!text.trim() || isLoading) return;

    setIsLoading(true);
    setCorrections([]);

    try {
      const response = await chatService.sendMessage(
        conversation.id,
        text,
        conversation.language,
        conversation.difficulty_level
      );

      if (response.corrections && response.corrections.length > 0) {
        setCorrections(response.corrections);
      }

      // Reload messages to get the updated conversation
      await loadMessages();

      // Play TTS for assistant response
      try {
        const audioBlob = await ttsService.synthesize(
          response.assistant_message,
          conversation.language
        );
        const audio = new Audio(URL.createObjectURL(audioBlob));
        audio.play();
      } catch (ttsError) {
        console.error('TTS not available:', ttsError);
      }

      setInputText('');
    } catch (error) {
      console.error('Failed to send message:', error);
      alert('Failed to send message. Please check your API configuration.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleVoiceRecording = async (audioBlob: Blob) => {
    setIsLoading(true);
    try {
      const transcription = await speechService.transcribe(
        audioBlob,
        conversation.id,
        conversation.language
      );

      // Use the transcribed text
      await handleSendMessage(transcription.text);
    } catch (error) {
      console.error('Failed to process voice recording:', error);
      alert('Failed to process voice recording.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="conversation-interface">
      <div className="conversation-header">
        <button className="back-button" onClick={onBack}>
          ← Back
        </button>
        <div className="conversation-info">
          <h2>{conversation.language}</h2>
          <span className="difficulty-badge">{conversation.difficulty_level}</span>
        </div>
      </div>

      <div className="messages-container">
        {messages.length === 0 ? (
          <div className="empty-state">
            <p>👋 Start your conversation!</p>
            <p>Try introducing yourself or asking a question.</p>
          </div>
        ) : (
          messages.map((message) => (
            <MessageBubble key={message.id} message={message} />
          ))
        )}
        {isLoading && (
          <div className="message assistant">
            <div className="message-content loading">
              <span className="dot">.</span>
              <span className="dot">.</span>
              <span className="dot">.</span>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {corrections.length > 0 && (
        <div className="corrections-panel">
          <h4>💡 Helpful Corrections</h4>
          {corrections.map((correction, index) => (
            <div key={index} className="correction-item">
              <div className="correction-type">{correction.type}</div>
              <div className="correction-text">
                <span className="original">{correction.original}</span>
                <span className="arrow">→</span>
                <span className="corrected">{correction.corrected}</span>
              </div>
              <div className="correction-explanation">{correction.explanation}</div>
            </div>
          ))}
        </div>
      )}

      <div className="input-container">
        <VoiceRecorder
          onRecordingComplete={handleVoiceRecording}
          isRecording={isRecording}
          setIsRecording={setIsRecording}
          disabled={isLoading}
        />
        
        <input
          type="text"
          className="message-input"
          placeholder="Type your message or use voice..."
          value={inputText}
          onChange={(e) => setInputText(e.target.value)}
          onKeyPress={(e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
              e.preventDefault();
              handleSendMessage(inputText);
            }
          }}
          disabled={isLoading || isRecording}
        />
        
        <button
          className="send-button"
          onClick={() => handleSendMessage(inputText)}
          disabled={!inputText.trim() || isLoading || isRecording}
        >
          Send
        </button>
      </div>
    </div>
  );
};

export default ConversationInterface;
