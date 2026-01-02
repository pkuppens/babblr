import React, { useRef, useEffect, useState } from 'react';
import { Mic, Square, Play, Pause, RotateCcw, Send } from 'lucide-react';
import { useAudioRecorder } from '../hooks/useAudioRecorder';

/**
 * Props for the AudioRecorder component
 */
export interface AudioRecorderProps {
  /** Callback when audio recording is ready to submit */
  onSubmit: (audioBlob: Blob) => void;
  /** Whether the component is disabled (e.g., during loading) */
  disabled?: boolean;
}

/**
 * Format seconds to MM:SS
 */
function formatTime(seconds: number): string {
  const mins = Math.floor(seconds / 60);
  const secs = Math.floor(seconds % 60);
  return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
}

/**
 * AudioRecorder Component
 * 
 * A full-featured audio recording component with visual feedback, waveform visualization,
 * and playback controls. Inspired by iOS Voice Memos.
 * 
 * Features:
 * - Large circular record button that changes to stop when recording
 * - Pulsing animation while recording
 * - Real-time waveform visualization using Canvas
 * - Timer display in MM:SS format
 * - Maximum recording length: 60 seconds (auto-stop)
 * - Playback controls (play/pause)
 * - Re-record and Submit buttons
 * - Error handling for microphone issues
 * - Fully accessible with keyboard navigation and ARIA labels
 * 
 * @param {AudioRecorderProps} props - Component props
 * @returns {JSX.Element} Audio recorder component
 * 
 * @example
 * ```tsx
 * <AudioRecorder
 *   onSubmit={(blob) => handleAudioSubmit(blob)}
 *   disabled={isLoading}
 * />
 * ```
 */
