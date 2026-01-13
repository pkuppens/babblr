import React, { useCallback, useMemo, useState, useEffect, useRef } from 'react';
import { Mic, Square, Send, Volume2, Play, RotateCcw, Check } from 'lucide-react';
import type { Conversation, Message, Correction, STTCorrection } from '../types';
import { conversationService, chatService, speechService } from '../services/api';
import MessageBubble from './MessageBubble';
import { TTSControls } from './TTSControls';
import { getPreferredVoiceURI, useTTS } from '../hooks/useTTS';
import { formatLevelLabel, getDefaultTtsRateForLevel, normalizeToCefrLevel } from '../utils/cefr';
import { getStarterMessage } from '../utils/starterMessages';
import { getUIStrings } from '../utils/uiTranslations';
import { useInlineRecorder } from '../hooks/useInlineRecorder';
import type { TimeFormat } from '../services/settings';
import './ConversationInterface.css';

interface ConversationInterfaceProps {
  conversation: Conversation;
  onBack: () => void;
  timezone?: string;
  timeFormat?: TimeFormat;
}

/**
 * Format seconds to display with 1 decimal place (e.g., "5.3s")
 */
function formatDuration(seconds: number): string {
  return `${seconds.toFixed(1)}s`;
}

const ConversationInterface: React.FC<ConversationInterfaceProps> = ({
  conversation,
  onBack,
  timezone = 'UTC',
  timeFormat = '24h',
}) => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputText, setInputText] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [corrections, setCorrections] = useState<Correction[]>([]);
  const [sttCorrections, setSttCorrections] = useState<STTCorrection[]>([]);
  const [originalSttText, setOriginalSttText] = useState<string>('');
  const [correctedSttText, setCorrectedSttText] = useState<string>('');
  const [lastRecordingUrl, setLastRecordingUrl] = useState<string | null>(null);
  const [isPlayingRecording, setIsPlayingRecording] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const recordingAudioRef = useRef<HTMLAudioElement | null>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const animationRef = useRef<number | null>(null);

  // Inline recorder hook - pre-initializes microphone
  const recorder = useInlineRecorder();

  const { speak, stop, pause, resume, isSpeaking, isPaused, supported, voices, lastError } =
    useTTS();

  const [activeMessageId, setActiveMessageId] = useState<number | null>(null);
  const [lastAutoPlayedAssistantId, setLastAutoPlayedAssistantId] = useState<number | null>(null);

  const legacyRateStorageKey = 'babblr.tts.rate';
  const legacyRateCustomizedStorageKey = 'babblr.tts.rate.customized';

  const cefrLevel = useMemo(() => {
    return normalizeToCefrLevel(conversation.difficulty_level) ?? 'A1';
  }, [conversation.difficulty_level]);

  const rateStorageKey = useMemo(() => {
    return `babblr.tts.rate.${cefrLevel}`;
  }, [cefrLevel]);
  const rateCustomizedStorageKey = useMemo(() => {
    return `babblr.tts.rate.customized.${cefrLevel}`;
  }, [cefrLevel]);
  const autoPlayStorageKey = 'babblr.tts.autoPlay';
  const voiceStorageKey = useMemo(
    () => `babblr.tts.voice.${conversation.language.toLowerCase()}`,
    [conversation.language]
  );

  const [ttsRate, setTtsRate] = useState<number>(() =>
    getDefaultTtsRateForLevel(conversation.difficulty_level)
  );
  const [ttsRateCustomized, setTtsRateCustomized] = useState<boolean>(false);
  const [ttsAutoPlay, setTtsAutoPlay] = useState<boolean>(() => {
    if (typeof window === 'undefined') return false;
    return window.localStorage.getItem(autoPlayStorageKey) === 'true';
  });
  const [ttsVoiceURI, setTtsVoiceURI] = useState<string | null>(() => {
    if (typeof window === 'undefined') return null;
    return window.localStorage.getItem(voiceStorageKey);
  });

  // Pre-initialize microphone when component mounts
  useEffect(() => {
    recorder.initMicrophone();
    return () => {
      recorder.releaseMicrophone();
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Draw waveform during recording
  const drawWaveform = useCallback(() => {
    const canvas = canvasRef.current;
    const analyser = recorder.getAnalyser();

    if (!canvas || !analyser) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const bufferLength = analyser.frequencyBinCount;
    const dataArray = new Uint8Array(bufferLength);

    const draw = () => {
      if (recorder.state.status !== 'recording') {
        return;
      }

      animationRef.current = requestAnimationFrame(draw);
      analyser.getByteTimeDomainData(dataArray);

      // Clear canvas
      ctx.fillStyle = '#f3f4f6';
      ctx.fillRect(0, 0, canvas.width, canvas.height);

      // Draw waveform
      ctx.lineWidth = 2;
      ctx.strokeStyle = '#ef4444';
      ctx.beginPath();

      const sliceWidth = canvas.width / bufferLength;
      let x = 0;

      for (let i = 0; i < bufferLength; i++) {
        const v = dataArray[i] / 128.0;
        const y = (v * canvas.height) / 2;

        if (i === 0) {
          ctx.moveTo(x, y);
        } else {
          ctx.lineTo(x, y);
        }

        x += sliceWidth;
      }

      ctx.lineTo(canvas.width, canvas.height / 2);
      ctx.stroke();
    };

    draw();
  }, [recorder]);

  // Start/stop waveform animation
  useEffect(() => {
    if (recorder.state.status === 'recording') {
      drawWaveform();
    } else if (animationRef.current) {
      cancelAnimationFrame(animationRef.current);
      animationRef.current = null;
    }

    return () => {
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current);
      }
    };
  }, [recorder.state.status, drawWaveform]);

  const scrollToBottom = useCallback(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, []);

  const loadMessages = useCallback(async () => {
    try {
      const msgs = await conversationService.getMessages(conversation.id);
      console.log(
        `[ConversationInterface] Loaded ${msgs.length} messages for conversation ${conversation.id}`
      );
      if (msgs.length > 0) {
        const lastMessage = msgs[msgs.length - 1];
        console.log(
          `[ConversationInterface] Last message (ID: ${lastMessage.id}): "${lastMessage.content.substring(0, 100)}..."`
        );
      }
      setMessages(msgs);
    } catch (error) {
      console.error('Failed to load messages:', error);
    }
  }, [conversation.id]);

  useEffect(() => {
    loadMessages();
  }, [loadMessages, conversation.updated_at]); // Reload when conversation is updated

  useEffect(() => {
    // Load TTS rate per CEFR level.
    if (typeof window === 'undefined') return;

    const fallback = getDefaultTtsRateForLevel(conversation.difficulty_level);

    const stored = window.localStorage.getItem(rateStorageKey);
    const legacyStored = stored === null ? window.localStorage.getItem(legacyRateStorageKey) : null;
    const raw = stored ?? legacyStored;

    const parsed = raw !== null ? Number(raw) : fallback;
    const nextRate = Number.isFinite(parsed) ? parsed : fallback;

    const customizedFlag = window.localStorage.getItem(rateCustomizedStorageKey);
    const legacyCustomizedFlag =
      customizedFlag === null ? window.localStorage.getItem(legacyRateCustomizedStorageKey) : null;
    const rawCustomized = customizedFlag ?? legacyCustomizedFlag;

    let nextCustomized = false;
    if (rawCustomized !== null) {
      nextCustomized = rawCustomized === 'true';
    } else if (raw !== null) {
      nextCustomized = Number.isFinite(parsed) && Math.abs(parsed - 1.0) > 1e-6;
    }

    setTtsRate(nextRate);
    setTtsRateCustomized(nextCustomized);

    if (stored === null && legacyStored !== null) {
      window.localStorage.setItem(rateStorageKey, String(nextRate));
    }
    if (customizedFlag === null && legacyCustomizedFlag !== null) {
      window.localStorage.setItem(rateCustomizedStorageKey, String(nextCustomized));
    }
  }, [
    conversation.id,
    conversation.difficulty_level,
    rateStorageKey,
    rateCustomizedStorageKey,
    legacyRateStorageKey,
    legacyRateCustomizedStorageKey,
  ]);

  useEffect(() => {
    scrollToBottom();
  }, [messages, scrollToBottom]);

  useEffect(() => {
    if (typeof window === 'undefined') return;
    setTtsVoiceURI(window.localStorage.getItem(voiceStorageKey));
  }, [voiceStorageKey]);

  useEffect(() => {
    if (!supported) return;
    if (ttsVoiceURI) return;
    if (!voices || voices.length === 0) return;

    const preferred = getPreferredVoiceURI(voices, conversation.language);
    if (preferred) setTtsVoiceURI(preferred);
  }, [supported, ttsVoiceURI, voices, conversation.language]);

  useEffect(() => {
    if (typeof window === 'undefined') return;
    window.localStorage.setItem(rateStorageKey, String(ttsRate));
  }, [rateStorageKey, ttsRate]);

  useEffect(() => {
    if (typeof window === 'undefined') return;
    window.localStorage.setItem(rateCustomizedStorageKey, String(ttsRateCustomized));
  }, [rateCustomizedStorageKey, ttsRateCustomized]);

  useEffect(() => {
    if (typeof window === 'undefined') return;
    if (ttsRateCustomized) return;

    const recommended = getDefaultTtsRateForLevel(conversation.difficulty_level);
    if (Number.isFinite(recommended) && Math.abs(ttsRate - recommended) > 1e-6) {
      setTtsRate(recommended);
    }
  }, [conversation.difficulty_level, ttsRateCustomized, ttsRate]);

  useEffect(() => {
    if (typeof window === 'undefined') return;
    window.localStorage.setItem(autoPlayStorageKey, String(ttsAutoPlay));
  }, [ttsAutoPlay]);

  useEffect(() => {
    if (typeof window === 'undefined') return;
    if (ttsVoiceURI) {
      window.localStorage.setItem(voiceStorageKey, ttsVoiceURI);
    } else {
      window.localStorage.removeItem(voiceStorageKey);
    }
  }, [ttsVoiceURI, voiceStorageKey]);

  const starterMessage: Message = useMemo(
    () => ({
      id: -1,
      conversation_id: conversation.id,
      role: 'assistant',
      content: getStarterMessage(conversation.language, conversation.difficulty_level),
      created_at: conversation.created_at ?? new Date().toISOString(),
    }),
    [conversation.id, conversation.language, conversation.difficulty_level, conversation.created_at]
  );

  useEffect(() => {
    // Auto-play assistant messages when autoPlay is enabled
    if (!supported || !ttsAutoPlay) return;
    if (isSpeaking) return;

    // Determine which message to play
    let messageToPlay: Message | null = null;

    if (messages.length === 0) {
      // New conversation: play the starter message
      messageToPlay = starterMessage;
    } else {
      // Existing conversation: play the last assistant message
      const lastAssistant = [...messages].reverse().find(m => m.role === 'assistant');
      if (lastAssistant) {
        messageToPlay = lastAssistant;
      }
    }

    if (!messageToPlay) return;

    // Don't auto-play if already played this message
    if (lastAutoPlayedAssistantId !== null && messageToPlay.id <= lastAutoPlayedAssistantId) {
      return;
    }

    setActiveMessageId(messageToPlay.id);
    speak(messageToPlay.content, {
      language: conversation.language,
      rate: ttsRate,
      autoPlay: ttsAutoPlay,
      voiceURI: ttsVoiceURI ?? undefined,
    });
    setLastAutoPlayedAssistantId(messageToPlay.id);
  }, [
    messages,
    starterMessage,
    supported,
    ttsAutoPlay,
    ttsRate,
    ttsVoiceURI,
    conversation.language,
    speak,
    isSpeaking,
    lastAutoPlayedAssistantId,
  ]);

  useEffect(() => {
    if (!isSpeaking) {
      setActiveMessageId(null);
    }
  }, [isSpeaking]);

  const handleUserRateChange = (rate: number) => {
    setTtsRateCustomized(true);
    setTtsRate(rate);
  };

  // Helper to clear STT correction panel
  const clearSttCorrectionPanel = useCallback(() => {
    setSttCorrections([]);
    setOriginalSttText('');
    setCorrectedSttText('');
    if (lastRecordingUrl) {
      URL.revokeObjectURL(lastRecordingUrl);
      setLastRecordingUrl(null);
    }
  }, [lastRecordingUrl]);

  const handleSendMessage = useCallback(
    async (text: string, fromVoice: boolean = false) => {
      if (!text.trim() || isLoading) return;

      setIsLoading(true);
      setCorrections([]);

      // Clear STT corrections when sending text (not voice)
      if (!fromVoice) {
        clearSttCorrectionPanel();
      }

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

        await loadMessages();
        setInputText('');
      } catch (error) {
        console.error('Failed to send message:', error);
      } finally {
        setIsLoading(false);
      }
    },
    [
      isLoading,
      clearSttCorrectionPanel,
      conversation.id,
      conversation.language,
      conversation.difficulty_level,
      loadMessages,
    ]
  );

  const handleMicClick = () => {
    if (recorder.state.status === 'idle' || recorder.state.status === 'error') {
      // Need to initialize first
      recorder.initMicrophone().then(success => {
        if (success) {
          recorder.startRecording();
        }
      });
    } else if (recorder.state.status === 'ready') {
      recorder.startRecording();
    }
  };

  const handleStopRecording = () => {
    recorder.stopRecording();
    // Recording will be auto-submitted via useEffect when blob is ready
  };

  const handleSubmitRecording = useCallback(async () => {
    if (!recorder.state.audioBlob) return;

    console.log('[Conversation] Submitting voice recording');
    setIsLoading(true);

    // Store the recording URL for playback in STT correction panel
    if (lastRecordingUrl) {
      URL.revokeObjectURL(lastRecordingUrl);
    }
    if (recorder.state.audioUrl) {
      setLastRecordingUrl(recorder.state.audioUrl);
    }

    try {
      const transcription = await speechService.transcribe(
        recorder.state.audioBlob,
        conversation.id,
        conversation.language
      );

      // Store STT correction data
      if (transcription.corrections && transcription.corrections.length > 0) {
        setSttCorrections(transcription.corrections);
        const originalText = transcription.corrections.map(c => c.original).join(' ');
        setOriginalSttText(originalText || transcription.text);
        setCorrectedSttText(transcription.text);
      } else {
        setSttCorrections([]);
        setOriginalSttText(transcription.text);
        setCorrectedSttText(transcription.text);
      }

      // Clear recording and send message
      recorder.clearRecording();
      await handleSendMessage(transcription.text, true); // fromVoice = true
    } catch (error) {
      console.error('Failed to process voice recording:', error);
      setSttCorrections([]);
      setOriginalSttText('');
      setCorrectedSttText('');
    } finally {
      setIsLoading(false);
    }
  }, [lastRecordingUrl, conversation.id, conversation.language, handleSendMessage, recorder]);

  // Auto-submit recording when it stops (no confirmation needed for voice)
  useEffect(() => {
    if (recorder.state.status === 'stopped' && recorder.state.audioBlob && !isLoading) {
      handleSubmitRecording();
    }
  }, [recorder.state.status, recorder.state.audioBlob, isLoading, handleSubmitRecording]);

  const handleReRecord = () => {
    recorder.clearRecording();
  };

  const handlePlayRecordingPreview = () => {
    if (!recorder.state.audioUrl) return;

    if (!recordingAudioRef.current) {
      recordingAudioRef.current = new Audio(recorder.state.audioUrl);
      recordingAudioRef.current.onended = () => setIsPlayingRecording(false);
    } else {
      recordingAudioRef.current.src = recorder.state.audioUrl;
    }

    if (isPlayingRecording) {
      recordingAudioRef.current.pause();
      recordingAudioRef.current.currentTime = 0;
      setIsPlayingRecording(false);
    } else {
      recordingAudioRef.current.play();
      setIsPlayingRecording(true);
    }
  };

  const handlePlayRecording = () => {
    if (!lastRecordingUrl) return;

    if (!recordingAudioRef.current) {
      recordingAudioRef.current = new Audio(lastRecordingUrl);
    } else {
      recordingAudioRef.current.src = lastRecordingUrl;
    }

    recordingAudioRef.current.play();
  };

  const handlePlayNativeTTS = () => {
    if (!correctedSttText) return;

    speak(correctedSttText, {
      language: conversation.language,
      rate: ttsRate,
      autoPlay: false,
      voiceURI: ttsVoiceURI ?? undefined,
    });
  };

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (lastRecordingUrl) {
        URL.revokeObjectURL(lastRecordingUrl);
      }
      if (recordingAudioRef.current) {
        recordingAudioRef.current.pause();
        recordingAudioRef.current = null;
      }
    };
  }, [lastRecordingUrl]);

  // Get UI strings in the study language
  const uiStrings = useMemo(() => getUIStrings(conversation.language), [conversation.language]);

  const isRecording = recorder.state.status === 'recording';
  const hasRecording = recorder.state.status === 'stopped';

  return (
    <div className="conversation-interface">
      <div className="conversation-header">
        <div className="conversation-header-left">
          <button className="back-button" onClick={onBack}>
            ← Back
          </button>
          <div className="conversation-info">
            <h2>{conversation.language}</h2>
            <span className="difficulty-badge">
              {formatLevelLabel(conversation.difficulty_level)}
            </span>
          </div>
        </div>

        <div className="conversation-header-right">
          <TTSControls
            language={conversation.language}
            supported={supported}
            voices={voices}
            selectedVoiceURI={ttsVoiceURI}
            rate={ttsRate}
            autoPlay={ttsAutoPlay}
            isSpeaking={isSpeaking}
            isPaused={isPaused}
            lastError={lastError}
            onSelectVoiceURI={setTtsVoiceURI}
            onRateChange={handleUserRateChange}
            onAutoPlayChange={setTtsAutoPlay}
            onPause={pause}
            onResume={resume}
            onStop={stop}
          />
        </div>
      </div>

      <div className="messages-container">
        {messages.length === 0 ? (
          <MessageBubble
            message={starterMessage}
            ttsSupported={supported}
            isSpeaking={isSpeaking}
            isActive={activeMessageId === starterMessage.id}
            onPlay={textToSpeak => {
              setActiveMessageId(starterMessage.id);
              speak(textToSpeak, {
                language: conversation.language,
                rate: ttsRate,
                autoPlay: ttsAutoPlay,
                voiceURI: ttsVoiceURI ?? undefined,
              });
            }}
            timezone={timezone}
            timeFormat={timeFormat}
          />
        ) : (
          messages.map(message => (
            <MessageBubble
              key={message.id}
              message={message}
              ttsSupported={supported}
              isSpeaking={isSpeaking}
              isActive={activeMessageId === message.id}
              onPlay={textToSpeak => {
                setActiveMessageId(message.id);
                speak(textToSpeak, {
                  language: conversation.language,
                  rate: ttsRate,
                  autoPlay: ttsAutoPlay,
                  voiceURI: ttsVoiceURI ?? undefined,
                });
              }}
              timezone={timezone}
              timeFormat={timeFormat}
            />
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

      {/* STT Correction Panel - shows speech recognition corrections */}
      {sttCorrections.length > 0 && originalSttText !== correctedSttText && (
        <div className="stt-correction-panel">
          <h4>🎤 Speech Recognition Correction</h4>
          <div className="stt-correction-content">
            <div className="stt-row">
              <span className="stt-label">{uiStrings.originalStt}:</span>
              <span className="stt-original">{originalSttText}</span>
              {lastRecordingUrl && (
                <button
                  className="stt-play-button"
                  onClick={handlePlayRecording}
                  title="Play your recording"
                >
                  ▶️
                </button>
              )}
            </div>
            <div className="stt-row">
              <span className="stt-label">{uiStrings.correctedStt}:</span>
              <span className="stt-corrected">{correctedSttText}</span>
              <button
                className="stt-play-button native"
                onClick={handlePlayNativeTTS}
                title={uiStrings.listenNative}
                disabled={!supported}
              >
                <Volume2 className="w-4 h-4" />
                <span>{uiStrings.listenNative}</span>
              </button>
            </div>
            {sttCorrections.map((correction, index) => (
              <div key={index} className="stt-reason">
                <span className="stt-correction-arrow">
                  "{correction.original}" → "{correction.corrected}"
                </span>
                <span className="stt-reason-text">{correction.reason}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Grammar Corrections Panel */}
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

      {/* Inline Input Container with Recording States */}
      <div
        className={`input-container compact ${isRecording ? 'recording' : ''} ${hasRecording ? 'has-recording' : ''}`}
      >
        {/* Recording Error */}
        {recorder.state.error && <div className="recording-error">{recorder.state.error}</div>}

        {/* Idle/Ready State: Normal input */}
        {!isRecording && !hasRecording && (
          <>
            <button
              className={`mic-button ${recorder.state.permissionGranted ? 'ready' : ''}`}
              onClick={handleMicClick}
              disabled={isLoading}
              title={recorder.state.permissionGranted ? 'Start recording' : 'Enable microphone'}
            >
              <Mic className="w-5 h-5" />
            </button>

            <input
              type="text"
              className="message-input"
              placeholder={uiStrings.placeholder}
              value={inputText}
              onChange={e => setInputText(e.target.value)}
              onKeyDown={e => {
                // CTRL+Enter, CMD+Enter, or SHIFT+Enter: send message
                if (e.key === 'Enter' && (e.ctrlKey || e.metaKey || e.shiftKey)) {
                  e.preventDefault();
                  handleSendMessage(inputText);
                }
              }}
              disabled={isLoading}
            />

            <button
              className="send-button compact"
              onClick={() => handleSendMessage(inputText)}
              disabled={!inputText.trim() || isLoading}
            >
              <Send className="w-4 h-4" />
              <span>{uiStrings.send}</span>
            </button>
          </>
        )}

        {/* Recording State: Waveform and stop button */}
        {isRecording && (
          <>
            <div className="recording-indicator">
              <span className="recording-dot" />
              <span className="recording-time">{formatDuration(recorder.state.duration)}</span>
            </div>

            <canvas ref={canvasRef} width={300} height={40} className="recording-waveform" />

            <button className="stop-button" onClick={handleStopRecording} title="Stop recording">
              <Square className="w-5 h-5" fill="white" />
            </button>
          </>
        )}

        {/* Stopped State: Playback, re-record, submit */}
        {hasRecording && (
          <>
            <button
              className="playback-button"
              onClick={handlePlayRecordingPreview}
              title={isPlayingRecording ? 'Stop' : 'Play'}
            >
              <Play className="w-4 h-4" fill={isPlayingRecording ? 'currentColor' : 'none'} />
            </button>

            <div className="recording-info">
              <span className="recording-duration">{formatDuration(recorder.state.duration)}</span>
            </div>

            <button
              className="rerecord-button"
              onClick={handleReRecord}
              disabled={isLoading}
              title="Re-record"
            >
              <RotateCcw className="w-4 h-4" />
            </button>

            <button
              className="submit-recording-button"
              onClick={handleSubmitRecording}
              disabled={isLoading}
              title="Submit recording"
            >
              <Check className="w-5 h-5" />
              <span>{uiStrings.send}</span>
            </button>
          </>
        )}
      </div>
    </div>
  );
};

export default ConversationInterface;