const AudioRecorder: React.FC<AudioRecorderProps> = ({ onSubmit, disabled = false }) => {
  const { state, startRecording, stopRecording, clearRecording, getAnalyser } = useAudioRecorder();
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const animationRef = useRef<number | null>(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const audioRef = useRef<HTMLAudioElement | null>(null);

  /**
   * Draw waveform visualization on canvas
   */
  const drawWaveform = () => {
    const canvas = canvasRef.current;
    const analyser = getAnalyser();
    
    if (!canvas || !analyser) {
      return;
    }

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const bufferLength = analyser.frequencyBinCount;
    const dataArray = new Uint8Array(bufferLength);

    const draw = () => {
      if (state.status !== 'recording') {
        return;
      }

      animationRef.current = requestAnimationFrame(draw);

      analyser.getByteTimeDomainData(dataArray);

      // Clear canvas
      ctx.fillStyle = 'rgb(243, 244, 246)'; // bg-gray-100
      ctx.fillRect(0, 0, canvas.width, canvas.height);

      // Draw waveform
      ctx.lineWidth = 2;
      ctx.strokeStyle = 'rgb(239, 68, 68)'; // red-500
      ctx.beginPath();

      const sliceWidth = (canvas.width * 1.0) / bufferLength;
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
  };

  /**
   * Start waveform visualization when recording starts
   */
  useEffect(() => {
    if (state.status === 'recording') {
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
  }, [state.status]); // eslint-disable-line react-hooks/exhaustive-deps

  /**
   * Handle main record/stop button click
   */
  const handleRecordClick = async () => {
    if (state.status === 'idle' || state.status === 'error') {
      await startRecording();
    } else if (state.status === 'recording') {
      stopRecording();
    }
  };

  /**
   * Handle playback toggle
   */
  const handlePlaybackToggle = () => {
    if (!state.audioUrl) return;

    if (!audioRef.current) {
      audioRef.current = new Audio(state.audioUrl);
      audioRef.current.addEventListener('ended', () => {
        setIsPlaying(false);
      });
    }

    if (isPlaying) {
      audioRef.current.pause();
      setIsPlaying(false);
    } else {
      audioRef.current.play();
      setIsPlaying(true);
    }
  };

  /**
   * Handle re-record button click
   */
  const handleReRecord = () => {
    if (audioRef.current) {
      audioRef.current.pause();
      audioRef.current = null;
    }
    setIsPlaying(false);
    clearRecording();
  };

  /**
   * Handle submit button click
   */
  const handleSubmit = () => {
    console.log('🎙️ Submitting audio recording, blob size:', state.audioBlob?.size, 'bytes');
    
    if (state.audioBlob) {
      if (audioRef.current) {
        audioRef.current.pause();
        audioRef.current = null;
      }
      setIsPlaying(false);
      onSubmit(state.audioBlob);
      clearRecording();
    }
  };

  /**
   * Cleanup audio element on unmount
   */
  useEffect(() => {
    return () => {
      if (audioRef.current) {
        audioRef.current.pause();
        audioRef.current = null;
      }
    };
  }, []);

  const isRecording = state.status === 'recording';
  const hasRecording = state.status === 'stopped';
  const isDisabled = disabled || state.status === 'recording';

  return (
    <div className="audio-recorder w-full max-w-md mx-auto">
      {/* Error Display */}
      {state.error && (
        <div 
          className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg text-red-800 text-sm"
          role="alert"
          aria-live="assertive"
        >
          <strong className="font-semibold">Error:</strong> {state.error}
        </div>
      )}

      {/* Main Recording Area */}
      <div className="recording-area bg-white rounded-2xl shadow-lg p-6 mb-4">
        {/* Timer */}
        <div className="text-center mb-4">
          <div 
            className="text-3xl font-mono font-semibold text-gray-800"
            aria-live="polite"
            aria-label={`Recording duration: ${formatTime(state.duration)}`}
          >
            {formatTime(state.duration)}
          </div>
          {isRecording && (
            <div className="text-sm text-gray-500 mt-1">
              Recording... (max 60 seconds)
            </div>
          )}
        </div>

        {/* Waveform Canvas */}
        <div className="waveform-container mb-6 bg-gray-100 rounded-lg overflow-hidden">
          <canvas
            ref={canvasRef}
            width={400}
            height={100}
            className="w-full"
            aria-label="Audio waveform visualization"
          />
        </div>

        {/* Record/Stop Button */}
        <div className="flex justify-center mb-4">
          <button
            onClick={handleRecordClick}
            disabled={disabled || hasRecording}
            className={`
              record-button
              w-20 h-20 rounded-full
              flex items-center justify-center
              transition-all duration-300
              focus:outline-none focus:ring-4 focus:ring-offset-2
              disabled:opacity-50 disabled:cursor-not-allowed
              ${
                isRecording
                  ? 'bg-red-500 hover:bg-red-600 focus:ring-red-300 animate-pulse-ring'
                  : 'bg-green-500 hover:bg-green-600 focus:ring-green-300 hover:scale-105'
              }
            `}
            aria-label={isRecording ? 'Stop recording' : 'Start recording'}
            aria-pressed={isRecording}
          >
            {isRecording ? (
              <Square className="w-8 h-8 text-white" fill="white" />
            ) : (
              <Mic className="w-8 h-8 text-white" />
            )}
          </button>
        </div>

        {/* Status Text */}
        <div className="text-center text-sm text-gray-600">
          {state.status === 'idle' && 'Press the microphone to start recording'}
          {state.status === 'recording' && 'Recording in progress...'}
          {state.status === 'stopped' && 'Recording complete'}
        </div>
      </div>

      {/* Playback and Action Controls */}
      {hasRecording && (
        <div className="controls-area bg-white rounded-2xl shadow-lg p-6">
          <div className="text-sm text-gray-600 mb-4 text-center">
            Review your recording before submitting
          </div>

          {/* Playback Button */}
          <div className="flex justify-center mb-4">
            <button
              onClick={handlePlaybackToggle}
              disabled={isDisabled}
              className="
                playback-button
                w-16 h-16 rounded-full
                bg-blue-500 hover:bg-blue-600
                flex items-center justify-center
                transition-all duration-300
                focus:outline-none focus:ring-4 focus:ring-blue-300 focus:ring-offset-2
                disabled:opacity-50 disabled:cursor-not-allowed
                hover:scale-105
              "
              aria-label={isPlaying ? 'Pause playback' : 'Play recording'}
            >
              {isPlaying ? (
                <Pause className="w-6 h-6 text-white" fill="white" />
              ) : (
                <Play className="w-6 h-6 text-white" fill="white" />
              )}
            </button>
          </div>

          {/* Re-record and Submit Buttons */}
          <div className="flex gap-3">
            <button
              onClick={handleReRecord}
              disabled={isDisabled}
              className="
                flex-1
                px-4 py-3 rounded-lg
                bg-gray-200 hover:bg-gray-300
                text-gray-800 font-medium
                transition-colors duration-200
                focus:outline-none focus:ring-4 focus:ring-gray-300 focus:ring-offset-2
                disabled:opacity-50 disabled:cursor-not-allowed
                flex items-center justify-center gap-2
              "
              aria-label="Re-record audio"
            >
              <RotateCcw className="w-5 h-5" />
              Re-record
            </button>

            <button
              onClick={handleSubmit}
              disabled={isDisabled}
              className="
                flex-1
                px-4 py-3 rounded-lg
                bg-green-500 hover:bg-green-600
                text-white font-medium
                transition-colors duration-200
                focus:outline-none focus:ring-4 focus:ring-green-300 focus:ring-offset-2
                disabled:opacity-50 disabled:cursor-not-allowed
                flex items-center justify-center gap-2
              "
              aria-label="Submit recording"
            >
              <Send className="w-5 h-5" />
              Submit
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default AudioRecorder;
